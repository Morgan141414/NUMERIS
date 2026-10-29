"""Diagnostics; differences are estimates, not automatically true errors."""

import numpy as np


def compare_solutions(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    delta = np.asarray(candidate) - np.asarray(reference)
    return {"rmse": float(np.sqrt(np.mean(delta * delta))), "max_abs": float(np.max(np.abs(delta)))}


def target_distortion(reference_value: float, candidate_value: float) -> dict[str, float]:
    """Measure absolute and relative distortion of a declared target."""
    absolute = abs(float(candidate_value) - float(reference_value))
    denominator = max(abs(float(reference_value)), np.finfo(float).eps)
    return {"absolute": absolute, "relative": absolute / denominator}
