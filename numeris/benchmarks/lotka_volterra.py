"""Lotka--Volterra predator--prey benchmark."""

import numpy as np

from numeris.models.base import ODEModel


def lotka_volterra(times: np.ndarray | None = None) -> ODEModel:
    """Return a two-state predator--prey model.

    Parameters are ordered as ``(alpha, beta, delta, gamma)``.
    """
    times = np.linspace(0.0, 30.0, 301) if times is None else np.asarray(times, dtype=float)

    def rhs(_t: float, x: np.ndarray, p: np.ndarray) -> np.ndarray:
        alpha, beta, delta, gamma = p
        prey, predator = x
        interaction = prey * predator
        return np.array([alpha * prey - beta * interaction, delta * interaction - gamma * predator])

    return ODEModel(
        rhs=rhs,
        initial_state=[10.0, 5.0],
        t_span=(float(times[0]), float(times[-1])),
        observation_times=times,
    )
