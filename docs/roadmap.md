# Implementation roadmap

The repository is organized around a falsifiable vertical slice.

## Completed foundation

- parameterized ODE model contract;
- instrumented SciPy solver adapter;
- Gaussian likelihood and deterministic parameter fitting;
- trajectory diagnostics and posterior-distance primitives;
- oscillator smoke benchmark;
- local-only specification boundary and publication safety check.

## Next executable milestones

1. Run all five model families over a fixed matrix of solvers, tolerances, noise seeds, and budgets.
2. Validate references by tolerance convergence and an independent solver where available.
3. Add a budget ledger around RHS calls, runtime, and repeat count.
4. Implement the goal-oriented controller as a plug-in policy and compare it with standard adaptive control.
5. Add posterior experiments only after deterministic likelihood distortion is characterized.
6. Publish tables, plots, raw configuration, and negative results together.

No item in this roadmap is a claim that NUMERIS is novel or superior. Those are outcomes to be tested.
