# Experiment entry points

The reproducible entry points currently live in `scripts/`:

- `run_oscillator_benchmark.py` for the first vertical slice;
- `run_all_benchmarks.py` for all five required model families.

The per-model directories are reserved for frozen configurations and reports. Generated results remain ignored by Git so a public repository cannot accidentally accumulate private or machine-specific artifacts.
