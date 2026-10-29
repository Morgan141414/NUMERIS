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
from numeris.budget.memory import (
    ProfileResult,
    ProfilingSummary,
    peak_process_memory_bytes,
    process_memory_bytes,
)
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
    parser.add_argument(
        "--hotspot-threshold",
        type=float,
        default=0.50,
        help="minimum cumulative-time share required to flag a measured hot spot",
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
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    total_profile_time = max(float(stats.total_tt), 0.0)
    top_functions = []
    for (filename, line, function), values in stats.stats.items():
        primitive_calls, calls, _self_s, cumulative_s, _callers = values
        share = cumulative_s / total_profile_time if total_profile_time else 0.0
        top_functions.append(
            {
                "function": f"{function} ({filename}:{line})",
                "primitive_calls": int(primitive_calls),
                "calls": int(calls),
                "cumulative_s": float(cumulative_s),
                "cumulative_share": float(share),
            }
        )
    top_functions.sort(key=lambda item: item["cumulative_s"], reverse=True)
    top_functions = top_functions[:20]
    measured_hot_spot = bool(
        top_functions
        and top_functions[0]["cumulative_share"] >= args.hotspot_threshold
    )
    cpp_gate_decision = {
        "decision": "investigate_cpp" if measured_hot_spot else "do_not_implement_cpp",
        "measured_hot_spot": measured_hot_spot,
        "hotspot_threshold": args.hotspot_threshold,
        "top_function": top_functions[0]["function"] if top_functions else None,
        "numerical_equivalence_verified": False,
        "reason": (
            "A cumulative hot spot was measured; implement C++ only after "
            "a numerical-equivalence test."
            if measured_hot_spot
            else "No cumulative hot spot met the configured threshold."
        ),
    }
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
        profiling_summary=ProfilingSummary(
            elapsed_s=elapsed,
            memory_source=source if source != "unavailable" else after_source,
            top_cumulative_functions=tuple(top_functions),
            cpp_gate_decision=cpp_gate_decision,
        ),
    )
    result.write_json(args.result_output)
    stats.print_stats(20)
    print(f"profile written to {args.output}")
    print(f"safe result written to {args.result_output}")
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
