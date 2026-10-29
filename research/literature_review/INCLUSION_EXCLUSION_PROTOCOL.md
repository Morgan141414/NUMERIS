# NUMERIS literature review: inclusion and exclusion protocol

Status: active protocol for the Research Foundation phase; source verification ledger updated 2026-10-30. This document is a review protocol, not a claim of systematic-review registration or completeness.

## 1. Review objective

The review maps methods and software relevant to controlling numerical error in parameterized ODE workflows where the downstream target is a scientific inference quantity. The review is intended to answer:

1. Which mechanisms already control local, global, functional, likelihood, posterior, or parameter-estimation error?
2. Which mechanisms allocate computational effort or adapt solver accuracy using a downstream target?
3. Which methods and software are realistic baselines for a deterministic ODE laboratory on macOS/Apple Silicon?
4. Which statements about NUMERIS remain hypotheses rather than established facts?

The review explicitly does **not** attempt to prove novelty, superiority, or publication suitability.

## 2. Scope and review units

The unit of analysis is a primary research publication, a primary software paper, or official first-party technical documentation for a maintained solver/library. A single work may occupy multiple categories.

### Included topic families

- adaptive step-size and error control for ODE initial-value problems;
- global, adjoint, variational, functional, and goal-oriented error estimation/control;
- probabilistic numerical methods and probabilistic ODE solvers;
- Bayesian inverse problems and numerical-discretization uncertainty;
- numerical solver error in likelihood, posterior, or parameter inference;
- likelihood-aware ODE methods, including DALTON;
- primary descriptions of SciPy, SUNDIALS/CVODE/CVODES, and SciML/DifferentialEquations.jl relevant to ODE solving, sensitivities, or solver selection.

### Population and setting

Parameterized deterministic ODEs, including stiff and non-stiff initial-value problems, with possible Gaussian or non-Gaussian observations and downstream parameter inference.

### Outcomes extracted

- controlled quantity and mathematical estimator;
- downstream target, if any;
- adaptation/allocation rule;
- uncertainty representation and calibration;
- computational complexity or cost accounting;
- benchmark models and comparison baselines;
- software availability and reproducibility evidence;
- explicit limitations and failure conditions.

## 3. Search strategy

### Sources searched

The ledger prioritizes publisher pages, official proceedings, official journal pages, official project documentation, and first-party repositories. Search engines are used only to locate the primary record; the primary record is the cited source.

### Search concepts

The following concept groups are combined with Boolean AND/OR variants:

- `ODE OR ordinary differential equation OR initial value problem`;
- `adaptive step size OR local error OR global error OR error control`;
- `adjoint OR variational OR goal-oriented OR functional error`;
- `probabilistic ODE OR probabilistic numerical OR numerical uncertainty`;
- `Bayesian inverse OR parameter inference OR likelihood OR posterior`;
- `solver error OR discretization error OR phantom optimum OR likelihood distortion`;
- `DALTON`, `SciPy solve_ivp`, `SUNDIALS CVODE CVODES`, `SciML DifferentialEquations.jl`.

### Search and screening log

Every candidate is recorded in `BIBLIOGRAPHY_LEDGER.md`, including the source URL, category, screening decision, and reason. The current ledger is an initial evidence set; it must be extended before any claim of completeness.

## 4. Inclusion criteria

A candidate is included in the core comparison matrix when **all** of the following hold:

1. It is a primary source for the method, experiment, or software capability being asserted.
2. It addresses ODE/IVP numerical computation, uncertainty, error control, or downstream inference relevant to NUMERIS.
3. The source provides enough methodological detail to extract at least one of: controlled quantity, target, adaptation rule, uncertainty model, cost, or limitation.
4. The bibliographic identity and a stable direct link can be verified.

A source may be included in the extended ledger but excluded from the matrix if it is useful background yet does not provide a comparable mechanism or experimental result.

## 5. Exclusion criteria

Exclude from the core evidence set:

- secondary surveys, blog posts, vendor summaries, or search-result pages when a primary source is available;
- papers about PDE/DAE/SDE methods with no transferable ODE/IVP content;
- purely analytical ODE theory with no relevant error-control, uncertainty, or inference consequence;
- software tutorials or examples that do not establish a solver capability;
- duplicate versions of the same work, unless the later version contains materially different evidence;
- sources whose claims cannot be checked from the linked primary record;
- benchmarks that compare only wall-clock time without defining numerical accuracy or downstream target accuracy;
- claims about novelty or priority inferred only from absence of search hits.

Excluded records are not deleted: they should be logged with `EXCLUDED` and a reason so that screening remains auditable.

## 6. Screening and extraction procedure

For each candidate:

1. Verify title, authors, venue/year, and persistent identifier.
2. Read the abstract and method/results sections needed for extraction.
3. Record the mathematical object being controlled: local defect, trajectory/global state error, functional, likelihood, posterior, or parameter estimate.
4. Record whether the method changes the solver, represents uncertainty, changes the likelihood, or only diagnoses error.
5. Record cost measures and whether comparisons are budget-matched.
6. Record limitations and conditions under which the method may fail.
7. Assign `INCLUDED`, `EXTENDED`, or `EXCLUDED` with a one-sentence decision reason.

## 7. Quality and evidence labels

- `P1`: peer-reviewed primary method paper or official proceedings paper with reproducible methodological detail.
- `P2`: primary software paper or official first-party documentation.
- `P3`: primary preprint or repository used only when no final record is available; not treated as stronger than a peer-reviewed record.
- `EVIDENCE-A`: directly demonstrates the extracted claim in the source.
- `EVIDENCE-B`: supports a capability or context but does not establish downstream superiority.
- `HYPOTHESIS`: a NUMERIS question requiring new experiments.

No `P1` or `P2` source is interpreted as evidence that NUMERIS is novel. The matrix records overlap and unresolved comparison requirements.

### Source verification status

The bibliography ledger now records a verification status for every entry:

- `VERIFIED-DIRECT`: the cited publisher, proceedings, official documentation, or first-party record was opened and the identity plus the extracted capability/claim was visible in the record;
- `VERIFIED-PRIMARY-INDEX`: the persistent DOI or official primary index was resolved, and the title/authors/abstract or official capability record was verified through the primary index or an authoritative record when the publisher page was inaccessible;
- `UNVERIFIED`: identity or extracted claim still requires source-level checking and must not be used as evidence.

Verification date is recorded in ISO format. A verification status does not mean that NUMERIS reproduced the source or that the source supports a superiority claim.

## 8. Update and stopping rule

The review remains open until each required category has:

- at least two primary method sources where the category is mature;
- at least one official software source for SciPy, SUNDIALS, and SciML;
- a documented search date and query family;
- a verification status and date for every ledger entry;
- an explicit list of unresolved nearest-neighbour comparisons.

The review may be frozen only by recording a date, ledger revision, and a signed/committed protocol version. Freezing the review does not imply that the research gap is real.

## 9. Current review boundary

The current evidence set is sufficient to establish that adaptive ODE control, adjoint/global error control, probabilistic numerical ODE methods, Bayesian inverse-problem theory, likelihood distortion, DALTON, and major solver ecosystems are established research or software areas. It is not sufficient to establish a unique NUMERIS mechanism or a performance advantage.
