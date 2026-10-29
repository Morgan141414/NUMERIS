import importlib.util
import json

import numpy as np
import pytest

from numeris.benchmarks import damped_oscillator, run_benchmark
from numeris.benchmarks.runner import SolverConfig
from numeris.budget import Budget, BudgetLedger, BudgetExceededError


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("scipy") is None,
    reason="SciPy is required for integration benchmark tests",
)


def test_oscillator_benchmark_collects_metrics_and_is_json_serializable():
    model = damped_oscillator(np.linspace(0.0, 4.0, 41))
    params = np.array([1.0, 0.1, 0.2])

    from numeris.solvers import solve_ode

    reference_states = solve_ode(
        model, params, method="DOP853", rtol=1e-11, atol=1e-13
    ).states
    report = run_benchmark(
        model,
        params,
        [
            SolverConfig("rk45", method="RK45", rtol=1e-6, atol=1e-8),
            {"name": "dop853", "method": "DOP853", "rtol": 1e-8, "atol": 1e-10},
        ],
        observations=model.observe(reference_states),
        sigma=0.05,
        reference_states=reference_states,
        name="oscillator",
    )

    assert report["name"] == "oscillator"
    assert report["n_configurations"] == 2
    for item in report["results"]:
        assert item["success"]
        assert item["trajectory"]["rmse"] is not None
        assert item["likelihood"]["available"]
        assert item["likelihood"]["negative_log_likelihood"] is not None
        assert item["cost"]["nfev"] > 0
        assert item["cost"]["runtime_s"] >= 0

    json.dumps(report, allow_nan=False)


def test_oscillator_runner_requires_sigma_for_likelihood():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    with pytest.raises(ValueError, match="sigma"):
        run_benchmark(
            model,
            np.array([1.0, 0.1, 0.0]),
            [SolverConfig("rk45", method="RK45")],
            observations=np.zeros((11, 2)),
        )


def test_runner_enforces_rhs_budget():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    with pytest.raises(BudgetExceededError, match="rhs evaluations"):
        run_benchmark(
            model,
            np.array([1.0, 0.1, 0.0]),
            [SolverConfig("rk45", method="RK45")],
            budget=BudgetLedger(Budget(max_rhs_evals=1)),
        )
