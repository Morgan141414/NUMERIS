import json

import numpy as np
import pytest

from numeris.inference import PairedBootstrapResult, paired_bootstrap_difference


def test_paired_bootstrap_is_deterministic_and_json_friendly():
    reference = np.array([1.0, 2.0, 3.0, 4.0])
    candidate = reference + np.array([0.2, 0.4, 0.1, 0.3])

    first = paired_bootstrap_difference(reference, candidate, n_resamples=300, seed=17)
    second = paired_bootstrap_difference(reference, candidate, n_resamples=300, seed=17)

    assert isinstance(first, PairedBootstrapResult)
    assert first == second
    encoded = json.dumps(first.summary(), allow_nan=False)
    decoded = json.loads(encoded)
    assert decoded["schema_version"] == "paired-bootstrap-v1"
    assert decoded["observed_difference"] == pytest.approx(0.25)
    assert decoded["n_pairs"] == 4
    assert decoded["seed"] == 17
    assert decoded["confidence_interval"]["lower"] <= 0.25 <= decoded["confidence_interval"]["upper"]


def test_paired_bootstrap_preserves_pairing_and_supports_median():
    result = paired_bootstrap_difference(
        [10.0, 20.0, 30.0],
        [11.0, 22.0, 36.0],
        statistic="median",
        n_resamples=100,
        seed=3,
    )
    assert result.statistic == "median"
    assert result.observed_difference == pytest.approx(2.0)
    assert result.n_pairs == 3


def test_small_sample_limitation_is_explicit():
    result = paired_bootstrap_difference([1.0], [1.5], n_resamples=20, seed=0)
    assert any("Small sample limitation" in item for item in result.limitations)
    assert any("one paired seed" in item for item in result.limitations)


@pytest.mark.parametrize(
    "call",
    [
        lambda: paired_bootstrap_difference([], []),
        lambda: paired_bootstrap_difference([1.0], [1.0, 2.0]),
        lambda: paired_bootstrap_difference([1.0, np.nan], [1.0, 2.0]),
        lambda: paired_bootstrap_difference([1.0], [1.0], n_resamples=0),
        lambda: paired_bootstrap_difference([1.0], [1.0], confidence_level=1.0),
    ],
)
def test_paired_bootstrap_validates_inputs(call):
    with pytest.raises(ValueError):
        call()
