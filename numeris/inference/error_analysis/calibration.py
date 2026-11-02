"""Small diagnostics for calibrating emitted numerical-error bounds.

This module compares a bound emitted by a numerical workflow with an
independently computed reference error over a fixed tolerance sweep.  It is a
diagnostic for a particular experiment, not a proof of a numerical method or
of statistical calibration in general.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


ArrayLike = float | Sequence[float] | np.ndarray
ValueProvider = Callable[[float], ArrayLike]


@dataclass(frozen=True)
class NumericalReliabilityCalibration:
    """Calibration summary for one emitted bound/reference sweep.

    ``coverage`` is the fraction of tolerance points where the emitted bound
    contains the independently measured reference error.  ``overconfidence``
    is the complementary fraction: points where the bound is smaller than
    the reference error.  These are finite-sweep diagnostics and do not imply
    a confidence guarantee or establish a method's superiority.
    """

    tolerances: np.ndarray
    emitted_bounds: np.ndarray
    reference_errors: np.ndarray
    covered: np.ndarray

    def __post_init__(self) -> None:
        tolerances = np.asarray(self.tolerances, dtype=float)
        bounds = np.asarray(self.emitted_bounds, dtype=float)
        errors = np.asarray(self.reference_errors, dtype=float)
        covered = np.asarray(self.covered, dtype=bool)
        if any(value.ndim != 1 for value in (tolerances, bounds, errors, covered)):
            raise ValueError("calibration fields must be one-dimensional")
        if not (tolerances.size > 0 and bounds.size == tolerances.size == errors.size == covered.size):
            raise ValueError("calibration fields must have equal non-empty length")
        if not all(np.all(np.isfinite(value)) for value in (tolerances, bounds, errors)):
            raise ValueError("calibration fields must be finite")
        if np.any(tolerances <= 0) or np.any(bounds < 0) or np.any(errors < 0):
            raise ValueError("tolerances must be positive and values non-negative")

    @property
    def coverage(self) -> float:
        """Fraction of sweep points covered by the emitted bound."""
        return float(np.mean(self.covered))

    @property
    def overconfidence(self) -> float:
        """Fraction of sweep points where the bound is too small."""
        return float(1.0 - self.coverage)

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly diagnostic summary."""
        return {
            "tolerances": self.tolerances.tolist(),
            "emitted_bounds": self.emitted_bounds.tolist(),
            "reference_errors": self.reference_errors.tolist(),
            "covered": self.covered.tolist(),
            "coverage": self.coverage,
            "overconfidence": self.overconfidence,
            "undercoverage_count": int(np.count_nonzero(~self.covered)),
            "mean_bound": float(np.mean(self.emitted_bounds)),
            "mean_reference_error": float(np.mean(self.reference_errors)),
            "max_bound_to_error_ratio": float(
                np.max(
                    np.divide(
                        self.emitted_bounds,
                        self.reference_errors,
                        out=np.full_like(self.emitted_bounds, np.inf),
                        where=self.reference_errors > 0,
                    )
                )
            ),
            "limitations": [
                "Finite tolerance-sweep diagnostic only.",
                "Reference errors must be independently computed by the caller.",
                "This result is not a proof of a method or a superiority claim.",
            ],
        }


def _evaluate_provider(provider: ValueProvider | ArrayLike, tolerances: np.ndarray) -> np.ndarray:
    if callable(provider):
        values = [provider(float(tolerance)) for tolerance in tolerances]
        flattened = [np.asarray(value, dtype=float).reshape(-1) for value in values]
        if any(value.size != 1 for value in flattened):
            raise ValueError("providers must return one scalar per tolerance")
        return np.asarray([float(value[0]) for value in flattened], dtype=float)
    values = np.asarray(provider, dtype=float)
    if values.ndim != 1 or values.size != tolerances.size:
        raise ValueError("array providers must match the tolerance sweep")
    return values.copy()


def calibrate_tolerance_sweep(
    tolerances: Sequence[float] | np.ndarray,
    emitted_bound: ValueProvider | ArrayLike,
    reference_error: ValueProvider | ArrayLike,
    *,
    atol: float = 0.0,
) -> NumericalReliabilityCalibration:
    """Compare emitted bounds with independent errors over a tolerance sweep.

    ``emitted_bound`` and ``reference_error`` may be arrays aligned with
    ``tolerances`` or callables evaluated once per tolerance.  A reference
    error is considered covered when ``reference_error <= emitted_bound +
    atol``.  The caller is responsible for constructing the reference error
    independently (for example, from a tighter solver or a verified
    reference); this function does not label any reference as exact.
    """
    sweep = np.asarray(tolerances, dtype=float)
    if sweep.ndim != 1 or sweep.size == 0 or not np.all(np.isfinite(sweep)):
        raise ValueError("tolerances must be a finite, non-empty 1-D array")
    if np.any(sweep <= 0) or np.any(np.diff(sweep) == 0):
        raise ValueError("tolerances must be positive and unique")
    if not np.isfinite(atol) or atol < 0:
        raise ValueError("atol must be finite and non-negative")

    bounds = _evaluate_provider(emitted_bound, sweep)
    errors = _evaluate_provider(reference_error, sweep)
    if not np.all(np.isfinite(bounds)) or not np.all(np.isfinite(errors)):
        raise ValueError("emitted bounds and reference errors must be finite")
    if np.any(bounds < 0) or np.any(errors < 0):
        raise ValueError("emitted bounds and reference errors must be non-negative")
    return NumericalReliabilityCalibration(
        tolerances=sweep.copy(),
        emitted_bounds=bounds,
        reference_errors=errors,
        covered=errors <= bounds + float(atol),
    )
