import numpy as np

from numeris.inference import hellinger_distance, wasserstein_1d


def test_distribution_metrics_zero_for_identical_inputs():
    p = np.array([1.0, 2.0, 1.0])
    assert hellinger_distance(p, p) == 0.0
    assert wasserstein_1d(p, p) == 0.0
