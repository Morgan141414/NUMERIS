#!/usr/bin/env python3
"""Profile a representative NUMERIS workload for the optional C++ gate."""

from __future__ import annotations

import argparse
import cProfile
import pstats
import time
from pathlib import Path

import numpy as np

from numeris.benchmarks import damped_oscillator
from numeris.budget.memory import ProfileResult, peak_process_memory_bytes, process_memory_bytes
from numeris.solvers import solve_ode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", default="DOP853")
    parser.add_argument("--output", type=Path, default=Path("results/profile.prof"))
    parser.add_argument(
        "--result-output",
        type=Path,
        default=Path("results/profile.json"),
        help="JSON profiling result (the .prof output remains available).",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model = damped_oscillator(np.linspace(0.0, 20.0, 201))
    params = np.array([1.0, 0.1, 0.2])
    before, source = process_memory_bytes()
    peak_before, peak_source = peak_process_memory_bytes()
    profiler = cProfile.Profile()
    started = time.perf_counter()
    error = None
    profiler.enable()
    try:
        solve_ode(model, params, method=args.method, rtol=1e-8, atol=1e-10)
    except Exception as exc:  # pragma: no cover - exercised by CLI failures
        error = f"{type(exc).__name__}: {exc}"
    finally:
        profiler.disable()
    elapsed = time.perf_counter() - started
    profiler.dump_stats(str(args.output))
    after, after_source = process_memory_bytes()
    peak_after, peak_source_after = peak_process_memory_bytes()
    measured = [value for value in (peak_before, peak_after) if value is not None]
    peak = max(measured) if measured else None
    delta = after - before if before is not None and after is not None else None
    result = ProfileResult(
        workload="damped_oscillator",
        method=args.method,
        profile_path=str(args.output),
        elapsed_s=elapsed,
        memory_before_bytes=before,
        memory_after_bytes=after,
        peak_memory_bytes=peak,
        memory_delta_bytes=delta,
        memory_source=source if source != "unavailable" else after_source,
        cprofile_enabled=True,
        success=error is None,
        error=error,
    )
    result.write_json(args.result_output)
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(20)
    print(f"profile written to {args.output}")
    print(f"safe result written to {args.result_output}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
