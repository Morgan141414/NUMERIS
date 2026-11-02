# Closest-baseline reproduction handoff record

Status: source-aligned handoff for Research Foundation, checked 2026-11-03.

This record does not add reproduction evidence. It defines the exact artifact
that must be produced before each closest baseline may move to R1, R2, or R3,
and records the blockers observed in the local environment. A status changes
only after the named artifact is reviewed and retained in the repository.

## 1. Scope and status rule

The closest-baseline set is the five-card set frozen in
`research/literature_review/BASELINE_REPRODUCTION_MANIFEST_v0.1.md`:

- `ADJ-GLOBAL` — Cao–Petzold and Lang–Verwer;
- `GO-FUNCTIONAL` — functional/goal-oriented control mechanism family;
- `LIKELIHOOD-DISTORTION` — Creswell et al.;
- `DALTON` — Wu–Lysy and the authors' `rodeo` artifact;
- `PROB-ODE` — one selected probabilistic ODE source must be chosen before
  this heterogeneous family can have a single reproduction target.

The tiers have the following meaning:

| Tier | Required meaning | Claim permitted after the artifact is accepted |
|---|---|---|
| R1 | Local smoke test exercising a source-compatible quantity or mechanism | “Local mechanism smoke test” |
| R2 | Source-aligned numerical reproduction with declared deviations | “Reproduced under the listed deviations” |
| R3 | Matched source benchmark with matched inputs, metrics, tolerances, and cost accounting | “Independent rerun of the source benchmark” |

R1 is not a reproduction of a published result. No tier authorizes a novelty
or superiority claim.

## 2. Current status snapshot

These statuses are transcribed from
`research/literature_review/BASELINE_REPRODUCTION_STATUS_2026-10-30.md` and
are not upgraded by this handoff record.

| Baseline | Current status | Source-aligned target | Current local blocker or gap |
|---|---|---|---|
| `ADJ-GLOBAL` | `R0` | One adjoint/global-error estimator or control rule for a declared scalar functional | Equations, assumptions, adjoint discretisation, tolerance relation, and cost accounting are not yet frozen in a local evidence record |
| `GO-FUNCTIONAL` | `CONCEPTUAL-BASELINE` | One explicitly named functional-to-estimator/refinement rule | No single canonical package/benchmark is selected; local sensitivity policy is not source reproduction |
| `LIKELIHOOD-DISTORTION` | `NOT-REPRODUCED` | Fixed Creswell-aligned Gaussian likelihood surface experiment | Local oscillator configuration and source-to-local mapping are not frozen; no source-aligned run record exists |
| `DALTON` | `BLOCKED` | One matched DALTON benchmark using a pinned `rodeo`/JAX environment | Required runtime/artifact is unavailable locally and no pinned revision or dependency lock is recorded |
| `PROB-ODE` | `BLOCKED` | One selected paper plus one pinned implementation target | v0.1 is deterministic; the family is heterogeneous and no separate probabilistic protocol exists |

## 3. Required handoff artifacts by baseline

### 3.1 `ADJ-GLOBAL` — Cao–Petzold / Lang–Verwer

Source anchors: `ADJ-01` and `ADJ-02` in
`research/literature_review/BIBLIOGRAPHY_LEDGER.md`.

**Artifact needed for R1.** Add a dated source-extraction record under
`research/protocol/baseline_records/` containing the selected source equations,
assumptions, adjoint/variational quantity, one declared scalar functional, one
smooth and one stiff NUMERIS model, reference construction, solver settings,
and an implementation mapping. The record must include a smoke-test output
with estimator value, independently computed functional error, tolerance, RHS-
equivalent cost, and failure status. If the source discretisation cannot be
implemented, the record must retain `CONCEPTUAL-BASELINE` rather than relabel
the local heuristic.

**Artifact needed for R2.** Add a versioned numerical reproduction record that
uses the extracted source equations and declared source assumptions, fixes the
functional and tolerance grid before execution, reports estimator error versus
an independent reference, and lists every deviation from each source. Include
all solver, adjoint/variational, stopping, cost, and non-convergence fields.

**Artifact needed for R3.** Add a matched benchmark bundle: source benchmark
inputs or an independently verified transcription, source-compatible model and
functional, tolerance/stopping rules, reference policy, reported metrics,
RHS/runtime accounting, and a machine-readable result with all failed and
over-budget runs retained. A generic SciPy trajectory comparison is not this
artifact.

**Handoff blocker now.** No R1 source-aligned estimator record is present.

### 3.2 `GO-FUNCTIONAL` — functional/goal-oriented control

Source anchors: the mechanism sources `ADJ-01` and `ADJ-02`; this card is a
mechanism family, not a single named package.

**Artifact needed for R1.** Add a mechanism-definition record naming one
functional, local-defect/error signal, discretisation, and functional-to-
refinement or allocation decision rule. Include a local run that exercises the
same quantity and records the standard comparator, tolerance, budget, and
negative weak-coupling case. Label a heuristic as heuristic.

**Artifact needed for R2.** Add a frozen source-aligned protocol and numerical
record covering the same ODE, functional, reference, tolerance grid, equal-
budget rule, predeclared seeds, estimator calibration, and declared deviations.
The record must show whether the functional estimate tracks independent error;
it must not infer validity from an improved parameter metric alone.

**Artifact needed for R3.** Add a matched source benchmark only if a named
source benchmark and executable mechanism mapping have been identified. The
bundle must contain source inputs, implementation revision, metrics, stopping
rules, budget accounting, and all negative/failed cases. Otherwise retain
`CONCEPTUAL-BASELINE` and record that no R3 target exists.

**Handoff blocker now.** The local sensitivity-aware policy is not evidence of
a source-aligned adjoint/goal-oriented method, and no canonical R1 target has
been frozen.

### 3.3 `LIKELIHOOD-DISTORTION` — Creswell et al.

Source anchor: `DIST-01`; the full text and official supplementary-material
record are listed in the bibliography ledger.

**Artifact needed for R1.** Add a source-to-local mapping record for one
low-dimensional Gaussian-observation experiment. It must identify the source
model, observation times/components, parameter ordering, noise, fixed grid,
solver accuracy levels, likelihood definition, reference policy, and metric
definitions. Then retain one local smoke output showing the computed likelihood
and its comparison quantity; this remains a smoke test, not a reproduction.

**Artifact needed for R2.** Add a versioned fixed-grid run at at least the
predeclared accuracy levels with the same observations and parameter ordering,
likelihood error against the independently converged reference, surface
roughness, maximizer displacement, optimization failures, and the complete
failed-run denominator. Declare every source deviation.

**Artifact needed for R3.** Add a matched benchmark bundle containing the
official supplementary artifact version/date or a documented source
transcription, exact model/data/grid/solver settings, reference and metric
definitions, seeds, cost accounting, and machine-readable results. Preserve
non-converged, failed, and over-budget cases; do not select seeds after
inspecting likelihood surfaces.

**Handoff blocker now.** No source-aligned local likelihood-distortion record
exists; the NUMERIS oscillator defaults are not treated as the source setup.

### 3.4 `DALTON` — Wu–Lysy / `rodeo`

Source anchor: `DAL-01`; implementation identity is the authors' `mlysy/rodeo`
artifact as recorded in the ledger.

**Artifact needed for R1.** Add an environment-and-import record containing the
pinned `rodeo` revision, compatible Python/JAX versions, dependency lock or
installation transcript, import/version checks, and one source-compatible
likelihood call on a documented toy problem. The record must identify the
observation model and objective; a NUMERIS grid posterior is not DALTON.

**Artifact needed for R2.** Add a source-aligned DALTON numerical record for
one published benchmark with matched parameterisation, observations, priors or
objective, solver/probabilistic settings, stopping rules, reference, metrics,
and declared implementation deviations. Retain installation failures and
non-convergence.

**Artifact needed for R3.** Add the pinned source benchmark bundle and a
matched-cost comparison record, including exact source commit, environment
lock, data/model configuration, likelihood/parameter metrics, cost definition,
repeated seeds, and all unsupported-feature or failed runs. Only this bundle
can support wording about an independent rerun of that benchmark.

**Handoff blocker now.** In the checked local `.venv`, `jax` and `rodeo` are
not importable. No source-compatible revision, lockfile, or benchmark mapping
has been recorded. This is an environment/protocol blocker, not evidence that
DALTON cannot be installed.

### 3.5 `PROB-ODE` — selected probabilistic ODE source

Source anchors: `PN-01`, `PN-02`, and `PN-03`. These papers are not one
reproducible method; one source must be selected before the card can move.

**Artifact needed for R1.** Add a scope-selection record naming exactly one
paper, one algorithmic target, one implementation target, one uncertainty
quantity, and one calibration test. Record why the other probabilistic ODE
papers are not being treated as the same baseline, then run a local smoke test
with the selected uncertainty output.

**Artifact needed for R2.** Add a separate versioned probabilistic protocol
with pinned implementation/environment, source-aligned model and data,
interrogation or posterior construction, uncertainty/calibration metrics,
solver settings, cost definition, and declared deviations. The deterministic
v0.1 protocol must remain unchanged.

**Artifact needed for R3.** Add a matched source benchmark bundle for the one
selected paper/implementation: source inputs, code revision, environment lock,
calibration target, uncertainty metrics, budget accounting, repeated seeds, and
all failed/non-converged runs. Do not combine results from multiple papers into
one claimed reproduction.

**Handoff blocker now.** `probdiffeq` is not importable locally; `PyMC`,
`NumPyro`, and `ArviZ` are also not importable. More importantly, no single
probabilistic target or separate protocol has been selected, so the current
deterministic v0.1 campaign cannot serve as evidence.

## 4. Observed local environment blockers

The following facts were checked on 2026-11-03 using the repository virtual
environment (`./.venv/bin/python`), Python `3.15.0rc1`:

| Check | Observed result | Interpretation |
|---|---|---|
| `scipy` importability | available | Supports deterministic SciPy baselines only; does not reproduce named adjoint, DALTON, or probabilistic methods |
| `jax` importability | unavailable | Blocks the recorded DALTON environment check |
| `rodeo` importability | unavailable | Blocks execution of the named DALTON artifact |
| `probdiffeq` importability | unavailable | No local implementation target for a probabilistic ODE smoke test |
| `pymc` importability | unavailable | No PyMC Bayesian implementation target in this environment |
| `numpyro` importability | unavailable | No NumPyro Bayesian implementation target in this environment |
| `arviz` importability | unavailable | Posterior diagnostic dependency is unavailable |

These checks are environment observations only. They do not establish that the
missing packages are impossible to install, nor do they lower or raise any
baseline status by themselves.

## 5. Handoff acceptance checklist

Before changing any current status, the next researcher must:

- attach the named artifact under `research/protocol/baseline_records/` or a
  versioned result directory;
- identify source IDs that resolve in `BIBLIOGRAPHY_LEDGER.md`;
- record repository commit, environment, model/data, target quantity, solver
  settings, tolerances, budget, metrics, deviations, failures, and permitted
  claim scope;
- preserve the predeclared protocol and increment its version for any changed
  factor;
- run the structural baseline checker;
- update the status record only after evidence review;
- keep `NOT-REPRODUCED`, `BLOCKED`, failed, non-converged, and over-budget
  outcomes visible.

Until these conditions are met, the current verdict remains:

`RESEARCH FOUNDATION REMAINS OPEN / NO REPRODUCTION, NOVELTY, OR SUPERIORITY CLAIM AUTHORIZED`.
