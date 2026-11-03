# Overlap-audit protocol checklist

Status: **frozen checklist for evidence collection; not a gap result**.

This checklist operationalises
`research/literature_review/OVERLAP_AUDIT_TEMPLATE.md`. It is mandatory for
each closest-baseline card before any claim about distinction is considered.
Until the complete evidence package is reviewed, the status is
**`GAP-UNRESOLVED`**.

## A. Freeze before running

- [ ] Select one primary source or official implementation.
- [ ] Record DOI/version/commit and exact environment.
- [ ] Select one declared ODE model and downstream target.
- [ ] Freeze observations, parameters, tolerances, seeds, stopping rules, and budget.
- [ ] Define an independently converged reference and its acceptance test.
- [ ] Declare all costs: RHS, adjoint/variational, likelihood, setup, runtime, and memory where available.
- [ ] Register the falsification rule before inspecting comparative results.
- [ ] Copy the overlap template and assign an immutable audit ID.

## B. Complete the seven mechanism fields

For each of `estimator`, `sensitivity source`, `allocation rule`, `stopping
rule`, `uncertainty representation`, `cost model`, and `downstream target`:

- [ ] Record the source equation/pseudocode and location.
- [ ] Record the NUMERIS equation/pseudocode and code/protocol path.
- [ ] State assumptions and applicability limits.
- [ ] State missing or unknown information explicitly.
- [ ] Assign one provisional classification:
  `same`, `known modification`, `unclear`, or `potentially distinct`.
- [ ] Define the exact test that could falsify that classification.

## C. Execute and retain evidence

- [ ] Run source-aligned smoke test or record a concrete blocker.
- [ ] Compare estimator against independent target error.
- [ ] Compare sensitivity error and sensitivity cost.
- [ ] Compare allocation decisions under the same budget.
- [ ] Compare stopping decisions over the frozen tolerance grid.
- [ ] Compare uncertainty calibration, coverage, and overconfidence where applicable.
- [ ] Compare downstream endpoint error using the same target definition.
- [ ] Retain all failures, non-convergence, missing, and over-budget outcomes.
- [ ] Record deviations from the source and their scientific impact.
- [ ] Attach machine-readable outputs and provenance metadata.

## D. Review gate

- [ ] Every classification is supported by a source location and local artifact.
- [ ] No failed reproduction is interpreted as baseline inferiority.
- [ ] No software wrapper or weighted score is treated as a new mechanism.
- [ ] `potentially distinct` is not called novelty.
- [ ] The matrix, handoff record, protocol, and evidence ledger agree.
- [ ] Public wording is limited to what the evidence supports.
- [ ] A reviewer records exactly one outcome:
  `PROCEED`, `REFRAME`, `STOP/NEGATIVE RESULT`, or `REMAIN UNRESOLVED`.

## E. Current project gate

This checklist is newly added infrastructure. It does not complete any
source-aligned reproduction, overlap classification, or mathematical proof.
The current project status therefore remains:

> **`RESEARCH GAP CLOSURE OPEN / GAP-UNRESOLVED`**

See `RESEARCH_GAP_CLOSURE_EXIT_CRITERIA.md` for the conditions required before
the status can change.
