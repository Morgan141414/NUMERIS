"""Small reproducible summaries for repeated benchmark runs."""

import numpy as np


def summarize(values: np.ndarray, *, confidence: float = 0.95) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise ValueError("values must be a non-empty finite 1-D array")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between zero and one")
    alpha = (1.0 - confidence) / 2.0
    return {
        "n": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
        "q_low": float(np.quantile(values, alpha)),
        "q_high": float(np.quantile(values, 1.0 - alpha)),
    }
