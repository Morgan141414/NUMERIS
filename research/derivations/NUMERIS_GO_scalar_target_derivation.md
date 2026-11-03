# Scalar-target NUMERIS-GO derivation

Status: derivation for a restricted candidate, not a novelty claim.

## 1. Target perturbation

For a terminal scalar observation `z = h(x(T))`, define

```text
J(x(T)) = (h(x(T)) - y)^2 / (2 sigma^2),   sigma > 0.
```

Let `x_hat(T) = x(T) + delta x` and let
`r = h(x(T)) - y`. If `h` is differentiable, the first-order perturbation is

```text
delta J = (r / sigma^2) * grad h(x(T))^T delta x + O(||delta x||^2).
```

For a linear observation `h(x) = H x`, the exact expansion is

```text
J(x + delta x) - J(x)
  = (r / sigma^2) H delta x
    + (H delta x)^2 / (2 sigma^2).
```

Using `|H delta x| <= ||H|| ||delta x||` gives

```text
|delta J|
  <= |r| ||H|| ||delta x|| / sigma^2
     + ||H||^2 ||delta x||^2 / (2 sigma^2).
```

For a nonlinear `h`, replace `||H||` by a valid Lipschitz constant `K_h` on
the trajectory tube. This reproduces the known Gaussian target perturbation
bound; it does not estimate the state error by itself.

## 2. Adjoint sensitivity

Let `v(t)` be a first-order state perturbation satisfying the variational
equation

```text
v'(t) = f_x(t, x(t); theta) v(t).
```

Define the terminal adjoint

```text
lambda(T) = (r / sigma^2) grad h(x(T)),
lambda'(t) = -f_x(t, x(t); theta)^T lambda(t).
```

Then integration by parts gives

```text
grad h(x(T))^T v(T) * r / sigma^2
  = lambda(t_i)^T v(t_i)
```

for every intermediate time `t_i`, subject to consistent forward and backward
linearized dynamics. Therefore the first-order target effect of a perturbation
at `t_i` is represented by `lambda(t_i)^T v(t_i)`.

For a numerical one-step defect `d_i` represented at `t_{i+1}`, the practical
indicator is

```text
eta_i = |lambda(t_{i+1})^T d_i|.
```

This is a first-order sensitivity indicator. It becomes a reliable bound only
after additional remainder and defect-propagation bounds are supplied; this
document supplies neither.

## 3. From indicators to budget decisions

Let `r_i` denote a candidate refinement of interval `i`. Suppose a diagnostic
model predicts proxy reduction `Delta_i` and cost `c_i`. The proposed decision
score is

```text
score_i = Delta_i / c_i.
```

Choosing the largest score is a greedy heuristic for a finite budget. It is not
an optimal allocation theorem because the reductions are generally coupled:
refining one interval changes the trajectory, adjoint, and indicators in other
intervals.

The prototype must recompute all quantities after each accepted refinement and
must record the predicted and realised reductions. The difference between them
is itself a calibration diagnostic.

## 4. Conditional reliability statement

If an independent method supplies a true terminal state-error bound `e_x`, then
the target bound is

```text
U_J(e_x) = |r_hat| K_h e_x / sigma^2
            + (K_h e_x)^2 / (2 sigma^2),
```

where `r_hat = h(x_hat(T)) - y`. The candidate's local-indicator proxy is not
allowed to inherit this theorem automatically. The implementation must keep
the fields `bound_source`, `proxy_source`, and `calibration_status` separate.

## 5. Claims permitted after the first prototype

Permitted if directly measured:

- the proxy's empirical calibration on the declared oscillator cases;
- the paired target-error difference under the frozen budget;
- failure modes and the range in which the heuristic behaves usefully.

Not permitted from this derivation alone:

- “new method”;
- “globally optimal allocation”;
- “convergent NUMERIS-GO solver”;
- “reliable posterior or parameter inference”;
- superiority on nonlinear, chaotic, or stiff systems;
- any publication claim.
