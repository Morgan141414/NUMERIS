"""Thin, instrumented interface over scipy.integrate.solve_ivp."""

from dataclasses import dataclass
from time import perf_counter

import numpy as np
from scipy.integrate import solve_ivp

from numeris.models.base import ODEModel


@dataclass(frozen=True)
class SolveResult:
    times: np.ndarray
    states: np.ndarray
    method: str
    rtol: float
    atol: float
    nfev: int
    runtime_s: float
    success: bool
    message: str


def solve_ode(model: ODEModel, params: np.ndarray, *, method="DOP853", rtol=1e-8,
              atol=1e-10, max_step=np.inf) -> SolveResult:
    start = perf_counter()
    result = solve_ivp(
        lambda t, x: model.rhs(t, x, np.asarray(params, dtype=float)),
        model.t_span, model.x0(), t_eval=np.asarray(model.observation_times),
        method=method, rtol=rtol, atol=atol, max_step=max_step,
    )
    return SolveResult(
        times=result.t, states=result.y.T, method=method, rtol=rtol, atol=atol,
        nfev=result.nfev, runtime_s=perf_counter() - start,
        success=bool(result.success), message=result.message,
    )
