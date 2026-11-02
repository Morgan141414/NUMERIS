"""Bounded, fail-closed analysis of paired primary endpoints.

The helper consumes already materialised paired seed records.  It is an
analysis layer, not a solver and not a scientific claim generator.  A record
has the following shape::

    {
        "seed": 7,
        "truth_parameters": [1.0, 0.1, 0.2],
        "reference_likelihood": 12.5,
        "baseline": {"success": True, "budget": {"within_budget": True},
                     "negative_log_likelihood": 12.6,
                     "parameter_estimate": [...]},
        "candidate": { ... }
    }

Missing, failed, and over-budget rows are retained.  They cannot contribute
to paired endpoint estimates, and they continue to contribute to rates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from numeris.inference.metrics import likelihood_distortion, parameter_rmse


_MISSING = object()


@dataclass(frozen=True)
class PrimaryEndpointConditions:
    """Predeclared pass/fail thresholds for the bounded decision rule."""

    min_comparable_pairs: int = 10
    max_failure_rate: float = 0.0
    max_budget_rate: float = 0.0
    max_paired_mean_difference: float = 0.0
    confidence: float = 0.95
    bootstrap_resamples: int = 2000
    bootstrap_seed: int = 0
    require_all_endpoints: bool = True

    def __post_init__(self) -> None:
        if self.min_comparable_pairs < 1:
            raise ValueError("min_comparable_pairs must be positive")
        for name in ("max_failure_rate", "max_budget_rate"):
            value = float(getattr(self, name))
            if not 0 <= value <= 1 or not np.isfinite(value):
                raise ValueError(f"{name} must be finite in [0, 1]")
        if not np.isfinite(self.max_paired_mean_difference):
            raise ValueError("max_paired_mean_difference must be finite")
        if not 0 < self.confidence < 1:
            raise ValueError("confidence must be between zero and one")
        if self.bootstrap_resamples < 100:
            raise ValueError("bootstrap_resamples must be at least 100")
        if self.bootstrap_seed < 0:
            raise ValueError("bootstrap_seed must be non-negative")

    def as_dict(self) -> dict[str, Any]:
        return {
            "min_comparable_pairs": int(self.min_comparable_pairs),
            "max_failure_rate": float(self.max_failure_rate),
            "max_budget_rate": float(self.max_budget_rate),
            "max_paired_mean_difference": float(self.max_paired_mean_difference),
            "confidence": float(self.confidence),
            "bootstrap_resamples": int(self.bootstrap_resamples),
            "bootstrap_seed": int(self.bootstrap_seed),
            "require_all_endpoints": bool(self.require_all_endpoints),
        }


def _conditions(value: PrimaryEndpointConditions | Mapping[str, Any] | None) -> tuple[PrimaryEndpointConditions, bool]:
    if value is None:
        return PrimaryEndpointConditions(), False
    if isinstance(value, PrimaryEndpointConditions):
        return value, True
    return PrimaryEndpointConditions(**dict(value)), True


def _value(mapping: Mapping[str, Any], *paths: tuple[str, ...]) -> Any:
    for path in paths:
        current: Any = mapping
        for key in path:
            if not isinstance(current, Mapping) or key not in current:
                current = _MISSING
                break
            current = current[key]
        if current is not _MISSING:
            return current
    return _MISSING


def _finite_scalar(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if np.isfinite(result) else None


def _finite_vector(value: Any) -> np.ndarray | None:
    try:
        result = np.asarray(value, dtype=float)
    except (TypeError, ValueError):
        return None
    if result.size == 0 or not np.all(np.isfinite(result)):
        return None
    return result


def _trial_status(trial: Any) -> tuple[bool, bool]:
    if not isinstance(trial, Mapping):
        return False, False
    success = bool(trial.get("success", False))
    budget = _value(trial, ("budget", "within_budget"), ("within_budget",))
    within_budget = budget is True or (isinstance(budget, (bool, np.bool_)) and bool(budget))
    return success, within_budget


def _likelihood(trial: Mapping[str, Any]) -> float | None:
    value = _value(
        trial,
        ("likelihood", "negative_log_likelihood"),
        ("negative_log_likelihood",),
        ("likelihood",),
    )
    return None if value is _MISSING else _finite_scalar(value)


def _parameters(trial: Mapping[str, Any]) -> np.ndarray | None:
    value = _value(
        trial,
        ("parameter_estimate",),
        ("parameters",),
        ("estimate",),
        ("params",),
    )
    return None if value is _MISSING else _finite_vector(value)


def _bootstrap_ci(values: Sequence[float], conditions: PrimaryEndpointConditions) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        return {"available": False, "n": int(array.size), "low": None, "high": None}
    rng = np.random.default_rng(conditions.bootstrap_seed)
    indices = rng.integers(0, array.size, size=(conditions.bootstrap_resamples, array.size))
    means = np.mean(array[indices], axis=1)
    alpha = (1.0 - conditions.confidence) / 2.0
    return {
        "available": True,
        "n": int(array.size),
        "low": float(np.quantile(means, alpha)),
        "high": float(np.quantile(means, 1.0 - alpha)),
        "confidence": float(conditions.confidence),
        "resamples": int(conditions.bootstrap_resamples),
        "seed": int(conditions.bootstrap_seed),
    }


def _metric_summary(values: Sequence[float]) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return {"n": 0, "mean": None, "values": []}
    return {"n": int(array.size), "mean": float(np.mean(array)), "values": [float(v) for v in array]}


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 1.0


def build_primary_endpoint_report(
    paired_records: Iterable[Mapping[str, Any]],
    *,
    conditions: PrimaryEndpointConditions | Mapping[str, Any] | None = None,
    parameter_truth: Sequence[float] | None = None,
    reference_likelihood: float | None = None,
    baseline_label: str = "baseline",
    candidate_label: str = "candidate",
) -> dict[str, Any]:
    """Compute bounded paired endpoints and an explicit fail-closed decision.

    Lower is better for likelihood distortion, parameter RMSE, and their
    paired candidate-minus-baseline differences.  ``CONFIRMED_ADVANTAGE`` is
    emitted only when caller-supplied predeclared conditions exist and every
    required condition passes.  The report itself makes no scientific claim.
    """
    if baseline_label == candidate_label:
        raise ValueError("baseline_label and candidate_label must differ")
    selected, predeclared = _conditions(conditions)
    fallback_truth = _finite_vector(parameter_truth) if parameter_truth is not None else None
    if parameter_truth is not None and fallback_truth is None:
        raise ValueError("parameter_truth must be finite and non-empty")
    fallback_reference = _finite_scalar(reference_likelihood)
    if reference_likelihood is not None and fallback_reference is None:
        raise ValueError("reference_likelihood must be a finite scalar")

    rows: list[dict[str, Any]] = []
    endpoint_values: dict[str, dict[str, list[float]]] = {
        "likelihood_distortion": {baseline_label: [], candidate_label: []},
        "parameter_rmse": {baseline_label: [], candidate_label: []},
    }
    paired_differences = {name: [] for name in endpoint_values}
    failure_counts = {baseline_label: 0, candidate_label: 0}
    budget_counts = {baseline_label: 0, candidate_label: 0}
    total = 0

    for record in paired_records:
        total += 1
        if not isinstance(record, Mapping):
            record = {}
        baseline = record.get(baseline_label)
        candidate = record.get(candidate_label)
        baseline_success, baseline_budget = _trial_status(baseline)
        candidate_success, candidate_budget = _trial_status(candidate)
        failure_counts[baseline_label] += not baseline_success
        failure_counts[candidate_label] += not candidate_success
        budget_counts[baseline_label] += not baseline_budget
        budget_counts[candidate_label] += not candidate_budget
        truth_value = _value(record, ("truth_parameters",), ("parameter_truth",))
        truth = fallback_truth if truth_value is _MISSING else _finite_vector(truth_value)
        reference_value = _value(
            record,
            ("reference_likelihood",),
            ("likelihood_reference",),
            ("reference", "negative_log_likelihood"),
        )
        reference = fallback_reference if reference_value is _MISSING else _finite_scalar(reference_value)
        baseline_likelihood = _likelihood(baseline) if isinstance(baseline, Mapping) else None
        candidate_likelihood = _likelihood(candidate) if isinstance(candidate, Mapping) else None
        baseline_params = _parameters(baseline) if isinstance(baseline, Mapping) else None
        candidate_params = _parameters(candidate) if isinstance(candidate, Mapping) else None
        metrics: dict[str, dict[str, float]] = {baseline_label: {}, candidate_label: {}}
        reasons: list[str] = []
        if not baseline_success or not candidate_success:
            reasons.append("failure_or_missing_success")
        if not baseline_budget or not candidate_budget:
            reasons.append("budget_missing_or_exceeded")
        if reference is None or baseline_likelihood is None or candidate_likelihood is None:
            reasons.append("likelihood_missing")
        if truth is None or baseline_params is None or candidate_params is None:
            reasons.append("parameters_missing")
        comparable = not reasons
        if comparable:
            try:
                likelihood_values = {
                    baseline_label: likelihood_distortion(reference, baseline_likelihood),
                    candidate_label: likelihood_distortion(reference, candidate_likelihood),
                }
                parameter_values = {
                    baseline_label: parameter_rmse(truth, baseline_params),
                    candidate_label: parameter_rmse(truth, candidate_params),
                }
            except ValueError as exc:
                comparable = False
                reasons.append(f"metric_error:{exc}")
        if comparable:
            for endpoint_name, values in (
                ("likelihood_distortion", likelihood_values),
                ("parameter_rmse", parameter_values),
            ):
                for label, value in values.items():
                    endpoint_values[endpoint_name][label].append(float(value))
                paired_differences[endpoint_name].append(
                    float(values[candidate_label] - values[baseline_label])
                )
                for label, value in values.items():
                    metrics[label][endpoint_name] = float(value)
        rows.append({
            "seed": record.get("seed"),
            "comparable": bool(comparable),
            "excluded_reasons": reasons,
            "metrics": metrics if comparable else {},
        })

    summaries: dict[str, Any] = {}
    for name, values in endpoint_values.items():
        summaries[name] = {
            label: _metric_summary(values[label]) for label in (baseline_label, candidate_label)
        }
        summaries[name]["paired_candidate_minus_baseline"] = {
            **_metric_summary(paired_differences[name]),
            "bootstrap_ci": _bootstrap_ci(paired_differences[name], selected),
        }

    n_comparable = len(paired_differences["likelihood_distortion"])
    rates = {
        label: {
            "failure_rate": _rate(failure_counts[label], total),
            "budget_rate": _rate(budget_counts[label], total),
        }
        for label in (baseline_label, candidate_label)
    }
    checks: dict[str, bool] = {
        "predeclared_conditions_supplied": predeclared,
        "minimum_comparable_pairs": n_comparable >= selected.min_comparable_pairs,
    }
    for label in (baseline_label, candidate_label):
        checks[f"{label}_failure_rate_within_limit"] = rates[label]["failure_rate"] <= selected.max_failure_rate
        checks[f"{label}_budget_rate_within_limit"] = rates[label]["budget_rate"] <= selected.max_budget_rate
    for name in paired_differences:
        ci = summaries[name]["paired_candidate_minus_baseline"]["bootstrap_ci"]
        checks[f"{name}_ci_available"] = bool(ci["available"])
        checks[f"{name}_ci_passes"] = bool(
            ci["available"] and ci["high"] < -selected.max_paired_mean_difference
        )
    required = list(checks.values())
    endpoint_pass = all(checks[f"{name}_ci_passes"] for name in paired_differences)
    if selected.require_all_endpoints:
        checks["all_required_endpoints_pass"] = endpoint_pass
    decision = "CONFIRMED_ADVANTAGE_UNDER_PREDECLARED_RULE" if all(required) and endpoint_pass else "NO_CONFIRMED_ADVANTAGE"
    return {
        "protocol": "bounded_primary_endpoint_report",
        "scientific_claim": "none; this report records a predeclared decision rule only",
        "decision": decision,
        "conditions": {"predeclared": predeclared, **selected.as_dict()},
        "counts": {"total_records": total, "comparable_pairs": n_comparable, "excluded_pairs": total - n_comparable},
        "rates": rates,
        "endpoints": summaries,
        "records": rows,
        "checks": checks,
        "limitations": [
            "Bounded paired analysis is not a full scientific validation campaign.",
            "Bootstrap intervals quantify sampling variation in the supplied records; they do not prove generalisation.",
            "Missing, failed, and over-budget cases remain visible and prevent silent advantage claims.",
        ],
    }
