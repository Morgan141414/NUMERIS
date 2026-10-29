"""Run the first NUMERIS smoke experiment."""

import numpy as np

from numeris.benchmarks import damped_oscillator
from numeris.inference import gaussian_negative_log_likelihood
from numeris.solvers import solve_ode


if __name__ == "__main__":
    model = damped_oscillator()
    truth = solve_ode(model, np.array([1.0, 0.1, 0.0]), rtol=1e-11, atol=1e-13)
    candidate = solve_ode(model, np.array([1.0, 0.1, 0.0]), rtol=1e-5, atol=1e-7)
    print({"candidate_nfev": candidate.nfev,
           "candidate_nll_against_reference": gaussian_negative_log_likelihood(candidate.states, truth.states, 1e-3)})
