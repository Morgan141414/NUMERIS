import numpy as np
import pytest

from numeris.inference import normalized_grid_posterior


def test_grid_posterior_is_normalized_and_stable():
    posterior = normalized_grid_posterior(np.array([-1000.0, -2.0, -1.0]))
    assert np.isclose(posterior.sum(), 1.0)
    assert posterior[-1] > posterior[0]


def test_grid_posterior_rejects_nonfinite_inputs():
    with pytest.raises(ValueError):
        normalized_grid_posterior(np.array([0.0, np.inf]))
