# Implementation Record — Minimal Frozen Oscillator Prototype v0.1

Status: **IMPLEMENTATION-INCOMPLETE — NO SCIENTIFIC EVIDENCE**  
Record date: 2026-11-06 (Asia/Almaty)  
Frozen specification: [`MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md`](MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md)  
Scope: exact damped-oscillator parameter-recovery prototype only

This record is an implementation ledger for the frozen protocol. It is not a
result report, a novelty statement, or evidence that NUMERIS-GO improves on a
baseline. A component is marked **implemented** only when its executable
behaviour, tests, and protocol compatibility are all demonstrated. Existing
diagnostic utilities and exploratory runners do not satisfy a missing gate by
themselves.

## 1. Current implementation snapshot

| Component | Current status | Evidence | Protocol consequence |
| --- | --- | --- | --- |
| Frozen specification | **IMPLEMENTED AS SPECIFICATION** | `research/protocol/MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md` | Defines the model, target, arms, budget, reference checks, analysis, and failure labels. It must not be overwritten after results inspection. |
| Exact protocol model | **NOT ACCEPTED** | The bounded runner contains an inline RHS matching the declared equations, but there is no separately accepted protocol model with a compatibility test. The general benchmark oscillator uses a different forcing/damping form. | No run may be called a valid frozen-protocol run until the exact model is isolated and tested. |
| `x1` observation | **PARTIAL / NOT ACCEPTED** | The bounded runner observes `states[:, 0]`; the general model interfaces support observations. | The observation map must be owned by the exact protocol model and tested to return only `x1` at the 201 declared times. |
| Multi-start bounded MLE | **PARTIAL / NOT ACCEPTED** | `scripts/run_minimal_oscillator.py` declares the three starts and bounds and uses L-BFGS-B, but its accounting is post-hoc and the run can exceed the cap during a solver call. | No parameter RMSE comparison is admissible until identical multi-start behaviour and hard per-arm accounting are validated. |
| Candidate controller | **NOT-IMPLEMENTED** | The runner explicitly returns `NOT-IMPLEMENTED`; `numeris/controller/adjoint_sensitivity.py` is an experimental sensitivity utility and not an end-to-end controller. | No candidate-versus-baseline inference result may be computed or relabelled as NUMERIS-GO evidence. |
| Reference validation | **NOT RESOLVED** | The runner creates a tight DOP853 setup reference, but does not yet produce an accepted record for the tighter DOP853 and independent Radau gates required by the frozen protocol. | Any inference comparison remains `REFERENCE-UNRESOLVED` until both checks pass and are recorded. |
| Paired campaign | **NOT RUN / NOT VALIDATED** | The bounded runner is exploratory, defaults to two seeds, and currently has no candidate arm. | There is no valid 10-seed matched-budget campaign and no scientific estimate of `delta_RMSE`. |
| Desktop UI | **OUT OF SCOPE FOR THIS GATE** | Native Tkinter wrapper exists separately. | UI availability does not satisfy any mathematical, budget, candidate, or validation gate. |

## 2. Required dependency chain

The frozen prototype has a strict dependency order. Later components cannot
be accepted by substituting a weaker or differently configured predecessor.

```text
exact protocol model
        |
        +--> x1 observation and synthetic data generation
        |           |
        |           +--> independent reference validation
        |           |
        |           +--> identical evaluator for both arms
        |                              |
        |                              +--> multi-start bounded MLE
        |                                             |
        |                    +------------------------+------------------------+
        |                    |                                                 |
        |             baseline arm                                      candidate arm
        |                    |                                                 |
        |                    +------------------------+------------------------+
        |                                             |
        +--> common hard RHS accounting and paired seed protocol
                                                      |
                                           primary metrics and bootstrap
                                                      |
                                              decision label / report
```

### 2.1 Exact model → `x1` observation

The accepted model must implement exactly:

```text
dx1/dt = x2
dx2/dt = -2*zeta*omega*x2 - omega^2*x1 + forcing*cos(omega*t)
x(0) = [1.0, 0.0]
t in [0, 20]
theta = [omega, zeta, forcing]
```

The accepted observation map is `y = x1(t)` at
`t_obs = linspace(0, 20, 201)`. It must not silently expose `x2`, use a
different forcing convention, or use a different time grid. Synthetic data
must be generated once per declared seed and reused verbatim by both arms.

### 2.2 Exact model and observation → common evaluator

The evaluator must use the same parameter bounds, Gaussian noise scale,
observation vector, solver output grid, objective definition, optimizer
settings, and three initial points for both arms. The true parameters may be
used only for data generation and the final reference metric, never by an arm
while selecting its estimate or accuracy.

### 2.3 Common evaluator → multi-start MLE

The accepted estimator is bounded Gaussian maximum likelihood from all three
predeclared starts:

```text
[1.0, 0.1, 0.2]
[0.8, 0.05, 0.1]
[1.2, 0.2, 0.3]
```

The selected estimate is the feasible completed start with the lowest
reported negative log-likelihood. Failed starts remain in the record. A
post-hoc tolerance sweep, a single-start fit, or an unbounded optimization is
not an implementation of this gate.

### 2.4 Multi-start MLE → candidate controller

The candidate controller must operate during the numerical computation and
must have a complete, deterministic contract for:

1. sensitivity of the parameter-recovery target to trajectory perturbations;
2. conversion of numerical diagnostics into predicted target impact;
3. refinement or tolerance action;
4. tie-breaking;
5. stopping;
6. maximum policy decisions.

An adjoint or sensitivity calculation by itself is not the controller. A
post-hoc comparison of tolerances is not the controller. A heuristic that
cannot expose this contract is `NOT-IMPLEMENTED`.

### 2.5 Both arms → reference validation and matched budget

Reference calculations are independent setup/validation work and are not
charged to either arm. Each arm nevertheless receives its own hard cap of
2,000 RHS evaluations per seed, with every RHS call from every estimation
solve counted. The accounting must prevent a new solver call when the
remaining cap is insufficient, or otherwise record the exact overrun and mark
the seed invalid for the matched comparison. The same accounting mechanism
must be used by baseline and candidate.

Reference acceptance requires all of the following:

- DOP853 at `rtol=1e-12`, `atol=1e-14`;
- tighter DOP853 comparison at `rtol=1e-13`, `atol=1e-15`;
- independent-family Radau comparison at `rtol=1e-12`, `atol=1e-14`;
- recorded tolerances, solver statuses, discrepancies, and acceptance result.

Until this record exists, the status is `REFERENCE-UNRESOLVED`.

## 3. Explicit acceptance gates

### Gate G0 — protocol identity

**Accept only if:** the executable run records the frozen specification path,
its commit hash, environment, model parameters, time grid, seeds, noise,
optimizer starts, bounds, solver settings, and budget before the comparison.

**Reject as:** `INVALID-PROTOCOL` if any declared input changes between arms
or changes after inspecting results without a new versioned specification.

### Gate G1 — exact model and observation

**Accept only if:** unit tests verify the two exact RHS equations, initial
state, interval, parameter ordering, 201-point grid, and `x1`-only
observation. The test must distinguish this model from the existing general
benchmark oscillator.

### Gate G2 — reference

**Accept only if:** both tighter DOP853 and independent-family Radau checks pass and
their machine-readable results are retained.

**Reject as:** `REFERENCE-UNRESOLVED`; do not interpret downstream metrics.

### Gate G3 — baseline estimator and accounting

**Accept only if:** the baseline uses DOP853 with the frozen settings, the
three identical bounded starts, common Gaussian likelihood, and a hard
per-seed RHS cap with no uncharged solver calls.

### Gate G4 — candidate contract

**Accept only if:** NUMERIS-GO-candidate-v0.1 is executable end-to-end and
records all six policy-contract elements in Section 2.4. It must not read the
reference, true parameters, or the other arm's result during decisions.

**Reject as:** `NOT-IMPLEMENTED`; do not replace it with an existing heuristic,
adjoint diagnostic, or tolerance sweep.

### Gate G5 — paired campaign

**Accept only if:** all ten predeclared seeds use paired observations,
identical estimator settings, independent arm budgets, retained failures and
over-budget cases, and at least eight pairs complete within budget for a
primary comparison.

### Gate G6 — predeclared analysis

**Accept only if:** the report contains parameter RMSE, paired
`candidate - baseline` differences, and the declared 10,000-resample
two-sided percentile bootstrap with seed `20261103`. Resource and
likelihood metrics remain separate and are not hidden in an undisclosed score.

### Gate G7 — decision label

The only permitted labels are those in the frozen specification:
`REFERENCE-UNRESOLVED`, `NOT-IMPLEMENTED`, `BUDGET-INCOMPLETE`,
`NO_CONFIRMED_ADVANTAGE`, `MIXED_RESULT`, `CANDIDATE-WORSE`, and
`CANDIDATE-BETTER-PRELIMINARY`. The positive label is permitted only when all
conditions in the frozen positive decision rule pass.

## 4. Current implementation blockers

1. The exact frozen oscillator must be separated from the general benchmark
   oscillator and covered by compatibility tests.
2. The `x1` observation contract must be explicit at the exact protocol
   boundary, not only an inline runner detail.
3. Multi-start MLE must use enforceable hard-budget accounting rather than
   relying on post-hoc detection after a solver call.
4. The candidate controller has no accepted end-to-end implementation.
5. Reference convergence and independent-family validation have no accepted
   frozen-protocol artifact.
6. The default bounded runner is not the ten-seed scientific campaign; its
   outputs must remain exploratory and must not be promoted to evidence.

## 5. Claims prohibited at this stage

Until every applicable gate above is accepted, the project must not claim:

- that NUMERIS-GO is mathematically novel;
- that NUMERIS-GO is implemented as an executable candidate controller;
- that NUMERIS is more accurate, more reliable, or more efficient than
  DOP853 or any other baseline;
- that a parameter-recovery, likelihood, posterior, or false-optimum result
  has been experimentally established;
- that the frozen oscillator run is complete or publication-ready;
- that the result generalizes beyond the declared oscillator protocol;
- that a desktop interface constitutes scientific validation;
- that the project satisfies the full technical specification or is ready for
  publication.

The honest current summary is:

> The frozen minimal prototype is specified and partially scaffolded. Its
> exact model boundary, enforceable matched-budget estimator, candidate
> controller, and reference-validation gates are not all accepted. Therefore
> there is no valid candidate-versus-baseline scientific result.

## 6. Required next record update

The next revision of this record may change only after implementation and
tests produce evidence for one or more gates. It must list the exact commit,
test commands, accepted artifacts, failed cases, and remaining blockers. A
successful software test may upgrade an implementation gate; it may not by
itself upgrade a scientific claim or establish superiority.

