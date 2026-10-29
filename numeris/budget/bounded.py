"""Fail-closed budget semantics for benchmark-level orchestration.

This module deliberately does not attempt to interrupt ``solve_ivp``.  A
SciPy call is an indivisible operation at this layer: its measured cost is
accounted for after it returns.  If it exceeds a cap, the report marks the
run as ``over_budget`` and no subsequent run is started.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping


def _non_negative_int(value: int | None, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or int(value) != value or value < 0:
        raise ValueError(f"{name} must be a non-negative integer or None")
    return int(value)


@dataclass(frozen=True)
class BoundedBenchmarkBudget:
    """Hard admission and accounting limits for a benchmark campaign.

    ``max_rhs_evals`` and ``max_time_s`` are checked against measured costs
    after a solver call.  They cannot interrupt that call.  ``max_runs`` is
    enforced before each call.  Optional estimates make RHS/time limits
    reject an entire planned campaign before the first solver call.
    """

    max_rhs_evals: int | None = None
    max_time_s: float | None = None
    max_runs: int | None = None
    _rhs_evals: int = field(default=0, init=False, repr=False)
    _time_s: float = field(default=0.0, init=False, repr=False)
    _attempted: int = field(default=0, init=False, repr=False)
    _completed: int = field(default=0, init=False, repr=False)
    _over_budget: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "max_rhs_evals", _non_negative_int(self.max_rhs_evals, "max_rhs_evals"))
        object.__setattr__(self, "max_runs", _non_negative_int(self.max_runs, "max_runs"))
        if self.max_time_s is not None and (self.max_time_s < 0 or self.max_time_s != self.max_time_s):
            raise ValueError("max_time_s must be finite and non-negative or None")

    def preflight(
        self,
        planned_runs: int,
        *,
        estimated_rhs_evals_per_run: int | None = None,
        estimated_time_s_per_run: float | None = None,
    ) -> dict[str, Any]:
        """Check whether a planned campaign may start without any solver call."""
        planned_runs = _non_negative_int(planned_runs, "planned_runs")
        assert planned_runs is not None
        estimated_rhs_evals_per_run = _non_negative_int(
            estimated_rhs_evals_per_run, "estimated_rhs_evals_per_run"
        )
        if estimated_time_s_per_run is not None and (
            estimated_time_s_per_run < 0 or estimated_time_s_per_run != estimated_time_s_per_run
        ):
            raise ValueError("estimated_time_s_per_run must be finite and non-negative or None")
        reasons: list[str] = []
        if self.max_runs is not None and planned_runs > self.max_runs:
            reasons.append("planned runs exceed max_runs")
        if (
            self.max_rhs_evals is not None
            and estimated_rhs_evals_per_run is not None
            and planned_runs * estimated_rhs_evals_per_run > self.max_rhs_evals
        ):
            reasons.append("estimated RHS evaluations exceed max_rhs_evals")
        if (
            self.max_time_s is not None
            and estimated_time_s_per_run is not None
            and planned_runs * estimated_time_s_per_run > self.max_time_s
        ):
            reasons.append("estimated runtime exceeds max_time_s")
        return {
            "status": "preflight_rejected" if reasons else "ready",
            "allowed": not reasons,
            "planned_runs": planned_runs,
            "reasons": reasons,
            "estimated_rhs_evals_per_run": estimated_rhs_evals_per_run,
            "estimated_time_s_per_run": (
                float(estimated_time_s_per_run) if estimated_time_s_per_run is not None else None
            ),
        }

    def can_start(self) -> bool:
        return not self._over_budget and (
            self.max_runs is None or self._attempted < self.max_runs
        )

    def start_run(self) -> None:
        """Admit one solver call, or reject it before execution."""
        if not self.can_start():
            raise RuntimeError("bounded benchmark budget does not admit another run")
        object.__setattr__(self, "_attempted", self._attempted + 1)

    def finish_run(self, cost: Mapping[str, Any]) -> dict[str, Any]:
        """Account a returned solver call and expose explicit over-budget state."""
        nfev = int(cost.get("nfev", 0))
        runtime = float(cost.get("runtime_s", 0.0))
        if nfev < 0 or runtime < 0:
            raise ValueError("solver cost must be non-negative")
        object.__setattr__(self, "_rhs_evals", self._rhs_evals + nfev)
        object.__setattr__(self, "_time_s", self._time_s + runtime)
        object.__setattr__(self, "_completed", self._completed + 1)
        violations: list[str] = []
        if self.max_rhs_evals is not None and self._rhs_evals > self.max_rhs_evals:
            violations.append("max_rhs_evals")
        if self.max_time_s is not None and self._time_s > self.max_time_s:
            violations.append("max_time_s")
        if violations:
            object.__setattr__(self, "_over_budget", True)
        return {
            "status": "over_budget" if violations else "completed",
            "violations": violations,
            "call_was_interrupted": False,
            "rhs_evals": nfev,
            "runtime_s": runtime,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_rhs_evals": self.max_rhs_evals,
            "max_time_s": self.max_time_s,
            "max_runs": self.max_runs,
            "rhs_evals": self._rhs_evals,
            "elapsed_time_s": self._time_s,
            "attempted_runs": self._attempted,
            "completed_runs": self._completed,
            "status": "over_budget" if self._over_budget else "within_budget",
            "solver_calls_are_not_interrupted": True,
        }


__all__ = ["BoundedBenchmarkBudget"]
