"""Repeated, JSON-friendly benchmark execution.

This module keeps repeated stochastic trials separate from the single-run
benchmark runner.  A seed controls only the synthetic observation noise; all
solver configurations receive the same observations for a given seed.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable, Iterable, Mapping

import numpy as np

from numeris.models.base import ODEModel

from .runner import SolverConfig, run_solver_configuration
from .statistics import summarize


def _as_model(factory_or_model: ODEModel | Callable[..., ODEModel], seed: int) -> ODEModel:
    """Resolve an ODE model or a zero/one-argument model factory."""
    if isinstance(factory_or_model, ODEModel):
        return factory_or_model
    if not callable(factory_or_model):
        raise TypeError("factory/model must be an ODEModel or callable factory")
    try:
        parameters = inspect.signature(factory_or_model).parameters
    except (TypeError, ValueError):
        parameters = {}
    positional = [
        parameter
        for parameter in parameters.values()
        if parameter.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    accepts_seed = (
        any(parameter.kind == inspect.Parameter.VAR_POSITIONAL for parameter in parameters.values())
        or any(parameter.default is inspect.Parameter.empty for parameter in positional)
        or any(parameter.name in {"seed", "random_seed"} for parameter in positional)
    )
    model = factory_or_model(seed) if accepts_seed else factory_or_model()
    if not isinstance(model, ODEModel):
        raise TypeError("model factory must return an ODEModel")
    return model


def _float_or_none(value: Any) -> float | None:
    value = float(value)
    return value if np.isfinite(value) else None


def _summary(values: list[float]) -> dict[str, float | int] | None:
    return summarize(np.asarray(values, dtype=float)) if values else None


def run_repeated(
    factory_or_model: ODEModel | Callable[..., ODEModel],
    params: np.ndarray,
    configurations: Iterable[SolverConfig | Mapping[str, Any]],
    seeds: Iterable[int],
    sigma: float,
    reference_states: np.ndarray,
    *,
    name: str = "repeated_benchmark",
) -> dict[str, Any]:
    """Run solver configurations over repeated synthetic-observation trials.

    ``target_error`` is the trajectory RMSE against the independently supplied
    reference trajectory.  Failures include solver failures and exceptions;
    failed trials are retained in ``runs`` but excluded from numerical
    summaries.  The returned structure contains only JSON-compatible values.
    """
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("sigma must be positive and finite")
    seed_values = [int(seed) for seed in seeds]
    if not seed_values:
        raise ValueError("seeds must contain at least one seed")
    reference = np.asarray(reference_states, dtype=float)
    if reference.ndim != 2 or not np.all(np.isfinite(reference)):
        raise ValueError("reference_states must be a finite 2-D array")

    normalized_configs = [
        config if isinstance(config, SolverConfig) else SolverConfig(**dict(config))
        for config in configurations
    ]
    if not normalized_configs:
        raise ValueError("configurations must contain at least one configuration")

    by_config: list[dict[str, Any]] = []
    for config in normalized_configs:
        runs: list[dict[str, Any]] = []
        nfev_values: list[float] = []
        runtime_values: list[float] = []
        target_values: list[float] = []
        failures = 0
        for seed in seed_values:
            model = _as_model(factory_or_model, seed)
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
                success = bool(result["success"])
                target_error = result["trajectory"]["rmse"]
                if not success or target_error is None:
                    failures += 1
                else:
                    nfev_values.append(float(result["cost"]["nfev"]))
                    runtime_values.append(float(result["cost"]["runtime_s"]))
                    target_values.append(float(target_error))
                runs.append(
                    {"seed": seed, "target_error": _float_or_none(target_error)
                     if target_error is not None else None, **result}
                )
            except Exception as exc:  # benchmark failures are data, not crashes
                failures += 1
                runs.append(
                    {
                        "seed": seed,
                        "success": False,
                        "target_error": None,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
        by_config.append(
            {
                "config": config.as_dict(),
                "n_trials": len(seed_values),
                "failure_rate": float(failures / len(seed_values)),
                "runs": runs,
                "summaries": {
                    "nfev": _summary(nfev_values),
                    "runtime_s": _summary(runtime_values),
                    "target_error": _summary(target_values),
                },
            }
        )
    return {
        "name": str(name),
        "n_configurations": len(by_config),
        "seeds": seed_values,
        "sigma": float(sigma),
        "target": {"name": "trajectory_rmse", "reference": "reference_states"},
        "results": by_config,
    }
