#!/usr/bin/env python3
"""Execute the bounded damped-oscillator prototype without candidate substitution."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from numeris.inference.gaussian import gaussian_negative_log_likelihood
from numeris.models.base import ODEModel
from numeris.solvers import solve_ode
from scipy.optimize import minimize

MANIFEST_PATH = "research/protocol/MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md"
TRUTH = np.array([1.0, 0.1, 0.2], dtype=float)
DEFAULT_SEEDS = (0, 1)
DEFAULT_SIGMA = 0.05
DEFAULT_RHS_BUDGET = 2_000
DEFAULT_RTOL = 1e-8
DEFAULT_ATOL = 1e-10
OPTIMIZER_STARTS = np.asarray(
    [[1.0, 0.1, 0.2], [0.8, 0.05, 0.1], [1.2, 0.2, 0.3]], dtype=float
)
PARAMETER_BOUNDS = ((0.5, 1.5), (0.02, 0.30), (0.0, 0.5))
Candidate = Callable[..., dict[str, Any]]


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def _environment() -> dict[str, Any]:
    packages = {}
    for name in ("numpy", "scipy"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "UNAVAILABLE"
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": packages,
    }


def _observations(seed: int, sigma: float):
    times = np.linspace(0.0, 20.0, 201)

    def rhs(t: float, state: np.ndarray, params: np.ndarray) -> np.ndarray:
        omega, zeta, forcing = params
        return np.array(
            [state[1], -2.0 * zeta * omega * state[1] - omega**2 * state[0]
             + forcing * np.cos(omega * t)]
        )

    model = ODEModel(
        rhs=rhs, initial_state=[1.0, 0.0], t_span=(0.0, 20.0),
        observation_times=times, observe=lambda states: np.asarray(states)[:, 0],
    )
    reference = solve_ode(model, TRUTH, method="DOP853", rtol=1e-12, atol=1e-14)
    if not reference.success:
        raise RuntimeError(f"reference solve failed: {reference.message}")
    rng = np.random.default_rng(seed)
    observations = model.observe(reference.states)
    return model, observations + rng.normal(0.0, sigma, observations.shape)


def _baseline(seed: int, *, sigma: float, budget: int, rtol: float, atol: float) -> dict[str, Any]:
    model, observations = _observations(seed, sigma)
    spent = 0
    solves = 0
    failures = []
    best = None
    for start in OPTIMIZER_STARTS:
        def objective(params: np.ndarray) -> float:
            nonlocal spent, solves
            if spent >= budget:
                return float("inf")
            result = solve_ode(model, params, method="DOP853", rtol=rtol, atol=atol)
            spent += int(result.nfev)
            solves += 1
            if not result.success or result.states.shape != observations.shape:
                return float("inf")
            return gaussian_negative_log_likelihood(model.observe(result.states), observations, sigma)

        fit = minimize(
            objective, start, method="L-BFGS-B", bounds=PARAMETER_BOUNDS,
            options={"maxiter": 25, "ftol": 1e-10},
        )
        if spent > budget:
            return {
                "status": "over_budget", "method": "DOP853",
                "budget": {"max_rhs_evals": budget, "rhs_evals": spent, "solves": solves},
                "failures": failures,
                "primary": {"parameter_rmse": None, "likelihood": None},
            }
        if not fit.success or not np.isfinite(fit.fun):
            failures.append({"start": start.tolist(), "message": str(fit.message)})
            continue
        params = np.asarray(fit.x, dtype=float)
        if best is None or float(fit.fun) < best[0]:
            best = (float(fit.fun), params)
    if best is None:
        return {
            "status": "failure", "method": "DOP853",
            "budget": {"max_rhs_evals": budget, "rhs_evals": spent, "solves": solves},
            "failures": failures,
            "primary": {"parameter_rmse": None, "likelihood": None},
        }
    return {
        "status": "completed", "method": "DOP853",
        "budget": {"max_rhs_evals": budget, "rhs_evals": spent, "solves": solves},
        "failures": failures,
        "primary": {
            "parameter_rmse": float(np.sqrt(np.mean((best[1] - TRUTH) ** 2))),
            "likelihood": float(best[0]), "estimated_parameters": best[1].tolist(),
        },
    }


def _candidate(candidate: Candidate | None) -> dict[str, Any]:
    if candidate is None:
        reason = "No frozen candidate implementation is registered; no heuristic was substituted."
    else:
        reason = "Candidate adapter contract is not implemented; supplied callable was refused."
    return {
        "status": "NOT-IMPLEMENTED", "contract": "NUMERIS-GO-candidate-v0.1",
        "reason": reason, "substitution_forbidden": True,
    }


def run_minimal_prototype(
    *, seeds: Sequence[int] = DEFAULT_SEEDS, sigma: float = DEFAULT_SIGMA,
    max_rhs_evals: int = DEFAULT_RHS_BUDGET, rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL, candidate: Candidate | None = None,
) -> dict[str, Any]:
    """Run bounded baseline diagnostics and an explicit candidate contract gate."""
    seed_values = [int(seed) for seed in seeds]
    if not seed_values or any(seed < 0 for seed in seed_values):
        raise ValueError("seeds must be a non-empty sequence of non-negative integers")
    if max_rhs_evals <= 0 or sigma <= 0 or rtol <= 0 or atol <= 0:
        raise ValueError("sigma, tolerances, and max_rhs_evals must be positive")
    runs = []
    baseline_rmse = []
    for seed in seed_values:
        baseline = _baseline(seed, sigma=sigma, budget=max_rhs_evals, rtol=rtol, atol=atol)
        if baseline["status"] == "completed":
            baseline_rmse.append(baseline["primary"]["parameter_rmse"])
        runs.append({"seed": seed, "baseline": baseline, "candidate": _candidate(candidate)})
    return {
        "schema_version": "minimal-oscillator-runner-v1", "scope": "exploratory", "campaign": "bounded",
        "protocol": {
            "manifest_path": MANIFEST_PATH, "manifest_commit": _git_commit(),
            "candidate_contract": "NUMERIS-GO-candidate-v0.1",
            "baseline": {"method": "DOP853", "rtol": rtol, "atol": atol},
            "paired_seeds": seed_values, "max_rhs_evals_per_seed": max_rhs_evals,
        },
        "environment": _environment(), "truth": TRUTH.tolist(), "observation_noise_sigma": sigma,
        "candidate": {"status": "NOT-IMPLEMENTED", "substitution_forbidden": True}, "runs": runs,
        "primary": {
            "parameter_rmse": {"baseline": baseline_rmse, "candidate": None, "candidate_status": "NOT-IMPLEMENTED"},
            "bootstrap": {
                "status": "not_computable", "observed_difference": None,
                "confidence_interval": None, "n_pairs": 0,
                "reason": "Candidate endpoint is unavailable; no paired bootstrap was fabricated.",
            },
            "decision": "NOT-IMPLEMENTED",
            "reason": "No candidate endpoint exists; candidate-vs-baseline inference is not computed.",
        },
        "limitations": [
            "Bounded exploratory runner; not the full frozen scientific campaign.",
            "Reference solves are excluded from the per-arm RHS budget and are recorded as setup only.",
            "Existing heuristics are not silently substituted for the candidate.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, action="append", dest="seeds", help="paired seed; repeatable")
    parser.add_argument("--max-rhs-evals", type=int, default=DEFAULT_RHS_BUDGET)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_minimal_prototype(seeds=DEFAULT_SEEDS if args.seeds is None else args.seeds, max_rhs_evals=args.max_rhs_evals)
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
