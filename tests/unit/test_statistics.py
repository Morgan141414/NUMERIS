import numpy as np
import pytest

from numeris.benchmarks import summarize


def test_summary_is_reproducible_and_includes_spread():
    result = summarize(np.array([1.0, 2.0, 3.0]))
    assert result["n"] == 3
    assert result["mean"] == pytest.approx(2.0)
    assert result["std"] == pytest.approx(1.0)


def test_summary_rejects_empty_input():
    with pytest.raises(ValueError):
        summarize(np.array([]))
