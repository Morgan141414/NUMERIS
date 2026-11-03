# NUMERIS-GO minimal mathematical specification

Status: research candidate for Phase II. This document is deliberately narrower
than the project vision. It defines one scalar Gaussian likelihood target on a
restricted smooth ODE class so that the first mathematical prototype can be
falsified. It does not establish novelty, convergence of a new solver, or
superiority over existing methods.

## 1. Restricted problem class

Let `x(t) in R^d` solve

```text
x'(t) = f(t, x(t); theta),       t in [0, T],
x(0) = x0(theta).
```

For this candidate, `theta` is fixed during one numerical-control episode.
Parameter estimation is deliberately outside the first theorem; it can be
added later by repeating the episode over a parameter grid.

Assume:

1. `f` is continuous in `t` and twice continuously differentiable in `x` on a
   tube containing the exact and numerical trajectories.
2. `f_x` is bounded on that tube: `||f_x(t, x; theta)|| <= L_f`.
3. The solution exists uniquely on `[0, T]` and remains inside the tube.
4. A scalar observation is made at the terminal time:

   ```text
   z = h(x(T)),       y = observed scalar,
   ```

   where `h: R^d -> R` is continuously differentiable and
   `||grad h(x)|| <= K_h` on the same tube.
5. The observation noise is Gaussian with known `sigma > 0`.

The first target omits the additive Gaussian constant:

```text
J(x(T)) = (h(x(T)) - y)^2 / (2 sigma^2).
```

This is one scalar negative log-likelihood value, not a posterior and not a
parameter estimate.

## 2. Required inputs and outputs

### Inputs

- ODE right-hand side `f`, initial state `x0`, interval `[0, T]`;
- fixed parameter value `theta`;
- observation `y`, observation map `h`, and `sigma > 0`;
- a partition `I_i = [t_i, t_{i+1}]`;
- a solver configuration and a finite budget `B`;
- a declared target tolerance `tau_J > 0`;
- either a trustworthy state-error proxy or a local defect proxy;
- a sensitivity source, as defined below.

### Outputs

The candidate controller returns:

- a numerical trajectory and target value `J_hat`;
- an estimated target error `E_hat_J`;
- the accepted local refinements `R`;
- spent and remaining budget;
- a stopping reason;
- diagnostic flags for violated assumptions or unavailable sensitivity.

The controller must return `UNVERIFIED` when it cannot construct the declared
proxy. It must not silently replace a missing estimate with a claim of
reliability.

## 3. Sensitivity source

For a terminal scalar target, the continuous adjoint is the most compact
sensitivity source. Along a sufficiently smooth reference trajectory `x`, set

```text
q = (h(x(T)) - y) / sigma^2,
lambda'(t) = - f_x(t, x(t); theta)^T lambda(t),
lambda(T) = q * grad h(x(T)).
```

For a local state perturbation `delta x_i` at time `t_i`, the first-order target
perturbation is approximated by

```text
delta J_i ~= lambda(t_i)^T delta x_i.
```

For a one-step defect `d_i` represented at the end of interval `I_i`, define
the sensitivity-weighted local indicator

```text
eta_i = |lambda(t_{i+1})^T d_i|.
```

If the implementation instead uses step-doubling, `d_i` is replaced by the
fine/coarse state difference transported to the interval endpoint. The source
of `d_i` must be recorded. A finite-difference or step-doubling indicator is a
diagnostic proxy, not an exact local truncation error.

The adjoint equation and the indicator are standard sensitivity constructions;
their use here is not claimed to be novel.

## 4. Error proxy for the scalar likelihood target

Let `e_x` be an independently justified bound on the terminal state error:

```text
||x_hat(T) - x(T)|| <= e_x.
```

Let `r_hat = h(x_hat(T)) - y`. By the Lipschitz assumption on `h`, the
observation perturbation is at most `K_h e_x`. Therefore the exact target
perturbation satisfies

```text
|J(x_hat(T)) - J(x(T))|
  <= |r_hat| K_h e_x / sigma^2
     + (K_h e_x)^2 / (2 sigma^2).
```

Call the right-hand side `U_J(e_x)`. This is a deterministic perturbation
bound conditional on the state-error bound and the stated smoothness
assumptions. It is the only theorem-level reliability statement in this
minimal candidate.

The controller may construct a heuristic proxy from local indicators:

```text
e_x,proxy = sum_i a_i * eta_i,
E_hat_J = U_J(e_x,proxy),
```

where `a_i >= 0` are transport or accumulation weights. Unless an independent
argument proves that these weights bound the actual state error, `E_hat_J` is
only a heuristic estimate. Calibration against an independently tightened
reference is mandatory before calling it reliable.

## 5. Budget allocation rule (heuristic)

At each decision point, a candidate refinement `r_i` for interval `I_i` has:

- predicted reduction `Delta_i >= 0` in the target-error proxy;
- predicted cost `c_i > 0`, measured in RHS evaluations or another frozen cost;
- admissibility under the remaining budget.

The minimal greedy rule is

```text
i* = argmax_i Delta_i / c_i,
```

followed by refinement of `I_i*` if its ratio is above a declared threshold
`rho_min`. After refinement, recompute the trajectory, sensitivities, local
indicators, and candidate ratios. Do not reuse stale indicators across a
nonlinear solver restart without recording that approximation.

This rule is a transparent budget-allocation heuristic. It is not asserted to
be globally optimal, and it is not asserted to improve on adaptive RK,
adjoint-based control, or probabilistic ODE methods.

## 6. Stopping rule (heuristic with a conditional certificate)

Stop with `TARGET_TOLERANCE_REACHED` when all of the following hold:

1. the proxy satisfies `E_hat_J <= tau_J`;
2. the remaining budget is nonnegative;
3. the current sensitivity and defect diagnostics are finite;
4. no declared assumption-violation flag is active.

Stop with `MARGINAL_GAIN_TOO_SMALL` when `max_i Delta_i / c_i < rho_min`.
Stop with `BUDGET_EXHAUSTED` when no admissible refinement remains. Stop with
`UNVERIFIED` whenever the proxy or its sensitivity source is unavailable or
fails calibration checks.

The label `TARGET_TOLERANCE_REACHED` is a conditional certificate about the
proxy. It is not a guarantee about the true target error unless `e_x` is an
independently valid bound. The stopping rule is therefore heuristic in the
planned prototype.

## 7. What is theorem-level and what is not

### Conditional theorem-level statement

Under assumptions 1--5, if a valid terminal state-error bound `e_x` is supplied,
then `U_J(e_x)` bounds the absolute error in the scalar Gaussian target. This is
the quadratic expansion and Cauchy--Schwarz argument in
`research/derivations/gaussian_target_bound.md`.

### Heuristic statements

- adjoint-weighted defects identify the intervals most relevant to `J`;
- the greedy `Delta_i / c_i` rule uses the budget efficiently;
- the proxy decreases predictably after refinement;
- the stopping labels correlate with actual target reliability;
- the method is better than a standard solver at equal cost.

Each heuristic requires an experiment. None is a mathematical conclusion of
this document.

## 8. Failure conditions

The minimal candidate must report failure or `UNVERIFIED` for any of these
conditions:

- `sigma <= 0`, non-finite observations, or non-finite target;
- solver failure, rejected steps, overflow, or trajectory leaving the declared
  smoothness tube;
- unavailable or ill-conditioned `f_x`/adjoint integration;
- a stiffness regime in which the restricted assumptions or chosen solver are
  not appropriate;
- discontinuous, nonsmooth, event-driven, or non-Lipschitz `f` or `h`;
- local indicator cancellation or a proxy that is not calibrated against an
  independent reference;
- a remaining budget too small for the initial solve or any admissible
  refinement;
- an inference objective that is not the declared scalar terminal Gaussian
  target.

Failure is a valid result. The controller must not convert failure into a
positive reliability claim.

## 9. Falsifiable minimal prototype

### Model

Use the smooth damped oscillator

```text
x1' = x2
x2' = -2 zeta omega x2 - omega^2 x1 + A cos(nu t),
```

with fixed positive `zeta`, `omega`, `A`, and `nu`, and a fixed initial state.
Use `T = 10`, `h(x) = x1`, one synthetic observation `y` generated from an
independently tightened reference plus fixed Gaussian noise, and fixed
`sigma`. The first prototype must keep the parameters fixed; it tests numerical
target control, not parameter inference.

### Compared policies

1. **Standard baseline:** the selected SciPy adaptive solver with the frozen
   global tolerance and no target-weighted allocation.
2. **NUMERIS-GO candidate:** the same solver family and initial tolerance,
   with the adjoint/defect proxy, greedy allocation, and stopping rule above.

Both policies receive the same RHS-evaluation budget and the same initial
partition. The reference target is computed independently using at least two
solver families and a documented convergence check.

### Primary endpoint

For each frozen seed and budget, record

```text
absolute target error = |J_hat - J_reference|
```

and RHS evaluations. Report paired differences
`error_NUMERIS-GO - error_baseline`, with confidence intervals only after the
predeclared repetitions have been executed.

### Falsification criteria

The candidate fails this minimal test if any of the following occurs:

- it cannot reach the same or lower target error than the baseline at the same
  budget on the predeclared oscillator cases;
- its proxy is systematically overconfident against the independent reference;
- it violates the budget or silently changes solver family/tolerances;
- the advantage disappears under a predeclared change of phase, observation,
  noise, or initial condition;
- its extra sensitivity cost removes any target-error benefit;
- it is indistinguishable from the baseline and has no separately justified
  mathematical distinction.

Passing this one-model prototype would only justify a larger experiment. It
would not establish novelty, generality, superiority, or publication readiness.
