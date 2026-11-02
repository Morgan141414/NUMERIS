"""Paired-bootstrap uncertainty diagnostics for seed-wise endpoints.

The helper in this module quantifies uncertainty in a paired endpoint
difference, for example the difference in likelihood distortion or parameter
RMSE measured on the same random seeds.  It is statistical infrastructure
only: it does not establish a scientific effect, superiority, or calibration.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np


Statistic = str | Callable[[np.ndarray], float]


def _as_finite_vector(values: Sequence[float] | np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{name} must be a non-empty one-dimensional sequence")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _statistic_name(statistic: Statistic) -> str:
    if isinstance(statistic, str):
        return statistic
    return getattr(statistic, "__name__", "custom")


def _evaluate_statistic(values: np.ndarray, statistic: Statistic) -> float:
    if isinstance(statistic, str):
        if statistic == "mean":
            result = float(np.mean(values))
        elif statistic == "median":
            result = float(np.median(values))
        else:
            raise ValueError("statistic must be 'mean', 'median', or a callable")
    elif callable(statistic):
        result = float(statistic(values))
    else:
        raise TypeError("statistic must be 'mean', 'median', or a callable")
    if not np.isfinite(result):
        raise ValueError("statistic must return a finite scalar")
    return result


@dataclass(frozen=True)
class PairedBootstrapResult:
    """JSON-friendly summary of a paired-bootstrap endpoint difference."""

    observed_difference: float
    confidence_interval: tuple[float, float]
    confidence_level: float
    statistic: str
    n_pairs: int
    n_resamples: int
    seed: int
    limitations: tuple[str, ...]

    def summary(self) -> dict[str, Any]:
        """Return a JSON-serializable result without NumPy scalar objects."""
        return {
            "schema_version": "paired-bootstrap-v1",
            "observed_difference": float(self.observed_difference),
            "confidence_interval": {
                "lower": float(self.confidence_interval[0]),
                "upper": float(self.confidence_interval[1]),
            },
            "confidence_level": float(self.confidence_level),
            "statistic": self.statistic,
            "n_pairs": int(self.n_pairs),
            "n_resamples": int(self.n_resamples),
            "seed": int(self.seed),
            "limitations": list(self.limitations),
        }


def paired_bootstrap_difference(
    reference: Sequence[float] | np.ndarray,
    candidate: Sequence[float] | np.ndarray,
    *,
    n_resamples: int = 2_000,
    confidence_level: float = 0.95,
    seed: int = 0,
    statistic: Statistic = "mean",
) -> PairedBootstrapResult:
    """Estimate a two-sided bootstrap interval for a paired endpoint difference.

    ``reference`` and ``candidate`` must contain one endpoint value per common
    seed, in the same order.  The paired difference is ``candidate -
    reference``.  Resampling is performed on seed rows, preserving the
    within-seed pairing.  The interval is a percentile interval over the
    requested statistic (mean by default).

    This is a finite-sample diagnostic.  It does not correct for biased
    endpoints, dependence between seeds, multiple comparisons, or adaptive
    experiment selection.
    """
    reference_values = _as_finite_vector(reference, "reference")
    candidate_values = _as_finite_vector(candidate, "candidate")
    if reference_values.shape != candidate_values.shape:
        raise ValueError("reference and candidate must have the same length")
    if isinstance(n_resamples, bool) or not isinstance(n_resamples, (int, np.integer)) or n_resamples < 1:
        raise ValueError("n_resamples must be a positive integer")
    if not np.isfinite(confidence_level) or not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must be between 0 and 1")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")

    differences = candidate_values - reference_values
    observed = _evaluate_statistic(differences, statistic)
    rng = np.random.default_rng(int(seed))
    indices = rng.integers(0, differences.size, size=(int(n_resamples), differences.size))
    bootstrap_values = np.asarray(
        [_evaluate_statistic(differences[sample], statistic) for sample in indices],
        dtype=float,
    )
    alpha = 1.0 - float(confidence_level)
    lower, upper = np.quantile(bootstrap_values, [alpha / 2.0, 1.0 - alpha / 2.0])

    limitations = [
        "Paired bootstrap uncertainty only; this is not a scientific result.",
        "The interval assumes the supplied seed-wise pairs are representative and exchangeable.",
        "It does not account for dependence, bias, multiple comparisons, or adaptive selection.",
    ]
    if differences.size < 10:
        limitations.append(
            "Small sample limitation: fewer than 10 paired seeds can make percentile intervals unstable."
        )
    if differences.size < 2:
        limitations.append("With one paired seed, uncertainty cannot be empirically estimated.")

    return PairedBootstrapResult(
        observed_difference=observed,
        confidence_interval=(float(lower), float(upper)),
        confidence_level=float(confidence_level),
        statistic=_statistic_name(statistic),
        n_pairs=int(differences.size),
        n_resamples=int(n_resamples),
        seed=int(seed),
        limitations=tuple(limitations),
    )


__all__ = ["PairedBootstrapResult", "paired_bootstrap_difference"]
