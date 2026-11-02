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
        assert (artifact_dir / f"profile_{workload}.json").is_file()

    gate_report = json.loads((artifact_dir / "cpp_gate.json").read_text())
    assert gate_report["decision"] == "KEEP_PYTHON"
    assert gate_report["predicates"]["EQUIVALENT"]["passed"] is False
    assert gate_report["predicates"]["FASTER_AFTER_WARMUP"]["passed"] is False
