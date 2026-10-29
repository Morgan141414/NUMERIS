"""Falsifiable first controller: rank refinements by target sensitivity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GoalOrientedDiagnostic:
    """A diagnostic policy, deliberately not presented as a proven method."""

    target_tolerance: float

    def should_refine(self, estimated_target_error: float, cost: float = 1.0,
                      remaining_budget: float = float("inf")) -> bool:
        if cost <= 0:
            raise ValueError("cost must be positive")
        return estimated_target_error > self.target_tolerance and cost <= remaining_budget
