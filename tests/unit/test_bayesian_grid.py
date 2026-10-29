import numpy as np
import pytest

from numeris.inference import (
    GridPosterior,
    grid_posterior,
    posterior_distance,
    run_parameter_recovery,
)
from numeris.models import ODEModel


def _decay_model():
    times = np.linspace(0.0, 1.0, 6)

    def rhs(_t, state, params):
        return np.array([-params[0] * state[0]])

    return ODEModel(rhs=rhs, initial_state=[1.0], t_span=(0.0, 1.0), observation_times=times)


def test_grid_posterior_runs_ode_likelihood_and_summarises():
    model = _decay_model()
    observations = np.exp(-0.7 * model.observation_times)[:, None]
    grid = np.array([[0.4], [0.7], [1.0]])

    result = grid_posterior(model, observations, 0.02, grid, parameter_names=["rate"])

    assert isinstance(result, GridPosterior)
    assert np.isclose(result.posterior.sum(), 1.0)
    assert result.mode[0] == pytest.approx(0.7)
    assert result.summary()["parameter_names"] == ["rate"]
    assert result.credible_intervals().shape == (1, 2)


def test_posterior_distance_is_zero_for_same_posterior():
    model = _decay_model()
    observations = np.exp(-0.7 * model.observation_times)[:, None]
    grid = np.array([[0.5], [0.7], [0.9]])
    posterior = grid_posterior(model, observations, 0.02, grid)

    assert posterior_distance(posterior, posterior) == pytest.approx(0.0)
    assert posterior_distance(posterior.posterior, posterior.posterior, metric="total_variation") == pytest.approx(0.0)


def test_grid_posterior_validates_shape_and_names():
    model = _decay_model()
    observations = np.ones((6, 1))
    with pytest.raises(ValueError, match="parameter_names"):
        grid_posterior(model, observations, 0.1, [[0.5], [0.7]], parameter_names=["a", "b"])
    with pytest.raises(ValueError, match="log_prior"):
        grid_posterior(model, observations, 0.1, [[0.5], [0.7]], log_prior=[0.0])


def test_posterior_distance_rejects_unknown_metric():
    with pytest.raises(ValueError, match="metric"):
        posterior_distance(np.array([0.5, 0.5]), np.array([0.5, 0.5]), metric="unknown")


def test_parameter_recovery_returns_reproducible_summary_and_coverage():
    model = _decay_model()
    grid = np.array([[0.5], [0.7], [0.9]])
    first = run_parameter_recovery(
        model, [0.7], 0.01, grid, seed=12, parameter_names=["rate"],
    )
    second = run_parameter_recovery(
        model, [0.7], 0.01, grid, seed=12, parameter_names=["rate"],
    )

    assert first.map_estimate[0] == pytest.approx(0.7)
    assert first.posterior_mean.shape == (1,)
    assert first.map_rmse == pytest.approx(0.0)
    assert first.credible_interval_coverage.tolist() == [True]
    assert first.solver_settings == second.solver_settings
    assert np.allclose(first.posterior.posterior, second.posterior.posterior)
    assert "no superiority" in " ".join(first.limitations)
    assert first.summary()["truth"] == [0.7]


def test_parameter_recovery_accepts_provided_observations_and_validates_inputs():
    model = _decay_model()
    grid = np.array([[0.5], [0.7], [0.9]])
    observations = np.exp(-0.7 * model.observation_times)[:, None]
    result = run_parameter_recovery(
        model,
        [0.7],
        0.02,
        grid,
        observations=observations,
        seed=3,
        method="RK45",
        rtol=1e-6,
        atol=1e-8,
    )
    assert result.solver_settings["observation_source"] == "provided"
    assert result.solver_settings["method"] == "RK45"
    assert result.solver_settings["rtol"] == pytest.approx(1e-6)
    with pytest.raises(ValueError, match="truth dimensionality"):
        run_parameter_recovery(model, [0.7, 0.1], 0.02, grid)
    with pytest.raises(ValueError, match="observations must match"):
        run_parameter_recovery(model, [0.7], 0.02, grid, observations=np.ones((2, 1)))
