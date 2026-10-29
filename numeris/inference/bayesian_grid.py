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


__all__ = ["GridPosterior", "grid_posterior", "posterior_distance"]
