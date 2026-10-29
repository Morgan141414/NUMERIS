#!/usr/bin/env python3
"""Profile a representative NUMERIS workload for the optional C++ gate."""

from __future__ import annotations

import argparse
import cProfile
import pstats
from pathlib import Path

import numpy as np

from numeris.benchmarks import damped_oscillator
from numeris.solvers import solve_ode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", default="DOP853")
    parser.add_argument("--output", type=Path, default=Path("results/profile.prof"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model = damped_oscillator(np.linspace(0.0, 20.0, 201))
    params = np.array([1.0, 0.1, 0.2])
    profiler = cProfile.Profile()
    profiler.enable()
    solve_ode(model, params, method=args.method, rtol=1e-8, atol=1e-10)
    profiler.disable()
    profiler.dump_stats(str(args.output))
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)
    print(f"profile written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
