import json

import numpy as np

from numeris.benchmarks import damped_oscillator, run_bounded_benchmark
from numeris.benchmarks.runner import SolverConfig
from numeris.budget import BoundedBenchmarkBudget


def _fixture():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    params = np.array([1.0, 0.1, 0.2])
    return model, params


def test_preflight_rejects_campaign_before_solver_calls():
    model, params = _fixture()
    budget = BoundedBenchmarkBudget(max_runs=1)
    report = run_bounded_benchmark(
        model,
        params,
        [SolverConfig("a"), SolverConfig("b")],
        budget=budget,
    )
    assert report["status"] == "preflight_rejected"
    assert report["results"] == []
    assert report["budget"]["attempted_runs"] == 0
    json.dumps(report, allow_nan=False)


def test_overrun_is_explicit_and_stops_later_solver_calls():
    model, params = _fixture()
    budget = BoundedBenchmarkBudget(max_rhs_evals=1)
    report = run_bounded_benchmark(
        model,
        params,
        [SolverConfig("a"), SolverConfig("b")],
        budget=budget,
    )
    assert report["status"] == "over_budget"
    assert report["results"][0]["execution"]["status"] == "over_budget"
    assert report["results"][0]["execution"]["call_was_interrupted"] is False
    assert report["results"][1]["status"] == "not_started"
    assert report["budget"]["completed_runs"] == 1
    assert report["budget"]["attempted_runs"] == 1
    json.dumps(report, allow_nan=False)


def test_estimates_can_reject_rhs_campaign_without_running_solver():
    model, params = _fixture()
    budget = BoundedBenchmarkBudget(max_rhs_evals=10)
    report = run_bounded_benchmark(
        model,
        params,
        [SolverConfig("a"), SolverConfig("b")],
        budget=budget,
        estimated_rhs_evals_per_run=6,
    )
    assert report["status"] == "preflight_rejected"
    assert report["preflight"]["reasons"] == ["estimated RHS evaluations exceed max_rhs_evals"]
    assert report["budget"]["attempted_runs"] == 0
