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

    def x0(self) -> np.ndarray:
        return np.asarray(self.initial_state, dtype=float)
