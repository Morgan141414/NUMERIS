import json

import numpy as np
import pytest

from numeris.inference import ReliabilityCalibrationCase, run_reliability_calibration


def _cases():
    return [
        ReliabilityCalibrationCase(
            name="covered",
            tolerances=(1e-2, 1e-3),
            emitted_bound=(0.2, 0.1),
            reference_error=(0.1, 0.05),
        ),
        {
            "name": "mixed",
            "tolerances": np.array([1e-2, 1e-3]),
            "emitted_bound": lambda tolerance: tolerance * 5.0,
            "reference_error": lambda tolerance: tolerance * (2.0 if tolerance > 1e-3 else 8.0),
        },
    ]


def test_runner_is_bounded_and_json_friendly():
    result = run_reliability_calibration(_cases(), max_cases=1)
    encoded = json.dumps(result, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["schema_version"] == "reliability-calibration-v1"
    assert decoded["summary"]["requested_case_count"] == 2
    assert decoded["summary"]["processed_case_count"] == 1
    assert decoded["summary"]["coverage"] == 1.0
    assert len(decoded["cases"]) == 1
    assert decoded["limitations"]


def test_runner_aggregates_tolerance_points_and_is_reproducible():
    first = run_reliability_calibration(_cases())
    second = run_reliability_calibration(_cases())
    assert first == second
    assert first["summary"]["total_tolerance_points"] == 4
    assert first["summary"]["covered_tolerance_points"] == 3
    assert first["summary"]["coverage"] == pytest.approx(0.75)
    assert first["summary"]["overconfidence"] == pytest.approx(0.25)


def test_runner_rejects_invalid_bounds():
    with pytest.raises(ValueError, match="max_cases"):
        run_reliability_calibration(_cases(), max_cases=0)

    with pytest.raises(ValueError, match="missing 'name'"):
        run_reliability_calibration([{"tolerances": [1e-2], "emitted_bound": [1.0], "reference_error": [1.0]}])
