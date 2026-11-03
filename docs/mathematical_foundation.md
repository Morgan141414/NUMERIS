# Mathematical foundation (working note)

The first NUMERIS-GO candidate is intentionally restricted to one scalar
terminal Gaussian negative log-likelihood target for a smooth ODE. Its formal
specification is in
[`research/mathematical_notes/NUMERIS_GO_MINIMAL_SPEC.md`](../research/mathematical_notes/NUMERIS_GO_MINIMAL_SPEC.md),
and the derivation is in
[`research/derivations/NUMERIS_GO_scalar_target_derivation.md`](../research/derivations/NUMERIS_GO_scalar_target_derivation.md).

For a parameterized ODE `x' = f(t, x, theta)`, the research problem is to
estimate the target-relevant part of the numerical state error, quantify the
cost of reducing it, and choose refinements under `C(A) <= B`. The minimal
target is

```text
J(x(T)) = (h(x(T)) - y)^2 / (2 sigma^2).
```

The adjoint-weighted defect is a sensitivity heuristic. The scalar quadratic
perturbation bound is conditional on an independently valid state-error bound.
The proposed greedy allocation and stopping rules are not proven optimal or
reliable. The first falsifiable prototype therefore tests one smooth damped
oscillator against a matched standard solver under an equal RHS-evaluation
budget.

This stage does not establish a new method, convergence, superiority, or
publication readiness. Any stronger claim requires the baseline comparison,
calibration, and mathematical analysis specified in the research documents.
