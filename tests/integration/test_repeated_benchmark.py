import importlib.util
import json

import numpy as np
import pytest

from numeris.benchmarks import damped_oscillator
from numeris.benchmarks.repeated import run_repeated
from numeris.benchmarks.runner import SolverConfig


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("scipy") is None,
    reason="SciPy is required for repeated benchmark integration tests",
)


def test_repeated_benchmark_is_json_friendly_and_summarizes_trials():
    times = np.linspace(0.0, 2.0, 21)
    model = damped_oscillator(times)
    params = np.array([1.0, 0.1, 0.2])

    from numeris.solvers import solve_ode

    reference = solve_ode(model, params, method="DOP853", rtol=1e-11, atol=1e-13).states
    report = run_repeated(
        model,
        params,
        [
            SolverConfig("rk45", method="RK45", rtol=1e-6, atol=1e-8),
            SolverConfig("dop853", method="DOP853", rtol=1e-8, atol=1e-10),
        ],
        seeds=[1, 2, 3],
        sigma=0.05,
        reference_states=reference,
    )

    assert report["n_configurations"] == 2
    assert report["seeds"] == [1, 2, 3]
    for result in report["results"]:
        assert result["n_trials"] == 3
        assert result["failure_rate"] == 0.0
        assert result["summaries"]["nfev"]["n"] == 3
        assert result["summaries"]["runtime_s"]["n"] == 3
        assert result["summaries"]["target_error"]["n"] == 3
        assert all(run["target_error"] is not None for run in result["runs"])

    json.dumps(report, allow_nan=False)


def test_repeated_benchmark_counts_failed_trials():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    reference = np.zeros((11, 2))
    report = run_repeated(
        model,
        np.array([1.0, 0.1, 0.0]),
        [SolverConfig("invalid", method="not-a-solver")],
        seeds=[4, 5],
        sigma=0.05,
        reference_states=reference,
    )

    result = report["results"][0]
    assert result["failure_rate"] == 1.0
    assert result["summaries"] == {"nfev": None, "runtime_s": None, "target_error": None}
    assert all(run["success"] is False for run in result["runs"])
