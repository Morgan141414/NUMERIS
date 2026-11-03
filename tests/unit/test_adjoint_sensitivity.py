import numpy as np

from numeris.controller import (
    DampedOscillatorParameters,
    estimate_damped_oscillator_sensitivity,
)


def _inputs():
    times = np.linspace(0.0, 4.0, 41)
    params = DampedOscillatorParameters(zeta=0.1, omega=1.2, amplitude=0.3, nu=0.7)
    trajectory = np.column_stack((np.cos(times), -np.sin(times)))
    return times, trajectory, params


def test_analytic_adjoint_returns_explicit_unverified_result():
    times, trajectory, params = _inputs()

    result = estimate_damped_oscillator_sensitivity(
        times, trajectory, params, observation=0.2, sigma=0.1
    )

    assert result.status == "UNVERIFIED"
    assert "unverified" in result.message
    assert result.jacobian_mode == "analytic"
    assert result.adjoint.shape == (times.size, 2)
    assert result.parameter_sensitivity.shape == (4,)
    assert np.all(np.isfinite(result.parameter_sensitivity))


def test_finite_difference_and_analytic_jacobians_agree_for_target_sensitivity():
    times, trajectory, params = _inputs()
    analytic = estimate_damped_oscillator_sensitivity(
        times, trajectory, params, observation=0.2, sigma=0.1,
        jacobian_mode="analytic",
    )
    finite_difference = estimate_damped_oscillator_sensitivity(
        times, trajectory, params, observation=0.2, sigma=0.1,
        jacobian_mode="finite_difference",
    )

    assert finite_difference.status == "UNVERIFIED"
    np.testing.assert_allclose(
        finite_difference.initial_state_sensitivity,
        analytic.initial_state_sensitivity,
        rtol=1e-5,
        atol=1e-7,
    )
    np.testing.assert_allclose(
        finite_difference.parameter_sensitivity,
        analytic.parameter_sensitivity,
        rtol=1e-5,
        atol=1e-7,
    )


def test_invalid_inputs_return_failure_without_claiming_reliability():
    times, trajectory, params = _inputs()

    result = estimate_damped_oscillator_sensitivity(
        times[::-1], trajectory, params, observation=0.2, sigma=0.1
    )

    assert result.status == "FAILURE"
    assert "strictly increasing" in result.message
    assert result.adjoint.size == 0


def test_invalid_sigma_and_mode_are_reported_as_failure():
    times, trajectory, params = _inputs()

    bad_sigma = estimate_damped_oscillator_sensitivity(
        times, trajectory, params, observation=0.2, sigma=0.0
    )
    bad_mode = estimate_damped_oscillator_sensitivity(
        times, trajectory, params, observation=0.2, sigma=0.1,
        jacobian_mode="unsupported",  # type: ignore[arg-type]
    )

    assert bad_sigma.status == "FAILURE"
    assert bad_mode.status == "FAILURE"
