# Research Gap Closure: explicit exit criteria

Status: gate for the next NUMERIS phase. This document does not declare that
the gate has passed. It defines what must be true before moving from Research
Gap Closure to Mathematical Core as a justified research step.

## Exit decision

The phase is `PASS` only when every mandatory criterion below is `PASS`.
`PARTIAL`, `BLOCKED`, and `GAP-UNRESOLVED` are not passes. A negative or
inconclusive outcome is acceptable and must be recorded; it does not authorize
a novelty or superiority claim.

| ID | Mandatory criterion | Evidence required | Pass condition |
|---|---|---|---|
| G1 | Mechanism inventory | `RESEARCH_GAP_CLOSURE_MATRIX.md` | Every declared comparator has objective, estimator, control action, uncertainty, artifact, local status, and falsification test |
| G2 | Source identity | Bibliography ledger and direct primary/official artifacts | Every comparator resolves to a source ID; no comparator is represented only by a secondary summary |
| G3 | NUMERIS mechanism freeze | Dated mathematical note or protocol record | One target, estimator candidate, sensitivity source, control action, stopping rule, and budget are fixed before comparative results |
| G4 | Overlap classification | Line-by-line equation/pseudocode comparison | Each component is classified `same`, `known modification`, `unclear`, or `potentially distinct`; no `potentially distinct` item is called novel |
| G5 | Adjoint/global test | Source-aligned extraction and R1/R2 record, or explicit blocker | The record states whether NUMERIS is equivalent to, a known modification of, or unresolved against the adjoint/variational mechanism |
| G6 | Goal-oriented test | Frozen functional, estimator, allocation rule, calibration and weak-coupling negative case | The local heuristic is mapped to a named mechanism or remains `CONCEPTUAL-BASELINE` |
| G7 | Likelihood-aware test | Source-aligned fixed-grid likelihood-distortion record | Motivation reproduction is labelled reproduced, not reproduced, or blocked; it is not treated as proof of NUMERIS benefit |
| G8 | DALTON test | Pinned artifact/environment and one matched benchmark, or retained blocker | DALTON is compared under declared conditions or remains `BLOCKED`; no substitute is relabelled DALTON |
| G9 | Probabilistic ODE scope | One selected paper, implementation target, and separate protocol, or explicit exclusion | The heterogeneous family is not collapsed into one unsupported baseline claim |
| G10 | Falsification rule | Predeclared decision record | Equivalence, lack of calibrated benefit, baseline non-inferiority, or unreproducibility leads to `REFRAME`, `STOP/NEGATIVE RESULT`, or `REMAIN UNRESOLVED` |
| G11 | Claim register | Updated allowed/prohibited wording | No document claims novelty, firstness, superiority, or publication readiness before the relevant evidence gate passes |
| G12 | Handoff integrity | Versioned protocol, source matrix, status records and exact commands | A clean checkout can identify what is known, unknown, blocked, and the next reproducible action |

## Automatic failure conditions

The phase remains open if:

- NUMERIS is called novel because its software architecture differs;
- a heuristic sensitivity weight is described as an adjoint guarantee;
- likelihood-distortion reproduction is treated as controller superiority;
- DALTON or probabilistic ODE methods are silently replaced by another method;
- a budget, target, seed, or metric changes after inspecting results;
- failed, non-converged, blocked, or over-budget cases are removed;
- the estimator has no independent reference-error calibration;
- the final mechanism is not compared line by line with the closest rows;
- the matrix and status records disagree about local evidence.

## Permitted phase outcomes

At the gate review exactly one outcome must be recorded:

- `PROCEED`: a mechanism-level difference remains testable and the mathematical
  investigation is justified; this is not a novelty or superiority result.
- `REFRAME`: the proposed mechanism overlaps existing work, so the target or
  contribution is narrowed before further implementation.
- `STOP/NEGATIVE RESULT`: no defensible distinct mechanism or practical value
  remains under the frozen conditions.
- `REMAIN UNRESOLVED`: evidence is insufficient; no scientific claim is made.

Until the gate review is completed, the official status is:

`RESEARCH GAP CLOSURE OPEN / GAP-UNRESOLVED`
