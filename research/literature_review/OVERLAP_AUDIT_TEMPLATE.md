# NUMERIS overlap-audit template

Status: **TEMPLATE ONLY — `GAP-UNRESOLVED`**.

This document is a fillable, source-aligned comparison template. It does not
establish a research gap, novelty, superiority, or publication result. A row
may be completed only from a primary source, an official implementation, or a
retained local evidence record. Similar terminology or a different software
API is not evidence of a distinct mechanism.

## 1. Audit identity

| Field | Value |
|---|---|
| Audit ID | `OA-<source>-<date>-<revision>` |
| Comparator/source ID | `<bibliography ledger ID>` |
| Primary source / official artifact | `<DOI, URL, version, commit>` |
| NUMERIS protocol | `<path and version>` |
| Audited NUMERIS code revision | `<commit>` |
| Auditor | `<name/role>` |
| Evidence tier | `R0 / R1 / R2 / R3 / NOT-REPRODUCED / BLOCKED` |
| Overall classification | `same / known modification / unclear / potentially distinct` |
| Current gate status | **`GAP-UNRESOLVED`** until all required evidence is reviewed |

## 2. Source-aligned mechanism record

Complete every field from the source before comparing it with NUMERIS. Write
`UNKNOWN` when the source or local artifact does not support a determination;
do not infer a mechanism from a name or abstract alone.

| Component | Source mechanism and evidence location | NUMERIS candidate and evidence location | Classification | Open falsification test | Evidence status |
|---|---|---|---|---|---|
| Estimator | Equation/pseudocode, controlled error object, assumptions, source page/section | Equation/pseudocode and implementation path | `same / known modification / unclear / potentially distinct` | What matched derivation or numerical test could show equivalence? | `missing / partial / complete` |
| Sensitivity source | Adjoint, variational, finite difference, AD, probabilistic update, or `UNKNOWN`; cost and stability | Exact source of sensitivity and its error/cost | same / known modification / unclear / potentially distinct | Match source and compare sensitivity error and cost | missing / partial / complete |
| Allocation rule | How steps, tolerances, observations, or evaluations are allocated | NUMERIS ranking/refinement/budget rule | same / known modification / unclear / potentially distinct | Equal-budget comparison with identical target and candidates | missing / partial / complete |
| Stopping rule | Stopping condition, thresholds, failure behavior | NUMERIS stopping condition and trace | same / known modification / unclear / potentially distinct | Tolerance/budget sweep with independent target-error reference | missing / partial / complete |
| Uncertainty representation | Deterministic bound, interval, posterior, calibration, or none | NUMERIS error object and calibration claim | same / known modification / unclear / potentially distinct | Compare target, coverage, overconfidence, and failure cases | missing / partial / complete |
| Cost model | RHS calls, adjoint/variational calls, runtime, memory, setup cost | NUMERIS accounting and excluded costs | same / known modification / unclear / potentially distinct | Reproduce costs under the frozen budget contract | missing / partial / complete |
| Downstream target | State norm, scalar functional, likelihood, parameter, posterior, or other endpoint | Declared NUMERIS endpoint and observation model | same / known modification / unclear / potentially distinct | Match target and measure endpoint error against reference | missing / partial / complete |

## 3. Required evidence checklist

- [ ] Primary source and exact implementation revision are recorded.
- [ ] Source equations or pseudocode are transcribed with locations.
- [ ] NUMERIS equations/pseudocode are frozen before comparative results.
- [ ] Model, data, parameterisation, tolerances, seeds, and budget are fixed.
- [ ] Sensitivity computation and its cost are explicitly recorded.
- [ ] Independent reference construction is documented.
- [ ] Failed, non-converged, blocked, and over-budget cases are retained.
- [ ] Numerical and statistical uncertainty are not conflated.
- [ ] Equal-budget accounting includes all relevant source and NUMERIS work.
- [ ] Classification is supported by evidence, not by naming similarity.
- [ ] `potentially distinct` is explicitly treated as a hypothesis, not novelty.
- [ ] Allowed and prohibited public wording is recorded.

## 4. Decision record

| Decision field | Entry |
|---|---|
| Evidence reviewed | `<artifact paths, hashes, source locations>` |
| Matched components | `<list>` |
| Unresolved components | `<list>` |
| Negative or failed cases | `<list>` |
| Final component classifications | `<same / known modification / unclear / potentially distinct>` |
| Permitted wording | `<evidence-limited statement>` |
| Prohibited wording | `novel`, `first`, `superior`, `publication-ready`, unless separately authorized by evidence gates |
| Gate outcome | `REMAIN UNRESOLVED / PROCEED / REFRAME / STOP-NEGATIVE RESULT` |
| Review date and reviewer | `<date / reviewer>` |

The overall research-gap status remains:

> **`RESEARCH GAP CLOSURE OPEN / GAP-UNRESOLVED`**

It may be changed only through the exit criteria in
`RESEARCH_GAP_CLOSURE_EXIT_CRITERIA.md`, after source-aligned evidence is
retained and independently reviewed.
