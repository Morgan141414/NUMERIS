# NUMERIS

**Inference-Aware Numerical Computing**

NUMERIS is an experimental research laboratory for studying how numerical ODE error propagates into parameter estimation and other scientific conclusions. The first implementation is intentionally small: it provides a solver protocol, deterministic baselines, an inference objective, and a diagnostic goal-oriented controller that can be falsified by benchmark experiments.

This repository is a research prototype, not a claim of mathematical novelty or superiority. Results must be reported together with assumptions, budgets, negative results, and limitations.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
python examples/oscillator_demo.py
```

If the local Python version does not yet have compatible wheels, use Python 3.10–3.13 for the environment; the source remains version-pinned by `pyproject.toml` and `requirements.txt`.

The private technical specification is stored locally at `private/TECHNICAL_SPEC.md`. It is read-only and ignored by Git; it must never be committed or published.

## Research status

- Phase I: repository and reproducibility foundation — implemented.
- Phase II: mathematical method — an explicit falsifiable heuristic exists; novelty and guarantees remain open.
- Phase III: benchmark laboratory — five-model deterministic slice and CLI implemented.

## Design principles

1. Compare scientific target error, not only trajectory error.
2. Keep solver, inference, budget, and controller interfaces independent.
3. Record computational cost and numerical settings with every run.
4. Treat the controller as a hypothesis to test, including cases where it loses.

Run the complete deterministic slice with:

```bash
python scripts/run_all_benchmarks.py --solver BDF --seed 3
```

Use matched solver matrices and independently converged references before drawing scientific conclusions.

## License

Research code is released under the MIT License. See `LICENSE`.
