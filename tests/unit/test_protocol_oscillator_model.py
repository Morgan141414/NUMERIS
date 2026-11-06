"""Tests for the exact model declared by the frozen minimal protocol."""

import numpy as np
import pytest

from numeris.models.protocol_oscillator import (
    PROTOCOL_INITIAL_STATE,
    PROTOCOL_PARAMETER_NAMES,
    PROTOCOL_T_SPAN,
    PROTOCOL_TRUE_PARAMETERS,
    make_protocol_oscillator,
    observe_x1,
    protocol_oscillator_rhs,
)


def test_rhs_matches_frozen_protocol_equations() -> None:
    state = np.array([1.25, -0.4])
    parameters = np.array([1.1, 0.15, 0.2])
    t = 0.7

    expected = np.array(
        [
            state[1],
            -2.0 * parameters[1] * parameters[0] * state[1]
            - parameters[0] ** 2 * state[0]
            + parameters[2] * np.cos(parameters[0] * t),
        ]
    )

    np.testing.assert_allclose(protocol_oscillator_rhs(t, state, parameters), expected)


def test_factory_matches_frozen_protocol_contract() -> None:
    model = make_protocol_oscillator()

    assert model.t_span == PROTOCOL_T_SPAN
    np.testing.assert_array_equal(model.initial_state, PROTOCOL_INITIAL_STATE)
    np.testing.assert_array_equal(model.observation_times, np.linspace(0.0, 20.0, 201))
    assert PROTOCOL_PARAMETER_NAMES == ("omega", "zeta", "forcing")
    np.testing.assert_array_equal(PROTOCOL_TRUE_PARAMETERS, [1.0, 0.1, 0.2])


def test_observation_map_returns_only_x1() -> None:
    states = np.array([[1.0, 2.0], [3.0, 4.0]])

    np.testing.assert_array_equal(observe_x1(states), [1.0, 3.0])
    assert observe_x1(np.array([5.0, 6.0])) == 5.0


def test_factory_rejects_grid_outside_frozen_interval() -> None:
    with pytest.raises(ValueError, match="frozen interval"):
        make_protocol_oscillator(np.linspace(0.0, 19.0, 20))

