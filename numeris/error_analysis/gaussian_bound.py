"""A transparent upper bound for Gaussian target distortion.

For identity observations (or a supplied observation Lipschitz constant), if
the residual norm is ``r`` and the state perturbation norm is bounded by ``e``,
the quadratic Gaussian NLL perturbation is bounded by

    L * r * e / sigma**2 + (L * e)**2 / (2 * sigma**2).

This is a baseline inequality, not a NUMERIS novelty claim. It requires a
valid bound on the observation perturbation and positive Gaussian sigma.
"""

import math


def gaussian_nll_error_bound(
    residual_norm: float,
    state_error_bound: float,
    sigma: float,
    observation_lipschitz: float = 1.0,
) -> float:
    """Return a conservative absolute NLL perturbation bound."""
    values = (residual_norm, state_error_bound, sigma, observation_lipschitz)
    if not all(math.isfinite(float(value)) for value in values):
        raise ValueError("all inputs must be finite")
    if residual_norm < 0 or state_error_bound < 0 or observation_lipschitz < 0:
        raise ValueError("norms and Lipschitz constant must be non-negative")
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    output_error = observation_lipschitz * state_error_bound
    return float(
        residual_norm * output_error / sigma**2
        + output_error**2 / (2.0 * sigma**2)
    )
