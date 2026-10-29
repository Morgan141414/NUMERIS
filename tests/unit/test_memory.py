import json

import pytest

from numeris.budget.memory import (
    ProfileResult,
    peak_process_memory_bytes,
    process_memory_bytes,
)


def test_memory_measurements_are_non_negative_or_explicitly_unavailable():
    current, current_source = process_memory_bytes()
    peak, peak_source = peak_process_memory_bytes()
    assert current is None or current >= 0
    assert peak is None or peak >= 0
    assert current_source
    assert peak_source


def test_profile_result_is_json_safe_and_versioned(tmp_path):
    result = ProfileResult(
        workload="oscillator",
        method="DOP853",
        elapsed_s=0.25,
        memory_before_bytes=100,
        memory_after_bytes=130,
        peak_memory_bytes=150,
        memory_delta_bytes=30,
        memory_source="test",
        cprofile_enabled=True,
    )
    payload = json.loads(result.to_json())
    assert payload["schema_version"] == "1"
    assert payload["memory_delta_bytes"] == 30
    assert "measured hot spot" in payload["cpp_gate"]
    result.write_json(tmp_path / "profile.json")
    assert json.loads((tmp_path / "profile.json").read_text()) == payload


def test_profile_result_rejects_invalid_or_unsafe_values():
    with pytest.raises(ValueError, match="elapsed_s"):
        ProfileResult(elapsed_s=float("nan"))
    with pytest.raises(ValueError, match="memory"):
        ProfileResult(memory_after_bytes=-1)
    with pytest.raises(ValueError, match="error"):
        ProfileResult(success=False)
    with pytest.raises(ValueError, match="successful"):
        ProfileResult(success=True, error="failure")
