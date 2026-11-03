# NUMERIS Minimal Scientific Prototype v0.1

Status: **FROZEN — SPECIFICATION ONLY**  
Frozen on: 2026-11-03 (Asia/Almaty)  
Scope: one-model, one-target, matched-budget comparison  
Results: **none produced by this specification**

This document is a predeclared experiment specification. It is not an implementation, a result report, or evidence of novelty, reliability, or superiority. Any executed run must record this file path, its commit hash, and the exact software environment. A changed value requires a new versioned specification; this file must not be overwritten.

## 1. Research question

For the damped oscillator parameter-recovery task below, can a candidate goal-oriented accuracy policy reduce the error of the final parameter estimate at the same RHS-evaluation budget as a strong standard adaptive solver configuration?

The question is deliberately narrow. A null result, a mixed result, or a result favouring the baseline is valid and must be retained.

## 2. Model and observations

The model is the first-order system

```text
dx1/dt = x2
dx2/dt = -2*zeta*omega*x2 - omega^2*x1 + forcing*cos(omega*t)
```

with

```text
x(0) = [1.0, 0.0]
t in [0, 20]
theta = [omega, zeta, forcing]
theta_true = [1.0, 0.1, 0.2]
```

Observations are taken at `t_obs = linspace(0, 20, 201)` from the first state component:

```text
y_i = x1(t_i; theta_true) + epsilon_i
epsilon_i ~ Normal(0, sigma^2)
sigma = 0.05
```

The ten predeclared NumPy `default_rng` seeds are:

```text
0, 1, 2, 3, 4, 5, 6, 7, 8, 9
```

For each seed, one observation vector is generated once and reused verbatim by both arms. The true parameter vector is used to generate observations and the reference solution only; it is not supplied to the estimator.

## 3. Scientific target and estimator

The sole scientific target is parameter recovery. For each arm and seed, estimate `theta` by bounded Gaussian maximum likelihood using the same parameter box:

```text
0.5 <= omega <= 1.5
0.02 <= zeta <= 0.30
0.0 <= forcing <= 0.5
```

The optimizer, initial points, termination tolerances, and maximum optimizer evaluations must be identical between arms and declared in the executable run record before execution. The required initial point set is:

```text
[1.0, 0.1, 0.2]
[0.8, 0.05, 0.1]
[1.2, 0.2, 0.3]
```

The selected estimate is the feasible point with the lowest reported negative log-likelihood across these starts. If any start or the final selection fails, the seed is retained as a failed case; it is not silently replaced.

Primary metric:

```text
parameter_RMSE = sqrt(mean((theta_hat - theta_true)^2))
```

Secondary metrics:

- negative-log-likelihood at `theta_hat`;
- absolute likelihood distortion relative to the declared reference trajectory;
- RHS evaluations;
- runtime and peak RSS, reported descriptively only;
- failure and budget-violation status.

No posterior, MCMC, false-optimum, or publication claim belongs to this minimal prototype.

## 4. Compared arms

### Arm A — candidate NUMERIS-GO policy

Candidate policy name: `NUMERIS-GO-candidate-v0.1`.

The policy must allocate accuracy using a declared goal-oriented signal for the parameter-recovery target. Before execution, its implementation record must specify:

1. how the sensitivity of the target to trajectory perturbations is obtained;
2. how local numerical-error information is converted into a predicted target impact;
3. how the policy chooses refinement or tolerance changes;
4. the deterministic tie-breaking rule;
5. the stopping rule;
6. the maximum number of policy decisions.

The candidate is not allowed to use the true parameters, reference results, or observations generated with a different arm while making accuracy decisions. It may use the current model, current observations, current numerical diagnostics, and the remaining budget.

If this implementation contract cannot be satisfied, Arm A is `NOT-IMPLEMENTED`; the experiment must not relabel a heuristic or post-hoc tolerance sweep as NUMERIS-GO evidence.

### Arm B — strong standard baseline

Baseline: SciPy `DOP853` with its standard embedded adaptive local-error controller, using the same model, observations, parameter bounds, optimizer, and hard RHS budget.

The baseline's solver settings are fixed before execution:

```text
method = DOP853
rtol = 1e-8
atol = 1e-10
max_step = infinity
```

The baseline may reject a trial when its hard budget is exceeded, but may not receive extra evaluations. The baseline is a strong standard deterministic reference for this small non-stiff model; this statement does not imply that it is optimal.

## 5. Matched computational budget

Each arm receives an independent hard cap of **2,000 RHS evaluations per seed**, including all forward solves used by its parameter-estimation procedure. Reference calculations and pre-experiment validation are not charged to an arm, but cannot be used by an arm during decisions.

The comparison is valid only if the accounting definition is identical:

- count every RHS call made by every solver invocation in the arm;
- count failed solver calls up to their termination;
- do not count reference runs in either arm;
- mark `over_budget` before launching a run when the remaining cap is insufficient;
- retain `failure`, `over_budget`, and `not_started` cases in denominators;
- do not rerun a failed seed with a larger budget.

The candidate and baseline are paired by seed and observation vector. A run is not considered budget-matched if one arm receives a larger cap or if the accounting instrumentation differs.

## 6. Reference trajectory

The reference is generated independently with `DOP853`, `rtol=1e-12`, `atol=1e-14`, and `max_step=infinity`. It must pass:

1. a tighter comparison at `rtol=1e-13`, `atol=1e-15`;
2. an independent-family comparison using `Radau` at `rtol=1e-12`, `atol=1e-14`.

If either check fails, the prototype status is `REFERENCE-UNRESOLVED` and no inference comparison is interpreted as evidence. The reference is never used by either arm while selecting solver accuracy.

## 7. Predeclared analysis

The estimand is the paired difference over seeds:

```text
delta_RMSE = RMSE(candidate) - RMSE(baseline)
```

Smaller is better. Compute the mean paired difference and a two-sided percentile bootstrap 95% confidence interval using 10,000 resamples of the ten paired seed differences, with bootstrap seed `20261103`. The bootstrap is descriptive uncertainty quantification; it does not compensate for a small number of seeds or failed pairs.

The likelihood-distortion and resource metrics are reported separately and must not be collapsed into an undisclosed score. A failed or non-paired seed is shown explicitly. The primary RMSE comparison is not promoted to a superiority result if fewer than eight of ten seed pairs complete under the declared budget.

## 8. Failure rules and negative-result interpretation

The run is `INVALID-PROTOCOL` if any of the following occurs:

- observations, seeds, model parameters, optimizer starts, or budget differ between arms;
- an arm reads the reference trajectory or the other arm's result during decisions;
- the candidate implementation contract is incomplete;
- the budget counter is missing or inconsistent;
- the specification is changed after inspecting results without a new version.

Use these result labels:

- `REFERENCE-UNRESOLVED`: reference checks failed;
- `NOT-IMPLEMENTED`: candidate policy contract not executable;
- `BUDGET-INCOMPLETE`: fewer than eight paired seeds complete;
- `NO_CONFIRMED_ADVANTAGE`: candidate does not meet the positive rule below;
- `MIXED_RESULT`: one primary/secondary direction improves while another worsens;
- `CANDIDATE-WORSE`: candidate RMSE is worse and the bootstrap interval excludes zero on the worse side;
- `CANDIDATE-BETTER-PRELIMINARY`: candidate RMSE is lower with a bootstrap interval excluding zero, all validity conditions pass, and the result is explicitly limited to this oscillator protocol.

The last label is not a claim of general superiority, novelty, or publication readiness. If the confidence interval includes zero, report `NO_CONFIRMED_ADVANTAGE`, regardless of the point estimate.

## 9. Positive decision rule

The candidate may receive `CANDIDATE-BETTER-PRELIMINARY` only if all conditions hold:

1. reference status is resolved;
2. candidate policy contract is complete and executable;
3. at least 8/10 paired seeds complete within the cap;
4. mean `delta_RMSE` is negative;
5. the two-sided 95% bootstrap interval for `delta_RMSE` excludes zero;
6. candidate failure and budget-violation rates are not more than 5 percentage points above baseline;
7. no protocol invalidation occurred.

Otherwise the result is `NO_CONFIRMED_ADVANTAGE`, `MIXED_RESULT`, or a failure label above. No result from this protocol alone can close the NUMERIS research gap or justify a claim beyond the declared oscillator setting.

## 10. Required run artifacts

An executed run must create, outside this specification file:

- the exact commit hash and environment metadata;
- a copy or immutable reference to this manifest;
- arm configurations and implementation contract;
- per-seed observations metadata and paired statuses;
- solver/RHS accounting;
- parameter estimates and primary metrics;
- bootstrap configuration and output;
- failures, over-budget, and not-started cases;
- a machine-readable summary and a human-readable report.

Until these artifacts exist, this document must be described as **specification only** and not as experimental evidence.

