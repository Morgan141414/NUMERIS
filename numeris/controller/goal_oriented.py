"""Goal-oriented policies for numerical refinement experiments.

The policies in this module are deliberately diagnostic: they expose the
assumptions used to rank a possible refinement and do not claim an optimality
or convergence theorem.
"""

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


@dataclass(frozen=True)
class RefinementDecision:
    """Output of :class:`SensitivityAwarePolicy`.

    ``target_error_estimate`` is an estimate of the absolute error in the
    selected scientific target.  ``marginal_benefit`` is the predicted
    reduction in that error from the candidate refinement and
    ``marginal_cost`` is its supplied computational cost.  The decision is
    reproducible from these reported quantities and the policy thresholds.
    """

    target_error_estimate: float
    marginal_benefit: float
    marginal_cost: float
    benefit_cost_ratio: float
    refine: bool
    stop: bool
    reason: str


@dataclass(frozen=True)
class SensitivityAwarePolicy:
    """A simple, explicit sensitivity-aware refinement policy.

    Formal input to :meth:`evaluate`:

    * ``state_error_estimate``: non-negative estimate of the current
      numerical state error;
    * ``target_sensitivity``: absolute local sensitivity of the target to
      state error;
    * ``candidate_state_error_reduction``: non-negative predicted reduction
      in state error from one candidate refinement;
    * ``candidate_cost``: strictly positive predicted computational cost;
    * ``remaining_budget``: non-negative budget available for that refinement.

    The policy estimates ``E_target = |sensitivity| * state_error`` and
    ``benefit = |sensitivity| * state_error_reduction``.  It refines exactly
    when the target is above tolerance, the candidate fits the budget, and
    ``benefit / cost`` is at least ``min_benefit_cost_ratio``.  Otherwise it
    returns a stopping decision.  This is a transparent heuristic, not a
    claim of global optimality.
    """

    target_tolerance: float
    min_benefit_cost_ratio: float = 0.0

    def __post_init__(self) -> None:
        if self.target_tolerance < 0:
            raise ValueError("target_tolerance must be non-negative")
        if self.min_benefit_cost_ratio < 0:
            raise ValueError("min_benefit_cost_ratio must be non-negative")

    def evaluate(
        self,
        state_error_estimate: float,
        target_sensitivity: float,
        candidate_state_error_reduction: float,
        candidate_cost: float = 1.0,
        remaining_budget: float = float("inf"),
    ) -> RefinementDecision:
        """Evaluate one candidate refinement and return a formal decision."""

        values = {
            "state_error_estimate": state_error_estimate,
            "target_sensitivity": target_sensitivity,
            "candidate_state_error_reduction": candidate_state_error_reduction,
            "candidate_cost": candidate_cost,
            "remaining_budget": remaining_budget,
        }
        for name, value in values.items():
            if value < 0:
                raise ValueError(f"{name} must be non-negative")
        if candidate_cost == 0:
            raise ValueError("candidate_cost must be positive")

        sensitivity = abs(target_sensitivity)
        target_error = sensitivity * state_error_estimate
        benefit = sensitivity * candidate_state_error_reduction
        ratio = benefit / candidate_cost

        if target_error <= self.target_tolerance:
            reason = "target tolerance reached"
        elif candidate_cost > remaining_budget:
            reason = "candidate exceeds remaining budget"
        elif ratio < self.min_benefit_cost_ratio:
            reason = "marginal benefit-cost ratio below threshold"
        elif benefit == 0:
            reason = "candidate has no estimated target benefit"
        else:
            reason = "candidate meets target and budget policy"

        refine = reason == "candidate meets target and budget policy"
        return RefinementDecision(
            target_error_estimate=target_error,
            marginal_benefit=benefit,
            marginal_cost=candidate_cost,
            benefit_cost_ratio=ratio,
            refine=refine,
            stop=not refine,
            reason=reason,
        )
