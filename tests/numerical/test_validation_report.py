import json

import numpy as np

from numeris.benchmarks import ValidationCase, damped_oscillator, fitzhugh_nagumo, run_validation_suite


def _cases():
    oscillator = damped_oscillator(np.linspace(0.0, 2.0, 9))
    fhn = fitzhugh_nagumo(np.linspace(0.0, 2.0, 9))
    return [
        ValidationCase(
            name="oscillator",
            model=oscillator,
            truth=(1.0, 0.1, 0.2),
            sigma=0.01,
            parameter_grid=((0.9, 0.1, 0.2), (1.0, 0.1, 0.2), (1.1, 0.1, 0.2)),
        ),
        ValidationCase(
            name="fitzhugh_nagumo",
            model=fhn,
            truth=(0.7, 0.8, 0.08, 0.5),
            sigma=0.01,
            parameter_grid=(
                (0.7, 0.8, 0.08, 0.4),
                (0.7, 0.8, 0.08, 0.5),
                (0.7, 0.8, 0.08, 0.6),
            ),
        ),
    ]


def test_suite_is_json_serializable_and_reports_budget_and_limitations():
    report = run_validation_suite(_cases(), repetitions=1, seed=17)
    encoded = json.dumps(report, allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["schema_version"] == "validation-suite-v1"
    assert decoded["suite"]["case_count"] == 2
    assert decoded["cases"][0]["budget"]["total_ode_solves_upper_bound"] == 10
    assert decoded["limitations"]
    assert any("superiority" in item for item in decoded["limitations"])


def test_suite_seed_is_reproducible():
    first = run_validation_suite(_cases(), repetitions=1, seed=23)
    second = run_validation_suite(_cases(), repetitions=1, seed=23)
    assert first["cases"][0]["seed"] == second["cases"][0]["seed"]
    assert first["cases"][0]["calibration"]["coverage"] == second["cases"][0]["calibration"]["coverage"]

