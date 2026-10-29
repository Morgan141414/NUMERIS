"""Lorenz chaotic-system benchmark."""

import numpy as np

from numeris.models.base import ODEModel


def lorenz(times: np.ndarray | None = None) -> ODEModel:
    """Return the classical three-state Lorenz system.

    Parameters are ordered as ``(sigma, rho, beta)``.
    """
    times = np.linspace(0.0, 20.0, 401) if times is None else np.asarray(times, dtype=float)

    def rhs(_t: float, x: np.ndarray, p: np.ndarray) -> np.ndarray:
        sigma, rho, beta = p
        x_coord, y_coord, z_coord = x
        return np.array(
            [
                sigma * (y_coord - x_coord),
                x_coord * (rho - z_coord) - y_coord,
                x_coord * y_coord - beta * z_coord,
            ]
        )

    return ODEModel(
        rhs=rhs,
        initial_state=[1.0, 1.0, 1.0],
        t_span=(float(times[0]), float(times[-1])),
        observation_times=times,
    )
