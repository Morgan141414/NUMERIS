import numpy as np
import pytest

from numeris.inference import (
    PairedToleranceSweepResult,
    PosteriorCalibrationResult,
    calibrate_credible_intervals,
    paired_tolerance_sweep,
)
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


def test_paired_tolerance_sweep_reuses_observations_and_is_reproducible():
    model = _decay_model()
    kwargs = dict(
        model=model,
        truth=[0.7],
        sigma=0.01,
        parameter_grid=[[0.5], [0.7], [0.9]],
        tolerances=[(1e-6, 1e-8), (1e-10, 1e-12)],
        repetitions=3,
        seed=23,
        parameter_names=["rate"],
    )
    first = paired_tolerance_sweep(**kwargs)
    second = paired_tolerance_sweep(**kwargs)

    assert isinstance(first, PairedToleranceSweepResult)
    assert first.observation_seeds == second.observation_seeds
    assert np.array_equal(first.map_estimates, second.map_estimates)
    assert np.array_equal(first.posterior_means, second.posterior_means)
    assert np.allclose(first.posterior_distance_from_reference, second.posterior_distance_from_reference)
    assert first.map_estimates.shape == (3, 2, 1)
    assert first.posterior_means.shape == (3, 2, 1)
    assert np.allclose(first.map_shift_from_reference[:, 0], 0.0)
    assert np.allclose(first.posterior_distance_from_reference[:, 0], 0.0)
    summary = first.summary()
    assert summary["tolerances"] == [
        {"rtol": 1e-6, "atol": 1e-8},
        {"rtol": 1e-10, "atol": 1e-12},
    ]
    assert "same observations" in " ".join(summary["interpretation"])


def test_paired_tolerance_sweep_validates_tolerance_protocol():
    model = _decay_model()
    common = dict(
        truth=[0.7], sigma=0.01,
        parameter_grid=[[0.5], [0.7], [0.9]], repetitions=1,
    )
    with pytest.raises(ValueError, match="non-empty"):
        paired_tolerance_sweep(model, tolerances=[], **common)
    with pytest.raises(ValueError, match="positive rtol"):
        paired_tolerance_sweep(model, tolerances=[(0.0, 1e-8)], **common)
    with pytest.raises(ValueError, match="observation tolerances"):
        paired_tolerance_sweep(
            model, tolerances=[(1e-6, 1e-8)], observation_rtol=0.0, **common
        )
