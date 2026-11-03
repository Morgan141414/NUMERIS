"""Experimental adjoint sensitivity utility for the oscillator candidate.

This module is intentionally separate from the refinement policies.  It is a
small numerical instrument for the frozen minimal prototype, not a validated
NUMERIS-GO controller and not a novelty claim.
"""

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.integrate import solve_ivp


AdjointStatus = Literal["UNVERIFIED", "FAILURE"]


@dataclass(frozen=True)
class DampedOscillatorParameters:
    """Parameters of the smooth candidate oscillator.

    The state equation is ``x1'=x2`` and
    ``x2'=-2*zeta*omega*x2 - omega**2*x1 + amplitude*cos(nu*t)``.
    """

    zeta: float
    omega: float
    amplitude: float
    nu: float


@dataclass(frozen=True)
class AdjointSensitivityResult:
    """Declared output of :func:`estimate_damped_oscillator_sensitivity`.

    ``status`` is deliberately ``UNVERIFIED`` for every successful result:
    the helper has no reliability or convergence validation attached to it.
    ``initial_state_sensitivity`` is the adjoint at the initial time and
    ``parameter_sensitivity`` is a quadrature estimate for the four declared
    oscillator parameters.
    """

    status: AdjointStatus
    message: str
    jacobian_mode: str
    target_value: float | None
    target_error: float | None
    initial_state_sensitivity: np.ndarray
    parameter_sensitivity: np.ndarray
    adjoint: np.ndarray


def _failure(message: str, jacobian_mode: str) -> AdjointSensitivityResult:
    return AdjointSensitivityResult(
        status="FAILURE",
        message=message,
        jacobian_mode=jacobian_mode,
        target_value=None,
        target_error=None,
        initial_state_sensitivity=np.empty(0, dtype=float),
        parameter_sensitivity=np.empty(0, dtype=float),
        adjoint=np.empty((0, 2), dtype=float),
    )


def _rhs(t: float, state: np.ndarray, params: DampedOscillatorParameters) -> np.ndarray:
    x1, x2 = state
    return np.array(
        [x2, -2.0 * params.zeta * params.omega * x2 - params.omega**2 * x1
         + params.amplitude * np.cos(params.nu * t)],
        dtype=float,
    )


def _analytic_jacobian(params: DampedOscillatorParameters) -> np.ndarray:
    return np.array(
        [[0.0, 1.0], [-(params.omega**2), -2.0 * params.zeta * params.omega]],
        dtype=float,
    )


def _finite_difference_jacobian(
    t: float,
    state: np.ndarray,
    params: DampedOscillatorParameters,
    step: float,
) -> np.ndarray:
    jacobian = np.empty((2, 2), dtype=float)
    for column in range(2):
        delta = np.zeros(2, dtype=float)
        delta[column] = step
        jacobian[:, column] = (
            _rhs(t, state + delta, params) - _rhs(t, state - delta, params)
        ) / (2.0 * step)
    return jacobian


def estimate_damped_oscillator_sensitivity(
    times: np.ndarray,
    trajectory: np.ndarray,
    params: DampedOscillatorParameters,
    observation: float,
    sigma: float,
    *,
    jacobian_mode: Literal["analytic", "finite_difference"] = "analytic",
    finite_difference_step: float = 1e-6,
    rtol: float = 1e-9,
    atol: float = 1e-11,
) -> AdjointSensitivityResult:
    """Estimate sensitivity of a terminal Gaussian target for the oscillator.

    Inputs are the strictly increasing time grid, a state trajectory with
    shape ``(len(times), 2)``, oscillator parameters, one terminal
    observation, and its positive Gaussian scale.  The target is
    ``0.5*((x1(T)-observation)/sigma)**2``.  The returned adjoint solves the
    continuous backward linearized equation on the supplied trajectory and
    includes a trapezoidal parameter-gradient estimate.

    This is an experimental diagnostic.  A successful calculation is marked
    ``UNVERIFIED`` because no convergence, calibration, or reliability claim
    is made by this function.
    """

    mode = str(jacobian_mode)
    try:
        t = np.asarray(times, dtype=float)
        x = np.asarray(trajectory, dtype=float)
        if mode not in {"analytic", "finite_difference"}:
            return _failure("unknown jacobian_mode", mode)
        if t.ndim != 1 or t.size < 2 or not np.all(np.isfinite(t)):
            return _failure("times must be a finite one-dimensional grid", mode)
        if not np.all(np.diff(t) > 0.0):
            return _failure("times must be strictly increasing", mode)
        if x.shape != (t.size, 2) or not np.all(np.isfinite(x)):
            return _failure("trajectory must have shape (len(times), 2)", mode)
        if not np.isfinite(observation) or not np.isfinite(sigma) or sigma <= 0.0:
            return _failure("observation must be finite and sigma must be positive", mode)
        if finite_difference_step <= 0.0 or not np.isfinite(finite_difference_step):
            return _failure("finite_difference_step must be finite and positive", mode)
        if rtol <= 0.0 or atol <= 0.0:
            return _failure("rtol and atol must be positive", mode)
        if not all(np.isfinite(value) for value in vars(params).values()):
            return _failure("oscillator parameters must be finite", mode)
        if params.omega <= 0.0 or params.zeta < 0.0:
            return _failure("omega must be positive and zeta non-negative", mode)

        target_error = float((x[-1, 0] - observation) / sigma)
        terminal_adjoint = np.array([target_error / sigma, 0.0], dtype=float)

        def adjoint_rhs(time: float, adjoint: np.ndarray) -> np.ndarray:
            index = int(np.argmin(np.abs(t - time)))
            state_jacobian = (
                _analytic_jacobian(params)
                if mode == "analytic"
                else _finite_difference_jacobian(
                    time, x[index], params, finite_difference_step
                )
            )
            return -(state_jacobian.T @ adjoint)

        solution = solve_ivp(
            adjoint_rhs,
            (float(t[-1]), float(t[0])),
            terminal_adjoint,
            t_eval=t[::-1],
            rtol=rtol,
            atol=atol,
        )
        if not solution.success or solution.y.shape != (2, t.size):
            return _failure(f"adjoint integration failed: {solution.message}", mode)
        adjoint = solution.y.T[::-1]
        parameter_partials = np.column_stack(
            [
                np.zeros(t.size),
                -2.0 * params.omega * x[:, 1],
                -2.0 * params.zeta * x[:, 1] - 2.0 * params.omega * x[:, 0],
                -params.amplitude * t * np.sin(params.nu * t),
            ]
        )
        parameter_sensitivity = np.trapezoid(
            adjoint[:, 1, None] * parameter_partials, t, axis=0
        )
        target_value = float(0.5 * target_error**2)
        if not np.all(np.isfinite(adjoint)) or not np.all(np.isfinite(parameter_sensitivity)):
            return _failure("non-finite adjoint sensitivity", mode)
        return AdjointSensitivityResult(
            status="UNVERIFIED",
            message="experimental estimate; convergence and reliability are unverified",
            jacobian_mode=mode,
            target_value=target_value,
            target_error=target_error,
            initial_state_sensitivity=adjoint[0].copy(),
            parameter_sensitivity=parameter_sensitivity,
            adjoint=adjoint,
        )
    except (TypeError, ValueError, FloatingPointError) as exc:
        return _failure(f"invalid sensitivity input: {exc}", mode)
