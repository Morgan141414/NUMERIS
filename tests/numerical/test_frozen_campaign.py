import json

import pytest

from numeris.benchmarks import load_frozen_manifest, run_frozen_campaign


MANIFEST = "research/protocol/PROTOCOL_MANIFEST_v0.1.md"


def test_manifest_loader_reads_all_five_models():
    factors = load_frozen_manifest(MANIFEST)
    assert [model.model_id for model in factors.models] == ["OSC", "FHN", "LV", "LOR", "ROB"]
    assert factors.methods == ("RK45", "DOP853", "Radau", "BDF", "LSODA")
    assert factors.seeds == tuple(range(10))


def test_dry_run_is_bounded_and_never_claims_complete():
    report = run_frozen_campaign(
        manifest_path=MANIFEST,
        mode="dry-run",
        seeds=[0],
        sigmas=[0.01],
        methods=["BDF"],
        tolerance_levels=[(1e-4, 1e-6)],
        max_cells=3,
    )
    assert report["complete"] is False
    assert report["campaign_status"] == "bounded_incomplete"
    assert report["limits"] == {"max_cells": 3, "planned_cells": 5, "admitted_cells": 3}
    assert report["counts"]["not_started"] == 5
    assert report["negative_results"]["no_confirmed_advantage"] is True
    json.dumps(report, allow_nan=False)


def test_real_small_campaign_preserves_pairing_and_outcome_statuses():
    report = run_frozen_campaign(
        manifest_path=MANIFEST,
        mode="real",
        model_ids=["OSC"],
        seeds=[0],
        sigmas=[0.01],
        methods=["BDF", "DOP853"],
        tolerance_levels=[(1e-4, 1e-6)],
        max_cells=5,
    )
    assert report["limits"]["planned_cells"] == 2
    assert report["counts"]["success"] + report["counts"]["failure"] + report["counts"]["over_budget"] == 2
    successful = [row for row in report["cells"] if row["status"] == "success"]
    assert successful
    assert len({row["seed_metadata"]["observation_digest"] for row in successful}) == 1
    assert all(row["pair_id"] == "OSC:seed=0:sigma=0.01" for row in report["cells"])


def test_factors_and_manifest_are_mutually_exclusive():
    with pytest.raises(ValueError, match="exactly one"):
        run_frozen_campaign(manifest_path=MANIFEST, factors={})
