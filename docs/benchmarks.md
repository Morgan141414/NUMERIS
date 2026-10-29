# Benchmark protocol

Each benchmark run must identify the model, true parameters, observation grid, noise standard deviation and seed, solver method, `rtol`, `atol`, budget, and reference provenance. The runner records success, message, RHS evaluations, runtime, trajectory RMSE against the reference, and target likelihood error.

The mandatory families are the damped oscillator, FitzHugh–Nagumo, Lotka–Volterra, Lorenz, and Robertson kinetics. Robertson is expected to expose the distinction between explicit and stiff solvers. Lorenz trajectory divergence is not by itself a failure: report target statistics and parameter/inference metrics separately.

Comparisons must use matched budgets and include tuned standard baselines. Every claimed improvement needs repeated seeds, uncertainty summaries, and an ablation removing each controller component.
