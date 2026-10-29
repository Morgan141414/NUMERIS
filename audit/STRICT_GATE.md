# NUMERIS — Strict Compliance Gate

Дата аудита: 2026-10-30  
Аудируемая база: текущее рабочее дерево NUMERIS, HEAD `f972d84` (включает `401e374`, `1539572` и Gaussian-bound derivation) и локальная read-only спецификация `private/TECHNICAL_SPEC.md`.
Правило: наличие API, заглушки, документации или unit-теста не считается доказательством научного результата. `PASS` выставляется только при наличии проверяемого артефакта, который прямо закрывает требование. Этот файл — единственный изменённый артефакт аудита.

## Итоговый gate

**VERDICT: BLOCKED — NOT COMPLIANT WITH THE FULL RESEARCH SPECIFICATION.**

Инженерный прототип работает: `.venv/bin/python -m pytest -q` даёт `69 passed`; Python-модули компилируются; приватный файл имеет режим `0444` и исключён из Git. Добавлены draft протокола и profiling CLI, но фактические научные результаты и profiling artifact отсутствуют. Это не является доказательством математической новизны, преимуществ NUMERIS-GO или готовности публикации.

| Фаза | Статус | Причина блокировки / выхода |
|---|---|---|
| Phase I — Research Foundation | **PARTIAL** | Есть evidence-backed initial literature/gap matrix и draft predeclared protocol; protocol ещё не frozen/signed, systematic bibliography, closest-baseline reproduction и final novelty decision отсутствуют. |
| Phase II — Mathematical Core | **PARTIAL** | Добавлена прозрачная Gaussian NLL perturbation bound с assumptions и unit-тестами; это известный baseline, не solver-integrated estimator, не доказательство NUMERIS-GO и не validated reliability criterion. |
| Phase III — Software Laboratory | **PARTIAL** | Основной детерминированный каркас, draft protocol, profiler CLI и тесты есть; end-to-end inference, memory budget, frozen protocol и все обязательные научные отчёты не завершены. |
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
| Провести literature review по adaptive control, adjoint/goal-oriented, sensitivity, probabilistic ODE, Bayesian inverse problems, likelihood/posterior distortion | **PARTIAL** | `research/literature_review/README.md` теперь содержит 7 primary related-work entries и прямые DOI/PMLR/JMLR/PMC sources, включая Cao–Petzold, probabilistic ODE, DALTON и inference-distortion work | Завершить systematic inclusion/exclusion protocol, complete bibliography и source-level verification for every required family. |
| Составить research-gap matrix и сравнить математический механизм NUMERIS с существующими методами, включая DALTON, SciPy/SUNDIALS/SciML | **PARTIAL** | В `research/literature_review/README.md` есть mechanism comparison table и provisional gap statement; документ прямо запрещает считать gap доказанным | Воспроизвести ближайший inference-distortion baseline, добавить implementation-level comparison для SciPy/SUNDIALS/SciML/DALTON where feasible и принять final novelty decision only after method is fixed. |
| Сформулировать фальсифицируемую гипотезу, endpoints и условия самоопровержения до экспериментов | **PARTIAL** | `research/hypotheses/HYPOTHESIS.md` содержит гипотезу; `research/protocol/EXPERIMENT_PROTOCOL.md` задаёт seeds 0–9, noise grid, solver/tolerance grid, budgets, primary/secondary endpoints и decision rules, но имеет статус draft и не frozen | Freeze/commit a configuration manifest before runs; record exclusions, reference manifests and exact budget values without post hoc changes. |
| Определить, что является proof, empirical evidence и hypothesis | **PARTIAL** | `docs/mathematical_foundation.md`, `docs/limitations.md` явно не называют working note theorem | В research record разделить утверждения на theorem/proposition, numerical evidence и conjecture; не заявлять novelty до gap review. |

**Phase I exit:** literature/gap package, signed experiment protocol, closest-baseline reproduction и подтверждённая граница новизны. Initial review/matrix достигнуты, полный exit не достигнут.

## Phase II — Mathematical Core

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Формально определить входы/выходы controller-а, assumptions, cost и decision rule | **PARTIAL** | `numeris/controller/goal_oriented.py` документирует `SensitivityAwarePolicy`; `numeris/controller/temporal.py` — greedy allocator | Добавить formal specification с доменами, источниками estimates, стоимостью ошибок и failure modes, согласованную с реальным solver path. |
| Исследовать goal-oriented error estimator для declared scientific target | **FAIL** | Текущая формула `sensitivity * state_error` принимает внешние оценки; solver не вычисляет estimator и его validity не проверяется | Реализовать или обосновать estimator end-to-end, показать convergence/coverage against independently converged references на определённом классе задач. |
| Получить математическую baseline bound для declared Gaussian likelihood target | **PARTIAL** | `research/derivations/gaussian_target_bound.md`, `numeris/error_analysis/gaussian_bound.py`, `tests/unit/test_gaussian_bound.py`; derivation explicitly states assumptions and non-novel status | Проверить bound against numerical perturbations, quantify conservatism, and connect it to a declared controller decision without overclaiming parameter/posterior guarantees. |
| Исследовать budget-allocation rule | **PARTIAL** | `allocate_budget_by_sensitivity` — tested greedy ranking; docstring прямо говорит, что это baseline, не theorem | Определить допустимый allocation problem, доказать заявленные свойства либо честно назвать метод heuristic и измерить trade-off against tuned baselines. |
| Исследовать reliability stopping criterion | **PARTIAL** | `SensitivityAwarePolicy.evaluate` умеет `refine/stop`; нет calibrated target reliability | Показать predicted-vs-actual error coverage и stopping performance на held-out trials; задать acceptance threshold заранее. |
| Провести теоретический анализ корректности, устойчивости, сходимости и применимости | **FAIL** | `docs/mathematical_foundation.md` называет linearization starting point и не theorem; proofs/derivations отсутствуют | Добавить formal assumptions и доказательства заявленных properties, либо явно сузить claim до validated heuristic без mathematical contribution. |
| Сопоставить метод с adjoint/sensitivity/probabilistic alternatives до claim of novelty | **BLOCKED** | Initial matrix exists, but closest-baseline reproduction and final mechanism comparison are absent; controller нельзя квалифицировать как новый | Закрыть remaining Phase-I exit items and repeat novelty audit after the controller mechanism is fixed. |

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
| C++ profiling gate tooling | **PARTIAL** | `scripts/profile_benchmark.py` profiles one damped-oscillator solve with `cProfile` and writes a `.prof` file; `research/protocol/EXPERIMENT_PROTOCOL.md` defines the decision gate | Run representative workloads across required model/solver classes, retain profiling artifacts, identify a reproducible hot spot and measure whether a C++ kernel is justified. |
| Visualization for trajectories, errors, likelihood, posterior, budget and calibration | **PARTIAL** | `numeris/visualization/plots.py` covers basic trajectory/error/likelihood views | Add posterior, calibration, parameter-surface, repeated uncertainty and budget-frontier artifacts used by the scientific protocol. |
| Unit/integration/numerical/regression tests | **PASS** for software slice | `.venv/bin/python -m pytest -q`: `69 passed`; `compileall` passes | Keep tests green and add scientific acceptance tests for every new protocol component. This PASS does not imply scientific compliance. |
| Local execution and privacy boundary | **PASS** for checked properties | `private/TECHNICAL_SPEC.md` mode `0444`; Git ignore excludes it; archive scan finds no private/spec file; `git status` clean | Repeat safety scan before each push; never copy the specification into results or public docs. |

**Phase III exit:** complete end-to-end software protocol with five models, inference, budgets, reports, tests and reproducibility. Current status is partial.

## Phase IV — Scientific Validation

| MUST | Статус | Доказательство / отсутствие доказательства | Exit criterion |
|---|---|---|---|
| Converged reference for each model, checked by tolerance and independent method | **PARTIAL** | `research/protocol/EXPERIMENT_PROTOCOL.md` now requires tolerance convergence plus an independent solver family; only oscillator convergence test exists, with no five-model reference package | Store reproducible reference manifests and convergence plots/tables for all five families before accepting any result. |
| Controlled synthetic observations with known truth and noise | **PARTIAL** | Protocol fixes seeds `0..9` and `sigma ∈ {0.01, 0.05, 0.10}`; CLI/repeated runner supports seeded observations, but no complete frozen configuration manifest or dataset/report exists | Freeze truth, observation grid, sigma, seed set and reference provenance in versioned configs before the run. |
| Equal-budget comparison against correctly tuned RK45/DOP853/Radau/BDF/LSODA | **FAIL** | Cost fields and `BudgetLedger` exist, but no published equal-budget scientific matrix or matched stopping protocol | Run matrix across budgets/seeds/models; report target error, parameter RMSE, likelihood distortion and costs with uncertainty. |
| Parameter recovery and Parameter RMSE | **FAIL** as experiment | `parameter_rmse` is a tested primitive; runner does not execute parameter fitting against true parameters as a study | Produce repeated MLE recovery tables/plots for all applicable models and solver/controller conditions. |
| Likelihood error against a converged reference | **PARTIAL** | `likelihood_distortion` exists; no complete reference-NLL sweep/report | Add automated reference/candidate NLL comparison to every controlled tolerance study. |
| Posterior distance and Bayesian experiment | **FAIL** | No MCMC/NumPyro/PyMC pipeline or posterior experiment | Complete low-dimensional Bayesian protocol with posterior convergence and Hellinger/Wasserstein comparison, or narrow published scope. |
| False-optimum rate | **FAIL** as experiment | `false_optimum_rate` primitive has unit tests; no multi-start likelihood landscapes, truth set or observed rate | Define true-optimum construction, multi-start seeds, tolerance and report rate across models/budgets. |
| Repeated runs, confidence intervals and statistical tests | **PARTIAL** | Protocol requires paired seed-wise differences and confidence intervals; `benchmarks/repeated.py` repeats seeds and summarizes nfev/runtime/target error, but no executed inference CIs or statistical tests exist | Execute all declared replicates and publish CI method, paired comparisons and decision outputs. |
| Ablation of each controller component | **PARTIAL** as protocol, **FAIL** as evidence | `research/protocol/EXPERIMENT_PROTOCOL.md` explicitly requires estimator-only, allocation-only, stopping-only and full-policy ablations; no ablation runner or results exist | Execute all four ablations under identical seeds, models, tolerances and budgets; retain failures and report component-level effects. |
| Reliability calibration | **PARTIAL** as instrumentation, **FAIL** as validation | `error_bound_calibration` function and unit tests exist (`numeris/error_analysis/calibration.py`, `tests/unit/test_calibration.py`); no predicted-vs-actual controller calibration study | Produce coverage/excess/calibration curves on held-out solver trials and reject overconfident bounds under a predeclared threshold. |
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

**C++ gate status: PARTIAL infrastructure / BLOCKED evidence.** `research/protocol/EXPERIMENT_PROTOCOL.md` defines the profiling gate and `scripts/profile_benchmark.py` can write a `cProfile` artifact for one oscillator workload. No committed profiling output, representative multi-model workload, hot-spot analysis, Python/C++ equivalence test or measured speed/memory comparison exists; therefore C++ is still not justified.

## Required order of work after this audit

1. Phase I: literature/gap matrix, frozen protocol and configuration manifest.
2. Phase II: formal controller contract, estimator validity and reliability criterion.
3. Phase III: end-to-end model/config/inference/budget integration.
4. Phase IV: five-model equal-budget matrix, repeats, ablation, calibration and negative results.
5. Execute the profiling gate; add a C++ kernel only if measured evidence passes it.
6. Phase V: manuscript and independent reproduction.

Until these exit criteria are met, the only accurate public claim is: **NUMERIS is a tested deterministic research prototype; it is not yet a validated novel scientific method or publication-ready result.**
