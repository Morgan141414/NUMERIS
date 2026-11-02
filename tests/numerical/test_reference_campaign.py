import json

import pytest

from numeris.benchmarks import run_bounded_reference_campaign


def test_bounded_reference_campaign_covers_all_five_factories_and_is_json_safe():
    report = run_bounded_reference_campaign()
    assert report["model_count"] == 5
    assert report["planned_solver_runs"] == 20
    assert {item["factory"] for item in report["models"]} == {
        "damped_oscillator", "fitzhugh_nagumo", "lotka_volterra", "lorenz", "robertson"
    }
    json.dumps(report, allow_nan=False)
    assert all("superiority" in " ".join(item["limitations"]).lower() for item in report["models"])


def test_campaign_records_reference_status_for_selected_model():
    report = run_bounded_reference_campaign(model_ids=["ROB"])
    model = report["models"][0]
    assert model["status"] in {"REFERENCE-RESOLVED", "REFERENCE-UNRESOLVED"}
    assert len(model["checks"]) == 3
    assert model["configuration"]["reference_families"] == ["BDF", "Radau"]
    assert model["reference_report"] is not None or model["status"] == "REFERENCE-UNRESOLVED"


def test_campaign_is_bounded_and_rejects_unknown_or_excess_selection():
    with pytest.raises(ValueError, match="max_models"):
        run_bounded_reference_campaign(model_ids=["OSC", "FHN"], max_models=1)
    with pytest.raises(ValueError, match="no benchmark"):
        run_bounded_reference_campaign(model_ids=["unknown"])


def test_campaign_rejects_non_two_level_reference_protocol():
    with pytest.raises(ValueError, match="exactly two"):
        run_bounded_reference_campaign(model_ids=["OSC"], tolerance_levels=[(1e-8, 1e-10)])
