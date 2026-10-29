# Contributing to NUMERIS

NUMERIS is a research project. Contributions must preserve reproducibility and must not turn an empirical observation into a mathematical claim.

Before opening a pull request:

```bash
python -m pip install -e '.[dev]'
pytest -q
python scripts/check_publication_safety.py
git diff --check
```

Every benchmark change should state its model, solver, tolerances, seed, budget, reference provenance, and failure cases. Do not add the private specification, generated results, machine secrets, or unpublished material to Git.
