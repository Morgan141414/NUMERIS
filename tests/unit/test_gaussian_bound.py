import pytest

from numeris.error_analysis import gaussian_nll_error_bound


def test_gaussian_nll_bound_is_zero_for_zero_state_error():
    assert gaussian_nll_error_bound(2.0, 0.0, 0.5) == 0.0


def test_gaussian_nll_bound_matches_quadratic_expression():
    assert gaussian_nll_error_bound(2.0, 0.1, 0.5) == pytest.approx(0.82)


def test_gaussian_nll_bound_validates_sigma():
    with pytest.raises(ValueError):
        gaussian_nll_error_bound(1.0, 0.1, 0.0)
