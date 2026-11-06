"""Exact damped oscillator model from the frozen minimal protocol.

This module is deliberately separate from the existing benchmark models.  It
encodes only the model, initial condition, observation map, and time grid
declared by ``research/protocol/MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md``.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from numeris.models.base import ODEModel


PROTOCOL_MODEL_ID = "minimal_protocol_damped_oscillator_v0.1"
PROTOCOL_T_SPAN = (0.0, 20.0)
PROTOCOL_INITIAL_STATE = np.array([1.0, 0.0], dtype=float)
PROTOCOL_TRUE_PARAMETERS = np.array([1.0, 0.1, 0.2], dtype=float)
PROTOCOL_PARAMETER_NAMES = ("omega", "zeta", "forcing")
PROTOCOL_PARAMETER_BOUNDS = ((0.5, 1.5), (0.02, 0.30), (0.0, 0.5))
PROTOCOL_OBSERVATION_SIGMA = 0.05


def observe_x1(states: np.ndarray) -> np.ndarray:
    """Return only the first state component, as required by the protocol."""

    values = np.asarray(states, dtype=float)
    if values.ndim == 1:
        if values.size != 2:
            raise ValueError("a single oscillator state must have two components")
        return np.asarray(values[0])
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError("oscillator states must have shape (n, 2)")
    return values[:, 0]


def protocol_oscillator_rhs(
    t: float,
    state: np.ndarray,
    parameters: np.ndarray,
) -> np.ndarray:
    """Evaluate the exact frozen-protocol oscillator RHS.

    Parameters are ordered ``[omega, zeta, forcing]`` and the equation is
    ``x1' = x2`` and
    ``x2' = -2*zeta*omega*x2 - omega**2*x1 + forcing*cos(omega*t)``.
    """

    omega, zeta, forcing = np.asarray(parameters, dtype=float)
    x1, x2 = np.asarray(state, dtype=float)
    return np.array(
        [
            x2,
            -2.0 * zeta * omega * x2
            - omega**2 * x1
            + forcing * np.cos(omega * float(t)),
        ],
        dtype=float,
    )


def make_protocol_oscillator(
    observation_times: Sequence[float] | None = None,
) -> ODEModel:
    """Create the exact model contract used by the frozen protocol.

    By default, observations are on ``linspace(0, 20, 201)``.  A custom grid
    is accepted for unit tests and solver diagnostics, but it must remain
    within the frozen interval and contain at least two strictly increasing
    points.
    """

    times = (
        np.linspace(*PROTOCOL_T_SPAN, 201)
        if observation_times is None
        else np.asarray(observation_times, dtype=float)
    )
    if times.ndim != 1 or times.size < 2:
        raise ValueError("observation_times must be a 1-D grid with at least two points")
    if times[0] != PROTOCOL_T_SPAN[0] or times[-1] != PROTOCOL_T_SPAN[1]:
        raise ValueError("observation_times must span the frozen interval [0, 20]")

    return ODEModel(
        rhs=protocol_oscillator_rhs,
        initial_state=PROTOCOL_INITIAL_STATE.copy(),
        t_span=PROTOCOL_T_SPAN,
        observation_times=times.copy(),
        observe=observe_x1,
    )

