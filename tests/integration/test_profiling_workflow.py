import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_SCRIPT = PROJECT_ROOT / "scripts" / "profile_benchmark.py"


def test_suite_writes_predictable_artifacts_and_runs_fail_closed_gate(tmp_path):
    artifact_dir = tmp_path / "profiling" / "cpp_gate"
    completed = subprocess.run(
        [
            sys.executable,
            str(PROFILE_SCRIPT),
            "--suite",
            "--artifact-dir",
            str(artifact_dir),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "C++ gate decision: KEEP_PYTHON" in completed.stdout
    assert not (artifact_dir / "cpp_candidate_evidence.json").exists()

    for workload in ("oscillator", "fitzhugh_nagumo", "robertson"):
        assert (artifact_dir / f"profile_{workload}.prof").is_file()
        profile = json.loads((artifact_dir / f"profile_{workload}.json").read_text())
        assert profile["profiling_artifact_schema_version"] == "1"
        assert profile["provenance"]["command_argv"][:2] == [
            sys.executable,
            str(PROFILE_SCRIPT),
        ]
        assert profile["provenance"]["command"]
        assert profile["provenance"]["workload"] == workload
        assert profile["provenance"]["solver"]["name"] in {"DOP853", "BDF"}
        assert profile["provenance"]["solver"]["options"] == {
            "rtol": 1e-8,
            "atol": 1e-10,
        }
        assert profile["provenance"]["runtime"]["python_version"]
        assert profile["provenance"]["runtime"]["platform"]

    gate_report = json.loads((artifact_dir / "cpp_gate.json").read_text())
    assert gate_report["gate_artifact_schema_version"] == "1"
    assert gate_report["decision"] == "KEEP_PYTHON"
    assert gate_report["provenance"]["command"]
    assert gate_report["provenance"]["fail_closed_without_candidate_evidence"] is True
    assert gate_report["predicates"]["EQUIVALENT"]["passed"] is False
    assert gate_report["predicates"]["FASTER_AFTER_WARMUP"]["passed"] is False

    manifest = json.loads((artifact_dir / "suite_manifest.json").read_text())
    assert manifest["suite_artifact_schema_version"] == "1"
    assert manifest["provenance"]["command"]
    assert [item["name"] for item in manifest["workloads"]] == [
        "oscillator",
        "fitzhugh_nagumo",
        "robertson",
    ]
    assert [item["solver"]["name"] for item in manifest["workloads"]] == [
        "DOP853",
        "DOP853",
        "BDF",
    ]
    assert manifest["gate"]["decision"] == "KEEP_PYTHON"
    assert manifest["gate"]["fail_closed_without_candidate_evidence"] is True
