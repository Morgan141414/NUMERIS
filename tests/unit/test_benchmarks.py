import numpy as np
import pytest

from numeris.benchmarks import (
    damped_oscillator,
    fitzhugh_nagumo,
    lotka_volterra,
    lorenz,
    robertson,
)


@pytest.mark.parametrize(
    ("factory", "parameters", "dimension"),
    [
        (damped_oscillator, [1.0, 0.1, 0.0], 2),
        (fitzhugh_nagumo, [0.7, 0.8, 0.08, 0.5], 2),
        (lotka_volterra, [1.5, 1.0, 0.75, 1.0], 2),
        (lorenz, [10.0, 28.0, 8.0 / 3.0], 3),
        (robertson, [0.04, 3.0e7, 1.0e4], 3),
    ],
)
def test_benchmark_factory_returns_valid_ode_model(factory, parameters, dimension):
    model = factory()
    times = model.observation_times
    values = model.rhs(times[0], model.x0(), np.asarray(parameters, dtype=float))

    assert model.x0().shape == (dimension,)
    assert times.ndim == 1
    assert len(times) > 1
    assert times[0] < times[-1]
    assert model.t_span == (float(times[0]), float(times[-1]))
    assert values.shape == (dimension,)
    assert np.all(np.isfinite(model.x0()))
    assert np.all(np.isfinite(values))


@pytest.mark.parametrize("factory", [fitzhugh_nagumo, lotka_volterra, lorenz, robertson])
def test_benchmark_factory_accepts_custom_observation_times(factory):
    times = np.array([0.0, 0.5, 1.0])
    model = factory(times=times)

    np.testing.assert_array_equal(model.observation_times, times)
    assert model.t_span == (0.0, 1.0)
