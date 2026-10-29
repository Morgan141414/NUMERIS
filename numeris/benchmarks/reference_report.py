"""Reproducible convergence and reference-solution reports.

This module deliberately keeps reference construction separate from the main
benchmark runner.  A report evaluates several tolerance levels and solver
configurations, then forms a *consensus reference* from explicitly supplied,
independent reference configurations.

The consensus is not an exact solution.  It is a reproducible numerical
surrogate accompanied by the disagreement between its reference candidates.
Consequently, the report can support convergence claims only to the extent
that the candidates agree and the tolerances are in a resolved regime.  It
does not establish truncation-error bounds, floating-point correctness, or a
mathematical ground truth.  A single very strict solve is intentionally never
treated as an absolute truth.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from numeris.models.base import ODEModel
from numeris.solvers.scipy_solver import SolveResult, solve_ode


@dataclass(frozen=True)
class SolverSpec:
    """A solver configuration used by the report."""

    method: str
    max_step: float = np.inf

    def as_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "max_step": None if not np.isfinite(self.max_step) else float(self.max_step),
        }


DEFAULT_REFERENCE_CONFIGS: tuple[SolverSpec, ...] = (
    SolverSpec("DOP853"),
    SolverSpec("Radau"),
)


def _json_value(value: Any) -> Any:
    """Convert NumPy/scalar values recursively to strict JSON values."""
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, np.ndarray):
        return [_json_value(item) for item in value.tolist()]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if np.isfinite(number) else None
    if isinstance(value, (str,)) or value is None:
        return value
    return str(value)


def _normalise_spec(value: SolverSpec | Mapping[str, Any] | str) -> SolverSpec:
    if isinstance(value, SolverSpec):
        return value
    if isinstance(value, str):
        return SolverSpec(value)
    raw = dict(value)
    max_step = raw.get("max_step", np.inf)
    return SolverSpec(str(raw["method"]), np.inf if max_step is None else float(max_step))


def _normalise_tolerances(
    values: Mapping[str, Sequence[float]] | Iterable[Sequence[float]],
) -> list[dict[str, float | str]]:
    if isinstance(values, Mapping):
        items = values.items()
        result = [
            {"name": str(name), "rtol": float(pair[0]), "atol": float(pair[1])}
            for name, pair in items
        ]
    else:
        result = []
        for index, pair in enumerate(values):
            result.append({"name": f"level_{index}", "rtol": float(pair[0]), "atol": float(pair[1])})
    if not result:
        raise ValueError("at least one tolerance level is required")
    if len(result) < 2:
        raise ValueError("at least two tolerance levels are required for convergence analysis")
    for item in result:
        if item["rtol"] <= 0 or item["atol"] <= 0:
            raise ValueError("rtol and atol must be positive")
    return result


def _run_candidate(
    model: ODEModel,
    params: np.ndarray,
    spec: SolverSpec,
    rtol: float,
    atol: float,
) -> tuple[SolveResult, dict[str, Any]]:
    result = solve_ode(model, params, method=spec.method, rtol=rtol, atol=atol, max_step=spec.max_step)
    return result, {
        "solver": spec.as_dict(),
        "rtol": float(rtol),
        "atol": float(atol),
        "success": bool(result.success),
        "message": str(result.message),
        "nfev": int(result.nfev),
        "runtime_s": float(result.runtime_s),
    }


def _distance(states: np.ndarray, reference: np.ndarray) -> dict[str, float]:
    error = np.asarray(states) - np.asarray(reference)
    return {
        "rmse": float(np.sqrt(np.mean(error * error))),
        "max_abs_error": float(np.max(np.abs(error))),
    }


def build_reference_report(
    model: ODEModel,
    params: Sequence[float] | np.ndarray,
    *,
    tolerance_levels: Mapping[str, Sequence[float]] | Iterable[Sequence[float]],
    solver_configs: Sequence[SolverSpec | Mapping[str, Any] | str],
    reference_configs: Sequence[SolverSpec | Mapping[str, Any] | str] = DEFAULT_REFERENCE_CONFIGS,
    name: str = "ode_reference_report",
) -> dict[str, Any]:
    """Build a JSON-serializable convergence report.

    ``reference_configs`` are run at the tightest supplied tolerance.  Their
    state trajectories are averaged pointwise only after all selected runs
    succeed.  The report records both candidate-to-consensus errors and the
    maximum pairwise candidate disagreement.  At least two distinct solver
    methods are required, preventing a single strict run from becoming an
    unexamined reference.
    """
    specs = [_normalise_spec(item) for item in solver_configs]
    refs = [_normalise_spec(item) for item in reference_configs]
    if not specs:
        raise ValueError("at least one solver configuration is required")
    if len({item.method for item in refs}) < 2:
        raise ValueError("reference_configs must contain at least two independent solver methods")
    levels = _normalise_tolerances(tolerance_levels)
    params_array = np.asarray(params, dtype=float)
    tightest = min(levels, key=lambda item: (float(item["rtol"]), float(item["atol"])))

    reference_candidates: list[tuple[SolveResult, dict[str, Any]]] = []
    for spec in refs:
        result, metadata = _run_candidate(
            model, params_array, spec, float(tightest["rtol"]), float(tightest["atol"])
        )
        if result.success:
            reference_candidates.append((result, metadata))
    if len(reference_candidates) < 2:
        raise RuntimeError("fewer than two independent reference candidates succeeded")

    candidate_states = [item[0].states for item in reference_candidates]
    reference_states = np.mean(np.stack(candidate_states, axis=0), axis=0)
    pairwise = [
        _distance(candidate_states[i], candidate_states[j])
        for i in range(len(candidate_states))
        for j in range(i + 1, len(candidate_states))
    ]
    runs: list[dict[str, Any]] = []
    for spec in specs:
        for level in levels:
            result, metadata = _run_candidate(
                model, params_array, spec, float(level["rtol"]), float(level["atol"])
            )
            row = {**metadata, "tolerance_level": level["name"]}
            row["distance_to_consensus"] = (
                _distance(result.states, reference_states) if result.success else None
            )
            runs.append(row)

    report = {
        "schema_version": "reference-report-v1",
        "name": str(name),
        "model": {
            "state_dimension": int(model.x0().size),
            "n_observation_times": int(np.asarray(model.observation_times).size),
            "t_span": [float(model.t_span[0]), float(model.t_span[1])],
        },
        "parameters": params_array,
        "tolerance_levels": levels,
        "reference_policy": {
            "kind": "independent_solver_consensus",
            "tightest_tolerance_level": tightest["name"],
            "candidate_configs": [item[1]["solver"] for item in reference_candidates],
            "requires_two_successful_methods": True,
            "not_absolute_truth": True,
        },
        "reference": {
            "candidate_count": len(reference_candidates),
            "pairwise_disagreement": pairwise,
            "max_pairwise_rmse": max(item["rmse"] for item in pairwise),
            "max_pairwise_abs_error": max(item["max_abs_error"] for item in pairwise),
        },
        "runs": runs,
        "limitations": [
            "The consensus is a numerical surrogate, not an exact or proven reference solution.",
            "Agreement between solvers can hide shared implementation or modelling errors.",
            "The report does not provide a rigorous global error bound or roundoff analysis.",
            "Runtime and memory metrics are environment-dependent and are not used as accuracy evidence.",
        ],
    }
    report = _json_value(report)
    json.dumps(report, allow_nan=False, sort_keys=True)
    return report


__all__ = ["DEFAULT_REFERENCE_CONFIGS", "SolverSpec", "build_reference_report"]
