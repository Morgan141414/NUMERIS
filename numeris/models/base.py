"""Core model contracts."""

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


RHS = Callable[[float, np.ndarray, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class ODEModel:
    """Parameterized ODE with a deterministic observation function."""

    rhs: RHS
    initial_state: Sequence[float]
    t_span: tuple[float, float]
    observation_times: np.ndarray
    observe: Callable[[np.ndarray], np.ndarray] = lambda state: state

    def __post_init__(self) -> None:
        state = np.asarray(self.initial_state, dtype=float)
        times = np.asarray(self.observation_times, dtype=float)
        if state.ndim != 1 or state.size == 0 or not np.all(np.isfinite(state)):
            raise ValueError("initial_state must be a finite, non-empty 1-D vector")
        if times.ndim != 1 or times.size < 2 or not np.all(np.isfinite(times)):
            raise ValueError("observation_times must be a finite 1-D vector with at least two points")
        if np.any(np.diff(times) <= 0):
            raise ValueError("observation_times must be strictly increasing")
        if self.t_span != (float(times[0]), float(times[-1])):
            raise ValueError("t_span must match the first and last observation times")

    def x0(self) -> np.ndarray:
        return np.asarray(self.initial_state, dtype=float)
