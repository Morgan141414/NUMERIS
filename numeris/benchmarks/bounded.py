"""Benchmark-level bounded execution without pretending to interrupt SciPy."""

from __future__ import annotations

import json
from typing import Any, Iterable, Mapping

import numpy as np

from numeris.budget import BoundedBenchmarkBudget
from numeris.models.base import ODEModel

from .runner import SolverConfig, run_solver_configuration


def run_bounded_benchmark(
    model: ODEModel,
    params: np.ndarray,
    configurations: Iterable[SolverConfig | Mapping[str, Any]],
    *,
    budget: BoundedBenchmarkBudget,
    observations: np.ndarray | None = None,
    sigma: float | None = None,
    reference_states: np.ndarray | None = None,
    name: str = "bounded_benchmark",
    estimated_rhs_evals_per_run: int | None = None,
    estimated_time_s_per_run: float | None = None,
) -> dict[str, Any]:
    """Run admitted configurations and stop after the first measured overrun.

    A completed SciPy call may exceed an RHS/time cap because this wrapper
    cannot safely interrupt it.  Such a call is retained with status
    ``over_budget`` and later configurations are marked ``not_started``.
    """
    configs = list(configurations)
    preflight = budget.preflight(
        len(configs),
        estimated_rhs_evals_per_run=estimated_rhs_evals_per_run,
        estimated_time_s_per_run=estimated_time_s_per_run,
    )
    results: list[dict[str, Any]] = []
    if not preflight["allowed"]:
        report = {
            "name": str(name),
            "status": "preflight_rejected",
            "preflight": preflight,
            "results": results,
            "budget": budget.as_dict(),
        }
        json.dumps(report, allow_nan=False)
        return report

    for config in configs:
        if not budget.can_start():
            results.append({"status": "not_started", "reason": "budget exhausted"})
            continue
        budget.start_run()
        try:
            result = run_solver_configuration(
                model,
                np.asarray(params, dtype=float),
                config,
                observations=observations,
                sigma=sigma,
                reference_states=reference_states,
            )
            accounting = budget.finish_run(result["cost"])
            results.append({**result, "execution": accounting})
        except Exception as exc:
            results.append(
                {
                    "status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                    "execution": {"call_was_interrupted": False},
                }
            )
    status = "over_budget" if budget.as_dict()["status"] == "over_budget" else "completed"
    report = {
        "name": str(name),
        "status": status,
        "preflight": preflight,
        "n_configurations": len(configs),
        "results": results,
        "budget": budget.as_dict(),
    }
    json.dumps(report, allow_nan=False)
    return report


__all__ = ["run_bounded_benchmark"]
