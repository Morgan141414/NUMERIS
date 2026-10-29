# NUMERIS predeclared experiment protocol v0.1

Status: protocol draft for review; no result is accepted as evidence until this file is frozen before the corresponding run.

## Scope

Deterministic parameterized ODEs with Gaussian observation noise on a local Apple Silicon/macOS-compatible Python environment. Models: damped oscillator, FitzHugh–Nagumo, Lotka–Volterra, Lorenz, Robertson. The primary deterministic target is likelihood error at a fixed RHS-evaluation budget; parameter RMSE is a co-primary endpoint for parameter-recovery runs. Posterior distances are secondary until the Bayesian sampler protocol is implemented.

## Fixed factors

- seeds: `0, 1, 2, 3, 4, 5, 6, 7, 8, 9`;
- noise levels: `sigma ∈ {0.01, 0.05, 0.10}` in model-output units;
- solver baselines: RK45, DOP853, Radau, BDF, LSODA where applicable;
- tolerance grid: `rtol ∈ {1e-4, 1e-6, 1e-8, 1e-10}`, with `atol = rtol * 1e-2` unless the model declares otherwise;
- budgets: fixed RHS-evaluation caps selected after a pilot run and reported before comparison;
- reference: tolerance-convergence plus an independent solver family; a strict tolerance alone is never labelled exact.

## Required comparisons

1. Standard adaptive solver at each tolerance.
2. NUMERIS target-error baseline with the same solver and budget.
3. Sensitivity-aware policy with estimator-only, allocation-only, stopping-only, and full-policy ablations.
4. A failed/over-budget run is retained and counted, not removed.

## Metrics

Primary: likelihood distortion and parameter RMSE at matched RHS budget.

Secondary: false-optimum rate, posterior distance when Bayesian support is complete, runtime, RHS evaluations, peak RSS, failure rate, calibration coverage, mean excess, and memory/maintenance cost for any optional C++ kernel.

## Decision rules

- Report paired seed-wise differences and confidence intervals.
- A positive result requires improvement on a primary endpoint without unacceptable failure/calibration degradation and must survive all declared model/noise/budget factors or state its applicability class.
- If a tuned baseline is equal or better, record a negative result.
- If the controller is overconfident, it fails the reliability claim even if mean target error is small.
- No novelty or superiority claim is allowed before the literature gap review and mechanism comparison are complete.

## C++ profiling gate

Before adding C++, run the Python workload profiler on representative benchmark configurations. A C++ kernel is justified only if a reproducible hot spot is identified, its interface can be isolated, numerical equivalence can be tested, and the measured speed/memory benefit outweighs build and reproducibility cost. Otherwise retain Python and record the negative profiling result.

## Current status

This protocol is not yet frozen. The next exit criterion is a signed/committed configuration manifest plus converged references for all five model families.
