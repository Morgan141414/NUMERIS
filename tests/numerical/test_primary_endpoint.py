import json

import pytest

from numeris.benchmarks import (
    PrimaryEndpointConditions,
    build_primary_endpoint_report,
)


def _record(seed, candidate_likelihood=10.1, candidate_params=(1.02, 0.98), **candidate_flags):
    base = {
        "success": True,
        "budget": {"within_budget": True},
        "negative_log_likelihood": 10.0,
        "parameter_estimate": [1.0, 1.0],
    }
    candidate = {
        "success": True,
        "budget": {"within_budget": True},
        "negative_log_likelihood": candidate_likelihood,
        "parameter_estimate": list(candidate_params),
    }
    candidate.update(candidate_flags)
    return {
        "seed": seed,
        "truth_parameters": [1.0, 1.0],
        "reference_likelihood": 10.0,
        "baseline": base,
        "candidate": candidate,
    }


def test_primary_endpoint_requires_predeclared_conditions_and_is_json_safe():
    report = build_primary_endpoint_report([_record(seed) for seed in range(3)])
    assert report["decision"] == "NO_CONFIRMED_ADVANTAGE"
    assert report["conditions"]["predeclared"] is False
    assert report["scientific_claim"].startswith("none")
    json.dumps(report, allow_nan=False)


def test_primary_endpoint_computes_paired_metrics_and_bootstrap_ci():
    records = [_record(seed, 10.01, (1.001, 1.001)) for seed in range(12)]
    for record in records:
        record["baseline"]["negative_log_likelihood"] = 10.2
        record["baseline"]["parameter_estimate"] = [1.1, 1.1]
    conditions = PrimaryEndpointConditions(
        min_comparable_pairs=10,
        max_failure_rate=0.0,
        max_budget_rate=0.0,
        bootstrap_resamples=300,
        bootstrap_seed=19,
    )
    report = build_primary_endpoint_report(records, conditions=conditions)
    assert report["counts"]["comparable_pairs"] == 12
    assert report["endpoints"]["likelihood_distortion"]["paired_candidate_minus_baseline"]["mean"] < 0
    assert report["endpoints"]["parameter_rmse"]["paired_candidate_minus_baseline"]["bootstrap_ci"]["available"]
    assert set(report["records"][0]["metrics"]["candidate"]) == {
        "likelihood_distortion",
        "parameter_rmse",
    }
    assert report["decision"] == "CONFIRMED_ADVANTAGE_UNDER_PREDECLARED_RULE"


def test_primary_endpoint_retains_missing_failure_and_budget_cases():
    records = [_record(seed) for seed in range(4)]
    records[1]["candidate"]["success"] = False
    records[2]["candidate"]["budget"]["within_budget"] = False
    del records[3]["candidate"]["parameter_estimate"]
    report = build_primary_endpoint_report(
        records,
        conditions={"min_comparable_pairs": 1, "bootstrap_resamples": 200},
    )
    assert report["counts"] == {"total_records": 4, "comparable_pairs": 1, "excluded_pairs": 3}
    assert report["rates"]["candidate"]["failure_rate"] == pytest.approx(0.25)
    assert report["rates"]["candidate"]["budget_rate"] == pytest.approx(0.25)
    assert report["decision"] == "NO_CONFIRMED_ADVANTAGE"
    assert report["records"][1]["excluded_reasons"]


def test_primary_endpoint_rejects_mismatched_parameter_dimensions():
    record = _record(1, candidate_params=(1.0,))
    report = build_primary_endpoint_report([record], conditions={"min_comparable_pairs": 1})
    assert report["counts"]["comparable_pairs"] == 0
    assert "metric_error" in report["records"][0]["excluded_reasons"][0]
