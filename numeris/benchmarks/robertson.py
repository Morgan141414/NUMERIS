"""Robertson chemical-kinetics benchmark."""

import numpy as np

from numeris.models.base import ODEModel


def robertson(times: np.ndarray | None = None) -> ODEModel:
    """Return the classical stiff Robertson kinetics system.

    Parameters are ordered as ``(k1, k2, k3)`` and the state is the
    concentration vector ``(y1, y2, y3)``.
    """
    times = np.geomspace(1e-6, 1e5, 301) if times is None else np.asarray(times, dtype=float)

    def rhs(_t: float, x: np.ndarray, p: np.ndarray) -> np.ndarray:
        k1, k2, k3 = p
        y1, y2, y3 = x
        reaction_1 = k1 * y1
        reaction_2 = k2 * y2**2
        reaction_3 = k3 * y2 * y3
        return np.array(
            [-reaction_1 + reaction_3, reaction_1 - reaction_2 - reaction_3, reaction_2]
        )

    return ODEModel(
        rhs=rhs,
        initial_state=[1.0, 0.0, 0.0],
        t_span=(float(times[0]), float(times[-1])),
        observation_times=times,
    )
