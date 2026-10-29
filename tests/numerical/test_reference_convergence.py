import numpy as np

from numeris.benchmarks import damped_oscillator
from numeris.error_analysis import compare_solutions
from numeris.solvers import solve_ode


def test_tightening_tolerance_reduces_oscillator_reference_discrepancy():
    model = damped_oscillator(np.linspace(0.0, 8.0, 161))
    params = np.array([1.0, 0.1, 0.2])
    loose = solve_ode(model, params, method="DOP853", rtol=1e-6, atol=1e-8)
    medium = solve_ode(model, params, method="DOP853", rtol=1e-9, atol=1e-11)
    tight = solve_ode(model, params, method="DOP853", rtol=1e-12, atol=1e-14)
    loose_error = compare_solutions(tight.states, loose.states)["rmse"]
    medium_error = compare_solutions(tight.states, medium.states)["rmse"]
    assert medium_error < loose_error
