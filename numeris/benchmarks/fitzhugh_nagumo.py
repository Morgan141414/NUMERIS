"""FitzHugh--Nagumo excitable-system benchmark."""

import numpy as np

from numeris.models.base import ODEModel


def fitzhugh_nagumo(times: np.ndarray | None = None) -> ODEModel:
    """Return a two-state FitzHugh--Nagumo model.

    Parameters are ordered as ``(a, b, epsilon, current)``.  The state is
    ``(v, w)``, where ``v`` is the membrane potential and ``w`` is the
    recovery variable.
    """
    times = np.linspace(0.0, 40.0, 401) if times is None else np.asarray(times, dtype=float)

    def rhs(_t: float, x: np.ndarray, p: np.ndarray) -> np.ndarray:
        a, b, epsilon, current = p
        v, w = x
        return np.array([v - v**3 / 3.0 - w + current, epsilon * (v + a - b * w)])

    return ODEModel(
        rhs=rhs,
        initial_state=[-1.0, 1.0 / 3.0],
        t_span=(float(times[0]), float(times[-1])),
        observation_times=times,
    )
