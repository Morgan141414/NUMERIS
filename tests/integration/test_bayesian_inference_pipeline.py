"""End-to-end test for the lightweight Bayesian inference slice."""

import numpy as np
import pytest

from numeris.inference import grid_posterior, posterior_distance, run_parameter_recovery
from numeris.models import ODEModel


pytest.importorskip("scipy")


def _decay_model() -> ODEModel:
    times = np.linspace(0.0, 1.0, 9)

    def rhs(_time, state, params):
        return np.array([-params[0] * state[0]])

    return ODEModel(
        rhs=rhs,
        initial_state=[1.0],
        t_span=(0.0, 1.0),
        observation_times=times,
    )


def test_reproducible_ode_likelihood_to_posterior_pipeline():
    model = _decay_model()
    truth = 0.7
    observations = np.exp(-truth * model.observation_times)[:, None]
    grid = np.array([[0.5], [0.7], [0.9]])

    first = grid_posterior(model, observations, 0.01, grid, parameter_names=["rate"])
    second = grid_posterior(model, observations, 0.01, grid, parameter_names=["rate"])

    assert np.array_equal(first.posterior, second.posterior)
    assert posterior_distance(first, second) == pytest.approx(0.0)
    assert first.mode.tolist() == [truth]
    assert first.summary()["credible_intervals"]


def test_end_to_end_parameter_recovery_exposes_solver_settings():
    model = _decay_model()
    result = run_parameter_recovery(
        model,
        [0.7],
        0.01,
        np.array([[0.5], [0.7], [0.9]]),
        seed=7,
        parameter_names=["rate"],
    )

    assert result.truth.tolist() == [0.7]
    assert result.map_estimate.tolist() == [0.7]
    assert result.map_rmse == pytest.approx(0.0)
    assert result.credible_interval_coverage.shape == (1,)
    assert result.solver_settings["method"] == "DOP853"
    assert result.summary()["limitations"]
