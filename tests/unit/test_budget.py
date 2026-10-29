import pytest

from numeris.budget import Budget, BudgetExceededError, BudgetLedger


def test_ledger_tracks_rhs_runs_and_remaining_capacity():
    ledger = BudgetLedger(Budget(max_rhs_evals=5, max_runs=2))
    ledger.charge_rhs(3)
    ledger.record_run()
    assert ledger.rhs_evals == 3
    assert ledger.remaining_rhs_evals == 2
    assert ledger.remaining_runs == 1


def test_rhs_limit_is_checked_before_charge():
    ledger = BudgetLedger(Budget(max_rhs_evals=2))
    with pytest.raises(BudgetExceededError, match="rhs evaluations"):
        ledger.charge_rhs(3)
    assert ledger.rhs_evals == 0


def test_run_limit_is_checked_for_repeated_runs():
    ledger = BudgetLedger(Budget(max_runs=1))
    ledger.start_run()
    with pytest.raises(BudgetExceededError, match="runs"):
        ledger.start_run()


def test_time_limit_can_be_charged_explicitly():
    ledger = BudgetLedger(Budget(max_time_s=1.0))
    ledger.charge_time(0.75)
    with pytest.raises(BudgetExceededError, match="time"):
        ledger.charge_time(0.3)


def test_budget_rejects_negative_limits():
    with pytest.raises(ValueError):
        Budget(max_rhs_evals=-1)
