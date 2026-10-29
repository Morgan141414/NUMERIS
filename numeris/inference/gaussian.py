"""Inference objectives used by the initial benchmark laboratory."""

import numpy as np


def gaussian_negative_log_likelihood(prediction: np.ndarray, observations: np.ndarray,
                                    sigma: float) -> float:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    residual = (np.asarray(prediction) - np.asarray(observations)) / sigma
    return float(0.5 * np.sum(residual * residual + np.log(2.0 * np.pi * sigma * sigma)))
