import numpy as np
import pytest

from numeris.error_analysis import error_bound_calibration


def test_error_bound_calibration_reports_coverage_and_excess():
    result = error_bound_calibration(np.array([1.0, 1.0]), np.array([0.5, 2.0]))
    assert result["coverage"] == pytest.approx(0.5)
    assert result["mean_excess"] == pytest.approx(0.5)


def test_error_bound_calibration_rejects_negative_values():
    with pytest.raises(ValueError):
        error_bound_calibration(np.array([-1.0]), np.array([0.0]))
