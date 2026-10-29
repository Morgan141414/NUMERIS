import numpy as np
import pytest

from numeris.inference import PosteriorCalibrationResult, calibrate_credible_intervals
from numeris.models import ODEModel


def _decay_model():
    times = np.linspace(0.0, 1.0, 6)

    def rhs(_t, state, params):
        return np.array([-params[0] * state[0]])

    return ODEModel(rhs=rhs, initial_state=[1.0], t_span=(0.0, 1.0), observation_times=times)


def test_calibration_is_reproducible_and_reports_coverage():
    model = _decay_model()
    kwargs = dict(
        model=model,
        truth=[0.7],
        sigma=0.01,
        parameter_grid=np.array([[0.5], [0.7], [0.9]]),
        repetitions=4,
        seed=19,
        parameter_names=["rate"],
    )
    first = calibrate_credible_intervals(**kwargs)
    second = calibrate_credible_intervals(**kwargs)

    assert isinstance(first, PosteriorCalibrationResult)
    assert first.coverage_counts.tolist() == [4]
    assert first.coverage.tolist() == [1.0]
    assert first.coverage_standard_error.tolist() == [0.0]
    assert first.coverage_confidence_level == 0.95
    assert first.coverage_confidence_interval.shape == (1, 2)
    lower, upper = first.coverage_confidence_interval[0]
    assert lower < first.coverage[0]
    assert first.coverage[0] <= upper + 1e-15
    assert first.replicate_coverage.shape == (4, 1)
    assert first.replicate_seeds == second.replicate_seeds
    assert np.array_equal(first.replicate_coverage, second.replicate_coverage)
    assert np.allclose(first.mean_interval_width, second.mean_interval_width)
    assert first.summary()["parameter_names"] == ["rate"]
    assert "no superiority" in " ".join(first.summary()["limitations"])


def test_calibration_validates_small_protocol_inputs():
    model = _decay_model()
    common = dict(truth=[0.7], sigma=0.01, parameter_grid=[[0.5], [0.7], [0.9]])
    with pytest.raises(ValueError, match="positive integer"):
        calibrate_credible_intervals(model, repetitions=0, **common)
    with pytest.raises(ValueError, match="credible_level"):
        calibrate_credible_intervals(model, credible_level=1.0, **common)
    with pytest.raises(ValueError, match="coverage_confidence_level"):
        calibrate_credible_intervals(model, coverage_confidence_level=1.0, **common)
    with pytest.raises(ValueError, match="parameter_names"):
        calibrate_credible_intervals(model, parameter_names=["a", "b"], **common)
    with pytest.raises(ValueError, match="truth dimensionality"):
        calibrate_credible_intervals(model, **{**common, "truth": [0.7, 0.1]})


def test_calibration_summary_exposes_monte_carlo_uncertainty():
    result = calibrate_credible_intervals(
        _decay_model(),
        truth=[0.7],
        sigma=0.01,
        parameter_grid=[[0.5], [0.7], [0.9]],
        repetitions=4,
        seed=19,
        coverage_confidence_level=0.9,
    )

    summary = result.summary()
    assert summary["coverage_confidence_level"] == 0.9
    interval = np.asarray(summary["coverage_confidence_interval"])
    assert interval.shape == (1, 2)
    assert 0.0 <= interval[0, 0] <= result.coverage[0] <= interval[0, 1] <= 1.0
