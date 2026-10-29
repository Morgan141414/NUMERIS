"""Distribution discrepancy metrics for posterior diagnostics."""

import numpy as np


def hellinger_distance(p: np.ndarray, q: np.ndarray) -> float:
    p, q = _normalise(p), _normalise(q)
    return float(np.sqrt(max(0.0, 1.0 - np.sum(np.sqrt(p * q)))) / np.sqrt(2.0))


def wasserstein_1d(samples_p: np.ndarray, samples_q: np.ndarray) -> float:
    """Empirical 1-D Wasserstein distance without an extra dependency."""
    p, q = np.sort(np.asarray(samples_p, dtype=float)), np.sort(np.asarray(samples_q, dtype=float))
    n = min(len(p), len(q))
    if n == 0:
        raise ValueError("samples must be non-empty")
    return float(np.mean(np.abs(p[:n] - q[:n])))


def _normalise(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if np.any(values < 0) or values.ndim != 1 or values.sum() <= 0:
        raise ValueError("inputs must be a non-negative 1-D array with positive mass")
    return values / values.sum()
