# Closest-baseline source-aligned reproduction status

Status: evidence record for Research Foundation, checked 2026-10-30.
Repository commit at inspection: `d520237`.

This record is a source audit and local reproducibility status record. It does
not report a numerical reproduction, establish equivalence, or support a
novelty/superiority claim. The artifact is considered exact only at the level
identified below; a paper, supplement, or reference implementation is not
treated as a reproduced result until its model, algorithm, inputs, tolerances,
stopping rules, metrics, and cost accounting are matched.

## Status vocabulary used here

The statuses follow `BASELINE_REPRODUCTION_MANIFEST_v0.1.md`:

- `R0`: source and mechanism extraction only;
- `R1`: local source-compatible smoke test;
- `R2`: source-aligned numerical reproduction with declared deviations;
- `R3`: matched source benchmark;
- `NOT-REPRODUCED`: no local reproduction and no confirmed hard blocker;
- `BLOCKED`: the next tier is blocked by a checkable source, dependency, or protocol condition;
- `CONCEPTUAL-BASELINE`: a local analogue is not a reproduction of the named method.

## Summary

| Baseline | Source artifact(s) | Local status | Public wording allowed now | Next evidence |
|---|---|---|---|---|
| ADJ-GLOBAL | Cao--Petzold 2004; Lang--Verwer 2007 | `R0` | “Primary adjoint/global-error prior art identified; not reproduced locally.” | Source-equation extraction, mapping to one scalar functional, then R1 estimator smoke record. |
| GO-FUNCTIONAL | Adjoint/global-error papers as mechanism sources; no single named package | `CONCEPTUAL-BASELINE` | “Conceptual functional-control comparator; named goal-oriented method not reproduced.” | Freeze functional and decision rule, implement source-aligned estimator or retain conceptual label, then calibration and negative weak-coupling case. |
| LIKELIHOOD-DISTORTION | Creswell et al. 2024 article and official supplementary material | `NOT-REPRODUCED` | “Published motivation identified; source-aligned local reproduction is pending.” | Match oscillator likelihood setup, fixed parameter grid, solver accuracies, metrics, and failed-run denominator; retain the record. |
| DALTON | Wu--Lysy 2024 paper and authors’ `mlysy/rodeo` repository | `BLOCKED` | “DALTON is a nearest comparator; local reproduction is blocked by the recorded environment/protocol condition.” | Pin a source-compatible `rodeo` revision and JAX environment, then match one DALTON benchmark before any comparison. |
| PROB-ODE | Hennig--Hauberg 2014; Chkrebtii et al. 2016; Bosch--Hennig--Tronarp 2021 | `BLOCKED` | “Probabilistic ODE literature baseline; excluded from deterministic v0.1 claims.” | Create a separate versioned probabilistic protocol and implementation/version record, then assess calibration and matched cost. |

## Detailed status records

### ADJ-GLOBAL — R0

**Exact source artifacts.**

- Cao and Petzold, *A Posteriori Error Estimation and Global Error Control
  for Ordinary Differential Equations by the Adjoint Method*, SIAM J.
  Sci. Comput. 26(2), 359--374 (2004): [publisher record and DOI](https://doi.org/10.1137/S1064827503420969), [open author manuscript](https://escholarship.org/content/qt3c59x9vs/qt3c59x9vs_noSplash_33d58690c175080060ac29f9f2252c0a.pdf).
- Lang and Verwer, *On Global Error Estimation and Control for Initial Value
  Problems*, SIAM J. Sci. Comput. 29(4), 1460--1475 (2007): [DOI](https://doi.org/10.1137/050646950).

The primary sources establish adjoint/variational global-error estimation and
control. The checked artifacts are publications, not a verified executable
reference implementation or a source benchmark bundle.

**Local reproducibility status.** `R0`. The ledger and plan identify the
mechanism, but no source-aligned estimator record exists under
`research/protocol/` and no local run is being promoted to R1.

**Blocker.** The target scalar functional, adjoint discretisation, source
assumptions, tolerance proportionality, and cost accounting have not yet been
transcribed into a frozen local reproduction record. A generic SciPy solve is
not sufficient evidence.

**Allowed public wording.** “NUMERIS has identified Cao--Petzold and
Lang--Verwer as primary adjoint/global-error prior art.” Do not say that
NUMERIS reproduces, improves, or is distinct from these methods.

**Next evidence.** Add a dated extraction note with equations and assumptions;
choose one smooth and one stiff model, one scalar functional, and a reference;
then add an R1 record containing estimator error, reference error, tolerance,
RHS-equivalent cost, and failures.

### GO-FUNCTIONAL — CONCEPTUAL-BASELINE

**Exact source artifacts.** The relevant source mechanism is the functional or
goal-oriented use of adjoint/dual information described in the Cao--Petzold
paper and its cited goal-oriented ODE discussion, together with the
Lang--Verwer global-control comparison. There is no single canonical package
or one uniquely reproducible benchmark attached to this family in the checked
sources.

**Local reproducibility status.** `CONCEPTUAL-BASELINE`. A sensitivity-weighted
policy can serve as a local diagnostic comparator, but it is not evidence of a
source-aligned adjoint estimator or theorem.

**Blocker.** The functional-to-refinement/allocation map and its discretisation
are not frozen against a named source. Calling the local heuristic a
goal-oriented reproduction would overstate the evidence.

**Allowed public wording.** “A conceptual functional-control comparator is
included for overlap analysis.” Do not call it a reproduction of an adjoint or
goal-oriented method.

**Next evidence.** Freeze the functional, local-defect signal, decision rule,
tolerance grid, equal-budget rule, and negative weak-coupling case before
running results. If the source-aligned estimator cannot be implemented, retain
this status and report the deviation explicitly.

### LIKELIHOOD-DISTORTION — NOT-REPRODUCED

**Exact source artifacts.** Creswell et al., *Understanding the Impact of
Numerical Solvers on Inference for Differential Equation Models*, J. R. Soc.
Interface 21(212), 20230369 (2024): [publisher DOI](https://doi.org/10.1098/rsif.2023.0369), [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10914510/), and the article’s [official supplementary-material record](https://doi.org/10.6084/m9.figshare.c.7075553).

The full text specifies, among other cases, a damped driven oscillator with
synthetic Gaussian observations and likelihood surfaces under different solver
accuracies. The supplementary record is the exact companion artifact to check
for source data, code, and detailed parameter tables; it is not assumed to be
locally reproduced merely because the paper is accessible.

**Local reproducibility status.** `NOT-REPRODUCED`. No source-aligned local
record currently demonstrates matched inputs, solver settings, grid, metrics,
or failed-run accounting.

**Blocker.** The NUMERIS oscillator configuration is not identical to the
source setup by default, and no manifest-versioned mapping from the source
oscillator/likelihood experiment to the local protocol has been recorded.

**Allowed public wording.** “Creswell et al. provide published motivation for
testing solver-induced likelihood distortion; NUMERIS has not yet reproduced
that benchmark.”

**Next evidence.** Record the supplementary artifact contents and version/date;
freeze the source-aligned model, observation times, noise, parameter slice,
solver accuracies, likelihood metric, reference, seeds, and failure denominator;
then run and archive the result without dropping non-converged cases.

### DALTON — BLOCKED

**Exact source artifacts.** Wu and Lysy, *Data-Adaptive Probabilistic
Likelihood Approximation for Ordinary Differential Equations*, AISTATS/PMLR
238:1018--1026 (2024): [paper and PDF](https://proceedings.mlr.press/v238/wu24b.html).
The authors’ public implementation artifact is [mlysy/rodeo](https://github.com/mlysy/rodeo), whose README identifies the `dalton` likelihood
approximation and the paper it implements. The repository’s current default
branch is not treated as a pinned source revision.

**Local reproducibility status.** `BLOCKED`. At inspection, the project
environment did not provide `jax` or `rodeo` (`find_spec` checks in the local
`.venv` returned false). No source-compatible DALTON benchmark was run.

**Blocker.** The local environment lacks the implementation/runtime needed to
execute the named artifact, and no pinned repository revision, dependency lock,
source benchmark inputs, or stopping-rule mapping has yet been recorded. This
is an environment/protocol blocker, not a claim that the artifact cannot be
installed.

**Allowed public wording.** “DALTON is the nearest likelihood-aware
comparator; local reproduction is currently blocked by an unpinned
source-compatible environment.” Do not substitute the NUMERIS Bayesian grid
helper and call it DALTON.

**Next evidence.** Pin a `rodeo` commit/tag and compatible JAX/Python
environment; record installation and import checks; map one published DALTON
benchmark’s observation model, parameterisation, priors/objective, stopping
rules, metrics, and cost; then preserve all failures and deviations.

### PROB-ODE — BLOCKED

**Exact source artifacts.** The v0.1 card covers multiple probabilistic-ODE
families and therefore has no single exact implementation target:

- Hennig and Hauberg (2014), [PMLR paper](https://proceedings.mlr.press/v33/hennig14.html);
- Chkrebtii et al. (2016), [Project Euclid full record](https://projecteuclid.org/journals/bayesian-analysis/volume-11/issue-4/Bayesian-Solution-Uncertainty-Quantification-for-Differential-Equations/10.1214/16-BA1017.full);
- Bosch, Hennig, and Tronarp (2021), [PMLR paper](https://proceedings.mlr.press/v130/bosch21a.html).

For a potential implementation artifact, `probdiffeq` is a relevant public
software project ([repository](https://github.com/pnkraemer/probdiffeq)), but it
must not be presented as a reproduction of all three papers without a
paper-to-code mapping.

**Local reproducibility status.** `BLOCKED`. Probabilistic ODE methods are
explicitly outside deterministic protocol v0.1, and no separate versioned
probabilistic protocol or calibrated source-aligned run exists.

**Blocker.** The baseline family is heterogeneous: posterior construction,
interrogation model, calibration target, and cost definitions differ by source.
Combining them into the deterministic v0.1 comparison would be methodologically
invalid.

**Allowed public wording.** “Probabilistic ODE methods are relevant prior art
and are excluded from deterministic v0.1 claims; no local reproduction is
claimed.”

**Next evidence.** Select one source and one implementation target, create a
new versioned probabilistic protocol, specify calibration and uncertainty
metrics, pin the environment, and compare under a separately defined matched
budget.

## Decision

`RESEARCH FOUNDATION REMAINS OPEN / NO REPRODUCTION CLAIM AUTHORIZED`.

The source check confirms that the current manifest names real and relevant
primary artifacts. It does not close Phase I: no baseline has reached R2 or R3,
and the DALTON/PROB-ODE entries require separate environment/protocol gates.
