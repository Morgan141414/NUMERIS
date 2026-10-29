# Closest-baseline reproduction plan

Status: Phase-I execution plan, frozen for planning on 2026-10-30. This is a
reproduction plan, not evidence that any baseline has already been reproduced.

## 1. Purpose and non-claims

The purpose is to determine whether the eventual NUMERIS mechanism is distinct
from, and fairly compared with, the closest established mechanisms. The plan
covers three baseline families:

1. adjoint/global-error control (Cao--Petzold; Lang--Verwer);
2. goal-oriented or functional error control, when its target functional can be
   stated explicitly and implemented without changing the target after seeing
   results;
3. likelihood-aware or probabilistic inference (Creswell et al.; DALTON),
   subject to implementation and dependency availability.

No reproduction may be described as an exact reproduction unless the source
algorithm, equations, data/model configuration, tolerances, stopping rules and
reported metrics are matched sufficiently to support that wording. A locally
implemented analogue must be labelled `CONCEPTUAL-BASELINE`.

## 2. Reproduction tiers

| Tier | Meaning | Permitted claim |
|---|---|---|
| R0 | Bibliographic and mechanism extraction from the primary source | The source establishes the stated mechanism; no numerical result claim |
| R1 | Local smoke test on a documented toy ODE with a source-compatible quantity | The implementation exercises the mechanism locally |
| R2 | Source-aligned numerical reproduction with declared deviations | Results are a reproduction under the listed deviations |
| R3 | Independent rerun of a source benchmark with matched inputs, metrics and tolerances | Numerical agreement or disagreement may be reported for that benchmark |

The project cannot claim that a baseline was “beaten” at R0 or R1. R2/R3
results must retain failed and non-converged runs.

## 3. Baseline cards

### A. Adjoint/global error: Cao--Petzold and Lang--Verwer

**Object to reproduce:** an a posteriori/global error estimate or control rule
for a declared scalar output/functional, including the adjoint or variational
quantity used by the source. The target must be written before running a
comparison; a generic trajectory norm is not an adequate substitute for a
goal-oriented target.

**Minimum local protocol:**

1. Extract the source equations and assumptions into a dated research note.
2. Choose one smooth non-stiff ODE and one stiff ODE from the NUMERIS model set.
3. Declare a scalar terminal or observation functional and its reference value.
4. Implement a source-aligned estimator, or mark the result
   `CONCEPTUAL-BASELINE` if the original adjoint discretisation is unavailable.
5. Compare estimator error with an independently converged reference and log
   RHS evaluations, adjoint/variational solves, tolerance, and failure status.
6. Compare the source-aligned global-control decision against ordinary adaptive
   control at equal total RHS-equivalent budget.

**Required outputs:** derivation trace, implementation mapping, deviations,
functional error, estimator error, calibration ratio, cost, and failure log.

**Cannot claim:** that an adjoint estimator, functional error control, or
goal-oriented allocation is novel merely because the NUMERIS wrapper or score
has a different name.

### B. Goal-oriented/functional control

This is a mechanism class, not a single package. The reproduction target is the
mathematical mapping from a declared functional and local defects to a global
error estimate or refinement decision.

**Minimum local protocol:** use the same ODE, functional, reference, tolerance
grid, and budget for the standard and goal-oriented arms; freeze the functional
and allocation rule before inspecting results; test estimator calibration over
all predeclared seeds; include a negative case where the functional is weakly
coupled to the region receiving extra work.

**Required distinction:** a heuristic sensitivity weight is not an adjoint
guarantee. It must be labelled heuristic until calibration and any stated
theorem are established.

### C. Likelihood distortion: Creswell et al.

**Object to reproduce:** the effect of insufficient ODE accuracy on likelihood
surfaces and parameter inference, including the possibility of phantom/local
optima. The primary source is the Royal Society paper linked in the ledger;
the PMC copy is used for accessible full text and supplementary links.

**Minimum local protocol:**

1. Recreate a low-dimensional synthetic Gaussian-observation problem with a
   high-accuracy reference likelihood.
2. Evaluate a fixed parameter grid at at least three solver accuracy levels,
   using the same observations and parameter ordering.
3. Record likelihood error against the reference, surface roughness, maximizer
   displacement, and optimization failure/local-optimum outcomes.
4. Repeat over the frozen NUMERIS seeds and noise factors; do not select a seed
   after looking at the surface.
5. Label the result `SOURCE-ALIGNED-REPRODUCTION` only after model, metric and
   accuracy mapping has been documented.

**Cannot claim:** that observing solver-induced likelihood distortion validates a
NUMERIS controller; it only validates the motivation for testing one.

### D. DALTON / likelihood-aware probabilistic inference

DALTON is a nearest-neighbour comparator, not an optional citation. First
record whether a source-compatible implementation and dependency environment
can be installed locally. If not, report `NOT-REPRODUCED-DEPENDENCY/BENCHMARK`
with the exact blocker and do not replace it silently with a different method.

**Minimum local protocol when feasible:**

- record source version/commit and environment;
- match observation model, observed components, parameterisation, priors or
  optimisation objective, and stopping criteria;
- compare likelihood/parameter error and cost against the exact deterministic
  likelihood and NUMERIS under matched data and budget;
- preserve non-convergence, unsupported model features, and failed runs;
- separate the paper's reported claims from results obtained on NUMERIS models.

**Cannot claim:** that a sensitivity-aware tolerance policy is distinct from
DALTON or probabilistic likelihood approximation without a line-by-line
mechanism comparison and a fair empirical comparison.

## 4. Execution order and evidence files

The order is deliberately staged:

1. R0 extraction and source verification in the ledger;
2. R1 local smoke tests and interface mapping;
3. R2/R3 only after the reference-solution and budget gates pass;
4. final overlap analysis after the NUMERIS mathematical mechanism is frozen.

Each run must produce a small, reviewable record in `research/protocol/` or an
experiment result directory: source ID, protocol version, commit, environment,
inputs, deviations, outputs, failures, and claim status. This plan does not
authorise changes to the frozen v0.1 manifest; any changed factor requires a
new versioned manifest.

## 5. Current reproducibility status

| Baseline | Local status at plan date | Allowed wording now | Next gate |
|---|---|---|---|
| Cao--Petzold / Lang--Verwer | R0 only | “Primary prior art identified” | Source-aligned estimator mapping and R1 |
| Goal-oriented/functional control | R0/conceptual comparison only | “Overlap risk is unresolved” | Explicit functional and decision-rule reproduction |
| Creswell et al. likelihood distortion | Motivation identified; source-aligned reproduction pending | “Published motivation, not yet reproduced locally” | Fixed-grid likelihood distortion run |
| DALTON | Source identified; local reproduction not established | “Nearest comparator, not yet reproduced” | Dependency/source compatibility check |
| Probabilistic ODE solvers | Literature baseline only in current protocol | “Not included in v0.1 claims” | Separate frozen probabilistic protocol |

Until these statuses change through recorded evidence, NUMERIS must not claim
novelty, superiority, publication readiness, or reproduction of a named method.
