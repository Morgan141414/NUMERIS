# Minimal API

```python
import numpy as np
from numeris.benchmarks import damped_oscillator
from numeris.solvers import solve_ode
from numeris.inference import gaussian_negative_log_likelihood

model = damped_oscillator()
result = solve_ode(model, np.array([1.0, 0.1, 0.0]), method="DOP853")
nll = gaussian_negative_log_likelihood(result.states, result.states, sigma=0.05)
```

For matched comparisons use `SolverConfig` and `run_benchmark`. For bounded studies pass a `BudgetLedger`; for publication-ready runs serialize `ReproducibilityMetadata` beside the numerical results.
