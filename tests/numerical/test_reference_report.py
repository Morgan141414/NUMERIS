import json

import numpy as np
import pytest

from numeris.benchmarks import damped_oscillator
from numeris.benchmarks.reference_report import SolverSpec, build_reference_report


def _report():
    model = damped_oscillator(np.linspace(0.0, 4.0, 41))
    return build_reference_report(
        model,
        [1.0, 0.1, 0.2],
        tolerance_levels={"loose": (1e-6, 1e-8), "tight": (1e-10, 1e-12)},
        solver_configs=[SolverSpec("DOP853"), SolverSpec("Radau")],
        reference_configs=[SolverSpec("DOP853"), SolverSpec("Radau")],
        name="oscillator-test",
    )


def test_reference_report_is_json_serializable_and_explicit_about_policy():
    report = _report()
    encoded = json.dumps(report, allow_nan=False)
    assert json.loads(encoded)["reference_policy"]["not_absolute_truth"] is True
    assert report["reference"]["candidate_count"] == 2
    assert len(report["runs"]) == 4
    assert report["schema_version"] == "reference-report-v1"


def test_tighter_level_is_closer_to_independent_consensus_for_oscillator():
    report = _report()
    errors = {
        (row["solver"]["method"], row["tolerance_level"]): row["distance_to_consensus"]["rmse"]
        for row in report["runs"]
    }
    assert errors[("DOP853", "tight")] < errors[("DOP853", "loose")]
    assert errors[("Radau", "tight")] < errors[("Radau", "loose")]


def test_one_method_cannot_be_used_as_reference():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    with pytest.raises(ValueError, match="at least two independent"):
        build_reference_report(
            model,
            [1.0, 0.1, 0.2],
            tolerance_levels=[(1e-8, 1e-10)],
            solver_configs=["DOP853"],
            reference_configs=["DOP853"],
        )


def test_convergence_report_requires_multiple_tolerance_levels():
    model = damped_oscillator(np.linspace(0.0, 1.0, 11))
    with pytest.raises(ValueError, match="two tolerance levels"):
        build_reference_report(
            model,
            [1.0, 0.1, 0.2],
            tolerance_levels=[(1e-8, 1e-10)],
            solver_configs=["DOP853"],
            reference_configs=["DOP853", "Radau"],
        )
