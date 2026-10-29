"""Reusable orchestration for controlled validation experiments.

This module is deliberately an experiment runner, not a claim about which
method is scientifically better.  It makes the comparison protocol explicit:
the same seed, observations, parameters, reference and budget caps are used
for each labelled configuration.  Results retain failures and budget
violations so that downstream analysis cannot silently turn an invalid trial
into evidence of superiority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

from numeris.models.base import ODEModel

from .repeated import _as_model
from .runner import SolverConfig, run_solver_configuration
from .statistics import summarize


DEFAULT_SOLVER_CONFIGS: tuple[SolverConfig, ...] = (
    SolverConfig("RK45", method="RK45", rtol=1e-6, atol=1e-8),
    SolverConfig("DOP853", method="DOP853", rtol=1e-8, atol=1e-10),
    SolverConfig("Radau", method="Radau", rtol=1e-8, atol=1e-10),
    SolverConfig("BDF", method="BDF", rtol=1e-8, atol=1e-10),
    SolverConfig("LSODA", method="LSODA", rtol=1e-8, atol=1e-10),
)


def predefined_solver_configs() -> tuple[SolverConfig, ...]:
    """Return fresh copies of the five predefined SciPy configurations."""
    return tuple(
        SolverConfig(
            name=config.name,
            method=config.method,
            rtol=config.rtol,
            atol=config.atol,
            max_step=config.max_step,
        )
        for config in DEFAULT_SOLVER_CONFIGS
    )


@dataclass(frozen=True)
class BudgetCaps:
    """Per-trial caps used for validation, not an implicit solver guarantee.

    A solver call is allowed to finish; the report then marks whether it
    exceeded a cap.  This avoids claiming that a post-hoc measurement is a
    hard interruption or a fair simulation of an interrupted solver.
    """

    max_rhs_evals: int | None = None
    max_time_s: float | None = None

    def __post_init__(self) -> None:
        if self.max_rhs_evals is not None and self.max_rhs_evals < 0:
            raise ValueError("max_rhs_evals must be non-negative")
        if self.max_time_s is not None and (
            self.max_time_s < 0 or not np.isfinite(self.max_time_s)
        ):
            raise ValueError("max_time_s must be finite and non-negative")

    def check(self, cost: Mapping[str, Any]) -> dict[str, Any]:
        nfev = int(cost.get("nfev", 0))
        runtime = float(cost.get("runtime_s", 0.0))
        rhs_ok = self.max_rhs_evals is None or nfev <= self.max_rhs_evals
        time_ok = self.max_time_s is None or runtime <= self.max_time_s
        return {
            "within_budget": bool(rhs_ok and time_ok),
            "rhs_evals": {"value": nfev, "cap": self.max_rhs_evals, "within": rhs_ok},
            "runtime_s": {
                "value": runtime,
                "cap": self.max_time_s,
                "within": time_ok,
            },
        }

    def as_dict(self) -> dict[str, Any]:
        return {"max_rhs_evals": self.max_rhs_evals, "max_time_s": self.max_time_s}


@dataclass(frozen=True)
class AblationCase:
    """One named controller/pipeline ablation configuration."""

    name: str
    baseline: SolverConfig | Mapping[str, Any]
    policy: SolverConfig | Mapping[str, Any]
    disabled_components: tuple[str, ...] = ()
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "baseline": _config(self.baseline).as_dict(),
            "policy": _config(self.policy).as_dict(),
            "disabled_components": list(self.disabled_components),
            "description": self.description,
        }


def _config(value: SolverConfig | Mapping[str, Any]) -> SolverConfig:
    return value if isinstance(value, SolverConfig) else SolverConfig(**dict(value))


def _finite_or_none(value: Any) -> float | None:
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def _paired_summary(values: Sequence[float]) -> dict[str, Any] | None:
    return summarize(np.asarray(values, dtype=float)) if values else None


def _run_labelled_trial(
    factory_or_model: ODEModel | Callable[..., ODEModel],
    params: np.ndarray,
    config: SolverConfig,
    seed: int,
    sigma: float,
    reference_states: np.ndarray,
    caps: BudgetCaps,
) -> dict[str, Any]:
    model = _as_model(factory_or_model, seed)
    reference = np.asarray(reference_states, dtype=float)
    clean_observations = np.asarray(model.observe(reference), dtype=float)
    observations = clean_observations + np.random.default_rng(seed).normal(
        0.0, sigma, size=clean_observations.shape
    )
    try:
        result = run_solver_configuration(
            model,
            np.asarray(params, dtype=float),
            config,
            observations=observations,
            sigma=sigma,
            reference_states=reference,
        )
        budget = caps.check(result["cost"])
        target_error = result["trajectory"].get("rmse")
        return {
            "seed": int(seed),
            "success": bool(result["success"]),
            "target_error": _finite_or_none(target_error),
            "budget": budget,
            "result": result,
        }
    except Exception as exc:  # failures remain visible as validation data
        return {
            "seed": int(seed),
            "success": False,
            "target_error": None,
            "budget": {"within_budget": False, "error": "trial did not complete"},
            "error": f"{type(exc).__name__}: {exc}",
        }


def _label_summary(trials: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    valid = [
        float(trial["target_error"])
        for trial in trials
        if trial.get("success") and trial.get("budget", {}).get("within_budget")
        and trial.get("target_error") is not None
    ]
    return {
        "n_trials": len(trials),
        "n_valid_within_budget": len(valid),
        "failure_rate": float(
            sum(not bool(trial.get("success")) for trial in trials) / len(trials)
        )
        if trials
        else 0.0,
        "target_error": _paired_summary(valid),
    }

def run_equal_budget_comparison(
    factory_or_model: ODEModel | Callable[..., ODEModel],
    params: np.ndarray,
    seeds: Iterable[int],
    sigma: float,
    reference_states: np.ndarray,
    *,
    baseline: SolverConfig | Mapping[str, Any],
    policy: SolverConfig | Mapping[str, Any],
    budget_caps: BudgetCaps | Mapping[str, Any] | None = None,
    baseline_label: str = "baseline",
    policy_label: str = "policy",
    name: str = "equal_budget_comparison",
) -> dict[str, Any]:
    """Run two labelled configurations on paired seeds under common caps."""
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("sigma must be positive and finite")
    seed_values = [int(seed) for seed in seeds]
    if not seed_values:
        raise ValueError("seeds must contain at least one seed")
    if baseline_label == policy_label:
        raise ValueError("baseline_label and policy_label must differ")
    caps = budget_caps if isinstance(budget_caps, BudgetCaps) else BudgetCaps(**dict(budget_caps or {}))
    configs = {baseline_label: _config(baseline), policy_label: _config(policy)}
    trials = {
        label: [
            _run_labelled_trial(
                factory_or_model, params, config, seed, sigma, reference_states, caps
            )
            for seed in seed_values
        ]
        for label, config in configs.items()
    }
    paired: list[dict[str, Any]] = []
    differences: list[float] = []
    for left, right in zip(trials[baseline_label], trials[policy_label]):
        comparable = bool(
            left.get("success")
            and right.get("success")
            and left.get("budget", {}).get("within_budget")
            and right.get("budget", {}).get("within_budget")
            and left.get("target_error") is not None
            and right.get("target_error") is not None
        )
        row = {"seed": left["seed"], "comparable": comparable}
        if comparable:
            difference = float(right["target_error"] - left["target_error"])
            differences.append(difference)
            row["target_error_difference_policy_minus_baseline"] = difference
        else:
            row["target_error_difference_policy_minus_baseline"] = None
        paired.append(row)
    return {
        "name": str(name),
        "protocol": "paired_equal_budget_comparison",
        "scientific_claim": "none; this report records observations only",
        "seeds": seed_values,
        "sigma": float(sigma),
        "budget_caps": caps.as_dict(),
        "configurations": {label: config.as_dict() for label, config in configs.items()},
        "results": {
            label: {"label": label, "trials": trials[label], "summary": _label_summary(trials[label])}
            for label in configs
        },
        "paired": {
            "n_pairs": len(paired),
            "n_comparable": len(differences),
            "pairs": paired,
            "target_error_difference_policy_minus_baseline": _paired_summary(differences),
        },
    }


def run_ablation_cases(
    factory_or_model: ODEModel | Callable[..., ODEModel],
    params: np.ndarray,
    seeds: Iterable[int],
    sigma: float,
    reference_states: np.ndarray,
    cases: Iterable[AblationCase],
    *,
    budget_caps: BudgetCaps | Mapping[str, Any] | None = None,
    name: str = "ablation_study",
) -> dict[str, Any]:
    """Run named ablations with the same paired, equal-budget protocol."""
    case_values = list(cases)
    if not case_values:
        raise ValueError("cases must contain at least one AblationCase")
    reports = []
    for case in case_values:
        report = run_equal_budget_comparison(
            factory_or_model,
            params,
            seeds,
            sigma,
            reference_states,
            baseline=case.baseline,
            policy=case.policy,
            budget_caps=budget_caps,
            name=f"{name}:{case.name}",
        )
        report["ablation"] = case.as_dict()
        reports.append(report)
    return {
        "name": str(name),
        "protocol": "paired_equal_budget_ablation",
        "scientific_claim": "none; ablation reports require separate scientific interpretation",
        "n_cases": len(reports),
        "cases": reports,
    }

