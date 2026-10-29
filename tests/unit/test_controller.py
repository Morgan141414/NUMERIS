import pytest

from numeris.controller import RefinementDecision, SensitivityAwarePolicy


def test_policy_estimates_target_error_and_refines_when_beneficial():
    policy = SensitivityAwarePolicy(
        target_tolerance=0.1,
        min_benefit_cost_ratio=0.4,
    )

    decision = policy.evaluate(
        state_error_estimate=0.5,
        target_sensitivity=2.0,
        candidate_state_error_reduction=0.2,
        candidate_cost=0.5,
        remaining_budget=1.0,
    )

    assert isinstance(decision, RefinementDecision)
    assert decision.target_error_estimate == pytest.approx(1.0)
    assert decision.marginal_benefit == pytest.approx(0.4)
    assert decision.benefit_cost_ratio == pytest.approx(0.8)
    assert decision.refine
    assert not decision.stop


def test_policy_stops_when_target_tolerance_is_reached():
    decision = SensitivityAwarePolicy(target_tolerance=0.1).evaluate(
        state_error_estimate=0.02,
        target_sensitivity=2.0,
        candidate_state_error_reduction=0.01,
    )

    assert decision.stop
    assert not decision.refine
    assert decision.reason == "target tolerance reached"


def test_policy_stops_when_budget_or_marginal_benefit_is_insufficient():
    policy = SensitivityAwarePolicy(target_tolerance=0.01, min_benefit_cost_ratio=1.0)

    budget_decision = policy.evaluate(1.0, 1.0, 0.8, candidate_cost=2.0, remaining_budget=1.0)
    assert budget_decision.stop
    assert budget_decision.reason == "candidate exceeds remaining budget"

    benefit_decision = policy.evaluate(1.0, 1.0, 0.2, candidate_cost=1.0, remaining_budget=1.0)
    assert benefit_decision.stop
    assert benefit_decision.reason == "marginal benefit-cost ratio below threshold"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"state_error_estimate": -1.0, "target_sensitivity": 1.0, "candidate_state_error_reduction": 1.0},
        {"state_error_estimate": 1.0, "target_sensitivity": 1.0, "candidate_state_error_reduction": -1.0},
        {"state_error_estimate": 1.0, "target_sensitivity": 1.0, "candidate_state_error_reduction": 1.0, "candidate_cost": 0.0},
    ],
)
def test_policy_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        SensitivityAwarePolicy(target_tolerance=0.1).evaluate(**kwargs)


def test_policy_rejects_invalid_thresholds():
    with pytest.raises(ValueError):
        SensitivityAwarePolicy(target_tolerance=-1.0)
    with pytest.raises(ValueError):
        SensitivityAwarePolicy(target_tolerance=1.0, min_benefit_cost_ratio=-1.0)
