# Mathematical foundation (working note)

For a parameterized ODE `x' = f(t, x, theta)`, let `G(x, theta)` be a declared scientific target. A first-order perturbation model is

`delta G ≈ G_x delta x + G_theta delta theta`.

The controller research problem is to estimate the target-relevant part of `delta x`, quantify the cost of reducing it, and choose refinements under `C(A) <= B`. This local linearization is an analysis starting point, not a theorem for the nonlinear inference pipeline. Any eventual guarantee must state smoothness, stability, observation, and optimization assumptions explicitly.
