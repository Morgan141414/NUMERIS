"""Explicit accounting for bounded NUMERIS experiments.

The ledger is deliberately independent from a solver.  A solver or benchmark
can charge RHS evaluations and elapsed time at the points where those values
are known, while an experiment harness can charge completed/repeated runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Optional


@dataclass(frozen=True)
class Budget:
    """Upper bounds for one experiment.

    ``None`` means that the corresponding resource is unlimited.  Limits are
    inclusive: consuming exactly the configured limit is allowed.
    """

    max_rhs_evals: Optional[int] = None
    max_time_s: Optional[float] = None
    max_runs: Optional[int] = None

    def __post_init__(self) -> None:
        for name in ("max_rhs_evals", "max_runs"):
            value = getattr(self, name)
            if value is not None and (isinstance(value, bool) or value < 0):
                raise ValueError(f"{name} must be a non-negative integer or None")
            if value is not None and int(value) != value:
                raise ValueError(f"{name} must be an integer or None")
        if self.max_time_s is not None and self.max_time_s < 0:
            raise ValueError("max_time_s must be non-negative or None")


class BudgetExceededError(RuntimeError):
    """Raised before an operation would exceed a configured budget."""

    def __init__(self, resource: str, requested: float, limit: float) -> None:
        self.resource = resource
        self.requested = requested
        self.limit = limit
        super().__init__(
            f"{resource} budget exceeded: requested {requested}, limit {limit}"
        )


@dataclass
class BudgetLedger:
    """Track consumption against a :class:`Budget`.

    Time is measured from ledger creation by default.  ``start_run`` and
    ``finish_run`` provide a convenient way to account for repeated runs;
    direct ``record_run`` is useful when timing is performed externally.
    """

    budget: Budget
    rhs_evals: int = 0
    elapsed_time_s: float = 0.0
    runs: int = 0
    _started_at: float | None = None

    def __post_init__(self) -> None:
        if self.rhs_evals < 0 or self.elapsed_time_s < 0 or self.runs < 0:
            raise ValueError("ledger counters must be non-negative")
        self._started_at = monotonic()
        self._check_limits()

    @property
    def remaining_rhs_evals(self) -> int | None:
        if self.budget.max_rhs_evals is None:
            return None
        return self.budget.max_rhs_evals - self.rhs_evals

    @property
    def remaining_time_s(self) -> float | None:
        if self.budget.max_time_s is None:
            return None
        return max(0.0, self.budget.max_time_s - self.elapsed_time_s)

    @property
    def remaining_runs(self) -> int | None:
        if self.budget.max_runs is None:
            return None
        return self.budget.max_runs - self.runs

    def _check_limits(self) -> None:
        checks = (
            ("rhs evaluations", self.rhs_evals, self.budget.max_rhs_evals),
            ("time", self.elapsed_time_s, self.budget.max_time_s),
            ("runs", self.runs, self.budget.max_runs),
        )
        for resource, value, limit in checks:
            if limit is not None and value > limit:
                raise BudgetExceededError(resource, value, limit)

    def check(self) -> None:
        """Raise if elapsed wall-clock time or counters exceed the budget."""
        if self._started_at is not None:
            self.elapsed_time_s = max(
                self.elapsed_time_s, monotonic() - self._started_at
            )
        self._check_limits()

    def charge_rhs(self, count: int = 1) -> None:
        """Charge RHS evaluations before executing them."""
        if isinstance(count, bool) or count < 0 or int(count) != count:
            raise ValueError("count must be a non-negative integer")
        proposed = self.rhs_evals + int(count)
        if self.budget.max_rhs_evals is not None and proposed > self.budget.max_rhs_evals:
            raise BudgetExceededError(
                "rhs evaluations", proposed, self.budget.max_rhs_evals
            )
        self.check()
        self.rhs_evals = proposed

    def charge_time(self, seconds: float) -> None:
        """Charge externally measured wall-clock time."""
        if seconds < 0:
            raise ValueError("seconds must be non-negative")
        proposed = self.elapsed_time_s + float(seconds)
        if self.budget.max_time_s is not None and proposed > self.budget.max_time_s:
            raise BudgetExceededError("time", proposed, self.budget.max_time_s)
        self.elapsed_time_s = proposed

    def record_run(self) -> None:
        """Record one completed or attempted repeated run."""
        proposed = self.runs + 1
        if self.budget.max_runs is not None and proposed > self.budget.max_runs:
            raise BudgetExceededError("runs", proposed, self.budget.max_runs)
        self.check()
        self.runs = proposed

    def start_run(self) -> None:
        """Reserve one run before starting it."""
        self.record_run()

    def finish_run(self, elapsed_time_s: float) -> None:
        """Charge time for a run whose reservation was made with ``start_run``."""
        self.charge_time(elapsed_time_s)
