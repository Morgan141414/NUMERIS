"""Run comparable solver configurations and collect benchmark metrics."""

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import numpy as np

from numeris.models.base import ODEModel
from numeris.budget import BudgetLedger


@dataclass(frozen=True)
class SolverConfig:
    """Configuration passed to ``scipy.integrate.solve_ivp``."""

    name: str
    method: str = "DOP853"
    rtol: float = 1e-8
    atol: float = 1e-10
    max_step: float = np.inf

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of this configuration."""
        max_step = float(self.max_step)
        return {
            "name": str(self.name),
            "method": str(self.method),
            "rtol": float(self.rtol),
            "atol": float(self.atol),
            "max_step": max_step if np.isfinite(max_step) else None,
        }


def _config_from(value: SolverConfig | Mapping[str, Any]) -> SolverConfig:
    if isinstance(value, SolverConfig):
        return value
    return SolverConfig(**dict(value))


def _float_or_none(value: float) -> float | None:
    value = float(value)
    return value if np.isfinite(value) else None


def _trajectory_metrics(states: np.ndarray, reference_states: np.ndarray | None) -> dict[str, Any]:
    metrics: dict[str, Any] = {
        "n_times": int(states.shape[0]),
        "state_dimension": int(states.shape[1]),
        "rmse": None,
        "max_abs_error": None,
    }
    if reference_states is None:
        return metrics
    reference = np.asarray(reference_states, dtype=float)
    if reference.shape != states.shape:
        raise ValueError("reference_states must match the computed trajectory shape")
    error = states - reference
    metrics["rmse"] = _float_or_none(np.sqrt(np.mean(error * error)))
    metrics["max_abs_error"] = _float_or_none(np.max(np.abs(error)))
    return metrics


def run_solver_configuration(
    model: ODEModel,
    params: np.ndarray,
    config: SolverConfig | Mapping[str, Any],
    *,
    observations: np.ndarray | None = None,
    sigma: float | None = None,
    reference_states: np.ndarray | None = None,
    budget: BudgetLedger | None = None,
) -> dict[str, Any]:
    """Run one configuration and return JSON-friendly metrics.

    Trajectory errors require an independently computed reference trajectory.
    The likelihood metric is Gaussian negative log-likelihood and requires
    both observations and ``sigma``.
    """
    from numeris.inference.gaussian import gaussian_negative_log_likelihood
    from numeris.solvers.scipy_solver import solve_ode

    normalized = _config_from(config)
    if budget is not None:
        budget.start_run()
    result = solve_ode(
        model,
        np.asarray(params, dtype=float),
        method=normalized.method,
        rtol=normalized.rtol,
        atol=normalized.atol,
        max_step=normalized.max_step,
    )
    if budget is not None:
        budget.charge_rhs(result.nfev)
        budget.charge_time(result.runtime_s)
    likelihood: float | None = None
    if observations is not None:
        if sigma is None:
            raise ValueError("sigma is required when observations are supplied")
        likelihood = gaussian_negative_log_likelihood(
            model.observe(result.states), observations, sigma
        )

    return {
        "config": normalized.as_dict(),
        "success": bool(result.success),
        "message": str(result.message),
        "trajectory": _trajectory_metrics(result.states, reference_states),
        "likelihood": {
            "negative_log_likelihood": (
                _float_or_none(likelihood) if likelihood is not None else None
            ),
            "available": likelihood is not None,
        },
        "cost": {
            "nfev": int(result.nfev),
            "runtime_s": _float_or_none(result.runtime_s),
            "peak_rss_bytes": result.peak_rss_bytes,
        },
    }


def run_benchmark(
    model: ODEModel,
    params: np.ndarray,
    configurations: Iterable[SolverConfig | Mapping[str, Any]],
    *,
    observations: np.ndarray | None = None,
    sigma: float | None = None,
    reference_states: np.ndarray | None = None,
    name: str = "benchmark",
    budget: BudgetLedger | None = None,
) -> dict[str, Any]:
    """Run several solver configurations on common inputs."""
    results = [
        run_solver_configuration(
            model,
            params,
            config,
            observations=observations,
            sigma=sigma,
            reference_states=reference_states,
            budget=budget,
        )
        for config in configurations
    ]
    report = {"name": str(name), "n_configurations": len(results), "results": results}
    if budget is not None:
        report["budget"] = {
            "rhs_evals": budget.rhs_evals,
            "elapsed_time_s": float(budget.elapsed_time_s),
            "runs": budget.runs,
        }
    return report
