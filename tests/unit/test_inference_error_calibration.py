import json

import numpy as np
import pytest

from numeris.inference.error_analysis import calibrate_tolerance_sweep


def test_tolerance_calibration_reports_coverage_and_overconfidence() -> None:
    result = calibrate_tolerance_sweep(
        [1e-2, 1e-3, 1e-4],
        emitted_bound=lambda tolerance: 2.0 * tolerance,
        reference_error=[1e-2, 3e-3, 1e-4],
    )

    assert result.covered.tolist() == [True, False, True]
    assert result.coverage == pytest.approx(2 / 3)
    assert result.overconfidence == pytest.approx(1 / 3)
    payload = result.summary()
    assert json.dumps(payload)
    assert payload["undercoverage_count"] == 1
    assert "not a proof" in " ".join(payload["limitations"])


def test_tolerance_calibration_accepts_array_inputs_and_absolute_slack() -> None:
    result = calibrate_tolerance_sweep(
        np.array([1e-3, 1e-2]),
        emitted_bound=np.array([1.0, 2.0]),
        reference_error=np.array([1.1, 2.1]),
        atol=0.1,
    )
    assert result.coverage == 1.0
    assert result.summary()["mean_reference_error"] == pytest.approx(1.6)


@pytest.mark.parametrize(
    "tolerances, emitted, reference, message",
    [
        ([1e-2, 1e-3], [1.0], [1.0, 1.0], "match the tolerance sweep"),
        ([1e-2, 1e-2], [1.0, 1.0], [1.0, 1.0], "positive and unique"),
        ([1e-2], [-1.0], [1.0], "non-negative"),
    ],
)
def test_tolerance_calibration_rejects_invalid_inputs(tolerances, emitted, reference, message) -> None:
    with pytest.raises(ValueError, match=message):
        calibrate_tolerance_sweep(tolerances, emitted, reference)
