#!/usr/bin/env python3
"""Run one reproducible deterministic slice across all required ODE families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from numeris.benchmarks import (
    damped_oscillator,
    fitzhugh_nagumo,
    lorenz,
    lotka_volterra,
    robertson,
    run_benchmark,
)
from numeris.benchmarks.runner import SolverConfig
from numeris.solvers import solve_ode
from numeris.reproducibility import ReproducibilityMetadata


CASES = {
    "oscillator": (damped_oscillator, [1.0, 0.1, 0.2]),
    "fitzhugh_nagumo": (fitzhugh_nagumo, [0.7, 0.8, 0.08, 0.5]),
    "lotka_volterra": (lotka_volterra, [1.5, 1.0, 0.75, 1.0]),
    "lorenz": (lorenz, [10.0, 28.0, 8.0 / 3.0]),
    "robertson": (robertson, [0.04, 3.0e7, 1.0e4]),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solver", nargs="+", default=["DOP853"],
                        choices=("RK45", "DOP853", "Radau", "BDF", "LSODA"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    rng = np.random.default_rng(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    reports = {}
    for name, (factory, parameter_values) in CASES.items():
        model = factory()
        parameters = np.asarray(parameter_values, dtype=float)
        reference_method = "BDF" if name == "robertson" else "DOP853"
        reference = solve_ode(model, parameters, method=reference_method, rtol=1e-11, atol=1e-13)
        sigma = 0.01
        observations = model.observe(reference.states) + rng.normal(0.0, sigma, reference.states.shape)
        configs = [SolverConfig(method.lower(), method=method, rtol=1e-8, atol=1e-10) for method in args.solver]
        reports[name] = run_benchmark(
            model, parameters, configs, observations=observations, sigma=sigma,
            reference_states=reference.states, name=name,
        )
        reports[name]["reference"] = {"method": reference_method, "rtol": 1e-11, "atol": 1e-13}
    report = {
        "seed": args.seed,
        "models": reports,
        "reproducibility": ReproducibilityMetadata.capture(
            seed=args.seed,
            solver_settings={"methods": args.solver, "rtol": 1e-8, "atol": 1e-10},
        ).to_dict(),
    }
    target = args.output_dir / "all_benchmarks.json"
    target.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(target), "models": list(reports)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
