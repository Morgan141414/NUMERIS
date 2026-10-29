# NUMERIS — Strict Compliance Gate

Дата аудита: 2026-10-30  
Аудируемый commit: `4abf2357db52c36fadf5ddd228f4215c23d7df15` (`4abf235`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение аудита: изменён только этот файл; код и GitHub не изменялись.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD представляет собой работающий и протестированный Python-прототип исследовательской лаборатории. Четыре запрошенных slices интегрированы на уровне файлов, импортов и тестов:

1. literature foundation;
2. Bayesian grid pipeline;
3. equal-budget/ablation validation infrastructure;
4. cross-platform memory profiling и C++ gate.

Однако ни один из этих фактов сам по себе не является научным evidence преимущества NUMERIS-GO. В текущем HEAD отсутствуют frozen protocol, ближайшее baseline reproduction, end-to-end controller experiment, фактические equal-budget результаты по пяти моделям, настоящая ablation study, calibration evidence, C++ equivalence/speed evidence и доказанная новизна.

## Проверяемые свойства HEAD

| Проверка | Результат | Фактическое основание |
|---|---|---|
| Git HEAD | **PASS** | `4abf235`; `main...origin/main`; рабочее дерево чистое |
| Полный тестовый набор | **PASS** для software slice | `.venv/bin/python -m pytest -q`: `81 passed in 0.50s` |
| Компиляция | **PASS** | `python -m compileall -q numeris scripts tests` |
| Public API/imports | **PASS** | Импортированы benchmark factories, validation exports, Bayesian grid exports и memory schema |
| Runtime validation smoke | **PASS** для инфраструктуры | Equal-budget и ablation runner выполнились на oscillator, но результаты не являются доказательством преимущества |
| Profiling CLI | **PASS** для инструмента | Созданы временные `.prof` и JSON; artifact не сохранён в репозитории и покрывает только oscillator/DOP853 |
| Publication safety | **PASS** | `scripts/check_publication_safety.py`: passed; archive scan не содержит private/spec/secret/confidential файлов |
| Private specification | **PASS** для privacy boundary | `private/TECHNICAL_SPEC.md` имеет режим `0444`, игнорируется Git и не отслеживается |
| Scientific completion | **FAIL/BLOCKED** | Нет frozen protocol, полного experiment package, valid controller evidence, C++ evidence или novelty decision |

## Статусы

- **PASS** — требование выполнено и подтверждено проверяемым артефактом; для научных claims нужен воспроизводимый результат, а не наличие API.
- **PARTIAL** — часть реализации есть, но обязательная научная проверка, интеграция или критерий выхода отсутствует.
- **FAIL** — требование применимо, но необходимый результат отсутствует.
- **BLOCKED** — зависимый этап нельзя закрыть честно до выполнения предыдущих exit criteria.

## Аудит четырёх специализированных slices

### 1. Literature foundation — PARTIAL

Интеграция подтверждена:

- `research/literature_review/INCLUSION_EXCLUSION_PROTOCOL.md`;
- `BIBLIOGRAPHY_LEDGER.md`;
- `COMPARISON_MATRIX.md`;
- `README.md`.

Зафиксированы Cao–Petzold, Lang–Verwer, probabilistic ODE work, Bayesian inverse problems, Tiemann et al., DALTON, SciPy, SUNDIALS и SciML. Документы корректно предупреждают, что gap и novelty пока не доказаны.

Научный статус: **PARTIAL**, не PASS. `research/protocol/EXPERIMENT_PROTOCOL.md` прямо имеет статус `draft`; отсутствуют complete systematic screening, reproduction ближайшего inference-distortion baseline и final novelty decision после фиксации механизма контроллера. В public tree есть ссылки и сравнительная матрица, но нет evidence, что NUMERIS отличен от adjoint/goal-oriented или likelihood-aware методов.

**Phase-I exit criterion: NOT MET.** Требуются frozen/committed configuration manifest, завершённый screening ledger, closest-baseline reproduction и post-mechanism novelty audit.

### 2. Bayesian grid pipeline — PARTIAL

Интеграция подтверждена:

- `numeris/inference/bayesian_grid.py`;
- exports из `numeris/inference/__init__.py`;
- `tests/unit/test_bayesian_grid.py`;
- `tests/integration/test_bayesian_inference_pipeline.py`;
- успешный public import `GridPosterior`, `grid_posterior`, `posterior_distance`.

Pipeline действительно оценивает Gaussian ODE likelihood на явной конечной сетке, нормализует posterior, даёт mode/mean/standard deviation/credible intervals и Hellinger/total-variation diagnostics. Это воспроизводимый low-dimensional diagnostic baseline.

Научный статус: **PARTIAL**, не PASS. Модуль сам документирует ограничения: finite grid, scalar independent Gaussian noise, отсутствие MCMC convergence diagnostics, posterior predictive checks и hierarchical priors. Это не PyMC/NumPyro Bayesian sampling, не полноценная posterior reliability study и не доказательство posterior improvement NUMERIS-GO. В tracked `results/` отсутствует committed posterior comparison report.

**Phase-III Bayesian exit criterion: NOT MET.** Требуется заранее объявленный posterior protocol, grid/sampler convergence check, numerical-versus-statistical uncertainty separation, repeated seeds и posterior comparison against a converged reference.

### 3. Equal-budget / ablation validation — PARTIAL

Интеграция подтверждена:

- `numeris/benchmarks/validation.py`;
- exports `BudgetCaps`, `AblationCase`, `predefined_solver_configs`, `run_equal_budget_comparison`, `run_ablation_cases`;
- `tests/integration/test_validation.py`;
- runtime smoke: paired equal-budget report и ablation report сформированы.

Положительные свойства реализации:

- paired seeds;
- одинаковые sigma и reference для сравниваемых labels;
- сохранение failures и budget violations;
- JSON-friendly reports;
- явная строка `scientific_claim: none`;
- пять требуемых SciPy solver families присутствуют в predefined configs.

Критические ограничения:

- `BudgetCaps` проверяет cap post hoc после завершения solver call; это не hard interruption и не строгая симуляция общего бюджета;
- `target_error` в validation runner — trajectory RMSE относительно reference, а не полный набор primary endpoints из ТЗ: likelihood distortion, parameter RMSE, posterior distance, false-optimum rate и calibration;
- `AblationCase` записывает `disabled_components` как metadata, но runner не переключает реальные estimator/allocation/stopping компоненты NUMERIS-GO; следовательно, это orchestration scaffold, а не доказанная ablation study;
- результаты smoke-run не сохранены как frozen scientific artifact;
- в tracked `results/` есть только `.gitkeep`, поэтому нет воспроизводимой таблицы equal-budget outcomes по пяти моделям/noise/budget factors.

**Phase-IV validation exit criterion: NOT MET.** Требуются frozen protocol, converged independent references для всех пяти моделей, equal-budget inference runs, реальные controller ablations, paired confidence intervals, failure/negative-results ledger и calibration analysis.

### 4. Cross-platform memory / C++ gate — PARTIAL infrastructure, BLOCKED evidence

Интеграция подтверждена:

- `numeris/budget/memory.py` содержит `ProfileResult`, RSS/peak-memory helpers, JSON-safe schema и optional-platform fallbacks;
- `scripts/profile_benchmark.py` запускается и создаёт cProfile/JSON artifact;
- `tests/unit/test_memory.py` покрывает schema/validation;
- в текущей среде peak RSS был измерим через `resource`, текущий RSS через доступный backend был `unavailable`; это корректно отражено как `None`, а не подменено нулём;
- `ProfileResult.cpp_gate` явно требует measured hot spot и numerical equivalence.

C++ фактически отсутствует: поиск по public tree не обнаружил C++ kernel, pybind/nanobind binding или equivalence test. `ctypes` в `memory.py` — Windows API fallback для измерения памяти, не C++ implementation.

`profile_benchmark.py` покрывает только один damped-oscillator workload и один solver invocation. Нет committed representative multi-model profiles, hot-spot attribution, isolated kernel interface, Python/C++ numerical equivalence, wall-time/memory comparison или maintenance-cost decision. Поэтому отсутствие C++ сейчас соответствует условному gate ТЗ: добавлять C++ без profiling evidence было бы фиктивным выполнением требования.

**C++ gate: BLOCKED.** Сначала нужны representative profiling artifacts и reproducible hot-spot; только затем допустима реализация узкого C++ kernel, если измеренная польза превышает build/reproducibility cost.

## Phase gate против ТЗ

### Phase I — Research Foundation: **PARTIAL**

Выполнены scope, initial bibliography и provisional comparison matrix. Не выполнены frozen protocol, complete systematic review, closest-baseline reproduction и final novelty decision.

**Exit: NOT MET.**

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty claim**

Есть:

- формальная постановка constrained target/cost problem;
- `SensitivityAwarePolicy` и temporal allocator как прототипы;
- Gaussian NLL perturbation bound в `research/derivations/gaussian_target_bound.md` и `numeris/error_analysis/gaussian_bound.py`.

Но Gaussian bound explicitly обозначен как known baseline. Текущий controller получает внешние sensitivity/state-error estimates; он не предоставляет solver-integrated validated goal-oriented estimator. Нет доказательств устойчивости/сходимости/coverage и нет line-by-line equivalence analysis с adjoint, probabilistic ODE и DALTON.

**Exit: NOT MET.** Допустимая текущая формулировка — baseline/heuristic research prototype, не новый математический метод.

### Phase III — Software Laboratory: **PARTIAL**

Основные модули и tests работают: модели, solver interface, observatory, Gaussian inference, grid posterior, budget ledger, validation scaffolding, memory profiling, visualization, reproducibility metadata и required benchmark factories.

Не закрыты: end-to-end `ModelConfig` contract во всех paths, multi-start/uncertainty diagnostics, hard budget behavior, full inference-distortion decomposition, full posterior protocol, five-model research matrix и complete scientific reporting. Software tests PASS, но это не означает scientific compliance.

**Exit: NOT MET.**

### Phase IV — Scientific Validation: **FAIL**

Нет tracked evidence для:

- five-model repeated equal-budget inference matrix;
- parameter-recovery experiments;
- likelihood distortion study;
- posterior-distance study against reference;
- false-optimum rate experiment;
- actual estimator/allocation/stopping ablations;
- reliability calibration coverage;
- statistical significance and confidence intervals;
- explicit populated negative-results ledger.

API и smoke tests не заменяют эти результаты.

**Exit: NOT MET.**

### Phase V — Publication readiness: **BLOCKED**

Нет установленного scientific contribution, final method comparison, manuscript, publication-quality figures/tables или independent reproduction package. Публикация не может быть заявлена.

**Exit: BLOCKED by Phases I–IV.**

## Required next exit criteria

1. Freeze and commit the exact experiment manifest before scientific runs.
2. Complete source-level literature screening and reproduce the closest inference-distortion result.
3. Freeze the controller mechanism and perform equivalence analysis against known methods.
4. Generate converged, independently checked references for oscillator, FitzHugh–Nagumo, Lotka–Volterra, Lorenz and Robertson.
5. Run paired equal-budget experiments over declared seeds, noise levels, tolerances and budgets.
6. Connect validation to actual NUMERIS-GO estimator, allocation and stopping switches; otherwise label it baseline-only.
7. Report parameter RMSE, likelihood error, posterior distance, false-optimum rate, RHS evaluations, runtime, peak RAM, failure rate and calibration.
8. Preserve failed and baseline-better runs in `research/negative_results.md` and commit machine-readable reports.
9. Run the profiling gate over representative workloads. Implement C++ only if a reproducible hot spot, isolated interface, numerical equivalence and measured benefit are all present.
10. Only after these gates, prepare manuscript and independent reproduction instructions.

## Final public claim allowed by this audit

> NUMERIS HEAD `4abf235` is a locally runnable, tested deterministic research prototype with literature, Bayesian-grid, validation-scaffold and memory-profiling infrastructure. It is not yet a validated novel method, not evidence of superiority over existing solvers, not a completed Bayesian scientific study, and not publication-ready.
