"""Budget-aware deterministic multi-start maximum-likelihood estimation.

This module is an orchestration helper for frozen experiments.  It does not
claim an inference improvement or enforce a solver's internal RHS budget: the
objective callback must report the cost of each evaluation, and any call that
would make an arm exceed its cap is recorded as ``over_budget`` and excluded
from model selection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
from scipy.optimize import OptimizeResult, minimize


@dataclass(frozen=True)
class ObjectiveEvaluation:
    """One objective evaluation returned by a user-supplied evaluator."""

    value: float
    rhs_evals: int = 0
    success: bool = True
    message: str = ""


@dataclass(frozen=True)
class MLEArmResult:
    """Outcome of one fixed starting point (one independent budget arm)."""

    index: int
    start: tuple[float, ...]
    status: str
    params: tuple[float, ...] | None
    objective: float | None
    objective_evals: int
    rhs_evals: int
    optimizer_success: bool
    message: str


@dataclass(frozen=True)
class MultiStartMLEResult:
    """Deterministic aggregate result with auditable arm-level outcomes."""

    status: str
    best_params: tuple[float, ...] | None
    best_objective: float | None
    best_arm_index: int | None
    arms: tuple[MLEArmResult, ...]
    attempted_arms: int
    completed_arms: int
    over_budget_arms: int
    failed_arms: int
    total_objective_evals: int
    total_rhs_evals: int


Evaluator = Callable[[np.ndarray], ObjectiveEvaluation]


class _BudgetStop(Exception):
    """Internal control flow used to stop scipy before another evaluation."""


def budget_aware_multistart_mle(
    evaluator: Evaluator,
    starts: Sequence[Sequence[float]],
    *,
    bounds: Sequence[tuple[float | None, float | None]] | None = None,
    max_rhs_evals_per_arm: int | None = None,
    max_objective_evals_per_arm: int | None = None,
    method: str = "L-BFGS-B",
    options: dict[str, object] | None = None,
) -> MultiStartMLEResult:
    """Run fixed-start MLE arms in input order under independent budgets.

    ``evaluator`` receives a fresh parameter array for every objective call and
    returns its negative log-likelihood and actual RHS cost.  An arm is
    ``completed`` only when SciPy reports success, every evaluated objective is
    finite/successful, and neither per-arm cap was exceeded.  Arms are never
    reordered; ties select the first completed arm, making the result
    deterministic.  No superiority or scientific reliability claim is made.
    """
    starts_array = _validate_starts(starts)
    normalized_bounds = _validate_bounds(bounds, starts_array.shape[1])
    _validate_limit(max_rhs_evals_per_arm, "max_rhs_evals_per_arm")
    _validate_limit(max_objective_evals_per_arm, "max_objective_evals_per_arm")

    arm_results: list[MLEArmResult] = []
    for index, start in enumerate(starts_array):
        arm_results.append(
            _run_arm(
                evaluator,
                index,
                start,
                normalized_bounds,
                max_rhs_evals_per_arm,
                max_objective_evals_per_arm,
                method,
                options,
            )
        )

    completed = [arm for arm in arm_results if arm.status == "completed"]
    best = min(completed, key=lambda arm: (float(arm.objective), arm.index), default=None)
    if best is not None:
        status = "completed"
    elif any(arm.status == "over_budget" for arm in arm_results):
        status = "over_budget"
    elif arm_results:
        status = "failed"
    else:  # guarded by _validate_starts, kept for defensive clarity
        status = "failed"

    return MultiStartMLEResult(
        status=status,
        best_params=best.params if best else None,
        best_objective=best.objective if best else None,
        best_arm_index=best.index if best else None,
        arms=tuple(arm_results),
        attempted_arms=len(arm_results),
        completed_arms=sum(arm.status == "completed" for arm in arm_results),
        over_budget_arms=sum(arm.status == "over_budget" for arm in arm_results),
        failed_arms=sum(arm.status == "failed" for arm in arm_results),
        total_objective_evals=sum(arm.objective_evals for arm in arm_results),
        total_rhs_evals=sum(arm.rhs_evals for arm in arm_results),
    )


def _run_arm(
    evaluator: Evaluator,
    index: int,
    start: np.ndarray,
    bounds: Sequence[tuple[float | None, float | None]] | None,
    rhs_cap: int | None,
    objective_cap: int | None,
    method: str,
    options: dict[str, object] | None,
) -> MLEArmResult:
    objective_evals = 0
    rhs_evals = 0
    over_budget = False
    failed = False
    last_message = ""

    def objective(params: np.ndarray) -> float:
        nonlocal objective_evals, rhs_evals, over_budget, failed, last_message
        if objective_cap is not None and objective_evals >= objective_cap:
            over_budget = True
            last_message = "objective evaluation budget exceeded"
            raise _BudgetStop(last_message)
        try:
            evaluation = evaluator(np.asarray(params, dtype=float).copy())
            if not isinstance(evaluation, ObjectiveEvaluation):
                raise TypeError("evaluator must return ObjectiveEvaluation")
            if evaluation.rhs_evals < 0:
                raise ValueError("rhs_evals must be non-negative")
            objective_evals += 1
            rhs_evals += int(evaluation.rhs_evals)
            last_message = evaluation.message
            if rhs_cap is not None and rhs_evals > rhs_cap:
                over_budget = True
                last_message = "RHS evaluation budget exceeded"
                raise _BudgetStop(last_message)
            if not evaluation.success or not np.isfinite(evaluation.value):
                failed = True
                return np.inf
            return float(evaluation.value)
        except _BudgetStop:
            raise
        except Exception as exc:  # an invalid arm must not abort the campaign
            objective_evals += 1
            failed = True
            last_message = f"evaluator failed: {exc}"
            return np.inf

    try:
        result: OptimizeResult = minimize(
            objective,
            start.copy(),
            bounds=bounds,
            method=method,
            options=options,
        )
    except _BudgetStop as exc:
        over_budget = True
        last_message = str(exc)
        result = OptimizeResult(success=False, x=start, fun=np.inf, message=last_message)
    except Exception as exc:
        failed = True
        last_message = f"optimizer failed: {exc}"
        result = OptimizeResult(success=False, x=start, fun=np.inf, message=last_message)

    if over_budget:
        status = "over_budget"
    elif failed or not bool(result.success) or not np.isfinite(result.fun):
        status = "failed"
    else:
        status = "completed"

    message = last_message or str(getattr(result, "message", ""))
    return MLEArmResult(
        index=index,
        start=tuple(float(value) for value in start),
        status=status,
        params=tuple(float(value) for value in result.x) if status == "completed" else None,
        objective=float(result.fun) if status == "completed" else None,
        objective_evals=objective_evals,
        rhs_evals=rhs_evals,
        optimizer_success=bool(result.success),
        message=message,
    )


def _validate_starts(starts: Sequence[Sequence[float]]) -> np.ndarray:
    array = np.asarray(starts, dtype=float)
    if array.ndim != 2 or array.shape[0] == 0 or array.shape[1] == 0:
        raise ValueError("starts must be a non-empty two-dimensional sequence")
    if not np.all(np.isfinite(array)):
        raise ValueError("starts must contain only finite values")
    return array


def _validate_bounds(
    bounds: Sequence[tuple[float | None, float | None]] | None, dimension: int
) -> tuple[tuple[float | None, float | None], ...] | None:
    if bounds is None:
        return None
    if len(bounds) != dimension:
        raise ValueError("bounds dimension must match starts")
    normalized = []
    for lower, upper in bounds:
        if lower is not None and upper is not None and lower > upper:
            raise ValueError("each lower bound must be <= its upper bound")
        normalized.append((lower, upper))
    return tuple(normalized)


def _validate_limit(value: int | None, name: str) -> None:
    if value is not None and (not isinstance(value, (int, np.integer)) or value < 1):
        raise ValueError(f"{name} must be a positive integer or None")
