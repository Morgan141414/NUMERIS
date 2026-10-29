"""Metrics for evaluating inference distortion and optimisation results."""

from __future__ import annotations

from typing import Any

import numpy as np


def parameter_rmse(truth: Any, estimate: Any) -> float:
    """Return the root-mean-square error between parameter arrays.

    ``truth`` and ``estimate`` must be finite, non-empty numeric arrays with
    identical shapes.  The function accepts scalars as well as parameter
    vectors or matrices.
    """
    truth_array, estimate_array = _matching_finite_arrays(truth, estimate)
    return float(np.sqrt(np.mean(np.square(estimate_array - truth_array))))


def likelihood_distortion(reference: Any, candidate: Any) -> float:
    """Return relative distortion of a candidate likelihood value.

    The metric is ``abs(candidate - reference) / abs(reference)``.  When the
    reference is zero, its denominator is replaced by machine epsilon so that
    any non-zero candidate is reported as a large, finite distortion while
    identical zero values still return zero.
    """
    reference_value = _finite_scalar(reference, "reference")
    candidate_value = _finite_scalar(candidate, "candidate")
    absolute_error = abs(candidate_value - reference_value)
    denominator = max(abs(reference_value), np.finfo(float).eps)
    return float(absolute_error / denominator)


def false_optimum_rate(
    true_optima: Any,
    found_optima: Any,
    tolerance: float,
) -> float:
    """Return the fraction of found optima that are false.

    Each found optimum is considered valid when its Euclidean distance from at
    least one true optimum is at most ``tolerance``.  Inputs may be one-
    dimensional collections of scalar optima or two-dimensional collections
    of parameter vectors.  An empty ``found_optima`` collection has rate
    ``0.0`` because no false optimum was reported.
    """
    true_array = _optima_array(true_optima, "true_optima", allow_empty=False)
    found_array = _optima_array(found_optima, "found_optima", allow_empty=True)
    tolerance_value = _finite_scalar(tolerance, "tolerance")
    if tolerance_value < 0:
        raise ValueError("tolerance must be non-negative")

    if true_array.shape[1] != found_array.shape[1]:
        raise ValueError("true_optima and found_optima must have the same dimension")
    if found_array.shape[0] == 0:
        return 0.0

    distances = np.linalg.norm(
        found_array[:, np.newaxis, :] - true_array[np.newaxis, :, :], axis=2
    )
    matched = np.any(distances <= tolerance_value, axis=1)
    return float(1.0 - np.mean(matched))


def _matching_finite_arrays(first: Any, second: Any) -> tuple[np.ndarray, np.ndarray]:
    first_array = _finite_array(first, "truth")
    second_array = _finite_array(second, "estimate")
    if first_array.shape != second_array.shape:
        raise ValueError("truth and estimate must have identical shapes")
    if first_array.size == 0:
        raise ValueError("truth and estimate must be non-empty")
    return first_array, second_array


def _finite_array(value: Any, name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def _finite_scalar(value: Any, name: str) -> float:
    array = _finite_array(value, name)
    if array.ndim != 0:
        raise ValueError(f"{name} must be a finite scalar")
    return float(array)


def _optima_array(value: Any, name: str, *, allow_empty: bool) -> np.ndarray:
    array = _finite_array(value, name)
    if array.ndim == 0 or array.ndim > 2:
        raise ValueError(f"{name} must be a 1-D or 2-D array")
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if not allow_empty and array.shape[0] == 0:
        raise ValueError(f"{name} must contain at least one optimum")
    return array
