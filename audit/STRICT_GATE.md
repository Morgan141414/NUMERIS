# NUMERIS — Strict Compliance Gate

Дата аудита: 2026-10-30  
Аудируемая база: текущее рабочее дерево NUMERIS, commit `1539572` и локальная read-only спецификация `private/TECHNICAL_SPEC.md`.  
Правило: наличие API, заглушки, документации или unit-теста не считается доказательством научного результата. `PASS` выставляется только при наличии проверяемого артефакта, который прямо закрывает требование. Этот файл — единственный изменённый артефакт аудита.

## Итоговый gate

**VERDICT: BLOCKED — NOT COMPLIANT WITH THE FULL RESEARCH SPECIFICATION.**

Инженерный прототип работает: `.venv/bin/python -m pytest -q` даёт `66 passed`; Python-модули компилируются; приватный файл имеет режим `0444` и исключён из Git. Это не является доказательством математической новизны, преимуществ NUMERIS-GO или готовности публикации.

| Фаза | Статус | Причина блокировки / выхода |
|---|---|---|
| Phase I — Research Foundation | **FAIL** | Нет фактического literature review, библиографии, comparison/gap matrix и проверенного сравнения с DALTON, adjoint/goal-oriented и probabilistic methods. |
| Phase II — Mathematical Core | **FAIL** | Есть эвристика и working note, но нет solver-integrated estimator, теорем, доказательств свойств и validated reliability criterion. |
| Phase III — Software Laboratory | **PARTIAL** | Основной детерминированный каркас и тесты есть; end-to-end inference, memory budget, единый research protocol и все обязательные научные отчёты не завершены. |
| Phase IV — Scientific Validation | **FAIL** | Нет опубликованных equal-budget inference runs, repeated parameter/posterior studies, ablation, calibration и фактического false-optimum эксперимента. |
| Phase V — Publication readiness | **BLOCKED** | Научный вклад не установлен; нет manuscript, результатов, limitations backed by experiments и reproducibility package для claims. |

## Status definitions

- **PASS** — требование выполнено и подтверждено конкретным файлом, тестом или воспроизводимым экспериментом.
- **PARTIAL** — часть реализации есть, но обязательная проверка или интеграция отсутствует.
- **FAIL** — требование применимо, но доказательства или обязательного результата нет.
- **BLOCKED** — следующий этап нельзя честно закрыть, пока не выполнены зависимости предыдущего этапа.

## Phase I — Research Foundation

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Зафиксировать scope: deterministic parameterized ODE, Gaussian observations, local reproducible execution | **PASS** | `private/TECHNICAL_SPEC.md`; `README.md`; `numeris/models`, `numeris/inference/gaussian.py`; 66 software tests pass | Сохранить scope и не расширять его без отдельного решения. |
| Формально зафиксировать исследовательскую задачу `min_A E_target(A) subject to C(A) <= B` | **PARTIAL** | `docs/mathematical_foundation.md`, `research/hypotheses/HYPOTHESIS.md` | Указать полный target/cost contract для каждого benchmark и связать его с исполняемым runner. |
| Провести literature review по adaptive control, adjoint/goal-oriented, sensitivity, probabilistic ODE, Bayesian inverse problems, likelihood/posterior distortion | **FAIL** | `research/literature_review/README.md` — это ledger-инструкция, а не обзор; библиографии и источников в репозитории нет | Добавить датированную библиографию и краткие проверяемые summaries по каждому required family. |
| Составить research-gap matrix и сравнить математический механизм NUMERIS с существующими методами, включая DALTON, SciPy/SUNDIALS/SciML | **FAIL** | Нет comparison matrix, implementation study или reproducible comparison | Для каждого аналога указать objective, estimator, control variable, cost model, assumptions, overlap и exact distinction; отдельно отметить, если distinction не найден. |
| Сформулировать фальсифицируемую гипотезу, endpoints и условия самоопровержения до экспериментов | **PARTIAL** | `research/hypotheses/HYPOTHESIS.md` содержит гипотезу и falsification conditions | Добавить preregistered protocol: budgets, seeds, primary/secondary endpoints, exclusion rules и decision rule. |
| Определить, что является proof, empirical evidence и hypothesis | **PARTIAL** | `docs/mathematical_foundation.md`, `docs/limitations.md` явно не называют working note theorem | В research record разделить утверждения на theorem/proposition, numerical evidence и conjecture; не заявлять novelty до gap review. |

**Phase I exit:** literature/gap package, signed experiment protocol и подтверждённая граница новизны. Сейчас не достигнут.

## Phase II — Mathematical Core

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Формально определить входы/выходы controller-а, assumptions, cost и decision rule | **PARTIAL** | `numeris/controller/goal_oriented.py` документирует `SensitivityAwarePolicy`; `numeris/controller/temporal.py` — greedy allocator | Добавить formal specification с доменами, источниками estimates, стоимостью ошибок и failure modes, согласованную с реальным solver path. |
| Исследовать goal-oriented error estimator для declared scientific target | **FAIL** | Текущая формула `sensitivity * state_error` принимает внешние оценки; solver не вычисляет estimator и его validity не проверяется | Реализовать или обосновать estimator end-to-end, показать convergence/coverage against independently converged references на определённом классе задач. |
| Исследовать budget-allocation rule | **PARTIAL** | `allocate_budget_by_sensitivity` — tested greedy ranking; docstring прямо говорит, что это baseline, не theorem | Определить допустимый allocation problem, доказать заявленные свойства либо честно назвать метод heuristic и измерить trade-off against tuned baselines. |
| Исследовать reliability stopping criterion | **PARTIAL** | `SensitivityAwarePolicy.evaluate` умеет `refine/stop`; нет calibrated target reliability | Показать predicted-vs-actual error coverage и stopping performance на held-out trials; задать acceptance threshold заранее. |
| Провести теоретический анализ корректности, устойчивости, сходимости и применимости | **FAIL** | `docs/mathematical_foundation.md` называет linearization starting point и не theorem; proofs/derivations отсутствуют | Добавить formal assumptions и доказательства заявленных properties, либо явно сузить claim до validated heuristic без mathematical contribution. |
| Сопоставить метод с adjoint/sensitivity/probabilistic alternatives до claim of novelty | **BLOCKED** | Phase I comparison отсутствует; controller пока нельзя квалифицировать как новый | Закрыть Phase I и повторить novelty audit с exact mechanism comparison. |

**Phase II exit:** mathematically specified and independently validated method, либо документированное решение о том, что результат — baseline/negative result, а не новый метод. Сейчас не достигнут.

## Phase III — Software Laboratory

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Model definition with model ID, parameters, bounds, observations and noise metadata | **PARTIAL** | `numeris/models/config.py`, `ParameterSpec`, `ModelConfig`, serialization tests | Make `ModelConfig` the required end-to-end contract for model, solver, inference and CLI; add integration test. |
| Solver interface for RK45, DOP853, Radau, BDF, LSODA with settings and instrumentation | **PARTIAL** | `numeris/solvers/scipy_solver.py`, `tests/integration/test_benchmark_runner.py`, public API tests | Demonstrate all methods in a controlled matrix with reference provenance and budget behavior; hard budget interruption remains unimplemented. |
| Numerical Error Observatory with tolerance convergence, interval/error analysis and reference checks | **PARTIAL** | `numeris/error_analysis/observatory.py`, `tests/numerical/test_reference_convergence.py` | Produce per-model convergence reports and an independent-method check; never label one strict solve as exact. |
| Inference engine: Gaussian MLE, bounds, multi-start, intervals and convergence diagnostics | **PARTIAL** | `numeris/inference/gaussian.py` provides MLE/bounds; no multi-start orchestration or intervals | Implement and test multi-start, optimizer diagnostics, confidence/uncertainty outputs, and connect them to benchmark reports. |
| Inference-distortion detector separating numerical and statistical uncertainty | **PARTIAL** | `metrics.py` has RMSE, likelihood distortion and false-optimum primitives; no end-to-end decomposition | Build tolerance-sweep and repeated-noise protocol with separate numerical reference and statistical replicate components. |
| Bayesian inference and posterior diagnostics | **FAIL** | `normalized_grid_posterior` is explicitly a low-dimensional diagnostic; no PyMC/NumPyro sampler, MCMC diagnostics or ODE posterior pipeline | Either implement the limited Bayesian experiment required by scope with convergence diagnostics, or formally amend scope before claiming completion. |
| Budget manager for RHS, time, runs and memory | **PARTIAL** | `numeris/budget/ledger.py` handles RHS/time/runs; memory limit and pre-emption are absent | Add measured memory policy and deterministic budget-exhaustion behavior, or document an accepted deferred requirement. |
| Benchmark laboratory for five required systems | **PARTIAL** | Factories in `numeris/benchmarks/`; runner and CLI exist; tests cover construction/smoke execution | Run the full research protocol—not merely one solver smoke run—for oscillator, FHN, Lotka–Volterra, Lorenz and Robertson. |
| Reproducibility engine | **PARTIAL** | `numeris/reproducibility/metadata.py`, CLI metadata and serialization tests | Ensure every benchmark/inference path records model, truth, observation/noise, reference provenance, solver, budget, seed and versions. |
| Visualization for trajectories, errors, likelihood, posterior, budget and calibration | **PARTIAL** | `numeris/visualization/plots.py` covers basic trajectory/error/likelihood views | Add posterior, calibration, parameter-surface, repeated uncertainty and budget-frontier artifacts used by the scientific protocol. |
| Unit/integration/numerical/regression tests | **PASS** for software slice | `.venv/bin/python -m pytest -q`: `66 passed`; `compileall` passes | Keep tests green and add scientific acceptance tests for every new protocol component. This PASS does not imply scientific compliance. |
| Local execution and privacy boundary | **PASS** for checked properties | `private/TECHNICAL_SPEC.md` mode `0444`; Git ignore excludes it; archive scan finds no private/spec file; `git status` clean | Repeat safety scan before each push; never copy the specification into results or public docs. |

**Phase III exit:** complete end-to-end software protocol with five models, inference, budgets, reports, tests and reproducibility. Current status is partial.

## Phase IV — Scientific Validation

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Converged reference for each model, checked by tolerance and independent method | **PARTIAL** | Oscillator convergence test exists; no complete five-model reference package or independent-method evidence | Store reproducible reference manifests and convergence plots/tables for all five families. |
| Controlled synthetic observations with known truth and noise | **PARTIAL** | CLI/repeated runner supports seeded synthetic observations; no complete inference dataset/report across all models | Freeze truth, observation grid, sigma, seed set and reference provenance in versioned configs. |
| Equal-budget comparison against correctly tuned RK45/DOP853/Radau/BDF/LSODA | **FAIL** | Cost fields and `BudgetLedger` exist, but no published equal-budget scientific matrix or matched stopping protocol | Run matrix across budgets/seeds/models; report target error, parameter RMSE, likelihood distortion and costs with uncertainty. |
| Parameter recovery and Parameter RMSE | **FAIL** as experiment | `parameter_rmse` is a tested primitive; runner does not execute parameter fitting against true parameters as a study | Produce repeated MLE recovery tables/plots for all applicable models and solver/controller conditions. |
| Likelihood error against a converged reference | **PARTIAL** | `likelihood_distortion` exists; no complete reference-NLL sweep/report | Add automated reference/candidate NLL comparison to every controlled tolerance study. |
| Posterior distance and Bayesian experiment | **FAIL** | No MCMC/NumPyro/PyMC pipeline or posterior experiment | Complete low-dimensional Bayesian protocol with posterior convergence and Hellinger/Wasserstein comparison, or narrow published scope. |
| False-optimum rate | **FAIL** as experiment | `false_optimum_rate` primitive has unit tests; no multi-start likelihood landscapes, truth set or observed rate | Define true-optimum construction, multi-start seeds, tolerance and report rate across models/budgets. |
| Repeated runs, confidence intervals and statistical tests | **PARTIAL** | `benchmarks/repeated.py` repeats seeds and summarizes nfev/runtime/target error; no inference uncertainty intervals or significance tests | Add predeclared replicate count, CI method, paired comparison and statistical decision rule. |
| Ablation of each controller component | **FAIL** | No ablation runner or results; documentation only states requirement | Compare baseline, estimator-only, allocation-only, stopping-only and full controller under identical seeds/budgets. |
| Reliability calibration | **FAIL** as validation | `error_bound_calibration` function and unit test exist; no predicted-vs-actual controller calibration study | Produce coverage/excess/calibration curves and reject overconfident bounds under a predeclared threshold. |
| Negative results and cases where baseline wins | **FAIL** as evidence | `research/negative_results.md` is an empty ledger template; no recorded scientific cases | Record every failure, baseline win, cost reversal and miscalibration with configuration and impact on applicability. |

**Phase IV exit:** complete preregistered benchmark matrix, ablation, calibration, uncertainty/statistical analysis and negative-results ledger. Current status is failed.

## Phase V — Publication Readiness

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Mathematical contribution stated with scope and proof/evidence separation | **FAIL** | No proof package or validated novel mechanism; `docs/limitations.md` explicitly says this is not available | Write contribution statement only after Phases I–IV; label heuristic/negative result if novelty is not established. |
| Publication-grade methods and results | **FAIL** | No manuscript, tables, figures or completed results package; no `papers/` content was found | Add reproducible manuscript source, generated tables/figures, exact configs and result hashes. |
| Open repository reproducibility | **PARTIAL** | README, CI-related project files, docs, tests, CLI and CITATION exist; scientific result package absent | A clean checkout must install, run the declared protocol, regenerate figures/tables and match declared tolerances. |
| Limitations, negative results and applicability class | **PARTIAL** | `docs/limitations.md` and hypothesis conditions are honest; empirical negative-results ledger absent | Ground every limitation and applicability claim in an experiment or formal argument. |
| Scientific publication decision | **BLOCKED** | Novelty and superiority are explicitly unproven | Only submit after independent review of Phase I gap and Phase IV results; publication remains conditional. |

**Phase V exit:** publication package passes an independent reproduction and a claim-level audit. Current status is blocked.

## C++ requirement audit

### What the specification actually says

The authoritative local `private/TECHNICAL_SPEC.md` does **not** contain a mandatory C++ deliverable. In the full supplied project brief, C++ was described as an optional optimization path: it may be introduced later for proven hot spots, after a demonstrated need. Python/NumPy/SciPy are the required first implementation stack. Therefore, absence of C++ is **not** a current TЗ violation.

### What is still required before using C++

No C++ implementation should be added merely to create the appearance of compliance. The required experiment is:

1. Complete a correct Python reference implementation and scientific protocol.
2. Profile representative workloads, separately measuring solver/RHS, inference, controller and serialization time, plus peak memory.
3. Identify a hot path with a reproducible fraction of total runtime and a correctness-preserving target.
4. Implement only that isolated kernel in C++ behind the same interface.
5. Run numerical equivalence tests against Python within a predeclared tolerance.
6. Compare wall time, RHS-equivalent work, memory, build/toolchain burden and reproducibility on the target Apple Silicon environment.
7. Keep the C++ version only if the measured benefit outweighs maintenance and reproducibility cost; otherwise record a negative result.

**C++ gate status: NOT DUE / BLOCKED BY PROFILING.** No profiling artifact exists in the repository, so there is currently no evidence that a C++ rewrite is necessary or scientifically justified.

## Required order of work after this audit

1. Phase I: literature/gap matrix and frozen protocol.
2. Phase II: formal controller contract, estimator validity and reliability criterion.
3. Phase III: end-to-end model/config/inference/budget integration.
4. Phase IV: five-model equal-budget matrix, repeats, ablation, calibration and negative results.
5. Profiling gate and only then optional C++ kernel.
6. Phase V: manuscript and independent reproduction.

Until these exit criteria are met, the only accurate public claim is: **NUMERIS is a tested deterministic research prototype; it is not yet a validated novel scientific method or publication-ready result.**
