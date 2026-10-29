"""Reliability calibration metrics for predicted numerical-error bounds."""

import numpy as np


def error_bound_calibration(predicted_bounds: np.ndarray, actual_errors: np.ndarray) -> dict[str, float]:
    """Compare non-negative predicted bounds with observed absolute errors."""
    predicted = np.asarray(predicted_bounds, dtype=float)
    actual = np.asarray(actual_errors, dtype=float)
    if predicted.shape != actual.shape or predicted.ndim == 0 or predicted.size == 0:
        raise ValueError("predicted_bounds and actual_errors must be equal non-empty arrays")
    if np.any(~np.isfinite(predicted)) or np.any(~np.isfinite(actual)):
        raise ValueError("calibration inputs must be finite")
    if np.any(predicted < 0) or np.any(actual < 0):
        raise ValueError("calibration inputs must be non-negative")
    covered = actual <= predicted
    return {
        "coverage": float(np.mean(covered)),
        "mean_bound": float(np.mean(predicted)),
        "mean_actual_error": float(np.mean(actual)),
        "mean_excess": float(np.mean(np.maximum(actual - predicted, 0.0))),
    }
