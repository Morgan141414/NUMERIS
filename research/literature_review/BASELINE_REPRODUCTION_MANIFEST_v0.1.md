# Closest-baseline reproduction manifest v0.1

Status: executable handoff manifest, frozen for the current Research Foundation
cycle on 2026-10-30. This file records what is reproducible locally and what is
not. It is not evidence that an implementation has been reproduced.

The companion checker is:

    research/protocol/check_baseline_reproduction.sh

Run it from the repository root. A non-zero exit code is expected until every
mandatory Phase-I gate has a recorded result or an explicit blocker.

## 1. Status vocabulary

| Status | Meaning | Allowed wording |
|---|---|---|
| R0 | Primary-source and mechanism extraction only | “Prior art identified” |
| R1 | Local smoke test with source-compatible quantity | “Local mechanism smoke test” |
| R2 | Source-aligned numerical reproduction with declared deviations | “Reproduced under listed deviations” |
| R3 | Matched source benchmark, inputs, metrics, and tolerances | “Independent rerun of the source benchmark” |
| NOT-REPRODUCED | Reproduction has not been completed and no hard blocker is asserted | “Not reproduced locally” |
| BLOCKED | A documented dependency, source, or environment blocker prevents the next tier | “Blocked by the recorded condition” |
| CONCEPTUAL-BASELINE | Local analogue is useful for comparison but is not source reproduction | “Conceptual comparator only” |

R0 and R1 are not numerical reproduction. CONCEPTUAL-BASELINE must not be
silently upgraded to R1–R3. A missing status is a manifest error.

## 2. Baseline cards and current evidence

Every card has one owner, a fixed target, a required evidence record, and an
explicit stop rule. The current status is deliberately conservative.

| ID | Baseline family | Primary source IDs | Fixed reproduction target | Current status | Evidence required for next tier |
|---|---|---|---|---|---|
| ADJ-GLOBAL | Adjoint/global error control | ADJ-01, ADJ-02 | A posteriori/global error estimate or control for one declared scalar functional on one smooth and one stiff ODE | R0 | Dated equation/assumption extraction, source-aligned estimator mapping, R1 smoke record, calibration against independent reference |
| GO-FUNCTIONAL | Goal-oriented/functional control | ADJ-01, ADJ-02 plus mechanism sources | Fixed functional-to-refinement/allocation mapping under a frozen tolerance grid and budget | CONCEPTUAL-BASELINE | Functional and decision rule frozen before runs, negative weak-coupling case, estimator calibration record |
| LIKELIHOOD-DISTORTION | Solver-induced likelihood distortion | DIST-01 | Fixed parameter-grid Gaussian likelihood at at least three solver accuracy levels against a converged reference | NOT-REPRODUCED | Source-aligned model/metric mapping, fixed-grid run, surface roughness and maximizer-displacement record, failed-run denominator |
| DALTON | Likelihood-aware probabilistic inference | DAL-01 | Source-compatible local environment, observation model, objective, priors/stopping rules, and matched cost comparison | NOT-REPRODUCED | Dependency/source compatibility record; if unavailable, exact blocker record and no substitute claim |
| PROB-ODE | Probabilistic ODE solvers | PN-01, PN-02 | Separate frozen probabilistic protocol; not part of deterministic v0.1 claims | BLOCKED | New versioned protocol, implementation/version record, uncertainty calibration and matched budget |

The source IDs must resolve in BIBLIOGRAPHY_LEDGER.md. A SciPy run is a
deterministic solver baseline, not an ADJ-GLOBAL, GO-FUNCTIONAL, DALTON, or
PROB-ODE reproduction.

## 3. Required evidence record

For each card at R1 or higher, create a dated record under
research/protocol/baseline_records/ or an experiment result directory. The
record must contain all fields below; a blocker record may replace numerical
outputs only when the blocker is independently checkable.

    baseline_id: ADJ-GLOBAL
    status: R0 | R1 | R2 | R3 | NOT-REPRODUCED | BLOCKED | CONCEPTUAL-BASELINE
    source_ids: [ADJ-01]
    protocol_version: v0.1
    repository_commit: <full-or-short-commit>
    environment: <python/scipy/platform or exact blocker>
    model_and_data: <model, observations, parameterisation>
    target_functional: <scalar functional and observation times>
    solver_and_tolerances: <method, rtol, atol, max step>
    budget_definition: <RHS/runtime/memory and matching rule>
    metrics: [<predeclared metrics>]
    deviations: [<source deviation, or []>]
    result_files: [<paths, or [] for a blocker>]
    failures_and_nonconvergence: <included, or explicit none>
    claim_scope: <permitted wording only>
    next_gate: <single next action>

No result record may omit failed or over-budget runs. No parameter grid,
functional, seed, tolerance, or budget may be changed after inspecting results
without incrementing the protocol version and retaining the old record.

## 4. Phase-I completion checklist

Phase I remains open unless every mandatory item is checked and the companion
checker returns exit code 0.

- [ ] Every card above has a status and source IDs resolving in the ledger.
- [ ] Every status above R0 has a dated evidence record.
- [ ] Every NOT-REPRODUCED or BLOCKED status has a concrete next gate or blocker.
- [ ] Likelihood-distortion motivation is reproduced, not inferred from citation.
- [ ] Adjoint/global and functional/goal-oriented overlap is mapped line by line.
- [ ] DALTON compatibility is checked or its blocker is recorded without substitution.
- [ ] Target, budget, metrics, seeds, and falsification rule are frozen before comparison.
- [ ] No document calls a conceptual analogue a named-method reproduction.
- [ ] No negative, failed, non-converged, or over-budget run is removed.
- [ ] A written decision is recorded: PROCEED, REFRAME, or STOP/NEGATIVE RESULT.

Completion outcome at manifest creation: BLOCKED — evidence records and
source-aligned numerical reproductions are still incomplete.

## 5. Explicit limitations

This manifest does not implement adjoint, goal-oriented, probabilistic, or
DALTON methods. It does not establish novelty, superiority, publication
readiness, or equivalence. It only makes the reproduction boundary auditable.

The current statuses are based on project records available on 2026-10-30.
They must be changed only by adding evidence or a checkable blocker, never by
renaming a status after a result is observed.
