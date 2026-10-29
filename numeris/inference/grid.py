"""Small, deterministic posterior approximation for low-dimensional studies."""

import numpy as np


def normalized_grid_posterior(log_likelihood: np.ndarray, log_prior: np.ndarray | None = None) -> np.ndarray:
    """Return normalized posterior masses on a finite parameter grid.

    This is intentionally limited to diagnostic, low-dimensional experiments;
    it is not a replacement for MCMC or sequential Monte Carlo.
    """
    values = np.asarray(log_likelihood, dtype=float)
    if values.size == 0 or not np.all(np.isfinite(values)):
        raise ValueError("log_likelihood must be non-empty and finite")
    combined = values if log_prior is None else values + np.asarray(log_prior, dtype=float)
    if combined.shape != values.shape or not np.all(np.isfinite(combined)):
        raise ValueError("log_prior must have the same finite shape as log_likelihood")
    shifted = combined - np.max(combined)
    weights = np.exp(shifted)
    return weights / np.sum(weights)
