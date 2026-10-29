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
from statistics import NormalDist
from typing import Sequence

import numpy as np

from numeris.models.base import ODEModel

from .bayesian_grid import ParameterRecoveryResult, posterior_distance, run_parameter_recovery
from numeris.solvers.scipy_solver import solve_ode


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
    coverage_confidence_level: float
    coverage_confidence_interval: np.ndarray
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
        confidence_interval = np.asarray(self.coverage_confidence_interval, dtype=float)
        replicate_coverage = np.asarray(self.replicate_coverage, dtype=bool)
        if not 0.0 < self.coverage_confidence_level < 1.0:
            raise ValueError("coverage_confidence_level must be between zero and one")
        if any(array.shape != (n_parameters,) for array in (counts, coverage, widths, standard_error)):
            raise ValueError("calibration summaries must have one value per parameter")
        if confidence_interval.shape != (n_parameters, 2):
            raise ValueError("coverage_confidence_interval must have shape (n_parameters, 2)")
        if replicate_coverage.shape != (self.repetitions, n_parameters):
            raise ValueError("replicate_coverage has an invalid shape")
        if len(self.replicate_seeds) != self.repetitions:
            raise ValueError("replicate_seeds must contain one seed per replicate")
        if np.any(counts < 0) or np.any(counts > self.repetitions):
            raise ValueError("coverage_counts must be within the replicate count")
        if not all(np.all(np.isfinite(array)) for array in (coverage, widths, standard_error, confidence_interval)):
            raise ValueError("calibration summaries must be finite")
        if np.any(confidence_interval < 0.0) or np.any(confidence_interval > 1.0):
            raise ValueError("coverage confidence intervals must lie in [0, 1]")
        if np.any(confidence_interval[:, 0] > confidence_interval[:, 1]):
            raise ValueError("coverage confidence intervals must be ordered")

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
            "coverage_confidence_level": float(self.coverage_confidence_level),
            "coverage_confidence_interval": self.coverage_confidence_interval.tolist(),
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
    coverage_confidence_level: float = 0.95,
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
    coverage_confidence_level:
        Frequentist confidence level for the Wilson interval around the
        empirical repeated-sampling coverage.  This quantifies Monte Carlo
        uncertainty in the calibration estimate; it is not a posterior
        credible interval and does not account for model or grid error.
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
    if not 0.0 < coverage_confidence_level < 1.0:
        raise ValueError("coverage_confidence_level must be between zero and one")

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
    # Wilson intervals remain informative at coverage 0 and 1, unlike a
    # normal approximation based only on +/- standard error.
    z = NormalDist().inv_cdf(0.5 + float(coverage_confidence_level) / 2.0)
    denominator = 1.0 + z**2 / int(repetitions)
    centre = (coverage + z**2 / (2.0 * int(repetitions))) / denominator
    half_width = (
        z
        * np.sqrt(
            coverage * (1.0 - coverage) / int(repetitions)
            + z**2 / (4.0 * int(repetitions) ** 2)
        )
        / denominator
    )
    confidence_interval = np.column_stack((centre - half_width, centre + half_width))
    return PosteriorCalibrationResult(
        truth=truth_array.copy(),
        parameter_names=names,
        credible_level=float(credible_level),
        repetitions=int(repetitions),
        coverage_counts=counts,
        coverage=coverage,
        mean_interval_width=interval_widths.mean(axis=0),
        coverage_standard_error=standard_error,
        coverage_confidence_level=float(coverage_confidence_level),
        coverage_confidence_interval=confidence_interval,
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


@dataclass(frozen=True)
class PairedToleranceSweepResult:
    """Inference changes measured on the same observations at each tolerance.

    The observations are generated once per replicate and then passed to every
    tolerance configuration.  Consequently, differences between columns are
    paired numerical-tolerance diagnostics; they should not be interpreted as
    a separation of numerical error from all statistical uncertainty.  The
    repeated rows still contain finite-observation variation, which is exposed
    through the per-replicate arrays and their means.
    """

    truth: np.ndarray
    parameter_names: tuple[str, ...]
    tolerances: tuple[tuple[float, float], ...]
    reference_index: int
    repetitions: int
    map_estimates: np.ndarray
    posterior_means: np.ndarray
    map_rmse: np.ndarray
    posterior_mean_rmse: np.ndarray
    map_shift_from_reference: np.ndarray
    posterior_distance_from_reference: np.ndarray
    observation_seeds: tuple[int, ...]
    method: str
    sigma: float

    def __post_init__(self) -> None:
        truth = np.asarray(self.truth, dtype=float)
        if truth.ndim != 1 or truth.size == 0 or not np.all(np.isfinite(truth)):
            raise ValueError("truth must be a finite, non-empty 1-D array")
        n_tolerances = len(self.tolerances)
        if n_tolerances == 0:
            raise ValueError("tolerances must be non-empty")
        if len(self.parameter_names) != truth.size:
            raise ValueError("parameter_names must match truth dimensionality")
        if not 0 <= self.reference_index < n_tolerances:
            raise ValueError("reference_index must identify a tolerance")
        if self.repetitions <= 0:
            raise ValueError("repetitions must be positive")
        expected = (self.repetitions, n_tolerances, truth.size)
        for name in ("map_estimates", "posterior_means"):
            value = np.asarray(getattr(self, name), dtype=float)
            if value.shape != expected or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must be finite with shape {expected}")
        for name in ("map_rmse", "posterior_mean_rmse", "map_shift_from_reference"):
            value = np.asarray(getattr(self, name), dtype=float)
            expected_shape = (self.repetitions, n_tolerances) if name != "map_shift_from_reference" else expected
            if value.shape != expected_shape or not np.all(np.isfinite(value)):
                raise ValueError(f"{name} has an invalid shape")
        posterior_distance_values = np.asarray(self.posterior_distance_from_reference, dtype=float)
        if posterior_distance_values.shape != (self.repetitions, n_tolerances):
            raise ValueError("posterior_distance_from_reference has an invalid shape")
        if not np.all(np.isfinite(posterior_distance_values)):
            raise ValueError("posterior distances must be finite")
        if len(self.observation_seeds) != self.repetitions:
            raise ValueError("observation_seeds must contain one seed per replicate")

    def summary(self) -> dict[str, object]:
        """Return a JSON-friendly paired numerical-vs-statistical summary."""
        return {
            "truth": self.truth.tolist(),
            "parameter_names": list(self.parameter_names),
            "tolerances": [
                {"rtol": rtol, "atol": atol} for rtol, atol in self.tolerances
            ],
            "reference_index": self.reference_index,
            "repetitions": self.repetitions,
            "mean_map_rmse": self.map_rmse.mean(axis=0).tolist(),
            "mean_posterior_mean_rmse": self.posterior_mean_rmse.mean(axis=0).tolist(),
            "mean_map_shift_from_reference": self.map_shift_from_reference.mean(axis=0).tolist(),
            "mean_posterior_distance_from_reference": self.posterior_distance_from_reference.mean(axis=0).tolist(),
            "observation_seeds": list(self.observation_seeds),
            "method": self.method,
            "sigma": self.sigma,
            "interpretation": [
                "All tolerance configurations use the same observations within each replicate.",
                "Within-replicate differences are paired numerical-tolerance diagnostics.",
                "Across-replicate spread still reflects finite-observation statistical variation.",
                "This result makes no superiority or novelty claim.",
            ],
        }


def paired_tolerance_sweep(
    model: ODEModel,
    truth: Sequence[float] | np.ndarray,
    sigma: float,
    parameter_grid: np.ndarray | Sequence[Sequence[float]],
    tolerances: Sequence[tuple[float, float]],
    *,
    repetitions: int = 20,
    seed: int = 0,
    parameter_names: Sequence[str] | None = None,
    method: str = "DOP853",
    observation_rtol: float | None = None,
    observation_atol: float | None = None,
) -> PairedToleranceSweepResult:
    """Compare solver tolerances on paired synthetic observations.

    One noisy observation set is generated per replicate and reused for every
    pair in ``tolerances``.  This design prevents a new random dataset from
    being mistaken for a tolerance-induced change.  The observation trajectory
    uses ``observation_rtol``/``observation_atol`` (the strictest supplied
    values by default), while each inference run uses its own pair.
    """
    truth_array = np.asarray(truth, dtype=float)
    grid = np.asarray(parameter_grid, dtype=float)
    if truth_array.ndim != 1 or truth_array.size == 0 or not np.all(np.isfinite(truth_array)):
        raise ValueError("truth must be a finite, non-empty 1-D vector")
    if grid.ndim != 2 or grid.shape[0] == 0 or grid.shape[1] != truth_array.size:
        raise ValueError("parameter_grid must be non-empty and match truth dimensionality")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be a finite positive value")
    if not isinstance(repetitions, (int, np.integer)) or repetitions <= 0:
        raise ValueError("repetitions must be a positive integer")
    if not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")
    if not tolerances:
        raise ValueError("tolerances must be non-empty")
    tolerance_pairs = tuple((float(rtol), float(atol)) for rtol, atol in tolerances)
    if any(rtol <= 0 or atol <= 0 or not np.isfinite(rtol) or not np.isfinite(atol)
           for rtol, atol in tolerance_pairs):
        raise ValueError("each tolerance must contain finite positive rtol and atol")
    if parameter_names is None:
        names = tuple(f"parameter_{index}" for index in range(truth_array.size))
    else:
        names = tuple(parameter_names)
        if len(names) != truth_array.size or len(set(names)) != len(names) or not all(names):
            raise ValueError("parameter_names must be unique and match truth dimensionality")

    obs_rtol = min(rtol for rtol, _ in tolerance_pairs) if observation_rtol is None else float(observation_rtol)
    obs_atol = min(atol for _, atol in tolerance_pairs) if observation_atol is None else float(observation_atol)
    if obs_rtol <= 0 or obs_atol <= 0 or not np.isfinite(obs_rtol) or not np.isfinite(obs_atol):
        raise ValueError("observation tolerances must be finite and positive")

    child_sequences = np.random.SeedSequence(int(seed)).spawn(int(repetitions))
    observation_seeds = tuple(
        int(sequence.generate_state(1, dtype=np.uint64)[0] % np.iinfo(np.int64).max)
        for sequence in child_sequences
    )
    n_repetitions = int(repetitions)
    n_tolerances = len(tolerance_pairs)
    n_parameters = truth_array.size
    map_estimates = np.empty((n_repetitions, n_tolerances, n_parameters), dtype=float)
    posterior_means = np.empty_like(map_estimates)
    map_rmse = np.empty((n_repetitions, n_tolerances), dtype=float)
    posterior_mean_rmse = np.empty_like(map_rmse)
    map_shift = np.empty_like(map_estimates)
    posterior_shift = np.empty_like(map_rmse)

    for replicate, observation_seed in enumerate(observation_seeds):
        reference = solve_ode(model, truth_array, method=method, rtol=obs_rtol, atol=obs_atol)
        if not reference.success:
            raise RuntimeError(f"truth ODE solve failed: {reference.message}")
        clean = np.asarray(model.observe(reference.states), dtype=float)
        rng = np.random.default_rng(observation_seed)
        observations = clean + rng.normal(0.0, sigma, size=clean.shape)
        recoveries: list[ParameterRecoveryResult] = []
        for tolerance_index, (rtol, atol) in enumerate(tolerance_pairs):
            recovery = run_parameter_recovery(
                model, truth_array, sigma, grid, observations=observations,
                seed=observation_seed, parameter_names=names, method=method,
                rtol=rtol, atol=atol,
            )
            recoveries.append(recovery)
            map_estimates[replicate, tolerance_index] = recovery.map_estimate
            posterior_means[replicate, tolerance_index] = recovery.posterior_mean
            map_rmse[replicate, tolerance_index] = recovery.map_rmse
            posterior_mean_rmse[replicate, tolerance_index] = recovery.mean_rmse
        reference_recovery = recoveries[0]
        for tolerance_index, recovery in enumerate(recoveries):
            map_shift[replicate, tolerance_index] = np.abs(
                recovery.map_estimate - reference_recovery.map_estimate
            )
            posterior_shift[replicate, tolerance_index] = posterior_distance(
                recovery.posterior, reference_recovery.posterior
            )

    return PairedToleranceSweepResult(
        truth=truth_array.copy(), parameter_names=names, tolerances=tolerance_pairs,
        reference_index=0, repetitions=n_repetitions, map_estimates=map_estimates,
        posterior_means=posterior_means, map_rmse=map_rmse,
        posterior_mean_rmse=posterior_mean_rmse, map_shift_from_reference=map_shift,
        posterior_distance_from_reference=posterior_shift,
        observation_seeds=observation_seeds, method=method, sigma=float(sigma),
    )


__all__ = [
    "PosteriorCalibrationResult",
    "calibrate_credible_intervals",
    "PairedToleranceSweepResult",
    "paired_tolerance_sweep",
]
