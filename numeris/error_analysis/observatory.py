"""Diagnostics; differences are estimates, not automatically true errors."""

import numpy as np


def compare_solutions(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    delta = np.asarray(candidate) - np.asarray(reference)
    return {"rmse": float(np.sqrt(np.mean(delta * delta))), "max_abs": float(np.max(np.abs(delta)))}
