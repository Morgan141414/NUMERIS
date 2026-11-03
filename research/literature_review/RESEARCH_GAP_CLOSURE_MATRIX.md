# NUMERIS mechanism-level research-gap closure matrix

Status: working research artifact, not a novelty claim. Prepared on
2026-11-03 after read-only inspection of the current repository evidence.

This matrix compares mechanisms, not names or software interfaces. A row is
not considered closed because NUMERIS has a similarly named helper. The
`exact falsifiable difference` field states the experiment or derivation that
could show the proposed NUMERIS mechanism is equivalent, weaker, or distinct.
Until that test is completed, the status is `GAP-UNRESOLVED`.

## Controlled comparison

| Method/family | Objective | Mathematical estimator | Budget/control action | Uncertainty model | Implementation artifact | Local reproduction status | Exact falsifiable difference | Current status |
|---|---|---|---|---|---|---|---|---|
| Adjoint/global-error: Cao–Petzold; Lang–Verwer | Estimate or control global error of a declared ODE output/functional, using conditioning and sensitivity of the IVP | Adjoint or variational global-error representation; source-specific defect/conditioning terms and tolerance relation | Adjust tolerances/steps to control the global functional or state error; cost is solver plus adjoint/variational work | Deterministic a posteriori error estimate, not a posterior distribution | `ADJ-01`, `ADJ-02` in `BIBLIOGRAPHY_LEDGER.md`; local reproduction plan in `CLOSEST_BASELINE_REPRODUCTION_PLAN.md` | `R0`; no source-aligned local estimator record | Freeze the same scalar functional, reference, defect signal, tolerance grid and RHS-equivalent budget. If the NUMERIS estimator reduces to the same adjoint/variational representation and decision rule, the proposed distinction is falsified. | `GAP-UNRESOLVED` |
| Goal-oriented/functional error control | Minimize error in a selected quantity of interest rather than a norm of the full state | Usually dual-weighted residual, adjoint sensitivity, or functional error representation; exact formula depends on the named method | Refine steps/mesh/tolerances where estimated contribution to the quantity of interest is largest | Usually deterministic estimator; calibration is empirical unless a theorem is supplied | Current local comparator: `numeris/controller/goal_oriented.py`; source-aligned target is not yet selected | `CONCEPTUAL-BASELINE`; not a reproduction of a named method | Use identical functional, local-defect signal, allocation rule, weak-coupling negative case and budget. If NUMERIS only reweights the same dual-weighted contributions, it is a known modification, not a distinct mechanism. | `GAP-UNRESOLVED` |
| Likelihood-aware inference / solver-induced likelihood distortion | Protect likelihood, parameter estimates, or optimization landscape from forward-solver error | Likelihood is evaluated with approximate ODE states; distortion is measured against an independently converged likelihood/reference; no universal controller is implied | Inspect or tighten solver accuracy, or adapt computation to reduce likelihood distortion; the source motivation does not itself prescribe a NUMERIS allocation rule | Statistical observation noise plus numerical distortion relative to a reference; not automatically a posterior over numerical error | `DIST-01` and its supplementary artifact in `BIBLIOGRAPHY_LEDGER.md`; local fixed-grid reproduction is specified in the reproduction plan | `NOT-REPRODUCED`; published motivation identified, local source-aligned run absent | Reproduce the fixed likelihood grid and then compare NUMERIS's estimator/action. If the proposed controller is only tolerance tightening selected from likelihood distortion, without a distinct estimator or allocation theorem, the claimed gap is falsified. | `GAP-UNRESOLVED` |
| DALTON / data-adaptive probabilistic likelihood approximation | Approximate the likelihood used for ODE parameter inference while reducing repeated expensive forward computations | Data-adaptive probabilistic approximation to the likelihood conditioned on observations and model evaluations; source-specific approximation, not merely a solver tolerance | Allocate/interpolate probabilistic likelihood evaluations according to data and parameter sensitivity; compare inference quality and cost against deterministic likelihood | Probabilistic approximation of likelihood/inference quantities | Wu–Lysy paper and authors' `mlysy/rodeo` artifact (`DAL-01`); environment gate in `BASELINE_REPRODUCTION_HANDOFF_2026-11-03.md` | `BLOCKED`; `jax`/`rodeo` and a pinned compatible environment are not locally established | Match one published DALTON benchmark, objective, priors/parameterisation, stopping rule and cost. If NUMERIS's target-aware controller can be represented as the same data-adaptive likelihood approximation, no distinct mechanism remains. | `GAP-UNRESOLVED` |
| Probabilistic ODE solvers | Represent numerical/discretisation uncertainty in the ODE solution and propagate it to downstream quantities | Probabilistic numerical update, often a Gaussian-process/state-space posterior over the solution or discretisation error; calibration depends on the selected method | Probabilistic step/interrogation updates and adaptive step-size control; exact action is method-specific | Explicit posterior or calibrated distribution over numerical solution/error | Hennig–Hauberg, Chkrebtii et al., Bosch–Hennig–Tronarp (`PN-01`–`PN-03`); no single implementation target selected | `BLOCKED`; heterogeneous family, no separate frozen protocol or pinned local implementation | Select one paper and implementation, then match uncertainty target, calibration, cost and budget. If NUMERIS's error object is a calibrated posterior over the numerical solution, it overlaps this family rather than defining a new mechanism. | `GAP-UNRESOLVED` |
| Current NUMERIS heuristic | Intended to reduce error in a declared inference endpoint under a fixed computational budget | `SensitivityAwarePolicy` and related target-error/budget heuristics; current implementation does not establish a new estimator, theorem, or automatic sensitivity derivation | Rank/refine temporal regions or stop based on supplied sensitivity/target-error signals; current controller is not fully solver-integrated | Diagnostic point estimates/heuristic bounds; no validated posterior or reliability guarantee | `numeris/controller/goal_oriented.py`, `numeris/controller/temporal.py`, `research/derivations/gaussian_target_bound.md` | Implemented as a prototype; not validated as a source-aligned method and not a scientific result | Freeze one target, derive the estimator, compare line-by-line with all rows above, calibrate against an independent reference, and run equal-budget/ablation tests. The hypothesis is falsified by equivalence, no calibrated benefit, or baseline non-inferiority at declared budgets. | `GAP-UNRESOLVED` |

## Interpretation and claim rules

1. `GAP-UNRESOLVED` is required until the exact falsification test for the
   row has a retained derivation or run record.
2. A different API, weighted score, software wrapper, or combination of known
   components is not a mechanism-level difference by itself.
3. A positive endpoint result cannot establish novelty if the underlying
   estimator/control rule is mathematically equivalent to a listed method.
4. A failed reproduction is evidence about reproducibility, not evidence that
   the corresponding method is inferior.
5. The current NUMERIS row is a hypothesis record and must not be described as
   a new method, superior method, or publication result.

## Required evidence record for each row

Before changing a row from `GAP-UNRESOLVED`, retain in a versioned
`research/protocol` artifact:

- source identifier and exact implementation revision, where applicable;
- target quantity and uncertainty quantity;
- equations or pseudocode for estimator and control action;
- model, data, tolerance, stopping and budget settings;
- independent reference-error construction;
- deviations, failed runs, non-convergence and over-budget cases;
- paired cost-normalized results and uncertainty intervals;
- explicit classification: `same`, `known modification`, `unclear`, or
  `potentially distinct`;
- permitted public wording after review.

`potentially distinct` is not equivalent to `novel`.
