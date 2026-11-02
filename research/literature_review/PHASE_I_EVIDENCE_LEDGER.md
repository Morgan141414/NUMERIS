# Phase-I evidence ledger: R1–R3 blockers

Status: conservative Research Foundation checklist, frozen on 2026-11-03.

This ledger is an evidence-control artifact. It does not upgrade a baseline
status, establish numerical reproduction, establish novelty, or establish
superiority. The authoritative status vocabulary is defined in
`BASELINE_REPRODUCTION_MANIFEST_v0.1.md`; this file records the evidence still
missing before an R1, R2, or R3 label may be used.

## Decision rules

An evidence tier may be recorded only when every required field for that tier
is present in a dated record and the lower tier has already passed. A citation,
a generic SciPy run, a conceptual analogue, or a successful import is not
evidence of named-method reproduction.

- **R1 — local mechanism smoke test:** source-compatible quantity and
  mechanism exercised locally; no claim of numerical reproduction.
- **R2 — source-aligned numerical reproduction:** source inputs, method,
  metrics, tolerances, deviations, and failure accounting are matched and
  archived.
- **R3 — matched source benchmark:** R2 plus the source benchmark is rerun
  independently with matched inputs, metrics, tolerances, stopping rules, and
  cost accounting.

Any missing, ambiguous, or post-hoc field keeps the tier at the current lower
status. `BLOCKED` and `NOT-REPRODUCED` are valid outcomes; they are not failures
to be hidden by substituting a different implementation.

## Baseline evidence ledger

| Baseline | Current status | R1 evidence required | R2/R3 blocking condition | Next checkable action | Allowed wording now |
|---|---|---|---|---|---|
| `ADJ-GLOBAL` | `R0` | Dated extraction of the source equations and assumptions; one source-compatible scalar functional; local estimator smoke record with estimator/reference error, tolerance, RHS-equivalent cost, and failures | No frozen adjoint discretisation, functional, reference, or source-aligned estimator record exists. R2 additionally requires declared deviations and matched numerical outputs; R3 requires a matched source benchmark | Add a dated extraction record under `research/protocol/` after fixing one smooth and one stiff ODE and one scalar functional | “Primary adjoint/global-error prior art identified; not reproduced locally.” |
| `GO-FUNCTIONAL` | `CONCEPTUAL-BASELINE` | There is no named single implementation target. R1 requires a frozen functional, local-defect signal, and decision rule explicitly mapped to a source mechanism | The current sensitivity-aware policy is a local heuristic; no source-aligned adjoint estimator or canonical benchmark is identified. It must not be upgraded to R1–R3 by analogy | Either select one named source-aligned method and freeze its mapping, or retain conceptual status and record the deviation | “Conceptual functional-control comparator; named goal-oriented method not reproduced.” |
| `LIKELIHOOD-DISTORTION` | `NOT-REPRODUCED` | Source-compatible likelihood quantity and oscillator setup; fixed parameter slice/grid; one local smoke record with declared solver accuracy and reference | Current oscillator defaults are not documented as identical to the source experiment. R2/R3 are blocked until supplementary materials, inputs, solver settings, metrics, reference, seeds, and failed-run denominator are mapped and archived | Inspect and record the official supplementary artifact, then freeze the source-aligned mapping before running the grid | “Published motivation identified; source-aligned local reproduction is pending.” |
| `DALTON` | `BLOCKED` | Source-compatible import/environment check plus one source-compatible likelihood approximation quantity; no substitution with the NUMERIS Bayesian grid helper | Local environment lacks a pinned compatible `rodeo` revision and JAX environment. R2/R3 also require matched observation model, priors/objective, stopping rules, metrics, and cost | Pin the implementation revision and dependency environment; record install/import results before attempting the benchmark | “DALTON is a nearest comparator; local reproduction is blocked by the recorded environment/protocol condition.” |
| `PROB-ODE` | `BLOCKED` | No R1 is permitted for the heterogeneous family as a whole. Select one paper and one implementation target first, then define a source-compatible uncertainty quantity | The family combines different posterior constructions, interrogation models, calibration targets, and costs. Deterministic v0.1 evidence cannot be promoted to R1–R3 | Create a separate versioned probabilistic protocol and one paper-to-code mapping; then define calibration and matched-budget evidence | “Probabilistic ODE methods are relevant prior art; no local reproduction is claimed in deterministic v0.1.” |

## Required evidence-record checklist

For any future record claiming R1, R2, or R3, all applicable boxes below must
be checked in the record itself. An unchecked item is a blocker, not an implied
pass.

- [ ] Baseline ID and current tier are explicit.
- [ ] Every source ID resolves in `BIBLIOGRAPHY_LEDGER.md`.
- [ ] The exact source artifact, version/commit, and access date are recorded.
- [ ] Model, observations, parameters, functional/likelihood target, and
      initial conditions are source-aligned or every deviation is listed.
- [ ] Solver algorithm, implementation, tolerances, step limits, stopping
      rules, and random seeds are recorded.
- [ ] Reference construction and its independent convergence check are
      recorded; a strict-tolerance run is not called absolute truth.
- [ ] Metrics, budget definition, hardware, runtime, RHS evaluations, memory,
      and matching rule are recorded.
- [ ] Failed, non-converged, interrupted, and over-budget cases remain in the
      denominator.
- [ ] Result files are addressable from the repository and tied to a commit.
- [ ] Deviations from the source are explicit and their effect is discussed.
- [ ] The claim scope uses only the wording permitted by the current tier.
- [ ] The next gate is one concrete action, not a conclusion inferred from a
      citation or a convenient analogue.

## Phase-I stop conditions

Phase I remains open and no novelty/reproduction claim is authorized if any of
the following is true:

1. Any closest baseline lacks an explicit current status and next gate.
2. An R1 label is used without a source-compatible quantity and dated record.
3. An R2 label is used without matched inputs, metrics, tolerances, deviations,
   and failure accounting.
4. An R3 label is used without an independently rerun source benchmark and
   matched cost accounting.
5. A conceptual comparator or deterministic solver is described as a named
   adjoint, goal-oriented, probabilistic, or DALTON reproduction.
6. A negative, failed, non-converged, or over-budget run is removed after
   inspecting results.
7. A source, protocol, budget, or claim scope is changed after results without
   incrementing the protocol version and retaining the previous record.

Current decision: **RESEARCH FOUNDATION OPEN — R1–R3 evidence incomplete;
reproduction and novelty claims prohibited.**
