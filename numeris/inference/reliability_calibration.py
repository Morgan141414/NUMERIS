"""Bounded multi-case reliability calibration diagnostics.

This module composes :func:`calibrate_tolerance_sweep` across a small,
caller-supplied collection of model/reference cases.  It reports finite-sweep
diagnostics only; it does not establish statistical calibration, method
validity, novelty, or superiority.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

from .error_analysis.calibration import (
    ArrayLike,
    NumericalReliabilityCalibration,
    ValueProvider,
    calibrate_tolerance_sweep,
)


@dataclass(frozen=True)
class ReliabilityCalibrationCase:
    """One finite tolerance-sweep calibration case.

    ``emitted_bound`` and ``reference_error`` may be arrays aligned with
    ``tolerances`` or scalar-returning callables, as supported by
    :func:`calibrate_tolerance_sweep`.
    """

    name: str
    tolerances: Sequence[float] | np.ndarray
    emitted_bound: ValueProvider | ArrayLike
    reference_error: ValueProvider | ArrayLike
    atol: float = 0.0


def _case_value(case: ReliabilityCalibrationCase | Mapping[str, Any], key: str) -> Any:
    if isinstance(case, ReliabilityCalibrationCase):
        return getattr(case, key)
    if isinstance(case, Mapping):
        if key not in case:
            raise ValueError(f"calibration case is missing '{key}'")
        return case[key]
    raise TypeError("cases must contain ReliabilityCalibrationCase or mapping values")


def _calibrate_case(case: ReliabilityCalibrationCase | Mapping[str, Any]) -> NumericalReliabilityCalibration:
    atol = case.atol if isinstance(case, ReliabilityCalibrationCase) else case.get("atol", 0.0)
    return calibrate_tolerance_sweep(
        _case_value(case, "tolerances"),
        _case_value(case, "emitted_bound"),
        _case_value(case, "reference_error"),
        atol=float(atol),
    )


def run_reliability_calibration(
    cases: Sequence[ReliabilityCalibrationCase | Mapping[str, Any]],
    *,
    max_cases: int | None = None,
) -> dict[str, object]:
    """Run bounded reliability calibration over model/reference cases.

    Cases are processed in input order and truncated to ``max_cases`` when it
    is provided.  The aggregate is weighted by the number of tolerance points
    so every evaluated point contributes once.  The returned structure only
    contains JSON-compatible scalar/list/dict values.
    """
    if max_cases is not None and (isinstance(max_cases, bool) or max_cases <= 0):
        raise ValueError("max_cases must be a positive integer or None")
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)):
        raise TypeError("cases must be a sequence")

    selected = list(cases if max_cases is None else cases[:max_cases])
    case_summaries: list[dict[str, object]] = []
    covered_points = 0
    total_points = 0

    for case in selected:
        name = _case_value(case, "name")
        if not isinstance(name, str) or not name:
            raise ValueError("case name must be a non-empty string")
        result = _calibrate_case(case)
        summary = result.summary()
        summary["name"] = name
        case_summaries.append(summary)
        covered_points += int(np.count_nonzero(result.covered))
        total_points += int(result.covered.size)

    coverage = float(covered_points / total_points) if total_points else None
    overconfidence = float(1.0 - coverage) if coverage is not None else None
    return {
        "schema_version": "reliability-calibration-v1",
        "cases": case_summaries,
        "summary": {
            "requested_case_count": int(len(cases)),
            "processed_case_count": int(len(case_summaries)),
            "max_cases": None if max_cases is None else int(max_cases),
            "total_tolerance_points": int(total_points),
            "covered_tolerance_points": int(covered_points),
            "coverage": coverage,
            "overconfidence": overconfidence,
        },
        "limitations": [
            "Finite tolerance-sweep diagnostic only.",
            "Reference errors must be independently computed by the caller.",
            "No statistical calibration, novelty, or superiority claim is made.",
        ],
    }


__all__ = ["ReliabilityCalibrationCase", "run_reliability_calibration"]
