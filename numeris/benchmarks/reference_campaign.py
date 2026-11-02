"""Small, fail-closed reference campaign over the five NUMERIS benchmarks.

The campaign is deliberately bounded and diagnostic.  It checks two reference
tolerance levels with independent solver families, records all failures, and
never converts agreement into a superiority or ground-truth claim.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping, Sequence

import numpy as np

from numeris.solvers.scipy_solver import solve_ode

from .fitzhugh_nagumo import fitzhugh_nagumo
from .lorenz import lorenz
from .lotka_volterra import lotka_volterra
from .oscillator import damped_oscillator
from .robertson import robertson
from .reference_report import SolverSpec, build_reference_report


@dataclass(frozen=True)
class ReferenceCampaignSpec:
    """Bounded configuration for one benchmark factory."""

    model_id: str
    factory: str
    builder: Callable[[np.ndarray], Any]
    params: tuple[float, ...]
    times: np.ndarray
    primary_method: str
    independent_method: str
    disagreement_rtol: float = 1e-6
    disagreement_atol: float = 1e-8


def _default_specs() -> tuple[ReferenceCampaignSpec, ...]:
    # Short, deterministic grids preserve the model regimes while bounding
    # local runtime, especially for Lorenz and the stiff Robertson system.
    return (
        ReferenceCampaignSpec("OSC", "damped_oscillator", damped_oscillator,
                              (1.0, 0.1, 0.2), np.linspace(0.0, 8.0, 81), "DOP853", "Radau"),
        ReferenceCampaignSpec("FHN", "fitzhugh_nagumo", fitzhugh_nagumo,
                              (0.7, 0.8, 0.08, 0.5), np.linspace(0.0, 12.0, 97), "DOP853", "Radau"),
        ReferenceCampaignSpec("LV", "lotka_volterra", lotka_volterra,
                              (1.5, 1.0, 0.75, 1.0), np.linspace(0.0, 12.0, 97), "DOP853", "Radau"),
        ReferenceCampaignSpec("LOR", "lorenz", lorenz,
                              (10.0, 28.0, 2.6666666666666665), np.linspace(0.0, 8.0, 81), "DOP853", "Radau"),
        ReferenceCampaignSpec("ROB", "robertson", robertson,
                              (0.04, 30000000.0, 10000.0), np.geomspace(1e-6, 1e3, 81), "BDF", "Radau"),
    )


DEFAULT_REFERENCE_TOLERANCES: tuple[tuple[float, float], ...] = (
    (1e-12, 1e-14),
    (1e-13, 1e-15),
)


def _distance(left: np.ndarray, right: np.ndarray) -> dict[str, float]:
    error = np.asarray(left) - np.asarray(right)
    return {
        "rmse": float(np.sqrt(np.mean(error * error))),
        "max_abs_error": float(np.max(np.abs(error))),
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_json_safe(item) for item in value.tolist()]
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if np.isfinite(number) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value


def _run(spec: ReferenceCampaignSpec, method: str, tolerance: tuple[float, float]) -> dict[str, Any]:
    result = solve_ode(
        spec.builder(spec.times), np.asarray(spec.params, dtype=float),
        method=method, rtol=tolerance[0], atol=tolerance[1],
    )
    return {
        "method": method,
        "rtol": float(tolerance[0]),
        "atol": float(tolerance[1]),
        "success": bool(result.success),
        "message": str(result.message),
        "nfev": int(result.nfev),
        "runtime_s": float(result.runtime_s),
        "states": result.states,
    }


def _one_model(spec: ReferenceCampaignSpec, tolerances: tuple[tuple[float, float], ...]) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for method in (spec.primary_method, spec.independent_method):
        for tolerance in tolerances:
            try:
                runs.append(_run(spec, method, tolerance))
            except Exception as exc:  # preserve failures in the denominator
                runs.append({
                    "method": method, "rtol": float(tolerance[0]), "atol": float(tolerance[1]),
                    "success": False, "message": f"{type(exc).__name__}: {exc}",
                    "nfev": 0, "runtime_s": 0.0, "states": None,
                })

    by_key = {(row["method"], row["rtol"], row["atol"]): row for row in runs}
    checks: list[dict[str, Any]] = []
    for method in (spec.primary_method, spec.independent_method):
        loose = by_key[(method, tolerances[0][0], tolerances[0][1])]
        tight = by_key[(method, tolerances[1][0], tolerances[1][1])]
        if loose["success"] and tight["success"]:
            scale = max(1.0, float(np.max(np.abs(tight["states"]))))
            distance = _distance(loose["states"], tight["states"])
            limit = spec.disagreement_atol + spec.disagreement_rtol * scale
            checks.append({"kind": "within_family_convergence", "method": method,
                           "distance": distance, "limit": float(limit),
                           "passed": distance["max_abs_error"] <= limit})
        else:
            checks.append({"kind": "within_family_convergence", "method": method,
                           "distance": None, "limit": None, "passed": False,
                           "reason": "one or both tolerance runs failed"})

    tight_primary = by_key[(spec.primary_method, tolerances[1][0], tolerances[1][1])]
    tight_independent = by_key[(spec.independent_method, tolerances[1][0], tolerances[1][1])]
    if tight_primary["success"] and tight_independent["success"]:
        scale = max(1.0, float(np.max(np.abs(tight_primary["states"]))))
        distance = _distance(tight_primary["states"], tight_independent["states"])
        limit = spec.disagreement_atol + spec.disagreement_rtol * scale
        checks.append({"kind": "cross_family_agreement",
                       "methods": [spec.primary_method, spec.independent_method],
                       "distance": distance, "limit": float(limit),
                       "passed": distance["max_abs_error"] <= limit})
    else:
        checks.append({"kind": "cross_family_agreement",
                       "methods": [spec.primary_method, spec.independent_method],
                       "distance": None, "limit": None, "passed": False,
                       "reason": "tight reference run failed"})

    resolved = all(bool(check["passed"]) for check in checks)
    report: dict[str, Any] = {
        "model_id": spec.model_id,
        "factory": spec.factory,
        "status": "REFERENCE-RESOLVED" if resolved else "REFERENCE-UNRESOLVED",
        "configuration": {
            "observation_count": int(spec.times.size),
            "t_span": [float(spec.times[0]), float(spec.times[-1])],
            "params": list(spec.params),
            "reference_families": [spec.primary_method, spec.independent_method],
            "tolerances": [list(item) for item in tolerances],
        },
        "checks": checks,
        "runs": [{key: value for key, value in row.items() if key != "states"} for row in runs],
        "reference_report": None,
        "limitations": [
            "The reference is a bounded numerical diagnostic, not exact truth.",
            "Independent solver agreement can hide shared modelling or implementation errors.",
            "This report makes no novelty, superiority, or publication-readiness claim.",
        ],
    }
    if all(row["success"] for row in runs):
        report["reference_report"] = build_reference_report(
            spec.builder(spec.times), spec.params,
            tolerance_levels={"coarse": tolerances[0], "tight": tolerances[1]},
            solver_configs=[SolverSpec(spec.primary_method), SolverSpec(spec.independent_method)],
            reference_configs=[SolverSpec(spec.primary_method), SolverSpec(spec.independent_method)],
            name=f"{spec.model_id.lower()}-bounded-reference",
        )
    return _json_safe(report)


def run_bounded_reference_campaign(
    *,
    model_ids: Sequence[str] | None = None,
    max_models: int = 5,
    tolerance_levels: Sequence[Sequence[float]] = DEFAULT_REFERENCE_TOLERANCES,
) -> dict[str, Any]:
    """Run a small reference convergence campaign for all five factories.

    The campaign performs only four ODE solves per selected model by default.
    ``max_models`` is a hard bound and selected model failures are retained.
    """
    if not isinstance(max_models, (int, np.integer)) or not 0 < max_models <= 5:
        raise ValueError("max_models must be an integer in [1, 5]")
    tolerances = tuple(tuple(float(value) for value in pair) for pair in tolerance_levels)
    if len(tolerances) != 2 or any(len(pair) != 2 or any(value <= 0 for value in pair) for pair in tolerances):
        raise ValueError("exactly two positive (rtol, atol) tolerance levels are required")
    specs = _default_specs()
    requested = None if model_ids is None else {str(item).upper() for item in model_ids}
    selected = tuple(spec for spec in specs if requested is None or spec.model_id in requested)
    if not selected:
        raise ValueError("model_ids selected no benchmark factories")
    if len(selected) > max_models:
        raise ValueError(f"selected models exceed max_models={max_models}")
    models = [_one_model(spec, tolerances) for spec in selected]
    report: dict[str, Any] = {
        "schema_version": "bounded-reference-campaign-v1",
        "campaign_status": "complete_bounded_diagnostic",
        "model_count": len(models),
        "planned_solver_runs": len(models) * 4,
        "models": models,
        "summary": {
            "resolved": sum(item["status"] == "REFERENCE-RESOLVED" for item in models),
            "unresolved": sum(item["status"] == "REFERENCE-UNRESOLVED" for item in models),
        },
        "limitations": [
            "Bounded coverage is not a full validation campaign.",
            "REFERENCE-RESOLVED means only that declared numerical checks passed.",
            "No superiority, novelty, or publication claim is made by this helper.",
        ],
    }
    report = _json_safe(report)
    json.dumps(report, allow_nan=False, sort_keys=True)
    return report


__all__ = ["DEFAULT_REFERENCE_TOLERANCES", "ReferenceCampaignSpec", "run_bounded_reference_campaign"]
