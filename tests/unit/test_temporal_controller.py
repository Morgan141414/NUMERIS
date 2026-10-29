import numpy as np
import pytest

from numeris.controller import allocate_budget_by_sensitivity


def test_temporal_allocator_respects_budget_and_prefers_sensitive_intervals():
    allocations, spent = allocate_budget_by_sensitivity(
        np.array([1.0, 10.0, 2.0]), np.array([1.0, 1.0, 4.0]), 1.0
    )
    assert spent == pytest.approx(1.0)
    assert allocations[1].selected
    assert not allocations[0].selected


def test_temporal_allocator_validates_costs():
    with pytest.raises(ValueError):
        allocate_budget_by_sensitivity(np.array([1.0]), np.array([0.0]), 1.0)
