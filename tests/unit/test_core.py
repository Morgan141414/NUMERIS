import numpy as np

from numeris.benchmarks import damped_oscillator
from numeris.controller import GoalOrientedDiagnostic
from numeris.solvers import solve_ode


def test_oscillator_solver_runs_and_records_cost():
    result = solve_ode(damped_oscillator(), np.array([1.0, 0.1, 0.0]))
    assert result.success
    assert result.states.shape == (201, 2)
    assert result.nfev > 0
    assert result.runtime_s >= 0


def test_controller_respects_budget():
    controller = GoalOrientedDiagnostic(target_tolerance=1e-3)
    assert controller.should_refine(1e-2, cost=2, remaining_budget=2)
    assert not controller.should_refine(1e-2, cost=3, remaining_budget=2)
