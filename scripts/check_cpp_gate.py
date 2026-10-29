#!/usr/bin/env python3
"""Evaluate the optional C++ gate from explicit, pre-declared evidence.

This script is intentionally conservative: missing evidence is a failed gate,
never an implicit pass.  It does not compile, benchmark, or approve a C++
implementation; it only evaluates JSON evidence produced by a separately
documented experiment.

Exit status is zero only for ``APPROVE_CPP``.  Any missing, malformed, or
failed predicate returns status one and reports ``KEEP_PYTHON``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


DEFAULT_SPEEDUP = 1.25
REQUIRED_PROFILE_FIELDS = ("success", "workload", "profiling_summary")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON evidence {path} must contain an object")
    return value


def _is_true(mapping: dict[str, Any], key: str) -> bool:
    # ``== True`` would accept values such as 1; the gate requires an explicit
    # boolean assertion in the evidence artifact.
    return mapping.get(key) is True


def _profile_ok(profile: dict[str, Any]) -> bool:
    if any(field not in profile for field in REQUIRED_PROFILE_FIELDS):
        return False
    summary = profile.get("profiling_summary")
    decision = summary.get("cpp_gate_decision") if isinstance(summary, dict) else None
    return bool(
        profile["success"] is True
        and isinstance(profile["workload"], str)
        and profile["workload"]
        and isinstance(decision, dict)
        and decision.get("measured_hot_spot") is True
    )


def _predicate_report(
    profile_paths: list[Path], evidence: dict[str, Any] | None, min_profiles: int,
    speedup_threshold: float,
) -> dict[str, dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    profile_errors: list[str] = []
    for path in profile_paths:
        try:
            profile = _load_json(path)
        except ValueError as exc:
            profile_errors.append(str(exc))
            continue
        profiles.append(profile)
        if not _profile_ok(profile):
            profile_errors.append(f"profile failed hotspot checks: {path}")

    unique_workloads = {
        profile.get("workload") for profile in profiles if _profile_ok(profile)
    }
    hotspot_ok = (
        len(profile_paths) >= min_profiles
        and len(unique_workloads) >= min_profiles
        and not profile_errors
        and evidence is not None
        and _is_true(evidence.get("hotspot", {}), "representative_workloads")
        and _is_true(evidence.get("hotspot", {}), "repeated")
        and _is_true(evidence.get("hotspot", {}), "replaceable")
        and _is_true(evidence.get("hotspot", {}), "material")
    )

    equivalence = evidence.get("equivalence", {}) if evidence else {}
    equivalence_ok = all(
        _is_true(equivalence, key)
        for key in ("verified", "normal_cases", "difficult_cases", "near_failure_cases", "tolerance_declared")
    )

    speed = evidence.get("speed", {}) if evidence else {}
    median_speedup = speed.get("median_speedup")
    speedup_is_valid = isinstance(median_speedup, (int, float)) and not isinstance(
        median_speedup, bool
    ) and math.isfinite(float(median_speedup))
    speed_ok = (
        speedup_is_valid
        and float(median_speedup) >= speedup_threshold
        and _is_true(speed, "warmup_excluded")
        and _is_true(speed, "repeated_measurements")
        and _is_true(speed, "no_material_regression")
    )

    memory = evidence.get("memory", {}) if evidence else {}
    memory_ok = _is_true(memory, "measured_comparably") and _is_true(memory, "within_budget")

    reproducibility = evidence.get("reproducibility", {}) if evidence else {}
    reproducibility_ok = all(
        _is_true(reproducibility, key)
        for key in ("build_reproducible", "interface_documented", "deterministic", "artifacts_reproducible")
    )

    return {
        "HOTSPOT": {
            "passed": hotspot_ok,
            "profiles": len(profile_paths),
            "unique_workloads": sorted(value for value in unique_workloads if value),
            "errors": profile_errors,
            "required_profiles": min_profiles,
        },
        "EQUIVALENT": {"passed": equivalence_ok},
        "FASTER_AFTER_WARMUP": {
            "passed": speed_ok,
            "median_speedup": median_speedup,
            "required_speedup": speedup_threshold,
        },
        "MEMORY_ACCEPTABLE": {"passed": memory_ok},
        "REPRODUCIBLE": {"passed": reproducibility_ok},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile", type=Path, action="append", default=[],
        help="profile JSON; repeat for distinct representative workloads",
    )
    parser.add_argument(
        "--evidence", type=Path,
        help="candidate evidence JSON matching docs/performance_and_cpp.md",
    )
    parser.add_argument("--min-profiles", type=int, default=3)
    parser.add_argument("--speedup-threshold", type=float, default=DEFAULT_SPEEDUP)
    args = parser.parse_args()
    if args.min_profiles < 1 or not math.isfinite(args.speedup_threshold):
        parser.error("--min-profiles must be positive and --speedup-threshold finite")

    evidence = None
    if args.evidence is not None:
        try:
            evidence = _load_json(args.evidence)
        except ValueError as exc:
            print(f"KEEP_PYTHON: {exc}", file=sys.stderr)
            return 1

    report = _predicate_report(args.profile, evidence, args.min_profiles, args.speedup_threshold)
    approved = all(item["passed"] for item in report.values())
    print(json.dumps({"decision": "APPROVE_CPP" if approved else "KEEP_PYTHON", "predicates": report}, indent=2, sort_keys=True))
    return 0 if approved else 1


if __name__ == "__main__":
    raise SystemExit(main())
