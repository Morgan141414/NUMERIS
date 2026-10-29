import numpy as np

from numeris.benchmarks import damped_oscillator, fitzhugh_nagumo, lorenz, lotka_volterra, robertson
from numeris.solvers import solve_ode


def test_required_solver_methods_run_on_benign_model():
    model = damped_oscillator(np.linspace(0.0, 1.0, 21))
    params = np.array([1.0, 0.1, 0.2])
    for method in ("RK45", "DOP853", "Radau", "BDF", "LSODA"):
        result = solve_ode(model, params, method=method)
        assert result.success, (method, result.message)
        assert result.states.shape == (21, 2)


def test_required_benchmark_factories_remain_public():
    assert all(callable(factory) for factory in (
        damped_oscillator, fitzhugh_nagumo, lotka_volterra, lorenz, robertson
    ))
