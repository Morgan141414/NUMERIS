#!/usr/bin/env python3
"""Run the deterministic NUMERIS oscillator benchmark from the command line.

Example::

    python scripts/run_oscillator_benchmark.py \
        --solver RK45 DOP853 --rtol 1e-6 --atol 1e-8 \
        --seed 7 --output results/oscillator.json

The benchmark uses a high-accuracy DOP853 solve to construct synthetic
observations.  The selected solver configurations are then executed through
``numeris.benchmarks.runner.run_benchmark``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

import numpy as np

# Keep the script runnable directly from a source checkout without requiring
# an editable installation (``python scripts/run_oscillator_benchmark.py``).
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from numeris.benchmarks import damped_oscillator
from numeris.benchmarks.runner import SolverConfig, run_benchmark


SOLVER_CHOICES = ("RK45", "DOP853", "Radau", "BDF", "LSODA")
DEFAULT_SOLVERS = SOLVER_CHOICES
DEFAULT_PARAMS = np.array([1.0, 0.1, 0.2], dtype=float)
REFERENCE_RTOL = 1e-12
REFERENCE_ATOL = 1e-14
DEFAULT_SIGMA = 0.05


def build_parser() -> argparse.ArgumentParser:
    """Create the public command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--solver",
        nargs="+",
        choices=SOLVER_CHOICES,
        default=list(DEFAULT_SOLVERS),
        metavar="METHOD",
        help="solver methods to benchmark (default: all supported methods)",
    )
    parser.add_argument("--rtol", type=_positive_float, default=1e-8)
    parser.add_argument("--atol", type=_positive_float, default=1e-10)
    parser.add_argument("--seed", type=int, default=0, help="seed for synthetic noise")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write the full JSON report to this path (default: stdout only)",
    )
    return parser


def _positive_float(value: str) -> float:
    parsed = float(value)
    if not np.isfinite(parsed) or parsed <= 0:
        raise argparse.ArgumentTypeError("must be a finite positive number")
    return parsed


def run_cli(
    *,
    solvers: Sequence[str],
    rtol: float,
    atol: float,
    seed: int,
    output: Path | None,
) -> dict[str, object]:
    """Run the oscillator experiment and optionally persist its report."""
    # Import lazily so ``--help`` remains available in a source checkout
    # before optional numerical dependencies have been installed.
    from numeris.solvers import solve_ode
    from numeris.reproducibility import ReproducibilityMetadata

    model = damped_oscillator()
    params = DEFAULT_PARAMS.copy()
    reference = solve_ode(
        model,
        params,
        method="DOP853",
        rtol=REFERENCE_RTOL,
        atol=REFERENCE_ATOL,
    )

    rng = np.random.default_rng(seed)
    observations = model.observe(reference.states) + rng.normal(
        loc=0.0, scale=DEFAULT_SIGMA, size=reference.states.shape
    )
    configurations = [
        SolverConfig(name=method.lower(), method=method, rtol=rtol, atol=atol)
        for method in solvers
    ]
    report = run_benchmark(
        model,
        params,
        configurations,
        observations=observations,
        sigma=DEFAULT_SIGMA,
        reference_states=reference.states,
        name="damped_oscillator",
    )
    report["experiment"] = {
        "seed": int(seed),
        "parameters": params.tolist(),
        "observation_noise_sigma": DEFAULT_SIGMA,
        "reference_solver": {
            "method": "DOP853",
            "rtol": REFERENCE_RTOL,
            "atol": REFERENCE_ATOL,
        },
    }
    report["reproducibility"] = ReproducibilityMetadata.capture(
        seed=seed,
        solver_settings={"methods": list(solvers), "rtol": rtol, "atol": atol},
    ).to_dict()

    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, run the benchmark, and print the resulting report."""
    args = build_parser().parse_args(argv)
    report = run_cli(
        solvers=args.solver,
        rtol=args.rtol,
        atol=args.atol,
        seed=args.seed,
        output=args.output,
    )
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
