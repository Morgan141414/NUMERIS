# Baseline derivation: Gaussian NLL target perturbation

This is a known baseline derivation for Phase II, not a claim of novelty.

For an observation vector `y`, predicted observation `z`, and isotropic Gaussian noise `sigma`, omit the constant term and write

`L(z) = ||z - y||^2 / (2 sigma^2)`.

Let the numerical perturbation be `delta z`, with `||delta z|| <= e`. Expanding the quadratic gives

`L(z + delta z) - L(z) = ((z-y)^T delta z)/sigma^2 + ||delta z||^2/(2 sigma^2)`.

By Cauchy–Schwarz,

`|delta L| <= ||z-y|| e / sigma^2 + e^2/(2 sigma^2)`.

If the observation map `g(x)` is Lipschitz with constant `K`, then `e <= K ||delta x||`. The implementation in `numeris/error_analysis/gaussian_bound.py` evaluates this expression.

## Assumptions and limits

- Gaussian isotropic observation noise with positive `sigma`;
- a valid residual norm and state-error bound;
- a valid observation Lipschitz constant;
- this bounds NLL perturbation only, not parameter RMSE, posterior distance, or optimizer error;
- it is not an adjoint estimator and does not allocate solver steps automatically.

The next mathematical task is to test how conservative this bound is and whether its marginal-benefit signal can support a non-equivalent budget policy.
