"""Small, reproducible orchestration for numerical validation diagnostics.

The helper in this module combines the existing independent-solver reference
report with the existing finite-grid posterior calibration diagnostic.  It is
intended for short local smoke campaigns over several benchmark models, not
for an automated claim of solver superiority.  Every case records its
configuration, an explicit cost estimate, and limitations in the returned
JSON-friendly report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Sequence

import numpy as np

from numeris.inference.calibration import calibrate_credible_intervals
from numeris.models.base import ODEModel

from .reference_report import (
    DEFAULT_REFERENCE_CONFIGS,
    SolverSpec,
    build_reference_report,
)


@dataclass(frozen=True)
class ValidationCase:
    """One explicitly configured benchmark validation case.

    ``parameter_grid`` is deliberately explicit rather than a Cartesian-grid
    specification, so the inference cost is visible and reproducible.
    """

    name: str
    model: ODEModel
    truth: tuple[float, ...]
    sigma: float
    parameter_grid: tuple[tuple[float, ...], ...]
    parameter_names: tuple[str, ...] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        truth = np.asarray(self.truth, dtype=float)
        grid = np.asarray(self.parameter_grid, dtype=float)
        if not self.name:
            raise ValueError("case name must not be empty")
        if truth.ndim != 1 or truth.size == 0 or not np.all(np.isfinite(truth)):
            raise ValueError("truth must be a finite, non-empty vector")
        if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] != truth.size:
            raise ValueError("parameter_grid must match truth dimensionality")
        if not np.all(np.isfinite(grid)):
            raise ValueError("parameter_grid must be finite")
        if not np.isfinite(self.sigma) or self.sigma <= 0:
            raise ValueError("sigma must be finite and positive")
        if self.parameter_names is not None and len(self.parameter_names) != truth.size:
            raise ValueError("parameter_names must match truth dimensionality")


def _spec_dict(spec: SolverSpec | str) -> dict[str, Any]:
    value = spec if isinstance(spec, SolverSpec) else SolverSpec(spec)
    return value.as_dict()


def _case_budget(
    case: ValidationCase,
    solver_configs: Sequence[SolverSpec | str],
    reference_configs: Sequence[SolverSpec | str],
    tolerance_levels: Sequence[Sequence[float]],
    repetitions: int,
) -> dict[str, int]:
    """Return transparent upper-bound counts before any numerical work."""
    reference_solves = len(reference_configs)
    convergence_solves = len(solver_configs) * len(tolerance_levels)
    calibration_solves = repetitions * (1 + len(case.parameter_grid))
    return {
        "reference_solver_solves": reference_solves,
        "convergence_solver_solves": convergence_solves,
        "calibration_ode_solves_upper_bound": calibration_solves,
        "total_ode_solves_upper_bound": reference_solves + convergence_solves + calibration_solves,
    }


def run_validation_suite(
    cases: Sequence[ValidationCase],
    *,
    tolerance_levels: Sequence[Sequence[float]] = ((1e-6, 1e-8), (1e-9, 1e-11)),
    solver_configs: Sequence[SolverSpec | str] = ("DOP853", "Radau"),
    reference_configs: Sequence[SolverSpec | str] = DEFAULT_REFERENCE_CONFIGS,
    repetitions: int = 2,
    credible_level: float = 0.9,
    seed: int = 0,
    max_cases: int = 5,
    max_grid_points: int = 100,
    max_repetitions: int = 20,
) -> dict[str, Any]:
    """Run small reference and calibration diagnostics for several cases.

    The limits are safety rails for local experiments.  They fail before any
    solver call when a requested campaign is too large.  The result is a
    diagnostic report only: it contains no baseline comparison, significance
    test, or superiority claim.
    """
    if not cases:
        raise ValueError("at least one validation case is required")
    if len(cases) > max_cases:
        raise ValueError(f"at most {max_cases} cases are allowed by this local budget")
    if not isinstance(repetitions, (int, np.integer)) or not 0 < repetitions <= max_repetitions:
        raise ValueError(f"repetitions must be an integer in [1, {max_repetitions}]")
    if not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")
    if not tolerance_levels or len(tolerance_levels) < 2:
        raise ValueError("at least two tolerance levels are required")
    if not solver_configs or len(reference_configs) < 2:
        raise ValueError("solver_configs must be non-empty and reference_configs need two methods")

    normalised_levels = [tuple(float(item) for item in pair) for pair in tolerance_levels]
    if any(len(pair) != 2 for pair in normalised_levels):
        raise ValueError("each tolerance level must be an (rtol, atol) pair")
    child_seeds = np.random.SeedSequence(int(seed)).spawn(len(cases))
    reports: list[dict[str, Any]] = []
    for case, child in zip(cases, child_seeds):
        if len(case.parameter_grid) > max_grid_points:
            raise ValueError(
                f"case {case.name!r} has {len(case.parameter_grid)} grid points; "
                f"limit is {max_grid_points}"
            )
        case_seed = int(child.generate_state(1, dtype=np.uint64)[0] % np.iinfo(np.int64).max)
        budget = _case_budget(
            case, solver_configs, reference_configs, normalised_levels, int(repetitions)
        )
        reference = build_reference_report(
            case.model,
            case.truth,
            tolerance_levels=normalised_levels,
            solver_configs=solver_configs,
            reference_configs=reference_configs,
            name=f"{case.name}-reference",
        )
        calibration = calibrate_credible_intervals(
            case.model,
            case.truth,
            case.sigma,
            case.parameter_grid,
            repetitions=int(repetitions),
            credible_level=credible_level,
            seed=case_seed,
            parameter_names=case.parameter_names,
            method="DOP853",
            rtol=normalised_levels[-1][0],
            atol=normalised_levels[-1][1],
        )
        reports.append(
            {
                "name": case.name,
                "metadata": dict(case.metadata),
                "seed": case_seed,
                "budget": budget,
                "reference_report": reference,
                "calibration": calibration.summary(),
            }
        )

    report = {
        "schema_version": "validation-suite-v1",
        "suite": {"case_count": len(cases), "root_seed": int(seed)},
        "configuration": {
            "tolerance_levels": [list(pair) for pair in normalised_levels],
            "solver_configs": [_spec_dict(item) for item in solver_configs],
            "reference_configs": [_spec_dict(item) for item in reference_configs],
            "repetitions": int(repetitions),
            "credible_level": float(credible_level),
            "limits": {
                "max_cases": int(max_cases),
                "max_grid_points": int(max_grid_points),
                "max_repetitions": int(max_repetitions),
            },
        },
        "cases": reports,
        "limitations": [
            "This is a small orchestration diagnostic, not a complete benchmark campaign.",
            "Reference consensus is a numerical surrogate, not exact truth.",
            "Calibration uses a finite parameter grid and no MCMC.",
            "The report does not establish superiority, novelty, or publication readiness.",
            "Runtime, memory, and equal-budget inference comparisons are not performed here.",
        ],
    }
    json.dumps(report, allow_nan=False, sort_keys=True)
    return report


__all__ = ["ValidationCase", "run_validation_suite"]
