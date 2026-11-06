import numpy as np
import pytest

from numeris.inference.multistart import (
    ObjectiveEvaluation,
    budget_aware_multistart_mle,
)


def test_fixed_starts_are_run_in_order_and_best_tie_uses_first_arm():
    calls = []

    def evaluator(params):
        calls.append(tuple(params))
        return ObjectiveEvaluation(value=1.0, rhs_evals=2)

    result = budget_aware_multistart_mle(
        evaluator,
        starts=[[2.0], [0.0]],
        bounds=[(-3.0, 3.0)],
        options={"maxiter": 20},
    )

    assert result.status == "completed"
    assert result.best_arm_index == 0
    assert [arm.index for arm in result.arms] == [0, 1]
    assert result.arms[0].start == (2.0,)
    assert calls[0] == (2.0,)


def test_each_arm_has_independent_objective_budget_and_reports_over_budget():
    def evaluator(params):
        return ObjectiveEvaluation(value=float(params[0] ** 2), rhs_evals=1)

    result = budget_aware_multistart_mle(
        evaluator,
        starts=[[2.0], [3.0]],
        max_objective_evals_per_arm=1,
        options={"maxiter": 20},
    )

    assert result.status == "over_budget"
    assert result.over_budget_arms == 2
    assert all(arm.status == "over_budget" for arm in result.arms)
    assert all(arm.objective_evals == 1 for arm in result.arms)
    assert result.total_objective_evals == 2


def test_rhs_budget_is_checked_per_arm_and_incomplete_arms_are_not_selected():
    def evaluator(params):
        return ObjectiveEvaluation(value=float((params[0] - 4.0) ** 2), rhs_evals=3)

    result = budget_aware_multistart_mle(
        evaluator,
        starts=[[0.0], [4.0]],
        max_rhs_evals_per_arm=2,
        options={"maxiter": 20},
    )

    assert result.status == "over_budget"
    assert result.best_params is None
    assert result.total_rhs_evals == 6
    assert all(arm.status == "over_budget" for arm in result.arms)


def test_failed_evaluator_is_recorded_without_abort_or_false_success():
    def evaluator(params):
        if params[0] < 0:
            return ObjectiveEvaluation(value=np.nan, rhs_evals=4, success=False, message="invalid")
        return ObjectiveEvaluation(value=float(params[0] ** 2), rhs_evals=1)

    result = budget_aware_multistart_mle(
        evaluator,
        starts=[[-1.0], [2.0]],
        options={"maxiter": 20},
    )

    assert result.status == "completed"
    assert result.failed_arms == 1
    assert result.completed_arms == 1
    assert result.best_arm_index == 1
    assert result.arms[0].params is None


def test_invalid_inputs_are_rejected():
    evaluator = lambda params: ObjectiveEvaluation(value=0.0)
    with pytest.raises(ValueError, match="non-empty"):
        budget_aware_multistart_mle(evaluator, [])
    with pytest.raises(ValueError, match="dimension"):
        budget_aware_multistart_mle(evaluator, [[0.0]], bounds=[(0.0, 1.0), (0.0, 1.0)])
    with pytest.raises(ValueError, match="positive"):
        budget_aware_multistart_mle(evaluator, [[0.0]], max_rhs_evals_per_arm=0)
