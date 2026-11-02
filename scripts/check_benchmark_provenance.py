#!/usr/bin/env python3
"""Fail-closed validation of benchmark provenance artifacts.

This checker validates metadata only.  It does not certify scientific quality,
reference accuracy, or C++ performance; it verifies that an artifact records
enough context to be replayed and honestly classified.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


RUN_SCOPES = {"exploratory", "bounded", "full"}
REQUIRED_PROVENANCE = (
    "git_commit",
    "runtime",
    "protocol_path",
    "command",
    "run_scope",
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _resolve_artifact(manifest_path: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_file():
        return candidate
    relative_to_manifest = manifest_path.parent / candidate
    if relative_to_manifest.is_file():
        return relative_to_manifest
    return candidate


def _check_provenance(
    artifact: dict[str, Any], *, manifest_path: Path, label: str
) -> list[str]:
    errors: list[str] = []
    provenance = artifact.get("provenance")
    if not isinstance(provenance, dict):
        return [f"{label}: missing provenance object"]
    for key in REQUIRED_PROVENANCE:
        if key not in provenance:
            errors.append(f"{label}: missing provenance.{key}")
    commit = provenance.get("git_commit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        errors.append(f"{label}: provenance.git_commit is not a full Git commit")
    runtime = provenance.get("runtime")
    if not isinstance(runtime, dict):
        errors.append(f"{label}: provenance.runtime is missing")
    else:
        for key in ("python_version", "platform"):
            if not isinstance(runtime.get(key), str) or not runtime[key]:
                errors.append(f"{label}: runtime.{key} is missing")
    if not isinstance(provenance.get("protocol_path"), str) or not provenance["protocol_path"]:
        errors.append(f"{label}: protocol_path is missing")
    elif not Path(provenance["protocol_path"]).is_file():
        errors.append(f"{label}: protocol_path does not exist: {provenance['protocol_path']}")
    if not isinstance(provenance.get("command"), str) or not provenance["command"]:
        errors.append(f"{label}: command is missing")
    if provenance.get("run_scope") not in RUN_SCOPES:
        errors.append(f"{label}: run_scope must be exploratory, bounded, or full")
    return errors


def check_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = _load(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"manifest: {exc}"]
    errors.extend(_check_provenance(manifest, manifest_path=manifest_path, label="manifest"))
    workloads = manifest.get("workloads")
    if not isinstance(workloads, list) or not workloads:
        errors.append("manifest: workloads must be a non-empty list")
    else:
        for index, item in enumerate(workloads):
            if not isinstance(item, dict) or not isinstance(item.get("profile_artifact"), str):
                errors.append(f"manifest: workload {index} lacks profile_artifact")
                continue
            path = _resolve_artifact(manifest_path, item["profile_artifact"])
            try:
                profile = _load(path)
            except (OSError, json.JSONDecodeError, ValueError) as exc:
                errors.append(f"profile {item['profile_artifact']}: {exc}")
                continue
            errors.extend(
                _check_provenance(
                    profile,
                    manifest_path=manifest_path,
                    label=f"profile {item['profile_artifact']}",
                )
            )
    gate = manifest.get("gate", {})
    if not isinstance(gate, dict) or not isinstance(gate.get("artifact"), str):
        errors.append("manifest: gate.artifact is missing")
    else:
        path = _resolve_artifact(manifest_path, gate["artifact"])
        try:
            gate_artifact = _load(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"gate {gate['artifact']}: {exc}")
        else:
            errors.extend(
                _check_provenance(
                    gate_artifact,
                    manifest_path=manifest_path,
                    label=f"gate {gate['artifact']}",
                )
            )
            if gate_artifact.get("decision") != "KEEP_PYTHON":
                errors.append("gate: provenance check expects fail-closed KEEP_PYTHON")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="suite_manifest.json to validate")
    args = parser.parse_args()
    errors = check_manifest(args.manifest)
    result = {"passed": not errors, "manifest": str(args.manifest), "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
