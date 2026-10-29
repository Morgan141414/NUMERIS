"""Inference objectives used by the initial benchmark laboratory."""

import numpy as np
from scipy.optimize import minimize

from numeris.models.base import ODEModel
from numeris.solvers.scipy_solver import solve_ode


def gaussian_negative_log_likelihood(prediction: np.ndarray, observations: np.ndarray,
                                    sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    residual = (np.asarray(prediction) - np.asarray(observations)) / sigma
    return float(0.5 * np.sum(residual * residual + np.log(2.0 * np.pi * sigma * sigma)))


def fit_parameters(model: ODEModel, observations: np.ndarray, sigma: float,
                   initial_params: np.ndarray, *, bounds=None, method="DOP853",
                   rtol=1e-8, atol=1e-10):
    """Estimate parameters by deterministic Gaussian maximum likelihood.

    This deliberately exposes solver settings in the objective so an experiment
    can quantify inference distortion as tolerances change.
    """
    observations = np.asarray(observations, dtype=float)

    def objective(params):
        result = solve_ode(model, params, method=method, rtol=rtol, atol=atol)
        if not result.success or result.states.shape != observations.shape:
            return float("inf")
        return gaussian_negative_log_likelihood(model.observe(result.states), observations, sigma)

    return minimize(objective, np.asarray(initial_params, dtype=float), bounds=bounds,
                    method="L-BFGS-B" if bounds is not None else "BFGS")
