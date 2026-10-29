"""Experimental temporal budget allocation policy.

This greedy policy is a baseline for ablation, not an optimality theorem.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class IntervalAllocation:
    interval: int
    sensitivity: float
    estimated_cost: float
    selected: bool


def allocate_budget_by_sensitivity(
    sensitivities: np.ndarray,
    estimated_costs: np.ndarray,
    total_budget: float,
) -> tuple[list[IntervalAllocation], float]:
    """Greedily select time intervals by sensitivity per unit cost."""
    sensitivity = np.asarray(sensitivities, dtype=float)
    costs = np.asarray(estimated_costs, dtype=float)
    if sensitivity.ndim != 1 or costs.shape != sensitivity.shape or sensitivity.size == 0:
        raise ValueError("sensitivities and estimated_costs must be equal non-empty 1-D arrays")
    if np.any(~np.isfinite(sensitivity)) or np.any(~np.isfinite(costs)) or np.any(costs <= 0):
        raise ValueError("inputs must be finite and costs must be positive")
    if not np.isfinite(total_budget) or total_budget < 0:
        raise ValueError("total_budget must be finite and non-negative")
    order = np.argsort(-np.abs(sensitivity) / costs)
    selected = np.zeros(sensitivity.size, dtype=bool)
    spent = 0.0
    for index in order:
        if spent + costs[index] <= total_budget:
            selected[index] = True
            spent += costs[index]
    allocations = [
        IntervalAllocation(int(i), float(sensitivity[i]), float(costs[i]), bool(selected[i]))
        for i in range(sensitivity.size)
    ]
    return allocations, spent
