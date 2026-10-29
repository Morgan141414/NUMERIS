# Research Foundation: literature and gap matrix

Status: initial evidence-backed review. The review is governed by `INCLUSION_EXCLUSION_PROTOCOL.md`; it is not a claim of completeness or novelty.

## Controlled artifacts

- [Inclusion/exclusion protocol](INCLUSION_EXCLUSION_PROTOCOL.md)
- [Bibliography ledger](BIBLIOGRAPHY_LEDGER.md)
- [Comparison matrix](COMPARISON_MATRIX.md)

## Primary related work

| Work | Established contribution | Consequence for NUMERIS | Source |
|---|---|---|---|
| Cao & Petzold (2004) | Adjoint-based a posteriori error estimation and global error control for ODE initial-value problems | Adjoint error estimation is prior art; NUMERIS cannot claim it as its own contribution | [SIAM DOI](https://doi.org/10.1137/S1064827503420969) |
| Lang & Verwer (2007) | Global error estimation/control comparison using adjoint and variational approaches | Goal-oriented global control has additional prior art | [SIAM DOI](https://doi.org/10.1137/050646950) |
| Chkrebtii et al. (2016) | Bayesian treatment of numerical uncertainty in differential-equation models | Probabilistic numerical uncertainty and Bayesian calibration are established | [Bayesian Analysis DOI](https://doi.org/10.1214/15-BA956) |
| Bosch, Hennig & Tronarp (2021) | Calibrated adaptive probabilistic ODE solvers | Reliability calibration is an existing research direction; NUMERIS must compare or clearly distinguish its target | [PMLR](https://proceedings.mlr.press/v130/bosch21a.html) |
| Krämer & Hennig (2024) | Stable implementation of high-order probabilistic ODE solvers | Probabilistic solvers are practical baselines, not a future-only concept | [JMLR](https://www.jmlr.org/papers/volume25/20-1423.html) |
| Wu et al. (2024), DALTON | Data-adaptive probabilistic likelihood approximation for ODE parameter inference | Likelihood-aware parameter inference already has a close competitor | [PMLR](https://proceedings.mlr.press/v238/wu24b.html) |
| Tiemann et al. (2024) | Empirical analysis of ODE solver error distorting likelihood surfaces and creating phantom optima | The motivating problem is published; NUMERIS must reproduce/extend rather than rediscover it | [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10914510/) |

## Mechanism comparison

| Mechanism | What it controls | What NUMERIS still has to establish |
|---|---|---|
| Classical adaptive solver | Local/trajectory integration error | Whether target-aware allocation improves a declared inference target at equal cost |
| Adjoint/global error control | Goal-oriented functional error in the numerical solution | A non-equivalent target-and-budget policy, if one exists |
| Probabilistic ODE solver | Distribution over numerical solution/error | Whether its uncertainty is propagated and calibrated for the selected inference endpoint |
| DALTON/likelihood-aware methods | Approximate likelihood and parameter sensitivity | A distinct, reproducible mechanism and fair baseline comparison |
| NUMERIS-GO prototype | Sensitivity-weighted refinement and budget ranking | Validity, calibration, temporal allocation, equal-budget benefit, and non-redundancy |

## Research gap statement (provisional)

The review does **not** establish a new gap. It identifies a conditional research question:

> Under a fixed computational budget and a declared inference target, can a transparent target-error estimator plus temporal budget allocation provide a measurable benefit over correctly tuned trajectory-error control and existing likelihood/probabilistic baselines for a specified ODE class?

This question is only publishable if the final mechanism is not equivalent to prior goal-oriented/likelihood-aware control and if controlled experiments show a robust, cost-normalized effect. A negative answer remains a valid project outcome.

## Phase-I exit criteria

- [x] Primary related-work ledger with direct sources.
- [x] Explicit separation of established mechanisms and the NUMERIS hypothesis.
- [x] Provisional research-gap question.
- [ ] Systematic inclusion/exclusion protocol and complete bibliography.
- [ ] Reproduction of the closest inference-distortion baseline.
- [ ] Final novelty decision after mathematical mechanism is fixed.
