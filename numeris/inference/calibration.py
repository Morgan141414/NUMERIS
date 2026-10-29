"""Small reproducible coverage experiments for the grid posterior baseline.

The public helper in this module repeatedly generates synthetic observations
from a supplied :class:`~numeris.models.base.ODEModel`, runs the existing
finite-grid posterior recovery, and records whether the true parameters fall
inside the requested equal-tail credible intervals.

This is a calibration diagnostic, not a claim that the grid posterior is a
well-calibrated Bayesian procedure in general.  In particular, the number of
replicates is finite, the posterior is evaluated on a finite parameter grid,
and the observations use the same ODE solver settings as the recovery runs.
No MCMC is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from numeris.models.base import ODEModel

from .bayesian_grid import ParameterRecoveryResult, run_parameter_recovery


@dataclass(frozen=True)
class PosteriorCalibrationResult:
    """Empirical credible-interval coverage over synthetic replicates.

    ``coverage`` is the fraction of replicates in which each true parameter
    lies inside its marginal equal-tail interval.  It estimates repeated-
    sampling coverage at the requested nominal level; it is not a guarantee
    about posterior calibration or a comparison between inference methods.
    """

    truth: np.ndarray
    parameter_names: tuple[str, ...]
    credible_level: float
    repetitions: int
    coverage_counts: np.ndarray
    coverage: np.ndarray
    mean_interval_width: np.ndarray
    coverage_standard_error: np.ndarray
    replicate_coverage: np.ndarray
    replicate_seeds: tuple[int, ...]
    solver_settings: dict[str, object]

    def __post_init__(self) -> None:
        truth = np.asarray(self.truth, dtype=float)
        for name, value in (("truth", truth),):
            if value.ndim != 1 or value.size == 0 or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be a finite, non-empty 1-D array")
        n_parameters = truth.size
        if len(self.parameter_names) != n_parameters:
            raise ValueError("parameter_names must match truth dimensionality")
        if not 0.0 < self.credible_level < 1.0:
            raise ValueError("credible_level must be between zero and one")
        if self.repetitions <= 0:
            raise ValueError("repetitions must be positive")
        counts = np.asarray(self.coverage_counts)
        coverage = np.asarray(self.coverage, dtype=float)
        widths = np.asarray(self.mean_interval_width, dtype=float)
        standard_error = np.asarray(self.coverage_standard_error, dtype=float)
        replicate_coverage = np.asarray(self.replicate_coverage, dtype=bool)
        if any(array.shape != (n_parameters,) for array in (counts, coverage, widths, standard_error)):
            raise ValueError("calibration summaries must have one value per parameter")
        if replicate_coverage.shape != (self.repetitions, n_parameters):
            raise ValueError("replicate_coverage has an invalid shape")
        if len(self.replicate_seeds) != self.repetitions:
            raise ValueError("replicate_seeds must contain one seed per replicate")
        if np.any(counts < 0) or np.any(counts > self.repetitions):
            raise ValueError("coverage_counts must be within the replicate count")
        if not all(np.all(np.isfinite(array)) for array in (coverage, widths, standard_error)):
            raise ValueError("calibration summaries must be finite")

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly summary without per-replicate arrays."""
        return {
            "truth": self.truth.tolist(),
            "parameter_names": list(self.parameter_names),
            "credible_level": float(self.credible_level),
            "repetitions": self.repetitions,
            "coverage_counts": self.coverage_counts.tolist(),
            "coverage": self.coverage.tolist(),
            "mean_interval_width": self.mean_interval_width.tolist(),
            "coverage_standard_error": self.coverage_standard_error.tolist(),
            "replicate_seeds": list(self.replicate_seeds),
            "solver_settings": dict(self.solver_settings),
            "limitations": [
                "Finite-grid posterior; no MCMC is used.",
                "Coverage is a finite Monte Carlo diagnostic, not a guarantee.",
                "This result makes no superiority or novelty claim.",
            ],
        }


def calibrate_credible_intervals(
    model: ODEModel,
    truth: Sequence[float] | np.ndarray,
    sigma: float,
    parameter_grid: np.ndarray | Sequence[Sequence[float]],
    *,
    repetitions: int = 20,
    credible_level: float = 0.95,
    seed: int = 0,
    parameter_names: Sequence[str] | None = None,
    method: str = "DOP853",
    rtol: float = 1e-8,
    atol: float = 1e-10,
) -> PosteriorCalibrationResult:
    """Estimate marginal credible-interval coverage on synthetic ODE data.

    Each replicate uses the same ``model``, true parameter vector, Gaussian
    noise scale, finite parameter grid, and solver settings.  Its observation
    noise is generated from a deterministic child seed derived from ``seed``.
    The helper is intentionally small for local experiments and calls the
    existing :func:`run_parameter_recovery` implementation; it does not run
    MCMC or adapt the grid between replicates.

    Parameters
    ----------
    repetitions:
        Positive number of synthetic datasets.  Larger values reduce Monte
        Carlo noise but increase the number of ODE solves.
    credible_level:
        Equal-tail interval level passed to the grid posterior.
    seed:
        Root seed from which one reproducible integer seed is derived per
        replicate.
    """
    truth_array = np.asarray(truth, dtype=float)
    grid = np.asarray(parameter_grid, dtype=float)
    if truth_array.ndim != 1 or truth_array.size == 0 or not np.all(np.isfinite(truth_array)):
        raise ValueError("truth must be a finite, non-empty 1-D vector")
    if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] != truth_array.size:
        raise ValueError("parameter_grid must be non-empty and match truth dimensionality")
    if not isinstance(repetitions, (int, np.integer)) or repetitions <= 0:
        raise ValueError("repetitions must be a positive integer")
    if not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")
    if not 0.0 < credible_level < 1.0:
        raise ValueError("credible_level must be between zero and one")

    if parameter_names is None:
        names = tuple(f"parameter_{index}" for index in range(truth_array.size))
    else:
        names = tuple(parameter_names)
        if len(names) != truth_array.size or len(set(names)) != len(names) or not all(names):
            raise ValueError("parameter_names must be unique and match truth dimensionality")

    child_sequences = np.random.SeedSequence(int(seed)).spawn(int(repetitions))
    replicate_seeds = tuple(
        int(sequence.generate_state(1, dtype=np.uint64)[0] % np.iinfo(np.int64).max)
        for sequence in child_sequences
    )
    replicate_coverage = np.empty((int(repetitions), truth_array.size), dtype=bool)
    interval_widths = np.empty_like(replicate_coverage, dtype=float)
    for index, replicate_seed in enumerate(replicate_seeds):
        recovery: ParameterRecoveryResult = run_parameter_recovery(
            model,
            truth_array,
            sigma,
            grid,
            seed=replicate_seed,
            parameter_names=names,
            method=method,
            rtol=rtol,
            atol=atol,
            credible_level=credible_level,
        )
        replicate_coverage[index] = recovery.credible_interval_coverage
        interval_widths[index] = np.diff(recovery.credible_intervals, axis=1)[:, 0]

    counts = replicate_coverage.sum(axis=0).astype(int)
    coverage = counts / int(repetitions)
    standard_error = np.sqrt(coverage * (1.0 - coverage) / int(repetitions))
    return PosteriorCalibrationResult(
        truth=truth_array.copy(),
        parameter_names=names,
        credible_level=float(credible_level),
        repetitions=int(repetitions),
        coverage_counts=counts,
        coverage=coverage,
        mean_interval_width=interval_widths.mean(axis=0),
        coverage_standard_error=standard_error,
        replicate_coverage=replicate_coverage,
        replicate_seeds=replicate_seeds,
        solver_settings={
            "method": method,
            "rtol": float(rtol),
            "atol": float(atol),
            "sigma": float(sigma),
            "root_seed": int(seed),
            "credible_level": float(credible_level),
        },
    )


__all__ = ["PosteriorCalibrationResult", "calibrate_credible_intervals"]
