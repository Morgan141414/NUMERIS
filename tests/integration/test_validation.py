import importlib.util
import json

import numpy as np
import pytest

from numeris.benchmarks import damped_oscillator
from numeris.benchmarks.runner import SolverConfig
from numeris.benchmarks.validation import (
    AblationCase,
    BudgetCaps,
    predefined_solver_configs,
    run_ablation_cases,
    run_equal_budget_comparison,
)


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("scipy") is None,
    reason="SciPy is required for validation integration tests",
)


def _fixture():
    times = np.linspace(0.0, 1.0, 11)
    model = damped_oscillator(times)
    params = np.array([1.0, 0.1, 0.2])
    from numeris.solvers import solve_ode

    reference = solve_ode(model, params, method="DOP853", rtol=1e-11, atol=1e-13).states
    return model, params, reference


def test_predefined_configs_cover_required_solver_families():
    configs = predefined_solver_configs()
    assert [config.method for config in configs] == ["RK45", "DOP853", "Radau", "BDF", "LSODA"]
    assert all(config.as_dict()["max_step"] is None for config in configs)


def test_equal_budget_comparison_pairs_seeds_and_is_json_friendly():
    model, params, reference = _fixture()
    report = run_equal_budget_comparison(
        model,
        params,
        seeds=[3, 7, 11],
        sigma=0.05,
        reference_states=reference,
        baseline=SolverConfig("base", method="RK45", rtol=1e-6, atol=1e-8),
        policy=SolverConfig("candidate", method="DOP853", rtol=1e-8, atol=1e-10),
        budget_caps=BudgetCaps(max_rhs_evals=100_000),
    )
    assert report["scientific_claim"].startswith("none")
    assert report["paired"]["n_pairs"] == 3
    assert report["paired"]["n_comparable"] == 3
    assert [row["seed"] for row in report["paired"]["pairs"]] == [3, 7, 11]
    assert all(
        trial["budget"]["within_budget"]
        for result in report["results"].values()
        for trial in result["trials"]
    )
    json.dumps(report, allow_nan=False)

def test_budget_caps_keep_violations_visible_and_exclude_pairs():
    model, params, reference = _fixture()
    report = run_equal_budget_comparison(
        model,
        params,
        seeds=[1],
        sigma=0.05,
        reference_states=reference,
        baseline=SolverConfig("base", method="RK45"),
        policy=SolverConfig("candidate", method="DOP853"),
        budget_caps=BudgetCaps(max_rhs_evals=0),
    )
    assert report["paired"]["n_comparable"] == 0
    assert report["paired"]["pairs"][0]["target_error_difference_policy_minus_baseline"] is None
    assert all(
        trial["budget"]["within_budget"] is False
        for result in report["results"].values()
        for trial in result["trials"]
    )


def test_ablation_cases_preserve_case_metadata_and_pairing():
    model, params, reference = _fixture()
    report = run_ablation_cases(
        model,
        params,
        seeds=[5, 6],
        sigma=0.05,
        reference_states=reference,
        cases=[
            AblationCase(
                "without_temporal_allocation",
                baseline=SolverConfig("base", method="RK45"),
                policy=SolverConfig("candidate", method="DOP853"),
                disabled_components=("temporal_allocation",),
                description="Disable the temporal allocation component.",
            )
        ],
        budget_caps={"max_rhs_evals": 100_000},
    )
    assert report["n_cases"] == 1
    case = report["cases"][0]
    assert case["ablation"]["disabled_components"] == ["temporal_allocation"]
    assert case["paired"]["n_pairs"] == 2
    json.dumps(report, allow_nan=False)

