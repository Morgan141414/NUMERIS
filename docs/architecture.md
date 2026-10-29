# Architecture

`models` defines ODE contracts. `solvers` adapts established numerical methods and records cost. `inference` computes declared scientific targets. `error_analysis` compares candidates against references. `budget` accounts for resource constraints. `controller` contains falsifiable policies. `benchmarks` runs matched comparisons. `reproducibility` records execution context. `visualization` renders analysis artifacts without changing numerical results.

The layers are intentionally independent: a controller may consume diagnostics from any solver, and a benchmark can compare controller policies without replacing SciPy's integrators.
