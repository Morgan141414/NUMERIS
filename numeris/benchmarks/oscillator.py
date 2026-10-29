"""Small deterministic benchmark model."""

import numpy as np

from numeris.models.base import ODEModel


def damped_oscillator(times: np.ndarray | None = None) -> ODEModel:
    times = np.linspace(0.0, 20.0, 201) if times is None else np.asarray(times, dtype=float)

    def rhs(_t: float, x: np.ndarray, p: np.ndarray) -> np.ndarray:
        omega, damping, forcing = p
        return np.array([x[1], -omega * omega * x[0] - damping * x[1] + forcing])

    return ODEModel(rhs=rhs, initial_state=[1.0, 0.0], t_span=(float(times[0]), float(times[-1])),
                    observation_times=times)
