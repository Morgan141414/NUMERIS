# Negative-results and evidence ledger

Status: committed research-foundation record, checked 2026-11-03.

This ledger records only evidence that is currently checkable in the public
repository. It is a control artifact for negative, unresolved, incomplete, or
applicability-limited outcomes. It does **not** invent numerical results, infer
results from unit tests, or upgrade a baseline from a citation or an API to a
reproduction.

The frozen configurations and decision rules are defined by
[`research/protocol/PROTOCOL_MANIFEST_v0.1.md`](../protocol/PROTOCOL_MANIFEST_v0.1.md).
The closest-baseline status vocabulary is defined by
[`BASELINE_REPRODUCTION_MANIFEST_v0.1.md`](BASELINE_REPRODUCTION_MANIFEST_v0.1.md).

## Status vocabulary

- `REFERENCE-UNRESOLVED`: the protocol requires convergence and an independent
  solver-family check, but the repository contains no accepted result record
  proving both gates for the model.
- `NOT-REPRODUCED`: the declared source-aligned reproduction has not been
  completed and no hard environment blocker is asserted.
- `BLOCKED`: a documented dependency, source, or protocol condition prevents
  the next evidence tier.
- `NOT-ESTABLISHED`: no committed paired result establishes that one baseline
  is better than another.
- `BUDGET-EXHAUSTED/INCOMPLETE`: the declared campaign cannot be treated as a
  completed comparison because the recorded bounded run did not admit the full
  declared grid. This is not a numerical failure rate.
- `APPLICABILITY-LIMIT`: the protocol explicitly excludes the model, method,
  or claim from the current evidence scope.

These statuses are conservative. A status may be upgraded only by adding a
dated, reproducible evidence record; it must not be changed merely because a
future run is expected to succeed.

## 1. Declared closest-baseline gates

| Gate | Current evidence status | Checkable basis in repository | Negative or unresolved record | Next admissible evidence |
|---|---|---|---|---|
| `ADJ-GLOBAL` | `R0` / `NOT-REPRODUCED` | The manifest and Phase-I ledger identify Cao--Petzold and Lang--Verwer as prior art, but no source-aligned estimator result record is present under `research/protocol/`. | A generic SciPy solve is not a reproduction; no numerical advantage or equivalence is established. | Freeze one scalar functional, source assumptions, estimator mapping, reference, cost accounting, and an R1 smoke record. |
| `GO-FUNCTIONAL` | `CONCEPTUAL-BASELINE` | The repository describes a sensitivity-aware local policy, while the baseline manifest states that no named source-aligned implementation has been reproduced. | The local heuristic must not be called an adjoint/goal-oriented reproduction; overlap and distinctness remain unresolved. | Freeze the functional-to-decision mapping and include a weak-coupling negative case plus independent calibration. |
| `LIKELIHOOD-DISTORTION` | `NOT-REPRODUCED` | `BASELINE_REPRODUCTION_STATUS_2026-10-30.md` states that the Creswell et al. setup, grid, solver settings, metrics, and failure denominator are not yet matched. | Published motivation is not local evidence; no source-aligned likelihood-distortion result is recorded. | Archive the source-aligned setup and run the fixed-grid reproduction with failed/non-converged cases retained. |
| `DALTON` | `BLOCKED` | The checked status record documents that a pinned compatible `rodeo`/JAX environment and source benchmark mapping are absent. | The NUMERIS Bayesian grid helper must not be substituted for DALTON; no DALTON result or comparison is claimed. | Pin the implementation and environment, record import checks, then map one published benchmark. |
| `PROB-ODE` | `BLOCKED` / `APPLICABILITY-LIMIT` | The deterministic v0.1 manifest excludes probabilistic ODE superiority claims and no separate versioned probabilistic protocol is present. | The heterogeneous literature family cannot be treated as one reproduced baseline; posterior claims are outside this ledger's deterministic evidence. | Select one paper and implementation, create a separate protocol, calibrate uncertainty, and define matched cost. |
| SciPy `RK45`, `DOP853`, `Radau`, `BDF`, `LSODA` | `BASELINE-AVAILABLE; BETTER-UNESTABLISHED` | The frozen manifest declares these as solver configurations, but no committed completed campaign result compares NUMERIS against them under the full paired protocol. | Availability of a solver is not evidence that NUMERIS is better or worse. | Complete the paired campaign and report both primary endpoints, confidence intervals, failures, and budget violations. |

## 2. Model reference gates

The v0.1 protocol requires each reference to pass both a two-level tolerance
convergence check and an independent applicable solver-family check. The
repository contains implementation/report infrastructure and tests, but no
accepted per-model result record proving those gates. Therefore all five
declared model references remain unresolved for claims that depend on them.

| Model gate | Declared reference configuration | Current status | What is not established | Applicability limit |
|---|---|---|---|---|
| `OSC` damped oscillator | DOP853, `rtol=1e-12`, `atol=1e-14`, plus `1e-13/1e-15` convergence and independent-family check | `REFERENCE-UNRESOLVED` | No accepted convergence/error record is committed; no source-aligned likelihood-distortion reproduction is recorded. | Deterministic Gaussian-observation protocol only; no real-data or posterior claim in v0.1. |
| `FHN` FitzHugh--Nagumo | DOP853, `rtol=1e-12`, `atol=1e-14`, plus required checks | `REFERENCE-UNRESOLVED` | No accepted per-model reference gate or completed paired campaign is recorded. | Current manifest does not establish applicability to all fast/slow systems; this model alone cannot support a general claim. |
| `LV` Lotka--Volterra | DOP853, `rtol=1e-12`, `atol=1e-14`, plus required checks | `REFERENCE-UNRESOLVED` | No accepted convergence record or inference comparison is recorded. | Long-horizon/cyclic behavior beyond the declared grid is out of scope. |
| `LOR` Lorenz | DOP853, `rtol=1e-12`, `atol=1e-14`, plus required checks | `REFERENCE-UNRESOLVED` | No accepted reference gate or statistical-summary analysis is recorded. | Trajectory divergence in a chaotic system cannot by itself be interpreted as scientific-output error. |
| `ROB` Robertson kinetics | BDF, `rtol=1e-12`, `atol=1e-14`, plus required checks | `REFERENCE-UNRESOLVED` | No accepted stiff-reference convergence record or completed budget comparison is recorded. | The declared stiff-system result cannot be generalized to all stiff ODEs. |

`REFERENCE-UNRESOLVED` is a quality gate, not a claim that the configured
solver is inaccurate. Until it is closed for a model, that model cannot be
used to support a superiority claim under protocol v0.1.

## 3. Baseline-better and budget gates

| Gate | Current status | Evidence boundary | Required interpretation |
|---|---|---|---|
| NUMERIS better than standard solver | `NOT-ESTABLISHED` | No committed result table or paired confidence interval demonstrates improvement on the manifest's primary endpoints. | Do not claim superiority, non-inferiority, or a publication-grade effect. |
| Standard solver better than NUMERIS | `NOT-ESTABLISHED` | No completed full paired campaign is committed that could support a baseline-better conclusion. | Do not claim a negative numerical effect beyond the absence of established evidence. |
| Mixed/metric trade-off | `NOT-ESTABLISHED` | No completed campaign records both primary endpoints, calibration, failure rate, and budget-violation rate together. | If later observed, preserve both improved and worsened metrics; do not collapse them into one score. |
| Full frozen campaign | `BUDGET-EXHAUSTED/INCOMPLETE` | The strict audit records `3000 planned`, `2 admitted`, and `bounded_incomplete` for the bounded campaign. | This is an incomplete execution record, not a measured performance result and not a zero-error outcome. |
| Per-run hard budget | `PROTOCOL-REQUIRED; OUTCOME-INCOMPLETE` | The protocol and hard-budget orchestration define preflight rejection and retained over-budget/failure statuses, but no full campaign result denominator is committed here. | Failed, rejected, interrupted, and over-budget cases must remain in the denominator of a future report. |
| C++ necessity gate | `KEEP_PYTHON` / `APPLICABILITY-LIMIT` | The fail-closed profiling gate requires hotspot, numerical equivalence, warm-up speedup, memory, and reproducibility evidence; the repository records no complete C++ evidence package. | No production C++ speed or superiority claim is allowed. Python remains the applicable implementation for v0.1. |

The budget status must not be converted into a numerical result. A bounded
runner proving that a campaign can stop safely is not the same as a completed
equal-budget scientific comparison.

## 4. Declared applicability limits

The following limits are directly declared by protocol v0.1 and therefore are
not negative numerical findings:

1. Claims are limited to deterministic, parameterized ODE initial-value
   problems and the five named model factories.
2. Gaussian synthetic observations are included; real experimental data are
   excluded.
3. PDE, DAE, SDE, delay, hybrid, and discontinuous right-hand-side models are
   excluded.
4. PyMC/NumPyro MCMC and scientific posterior claims are excluded until a
   separate Bayesian protocol is frozen.
5. DALTON and probabilistic-ODE superiority claims are excluded from v0.1.
6. C++ implementation and speed claims are excluded unless the fail-closed
   evidence gate is completed.
7. Wall-clock comparisons across different machines are excluded.
8. A result from one model, seed, noise level, or tolerance cannot be promoted
   to a general applicability claim.

## 5. Evidence-preservation rules

- No numerical value is entered here unless it is already present in a
  committed, source-identifiable result record.
- A citation, source repository, API, unit test, or smoke test does not count
  as a numerical reproduction.
- `REFERENCE-UNRESOLVED`, `NOT-REPRODUCED`, `BLOCKED`, and
  `BUDGET-EXHAUSTED/INCOMPLETE` remain visible in future summaries.
- Failed, non-converged, rejected, interrupted, and over-budget cases must not
  be deleted or silently replaced.
- Any changed factor requires a new protocol version and must retain this
  record as historical evidence.

## Current decision

`RESEARCH FOUNDATION OPEN — NEGATIVE/UNRESOLVED EVIDENCE PRESERVED`.

The repository currently supports a reproducibility boundary and a falsifiable
experiment protocol. It does not support a claim that NUMERIS is novel,
superior, inferior, or publication-ready.
