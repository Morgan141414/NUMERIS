# NUMERIS frozen experiment manifest v0.1

Status: **FROZEN**  
Manifest date: 2026-10-30 (Asia/Almaty)  
Protocol owner: Amanat Korgan  
Parent protocol: `EXPERIMENT_PROTOCOL.md`  
Manifest purpose: make every factor needed to reproduce the first deterministic validation campaign explicit before results are inspected.

This manifest is a binding configuration record for protocol v0.1. A result produced with a different value is out of protocol and must be reported as an exploratory deviation. Freezing this manifest does not establish novelty, superiority, or publication readiness.

## 1. Inclusion and exclusion boundary

Included:

- deterministic, parameterized ODE initial-value problems;
- the five model factories named in Section 2;
- synthetic observations generated from the declared reference solution;
- Gaussian observation noise;
- solver configurations in Section 3;
- paired comparisons using the same seed, model, observations, endpoint, and budget cap;
- failed and over-budget runs, retained in the denominator.

Excluded from v0.1 claims:

- PDE, DAE, SDE, delay, hybrid, or discontinuous right-hand-side models;
- real experimental data;
- automatic model selection or solver selection learned from test outcomes;
- PyMC/NumPyro MCMC claims and posterior scientific claims;
- DALTON or probabilistic ODE superiority claims (not implemented in this protocol);
- any C++ implementation or speed claim;
- wall-clock comparisons across different machines;
- results obtained after changing this manifest.

## 2. Exact model and data configuration

All values below are in the parameter order implemented by the corresponding factory. The true parameter vector is used only to generate synthetic data and is not supplied to an inference method as an observed answer.

| ID | Factory | Initial state | Observation grid | True parameters | Noise sigma | Budget cap (RHS evaluations) |
|---|---|---|---|---|---:|---:|
| OSC | `damped_oscillator` | `[1.0, 0.0]` | `linspace(0, 20, 201)` | `[1.0, 0.1, 0.2]` | `0.01, 0.05, 0.10` | `2,000` |
| FHN | `fitzhugh_nagumo` | `[-1.0, 0.3333333333333333]` | `linspace(0, 40, 401)` | `[0.7, 0.8, 0.08, 0.5]` | `0.01, 0.05, 0.10` | `5,000` |
| LV | `lotka_volterra` | `[10.0, 5.0]` | `linspace(0, 30, 301)` | `[1.5, 1.0, 0.75, 1.0]` | `0.01, 0.05, 0.10` | `10,000` |
| LOR | `lorenz` | `[1.0, 1.0, 1.0]` | `linspace(0, 20, 401)` | `[10.0, 28.0, 2.6666666666666665]` | `0.01, 0.05, 0.10` | `20,000` |
| ROB | `robertson` | `[1.0, 0.0, 0.0]` | `geomspace(1e-6, 1e5, 301)` | `[0.04, 30000000.0, 10000.0]` | `0.01, 0.05, 0.10` | `5,000` |

Synthetic observations are generated as `observe(reference_states) + Normal(0, sigma)` with NumPy `default_rng(seed)`. The reference state is evaluated at the declared observation grid.

## 3. Exact solver configurations

Every model/noise/seed cell is run with the Cartesian product of all five methods and the four tolerance levels below. `max_step = infinity` means no user-imposed maximum step. `atol` is fixed by the table rather than derived at runtime.

| Configuration family | SciPy methods | `rtol` values | `atol` values | `max_step` |
|---|---|---|---|---:|
| Full declared grid | `RK45`, `DOP853`, `Radau`, `BDF`, `LSODA` | `1e-4`, `1e-6`, `1e-8`, `1e-10` | respectively `1e-6`, `1e-8`, `1e-10`, `1e-12` | `infinity` |

The primary analysis is predeclared as the full grid; any method/tolerance cell that fails or exceeds budget is retained as a failure and is not silently replaced by another cell.

## 4. Exact seeds and pairing

The campaign uses exactly these ten seeds, in this order:

```text
0, 1, 2, 3, 4, 5, 6, 7, 8, 9
```

For each `(model, seed)` pair, one observation array is generated and reused verbatim by every solver configuration and every declared policy arm. Seeds are not selected, removed, or replaced after seeing results. A failed trial remains a failure observation.

## 5. Reference solutions

Reference calculations are separate from scored configurations and are never charged against a solver arm's budget. They use:

- OSC, FHN, LV, LOR: `DOP853`, `rtol=1e-12`, `atol=1e-14`, `max_step=infinity`;
- ROB: `BDF`, `rtol=1e-12`, `atol=1e-14`, `max_step=infinity`.

The reference is accepted only after a two-level convergence check at `1e-12/1e-14` versus `1e-13/1e-15` and a cross-family check against the other applicable stiff/non-stiff family. If either check fails, the affected model is marked `REFERENCE-UNRESOLVED` and no superiority claim may use it.

## 6. Endpoints and decision rule

### Primary endpoints

1. **Likelihood distortion:** absolute difference between the scored negative Gaussian log-likelihood and the reference negative Gaussian log-likelihood, evaluated on the same observations and true parameter vector.
2. **Parameter RMSE:** Euclidean RMSE between estimated and true parameters for the declared parameter-recovery run.

The primary comparison is paired by `(model, seed, budget cap)`. The estimand is the mean paired difference (NUMERIS minus baseline), with a two-sided 95% bootstrap confidence interval over the ten seeds. A smaller value is better for both endpoints.

### Secondary endpoints

- false-optimum rate, only for a separately declared likelihood-surface run;
- posterior distance, only if a separately frozen Bayesian protocol is added;
- RHS evaluations, runtime, peak RSS;
- failure rate and budget-violation rate;
- reliability calibration coverage and mean excess, only when an error estimate is emitted.

### Decision rule

The v0.1 result is **positive for a declared applicability class** only if all conditions hold:

1. both primary endpoints improve versus the matched standard baseline, or one improves and the other is non-inferior under a predeclared margin of 5%;
2. the upper 95% CI for the primary paired difference is below zero for an improvement claim, or lies within the 5% non-inferiority margin for a non-inferiority claim;
3. failure rate and budget-violation rate are not higher by more than 5 percentage points;
4. reliability calibration does not fail when the controller reports an error estimate;
5. the result is not confined to one hand-picked seed or one post hoc factor level.

If any condition fails, report **NO CONFIRMED ADVANTAGE** and preserve the negative or mixed result. No novelty claim is permitted under this manifest.

## 7. Deviations and freeze record

Protocol v0.1 is frozen on 2026-10-30 before the validation campaign. Any change requires a new versioned manifest, a reason, and a separate analysis; it must not overwrite this file. The first results generated under this manifest must record the manifest path and commit hash.

