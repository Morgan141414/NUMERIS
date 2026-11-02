#!/usr/bin/env python3
"""Profile a representative NUMERIS workload for the optional C++ gate."""

from __future__ import annotations

import argparse
import cProfile
import json
import pstats
import platform
import shlex
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from numeris.benchmarks import damped_oscillator, fitzhugh_nagumo, robertson
from numeris.budget.memory import (
    ProfileResult,
    ProfilingSummary,
    peak_process_memory_bytes,
    process_memory_bytes,
)
from numeris.solvers import solve_ode


WORKLOADS = {
    "oscillator": (damped_oscillator, np.array([1.0, 0.1, 0.2]), "DOP853"),
    "fitzhugh_nagumo": (
        fitzhugh_nagumo,
        np.array([0.7, 0.8, 0.08, 0.5]),
        "DOP853",
    ),
    "robertson": (robertson, np.array([0.04, 3.0e7, 1.0e4]), "BDF"),
}
DEFAULT_ARTIFACT_DIR = Path("results/profiling/cpp_gate")


def _runtime_metadata() -> dict[str, object]:
    """Return serializable provenance for a profiling artifact."""
    try:
        import numpy
        numpy_version = numpy.__version__
    except Exception:  # pragma: no cover - defensive metadata fallback
        numpy_version = None
    try:
        import scipy
        scipy_version = scipy.__version__
    except Exception:  # pragma: no cover - defensive metadata fallback
        scipy_version = None
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "numpy_version": numpy_version,
        "scipy_version": scipy_version,
    }


def _command_provenance() -> dict[str, object]:
    """Capture the exact CLI invocation in both argv and shell form."""
    argv = [sys.executable, *sys.argv]
    return {"command_argv": argv, "command": shlex.join(argv)}


def _write_profile_artifact(
    result: ProfileResult,
    result_path: Path,
    *,
    workload: str,
    method: str,
    solver_options: dict[str, object],
) -> None:
    """Write a core profile record plus immutable run provenance.

    The metadata is added at the script boundary so the numerical core and
    its public schema remain unchanged.  It is deliberately explicit rather
    than inferred later from filenames or the current machine.
    """
    artifact = result.to_dict()
    artifact["profiling_artifact_schema_version"] = "1"
    artifact["provenance"] = {
        **_command_provenance(),
        "workload": workload,
        "solver": {"name": method, "options": solver_options},
        "runtime": _runtime_metadata(),
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _profile_workload(
    name: str,
    method: str,
    profile_path: Path,
    result_path: Path,
    hotspot_threshold: float,
) -> bool:
    factory, params, _reference_method = WORKLOADS[name]
    model = factory()
    before, source = process_memory_bytes()
    peak_before, _peak_source = peak_process_memory_bytes()
    profiler = cProfile.Profile()
    started = time.perf_counter()
    error = None
    profiler.enable()
    try:
        solve_ode(model, params, method=method, rtol=1e-8, atol=1e-10)
    except Exception as exc:  # pragma: no cover - exercised by CLI failures
        error = f"{type(exc).__name__}: {exc}"
    finally:
        profiler.disable()
    elapsed = time.perf_counter() - started
    profiler.dump_stats(str(profile_path))
    after, after_source = process_memory_bytes()
    peak_after, _peak_source_after = peak_process_memory_bytes()
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
        top_functions and top_functions[0]["cumulative_share"] >= hotspot_threshold
    )
    cpp_gate_decision = {
        "decision": "investigate_cpp" if measured_hot_spot else "do_not_implement_cpp",
        "measured_hot_spot": measured_hot_spot,
        "hotspot_threshold": hotspot_threshold,
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
        workload=name,
        method=method,
        profile_path=str(profile_path),
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
    _write_profile_artifact(
        result,
        result_path,
        workload=name,
        method=method,
        solver_options={"rtol": 1e-8, "atol": 1e-10},
    )
    stats.print_stats(20)
    print(f"profile written to {profile_path}")
    print(f"safe result written to {result_path}")
    return result.success


def _run_fail_closed_gate(
    profile_paths: tuple[Path, ...],
    gate_result_path: Path,
    min_profiles: int,
) -> tuple[bool, dict[str, object]]:
    """Run the C++ gate without candidate evidence and require KEEP_PYTHON.

    The profiling workflow must never manufacture C++ evidence.  A successful
    suite therefore means that profiling completed and the independent gate
    explicitly refused production C++ because no evidence file was supplied.
    """
    command = [
        sys.executable,
        str(Path(__file__).with_name("check_cpp_gate.py")),
        "--min-profiles",
        str(min_profiles),
    ]
    for profile_path in profile_paths:
        command.extend(("--profile", str(profile_path)))
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    stdout = completed.stdout.strip()
    try:
        report = json.loads(stdout)
    except json.JSONDecodeError:
        print("C++ gate produced invalid JSON:", stdout, file=sys.stderr)
        if completed.stderr.strip():
            print(completed.stderr.strip(), file=sys.stderr)
        return False, {}
    gate_command = [str(value) for value in command]
    report["gate_artifact_schema_version"] = "1"
    report["provenance"] = {
        "command_argv": gate_command,
        "command": shlex.join(gate_command),
        "runtime": _runtime_metadata(),
        "profile_artifacts": [str(path) for path in profile_paths],
        "fail_closed_without_candidate_evidence": True,
    }
    gate_result_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    decision = report.get("decision")
    print(f"C++ gate decision: {decision} (no C++ evidence supplied)")
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    return decision == "KEEP_PYTHON" and completed.returncode != 0, report


def _write_suite_manifest(
    artifact_dir: Path,
    *,
    profile_paths: list[Path],
    gate_path: Path,
    gate_report: dict[str, object],
) -> None:
    """Persist one auditable index for a complete profiling suite."""
    manifest = {
        "suite_artifact_schema_version": "1",
        "provenance": {
            **_command_provenance(),
            "runtime": _runtime_metadata(),
        },
        "workloads": [
            {
                "name": name,
                "solver": {"name": WORKLOADS[name][2], "options": {"rtol": 1e-8, "atol": 1e-10}},
                "profile_artifact": str(path),
            }
            for name, path in zip(WORKLOADS, profile_paths)
        ],
        "gate": {
            "artifact": str(gate_path),
            "decision": gate_report.get("decision"),
            "command": gate_report.get("provenance", {}).get("command"),
            "fail_closed_without_candidate_evidence": gate_report.get("provenance", {}).get(
                "fail_closed_without_candidate_evidence"
            ),
        },
    }
    (artifact_dir / "suite_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", default="DOP853")
    parser.add_argument(
        "--suite",
        action="store_true",
        help="profile the deterministic representative suite (three workloads)",
    )
    parser.add_argument(
        "--workload",
        choices=tuple(WORKLOADS),
        default="oscillator",
        help="single workload used when --suite is not selected",
    )
    parser.add_argument("--output", type=Path, default=Path("results/profile.prof"))
    parser.add_argument(
        "--result-output",
        type=Path,
        default=Path("results/profile.json"),
        help="JSON profiling result (the .prof output remains available).",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=None,
        help=(
            "directory for suite artifacts; defaults to "
            "results/profiling/cpp_gate"
        ),
    )
    parser.add_argument(
        "--hotspot-threshold",
        type=float,
        default=0.50,
        help="minimum cumulative-time share required to flag a measured hot spot",
    )
    args = parser.parse_args()
    workloads = tuple(WORKLOADS) if args.suite else (args.workload,)
    if args.suite and args.method != "DOP853":
        parser.error("--suite uses its declared solver methods; omit --method")
    if args.suite:
        artifact_dir = args.artifact_dir or DEFAULT_ARTIFACT_DIR
        artifact_dir.mkdir(parents=True, exist_ok=True)
        success = True
        profile_paths: list[Path] = []
        for name in workloads:
            _, _, declared_method = WORKLOADS[name]
            profile_path = artifact_dir / f"profile_{name}.prof"
            result_path = artifact_dir / f"profile_{name}.json"
            profile_paths.append(result_path)
            success = _profile_workload(
                name,
                declared_method,
                profile_path,
                result_path,
                args.hotspot_threshold,
            ) and success
        gate_ok, gate_report = _run_fail_closed_gate(
            tuple(profile_paths), artifact_dir / "cpp_gate.json", min_profiles=3
        )
        _write_suite_manifest(
            artifact_dir,
            profile_paths=profile_paths,
            gate_path=artifact_dir / "cpp_gate.json",
            gate_report=gate_report,
        )
        return 0 if success and gate_ok else 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.result_output.parent.mkdir(parents=True, exist_ok=True)
    return int(
        not _profile_workload(
            args.workload,
            args.method,
            args.output,
            args.result_output,
            args.hotspot_threshold,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
