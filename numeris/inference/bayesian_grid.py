"""Low-dimensional, deterministic Bayesian inference on an ODE parameter grid.

This module is deliberately a small reproducibility baseline.  It evaluates a
Gaussian observation likelihood for every point in a finite parameter grid and
normalises the resulting posterior masses.  It is useful for inspecting
solver-induced posterior changes without requiring PyMC or NumPyro.

Limitations
-----------
The grid must be finite and is practical only for low-dimensional problems.
The result is a discretisation of the posterior, not an MCMC estimate; grid
resolution can dominate the reported summaries.  The implementation currently
supports independent Gaussian observation noise with a scalar ``sigma`` and
does not provide convergence diagnostics, posterior predictive checks, or
hierarchical priors.  A finite grid also cannot discover mass outside the
specified bounds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from numeris.models.base import ODEModel
from numeris.solvers.scipy_solver import solve_ode

from .distances import hellinger_distance
from .gaussian import gaussian_negative_log_likelihood
from .metrics import parameter_rmse


@dataclass(frozen=True)
class GridPosterior:
    """Posterior masses and diagnostics evaluated on a finite parameter grid."""

    parameter_grid: np.ndarray
    log_likelihood: np.ndarray
    log_prior: np.ndarray
    posterior: np.ndarray
    parameter_names: tuple[str, ...]
    method: str
    rtol: float
    atol: float

    def __post_init__(self) -> None:
        grid = np.asarray(self.parameter_grid, dtype=float)
        likelihood = np.asarray(self.log_likelihood, dtype=float)
        prior = np.asarray(self.log_prior, dtype=float)
        posterior = np.asarray(self.posterior, dtype=float)
        if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] == 0:
            raise ValueError("parameter_grid must be a non-empty 2-D array")
        if any(array.shape != (grid.shape[0],) for array in (likelihood, prior, posterior)):
            raise ValueError("posterior arrays must have one value per grid point")
        if not all(np.all(np.isfinite(array)) for array in (grid, likelihood, prior, posterior)):
            raise ValueError("grid and posterior arrays must be finite")
        if np.any(posterior < 0) or not np.isclose(posterior.sum(), 1.0):
            raise ValueError("posterior must be non-negative and sum to one")
        if len(self.parameter_names) != grid.shape[1]:
            raise ValueError("parameter_names must match grid dimensionality")

    @property
    def mode(self) -> np.ndarray:
        """Return the grid point with the largest posterior mass."""
        return self.parameter_grid[int(np.argmax(self.posterior))].copy()

    def mean(self) -> np.ndarray:
        """Return the posterior mean for each parameter."""
        return np.sum(self.parameter_grid * self.posterior[:, None], axis=0)

    def standard_deviation(self) -> np.ndarray:
        """Return posterior standard deviations for each parameter."""
        mean = self.mean()
        return np.sqrt(np.sum((self.parameter_grid - mean) ** 2 * self.posterior[:, None], axis=0))

    def credible_intervals(self, level: float = 0.95) -> np.ndarray:
        """Return equal-tail credible intervals as an ``(n_parameters, 2)`` array."""
        if not 0.0 < level < 1.0:
            raise ValueError("level must be between zero and one")
        alpha = (1.0 - level) / 2.0
        return np.array([
            [_weighted_quantile(self.parameter_grid[:, column], self.posterior, alpha),
             _weighted_quantile(self.parameter_grid[:, column], self.posterior, 1.0 - alpha)]
            for column in range(self.parameter_grid.shape[1])
        ])

    def summary(self, level: float = 0.95) -> dict[str, object]:
        """Return JSON-friendly posterior summary statistics."""
        intervals = self.credible_intervals(level)
        return {
            "parameter_names": list(self.parameter_names),
            "mean": self.mean().tolist(),
            "standard_deviation": self.standard_deviation().tolist(),
            "mode": self.mode.tolist(),
            "credible_level": level,
            "credible_intervals": intervals.tolist(),
        }


@dataclass(frozen=True)
class ParameterRecoveryResult:
    """Reproducible summary of one low-dimensional parameter-recovery run.

    The result describes recovery on the supplied finite grid only.  It is not
    evidence that the grid posterior is calibrated, that the solver is
    superior to another solver, or that the scientific model is correct.
    """

    truth: np.ndarray
    map_estimate: np.ndarray
    posterior_mean: np.ndarray
    map_rmse: float
    mean_rmse: float
    credible_intervals: np.ndarray
    credible_interval_coverage: np.ndarray
    credible_level: float
    solver_settings: dict[str, object]
    posterior: GridPosterior
    limitations: tuple[str, ...] = (
        "Posterior inference is a finite-grid approximation, not MCMC.",
        "Coverage is a single-run diagnostic, not a calibration study.",
        "This result makes no superiority or novelty claim.",
    )

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly result summary without posterior arrays."""
        return {
            "truth": self.truth.tolist(),
            "map_estimate": self.map_estimate.tolist(),
            "posterior_mean": self.posterior_mean.tolist(),
            "map_rmse": self.map_rmse,
            "mean_rmse": self.mean_rmse,
            "credible_intervals": self.credible_intervals.tolist(),
            "credible_interval_coverage": self.credible_interval_coverage.tolist(),
            "credible_level": self.credible_level,
            "solver_settings": dict(self.solver_settings),
            "limitations": list(self.limitations),
        }


def grid_posterior(
    model: ODEModel,
    observations: np.ndarray,
    sigma: float,
    parameter_grid: np.ndarray | Sequence[Sequence[float]],
    *,
    log_prior: np.ndarray | None = None,
    parameter_names: Sequence[str] | None = None,
    method: str = "DOP853",
    rtol: float = 1e-8,
    atol: float = 1e-10,
) -> GridPosterior:
    """Evaluate a Gaussian ODE posterior on explicit parameter vectors.

    ``parameter_grid`` has shape ``(n_grid_points, n_parameters)``.  Supplying
    explicit points (rather than an implicit Cartesian-product API) makes the
    computational budget and the exact reproducibility record unambiguous.
    ``log_prior`` contains one log prior mass per point; omitted values mean a
    uniform prior over the supplied points.
    """
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("sigma must be a finite positive value")
    if rtol <= 0 or atol <= 0:
        raise ValueError("rtol and atol must be positive")
    grid = np.asarray(parameter_grid, dtype=float)
    if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] == 0 or not np.all(np.isfinite(grid)):
        raise ValueError("parameter_grid must be a finite, non-empty 2-D array")
    observations = np.asarray(observations, dtype=float)
    if not np.all(np.isfinite(observations)):
        raise ValueError("observations must be finite")
    if parameter_names is None:
        names = tuple(f"parameter_{index}" for index in range(grid.shape[1]))
    else:
        names = tuple(parameter_names)
        if len(names) != grid.shape[1] or len(set(names)) != len(names) or not all(names):
            raise ValueError("parameter_names must be unique and match grid dimensionality")
    if log_prior is None:
        prior = np.zeros(grid.shape[0], dtype=float)
    else:
        prior = np.asarray(log_prior, dtype=float)
        if prior.shape != (grid.shape[0],) or not np.all(np.isfinite(prior)):
            raise ValueError("log_prior must be finite and have one value per grid point")

    log_likelihood = np.empty(grid.shape[0], dtype=float)
    for index, params in enumerate(grid):
        result = solve_ode(model, params, method=method, rtol=rtol, atol=atol)
        if not result.success or result.states.shape != observations.shape:
            raise RuntimeError(f"ODE solve failed at grid index {index}: {result.message}")
        prediction = model.observe(result.states)
        log_likelihood[index] = -gaussian_negative_log_likelihood(prediction, observations, sigma)
    posterior = _normalise_log_weights(log_likelihood + prior)
    return GridPosterior(grid, log_likelihood, prior, posterior, names, method, rtol, atol)


def run_parameter_recovery(
    model: ODEModel,
    truth: Sequence[float] | np.ndarray,
    sigma: float,
    parameter_grid: np.ndarray | Sequence[Sequence[float]],
    *,
    seed: int = 0,
    observations: np.ndarray | None = None,
    log_prior: np.ndarray | None = None,
    parameter_names: Sequence[str] | None = None,
    method: str = "DOP853",
    rtol: float = 1e-8,
    atol: float = 1e-10,
    credible_level: float = 0.95,
) -> ParameterRecoveryResult:
    """Run one reproducible synthetic-data parameter-recovery experiment.

    If ``observations`` is omitted, the truth trajectory is solved with the
    same solver settings and independent Gaussian noise is added using
    ``seed``.  Passing observations permits evaluation on an external dataset
    while retaining the same inference protocol.  Coverage is reported per
    parameter as whether truth lies inside the finite-grid equal-tail interval.

    This helper is intentionally a diagnostic baseline.  It does not perform
    repeated coverage calibration, MCMC, posterior predictive checks, or an
    equal-budget comparison, and it does not establish scientific superiority.
    """
    truth_array = np.asarray(truth, dtype=float)
    grid = np.asarray(parameter_grid, dtype=float)
    if truth_array.ndim != 1 or truth_array.size == 0 or not np.all(np.isfinite(truth_array)):
        raise ValueError("truth must be a finite, non-empty 1-D vector")
    if grid.ndim != 2 or grid.shape[1] != truth_array.size:
        raise ValueError("truth dimensionality must match parameter_grid")
    if not 0.0 < credible_level < 1.0:
        raise ValueError("credible_level must be between zero and one")
    if not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")

    reference = solve_ode(model, truth_array, method=method, rtol=rtol, atol=atol)
    if not reference.success:
        raise RuntimeError(f"truth ODE solve failed: {reference.message}")
    clean_observations = np.asarray(model.observe(reference.states), dtype=float)
    if observations is None:
        rng = np.random.default_rng(int(seed))
        observed = clean_observations + rng.normal(0.0, sigma, size=clean_observations.shape)
    else:
        observed = np.asarray(observations, dtype=float)
        if observed.shape != clean_observations.shape:
            raise ValueError("observations must match the model observation shape")
        if not np.all(np.isfinite(observed)):
            raise ValueError("observations must be finite")

    posterior = grid_posterior(
        model,
        observed,
        sigma,
        grid,
        log_prior=log_prior,
        parameter_names=parameter_names,
        method=method,
        rtol=rtol,
        atol=atol,
    )
    intervals = posterior.credible_intervals(credible_level)
    mean = posterior.mean()
    mode = posterior.mode
    coverage = (intervals[:, 0] <= truth_array) & (truth_array <= intervals[:, 1])
    settings = {
        "method": method,
        "rtol": float(rtol),
        "atol": float(atol),
        "sigma": float(sigma),
        "seed": int(seed),
        "credible_level": float(credible_level),
        "observation_source": "synthetic" if observations is None else "provided",
    }
    return ParameterRecoveryResult(
        truth=truth_array.copy(),
        map_estimate=mode,
        posterior_mean=mean,
        map_rmse=parameter_rmse(truth_array, mode),
        mean_rmse=parameter_rmse(truth_array, mean),
        credible_intervals=intervals,
        credible_interval_coverage=coverage,
        credible_level=float(credible_level),
        solver_settings=settings,
        posterior=posterior,
    )


def posterior_distance(p: GridPosterior | np.ndarray, q: GridPosterior | np.ndarray,
                       *, metric: str = "hellinger") -> float:
    """Compare posterior masses using Hellinger or total-variation distance."""
    left = _posterior_values(p)
    right = _posterior_values(q)
    if left.shape != right.shape:
        raise ValueError("posterior masses must have the same shape")
    if metric == "hellinger":
        return hellinger_distance(left, right)
    if metric == "total_variation":
        return float(0.5 * np.sum(np.abs(left / left.sum() - right / right.sum())))
    raise ValueError("metric must be 'hellinger' or 'total_variation'")


def _normalise_log_weights(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    weights = np.exp(shifted)
    total = weights.sum()
    if not np.isfinite(total) or total <= 0:
        raise ValueError("could not normalise posterior weights")
    return weights / total


def _posterior_values(value: GridPosterior | np.ndarray) -> np.ndarray:
    masses = value.posterior if isinstance(value, GridPosterior) else np.asarray(value, dtype=float)
    if masses.ndim != 1 or masses.size == 0 or not np.all(np.isfinite(masses)) or np.any(masses < 0):
        raise ValueError("posterior masses must be a finite, non-negative 1-D array")
    if masses.sum() <= 0:
        raise ValueError("posterior masses must have positive total mass")
    return masses


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, quantile: float) -> float:
    order = np.argsort(values)
    sorted_values = values[order]
    cumulative = np.cumsum(weights[order]) / weights.sum()
    index = int(np.searchsorted(cumulative, quantile, side="left"))
    return float(sorted_values[min(index, len(sorted_values) - 1)])


__all__ = [
    "GridPosterior",
    "ParameterRecoveryResult",
    "grid_posterior",
    "posterior_distance",
    "run_parameter_recovery",
]
