# Performance and optional C++ gate

## Purpose

NUMERIS does not include C++ merely to satisfy a technology checklist. The
Python/SciPy implementation is the reference implementation until a measured
performance problem and a trustworthy replacement have both been established.
The gate below is a release decision, not a suggestion to rewrite the solver
core.

The relevant tooling is:

- `scripts/profile_benchmark.py` for a `cProfile` workload and a structured
  `ProfileResult` JSON record. Its `--suite` mode profiles three deterministic
  representative workloads: `oscillator` (non-stiff baseline),
  `fitzhugh_nagumo` (nonlinear dynamics), and `robertson` (stiff dynamics);
- `scripts/check_cpp_gate.py` for a conservative, evidence-only gate check;
- `numeris.budget.memory` for best-effort RSS/high-water-mark measurements;
- `research/protocol/EXPERIMENT_PROTOCOL.md` for the requirement to preserve a
  negative C++ decision when the evidence is insufficient.

## Formal production gate

Let `P` be the Python reference implementation and `C` a proposed C++ kernel.
Production C++ is approved only when every predicate below is true:

```text
APPROVE_CPP =
    HOTSPOT
    AND EQUIVALENT
    AND FASTER_AFTER_WARMUP
    AND MEMORY_ACCEPTABLE
    AND REPRODUCIBLE
```

Failure of any predicate means `KEEP_PYTHON`. A measured hotspot alone has the
intermediate status `INVESTIGATE_CPP`; it never means `APPROVE_CPP`.

### 1. Profiling hotspot (`HOTSPOT`)

The workload must be representative of the declared benchmark class, not a
micro-example selected after looking at the profile. The workload, solver
configuration, input data, machine, and hotspot threshold must be recorded
before the comparison. The current profiler uses a configurable cumulative
time threshold (default `0.50`) and reports the top cumulative functions.

The gate requires:

1. the hotspot to be reproducible across repeated runs;
2. the hotspot to be isolated to a replaceable kernel or interface;
3. the hotspot to be material for the target experiment, rather than profiler
   overhead or an incidental one-off startup cost;
4. profiling evidence from the representative workload set, including the
   relevant stiff/non-stiff and nonlinear cases when the proposed kernel would
   affect them.

### 2. Numerical equivalence (`EQUIVALENT`)

The C++ kernel must be compared with `P` on a frozen corpus and the same input
parameters. The comparison must cover all outputs consumed by NUMERIS, not just
one visually similar trajectory. At minimum this includes state values at the
observation times, derived observations, likelihood contributions, failure
and boundary behavior, and RHS/evaluation counters where applicable.

Acceptance tolerances must be declared before measuring speed and must be
appropriate to the solver tolerance and output scale. The test must include
normal, difficult, and near-failure cases. Any mismatch outside the declared
tolerance is a gate failure. A C++ result that is faster but changes inference
is not an acceptable optimization.

### 3. Speed after warm-up (`FASTER_AFTER_WARMUP`)

Timing must exclude compilation/import/startup effects and include the same
work for `P` and `C`. Use a pre-declared warm-up count, then multiple measured
repetitions on the same machine and environment. Report median and spread, not
the fastest run.

The default decision rule for a production candidate is:

```text
median_time(P) / median_time(C) >= 1.25
```

on the declared representative workload set, with no required workload showing
a material regression. A single favorable microbenchmark is insufficient.
The threshold may be changed only before a new experiment and must be recorded
with the result.

### 4. Memory (`MEMORY_ACCEPTABLE`)

Peak RSS/high-water mark must be measured with the same input, repetition
policy, and process conditions. `None` is an unavailable measurement, not zero
and not evidence of a benefit. The candidate must not exceed the Python
reference's declared memory budget or introduce an unexplained material peak.
If a memory increase is accepted in exchange for speed, that trade-off must be
explicitly approved in the experiment protocol and shown on every relevant
workload.

### 5. Reproducibility and rollback (`REPRODUCIBLE`)

The candidate must have a buildable, documented interface, pinned/recoverable
build inputs, deterministic equivalence tests, and benchmark artifacts that a
second run can reproduce. The original Python path must remain available until
the gate is passed.

Rollback is mandatory if any of the following occurs after integration:

- equivalence fails on a supported case;
- the measured speedup disappears after warm-up or across the representative
  workload set;
- memory or failure rate regresses beyond the declared limits;
- the build cannot be reproduced on the supported platform;
- maintenance/build cost outweighs the measured benefit.

Rollback means removing the C++ path from the production execution path and
recording the negative result. It does not mean weakening tolerances or
changing the benchmark after seeing an unfavorable result.

## Current evidence and decision

The profiling workflow can collect the representative workload set with:

```bash
python scripts/profile_benchmark.py --suite
```

Suite mode writes all artifacts to the predictable directory
`results/profiling/cpp_gate/` (override with `--artifact-dir`). It writes one
profile and one JSON record per workload:
`profile_oscillator.json`, `profile_fitzhugh_nagumo.json`, and
`profile_robertson.json`, plus `cpp_gate.json`. The solver method is declared
per workload: DOP853 for the two non-stiff cases and BDF for Robertson. It also
writes `suite_manifest.json`, the provenance index for the suite. Each profile
JSON records the exact profile CLI invocation as both `command_argv` and
shell-escaped `command`, the workload name, solver name and options,
platform/runtime metadata (OS, machine, Python executable/version, NumPy and
SciPy versions), and the artifact schema version. The gate JSON records the
exact gate invocation, referenced profile artifacts, runtime metadata, and the
observed decision. This is a small deterministic screening workload, not the
scientific benchmark campaign or proof of a C++ benefit.

After the three profiles are written, suite mode invokes
`scripts/check_cpp_gate.py` itself without `--evidence`, stores its JSON output
as `cpp_gate.json`, and requires the explicit fail-closed decision
`KEEP_PYTHON`. The command exits zero when profiling succeeds and this
expected negative gate decision is observed. It exits non-zero for a profiling
failure, malformed gate output, or any unexpected gate decision. Thus this
workflow cannot approve production C++ merely because a hotspot was measured.

The manifest and gate artifacts are intentionally redundant: the manifest is
the suite index, while `cpp_gate.json` remains directly consumable by
`check_cpp_gate.py`. Both preserve `KEEP_PYTHON` when no candidate evidence is
supplied.

The resulting records can be passed independently to the fail-closed gate:

```bash
python scripts/check_cpp_gate.py \
  --profile results/profiling/cpp_gate/profile_oscillator.json \
  --profile results/profiling/cpp_gate/profile_fitzhugh_nagumo.json \
  --profile results/profiling/cpp_gate/profile_robertson.json
```

The suite measures `solve_ode` as a candidate hotspot when the configured
threshold is met, but every record still reports
`numerical_equivalence_verified: false`. Without a real evidence file with
equivalence, warm-up-excluded speed, comparable memory, and reproducibility,
the gate must return `KEEP_PYTHON`.

This is not enough to authorize production C++:

| Gate predicate | Current status | Reason |
| --- | --- | --- |
| `HOTSPOT` | Partial | One representative smoke workload is profiled; multi-model evidence is not yet complete. |
| `EQUIVALENT` | Fail/absent | No C++ candidate or Python-vs-C++ equivalence corpus exists. |
| `FASTER_AFTER_WARMUP` | Absent | No C++ timing comparison with warm-up and repeated measurements exists. |
| `MEMORY_ACCEPTABLE` | Absent | Python memory is measured best-effort, but there is no comparable C++ process measurement. |
| `REPRODUCIBLE` | Absent | No C++ build, interface, or reproducible artifact has passed the preceding gates. |

Therefore the current decision is:

```text
KEEP_PYTHON / INVESTIGATE_CPP_ONLY
```

No production C++ kernel should be added at this revision. This is a valid
negative engineering decision under the technical specification: C++ is an
optional optimization after demonstrated need, not a mandatory first-version
dependency. The next permissible step is to collect representative profiles;
only if the hotspot remains material should a narrowly scoped candidate and
the equivalence gate be implemented.

## Evidence-only smoke check

The gate can be checked without adding or compiling C++:

The gate invocation above is the canonical smoke check; missing evidence is
expected to remain a non-approval (`KEEP_PYTHON`, exit status 1).

The evidence file is an experiment artifact, not a declaration. Its required
shape is:

```json
{
  "hotspot": {
    "representative_workloads": true,
    "repeated": true,
    "replaceable": true,
    "material": true
  },
  "equivalence": {
    "verified": true,
    "normal_cases": true,
    "difficult_cases": true,
    "near_failure_cases": true,
    "tolerance_declared": true
  },
  "speed": {
    "median_speedup": 1.25,
    "warmup_excluded": true,
    "repeated_measurements": true,
    "no_material_regression": true
  },
  "memory": {
    "measured_comparably": true,
    "within_budget": true
  },
  "reproducibility": {
    "build_reproducible": true,
    "interface_documented": true,
    "deterministic": true,
    "artifacts_reproducible": true
  }
}
```

The script returns `KEEP_PYTHON` and exit status 1 when the evidence file is
missing, incomplete, malformed, or any predicate fails. It requires at least
three successful profiles from distinct workloads by default. A profile that
only reports a hotspot is not enough: equivalence, warm-up-excluded median
speedup, comparable memory, and reproducibility remain independent gates.

