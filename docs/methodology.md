# Methodology

The initial NUMERIS protocol separates three quantities:

1. trajectory discrepancy against an independently tightened reference;
2. discrepancy in a declared scientific target such as Gaussian negative log-likelihood;
3. computational cost, recorded at the solver and experiment levels.

The first controller implementation is diagnostic only. It accepts an estimated target error and cost and decides whether refinement is affordable. It is a research hypothesis, not a claim of novelty, convergence, or superiority. Any future controller must be compared with standard adaptive tolerances, adjoint-based estimators, probabilistic ODE solvers, and relevant inference-aware methods.
