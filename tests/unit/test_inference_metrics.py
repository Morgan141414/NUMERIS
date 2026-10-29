import numpy as np
import pytest

from numeris.inference.metrics import (
    false_optimum_rate,
    likelihood_distortion,
    parameter_rmse,
)


def test_parameter_rmse_for_vectors():
    assert parameter_rmse([1.0, 2.0], [1.0, 4.0]) == pytest.approx(np.sqrt(2.0))


def test_likelihood_distortion_is_relative():
    assert likelihood_distortion(10.0, 12.0) == pytest.approx(0.2)
    assert likelihood_distortion(0.0, 0.0) == 0.0


def test_false_optimum_rate_matches_scalar_optima_with_tolerance():
    assert false_optimum_rate([1.0, 3.0], [1.05, 5.0], 0.1) == pytest.approx(0.5)


def test_false_optimum_rate_supports_parameter_vectors():
    true = np.array([[0.0, 0.0], [1.0, 1.0]])
    found = np.array([[0.05, 0.0], [3.0, 3.0]])
    assert false_optimum_rate(true, found, 0.1) == pytest.approx(0.5)


@pytest.mark.parametrize(
    "call",
    [
        lambda: parameter_rmse([1.0], [1.0, 2.0]),
        lambda: parameter_rmse([1.0, np.nan], [1.0, 2.0]),
        lambda: likelihood_distortion([1.0], 1.0),
        lambda: likelihood_distortion(1.0, np.inf),
        lambda: false_optimum_rate([], [1.0], 0.1),
        lambda: false_optimum_rate([1.0], [1.0], -0.1),
        lambda: false_optimum_rate([[1.0, 2.0]], [1.0], 0.1),
    ],
)
def test_metrics_validate_inputs(call):
    with pytest.raises(ValueError):
        call()
