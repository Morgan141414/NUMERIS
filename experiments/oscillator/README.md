# Minimal scientific prototype: damped oscillator

This directory is reserved for the execution artifacts of
`research/protocol/MINIMAL_SCIENTIFIC_PROTOTYPE_v0.1.md`.

The protocol is frozen and currently has **no results**. Do not place exploratory outputs here under the frozen-protocol name. A valid execution must record the protocol commit, environment, arm configurations, paired seed statuses, budget accounting, failures, and predeclared bootstrap analysis.

The experiment compares:

- `NUMERIS-GO-candidate-v0.1`, only if its implementation contract is complete;
- SciPy `DOP853` with fixed predeclared tolerances as the standard baseline.

The sole primary target is parameter RMSE under a matched cap of 2,000 RHS evaluations per seed. Any result must preserve negative, failed, over-budget, and incomplete cases and must not be interpreted as evidence of general superiority or novelty.

## Bounded runner

Run the executable diagnostic with its intentionally small defaults:

```bash
python scripts/run_minimal_oscillator.py --output results/oscillator_minimal.json
```

The artifact is labelled `exploratory`/`bounded`. The candidate contract is
currently not implemented, so the report returns `NOT-IMPLEMENTED` and does
not substitute an existing controller heuristic. It records the manifest
commit, environment, paired seeds, DOP853 baseline, budget/failure statuses,
and unavailable primary RMSE/bootstrap fields.

