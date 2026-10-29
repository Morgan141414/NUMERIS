# NUMERIS — строгий аудит соответствия ТЗ

Дата аудита: 2026-10-30

Аудируемая база: commit `33fdb96` (`Add compliance metrics repeated benchmarks and model configs`) и текущее дерево проекта.

Источник требований: локальный read-only файл `private/TECHNICAL_SPEC.md`.
Метод: сопоставление требований с фактически присутствующими файлами, публичными API, тестами и CLI; наличие заготовки или документации не считается доказательством научного результата.

## Статусы

- **YES** — требование реализовано на заявленном инженерном уровне и подтверждено кодом/тестами.
- **PARTIAL** — реализована только часть требования или есть функциональная заготовка без требуемой научной валидации.
- **NO** — требуемого компонента, эксперимента или доказательства нет.

## Матрица соответствия

| Требование ТЗ | Статус | Фактическое состояние и доказательства | Недостаёт / ограничение | Приоритет |
|---|---|---|---|---:|
| Исследовательская identity и фальсифицируемая гипотеза | PARTIAL | `README.md`, `research/hypotheses/HYPOTHESIS.md`, `docs/limitations.md` формулируют inference-aware цель и возможность отрицательного результата | Гипотеза экспериментально не подтверждена и не опровергнута | P0 |
| ODE scope и Gaussian observations | YES | `numeris/models/base.py`, `numeris/inference/gaussian.py`; детерминированные параметризованные ODE и Gaussian NLL работают | Полная схема модели пока не является обязательным runtime-контрактом | P1 |
| Формальная задача `min E_target` при `C <= B` | PARTIAL | `docs/mathematical_foundation.md`, `goal_oriented.py`, `temporal.py` задают постановку и эвристические решения | Нет доказанного оптимального метода, solver-integrated objective и теорем | P0 |
| Разделение trajectory/likelihood/parameter/posterior/statistical/cost errors | PARTIAL | trajectory RMSE/max error и NLL есть в runner; `parameter_rmse`, `likelihood_distortion`, `false_optimum_rate` есть в `inference/metrics.py`; posterior distances есть | Нет единого end-to-end отчёта, statistical uncertainty и reliability calibration | P0 |
| Literature review и research-gap analysis | NO | Есть только `research/literature_review/README.md` | Нет библиографии, таблицы аналогов и проверенного сравнения DALTON, adjoint, probabilistic ODE, SciML/SUNDIALS | P0 |
| Baseline solvers RK45/DOP853/Radau/BDF/LSODA | YES | `numeris/solvers/scipy_solver.py`, solver choices в CLI и regression tests поддерживают все пять методов | Полное научное сравнение на всех протоколах не проведено | P1 |
| Пять обязательных benchmark-моделей | YES | Oscillator, FitzHugh–Nagumo, Lotka–Volterra, Lorenz, Robertson в `numeris/benchmarks/`; unit/smoke coverage есть | Нет полной серии inference-экспериментов по всем моделям | P1 |
| Synthetic data, controlled noise, converged references | PARTIAL | CLI создают seeded synthetic observations; reference solve и convergence test есть; repeated runner использует общий reference | Независимая reference-проверка и protocol для каждой модели не оформлены как научный результат | P0 |
| Equal-budget comparison | PARTIAL | `Budget`, `BudgetLedger`, solver cost metrics и temporal allocator существуют | Budget ledger начисляет стоимость после solve; нет полноценной budget matrix и доказанного одинакового stopping protocol | P0 |
| Repeated runs и uncertainty summaries | PARTIAL | `numeris/benchmarks/repeated.py` повторяет trials по seeds, сохраняет runs, считает `failure_rate` и summaries для nfev/runtime/target_error; есть integration tests | Не повторяется parameter/posterior inference; нет confidence intervals/statistical tests и полного отчёта по всем моделям | P0 |
| Ablation study | NO | В документации упоминается как будущее сравнение | Нет runner/protocol/results для отключения компонентов controller | P0 |
| Parameter RMSE | PARTIAL | `numeris/inference/metrics.py` реализует и тестирует числовую метрику | В benchmark runner нет fitting против `true_parameters` и серии результатов | P0 |
| Likelihood error относительно reference | PARTIAL | `likelihood_distortion(reference, candidate)` реализована и протестирована; runner сохраняет candidate NLL | Reference NLL автоматически не вычисляется/не сравнивается как distortion в runner | P1 |
| Posterior distance | PARTIAL | `hellinger_distance`, ограниченный `normalized_grid_posterior`, `wasserstein_1d` присутствуют | Нет ODE posterior pipeline, MCMC и posterior experiments; Wasserstein — упрощённое 1-D сопоставление отсортированных samples | P1 |
| False-optimum rate | PARTIAL | `false_optimum_rate` реализует и тестирует rate для scalar/vector optima | Нет multi-start likelihood-landscape benchmark, truth set и фактических результатов | P0 |
| Runtime/RHS/peak RAM | PARTIAL | solver и runner сохраняют `nfev`, runtime и peak RSS | Peak RSS — process high-water mark; нет изолированного per-run memory measurement | P1 |
| Failure rate | PARTIAL | `run_repeated` считает failures по seed/config и сохраняет failed trials | Нет failure-rate результатов для полного научного протокола и inference failures | P1 |
| Reliability calibration | NO | Controller принимает внешнюю `state_error_estimate`; отдельной calibration implementation нет | Нет predicted-vs-actual coverage, calibration curves и acceptance results | P0 |
| Goal-oriented error estimator | PARTIAL | `SensitivityAwarePolicy` формально считает `target_error_estimate` и marginal benefit/cost | Это прозрачная эвристика; нет adjoint/sensitivity solver integration и доказанной estimator validity | P0 |
| Budget allocation по временным интервалам | PARTIAL | `controller/temporal.py` добавляет greedy `allocate_budget_by_sensitivity` с budget-respecting tests | Это baseline ranking по supplied sensitivities/costs; нет автоматического получения sensitivities, refinement и empirical superiority | P0 |
| Reliability stopping criterion | PARTIAL | `SensitivityAwarePolicy` имеет решения refine/stop по tolerance, budget и ratio | Нет calibrated target error и проверки, что stopping criterion обеспечивает заявленную reliability | P1 |
| Model Definition: params, bounds, observations, noise, ID, config | PARTIAL | `models/config.py` добавляет `ParameterSpec`/`ModelConfig`, bounds, model ID, observations/noise metadata и JSON round-trip; tests есть | Config не встроен в `ODEModel`, solver, inference и CLI как единый обязательный schema | P1 |
| Solver interface и instrumentation | PARTIAL | SciPy adapter, method/rtol/atol/max_step, trajectory, nfev/runtime/peak RSS работают | Hard budget interruption отсутствует; budget charge происходит после полного solve | P1 |
| Numerical Error Observatory | PARTIAL | `error_analysis/observatory.py` и convergence test сравнивают решения с reference | Нет полноценного local-error/interval-sensitivity/tolerance-sweep pipeline и автоматического накопления error report | P1 |
| Inference Engine: MLE, bounds, Gaussian, intervals, multi-start | PARTIAL | `fit_parameters` поддерживает deterministic Gaussian MLE и bounds; `ModelConfig` хранит bounds metadata | Нет confidence intervals, multi-start orchestration, inference budget и benchmark parameter recovery | P1 |
| Inference Distortion Detector | PARTIAL | Метрики distortion/RMSE/false-optimum и runner outputs добавлены | Нет автоматического tolerance sweep, сравнения fitted optima/posteriors и distinction numerical vs statistical uncertainty | P0 |
| Bayesian inference | NO | `normalized_grid_posterior` прямо ограничен low-dimensional diagnostic grid | Нет PyMC/NumPyro sampler, posterior protocol, convergence diagnostics и repeated Bayesian experiments | P0 |
| Budget manager RHS/time/runs/memory | PARTIAL | `BudgetLedger` учитывает RHS, время и runs | Memory limit не реализован; превышение выявляется после завершения solver | P1 |
| Benchmark laboratory и JSON | PARTIAL | `runner.py`, `repeated.py`, два CLI и JSON-friendly outputs есть | Нет единого полного protocol, объединяющего budgets, repeats, parameter/posterior metrics, calibration и ablation | P1 |
| Reproducibility engine | PARTIAL | `ReproducibilityMetadata` сериализует Python/NumPy/SciPy versions, seed, solver settings, hardware и timestamp; oscillator/all-model CLI включают metadata | Metadata не является частью всех benchmark/inference paths; runtime/RSS делают отчёты не полностью byte-identical | P1 |
| Visualization | PARTIAL | `numeris/visualization/plots.py` содержит trajectory/error/likelihood-budget plots | Нет posterior, calibration, parameter-surface, repeated uncertainty и multi-budget views | P2 |
| Unit/integration/numerical/regression tests | PARTIAL | Покрыты новые config, metrics, temporal allocator, repeated runner, CLI и прежние модули | Тесты проверяют software behavior, но не заменяют scientific acceptance, ablation и calibration | P1 |
| Local macOS/Apple Silicon и <=8 GB target | PARTIAL | Локальный Python/SciPy design и metadata hardware capture есть | Нет memory guard, workload policy и CI validation на Apple Silicon; peak RSS не ограничивается | P2 |
| Documentation/API/examples/limitations | PARTIAL | README, docs, API, example и limitations присутствуют | Документация не содержит завершённых scientific results и полного API/protocol reference | P2 |
| Research notes, derivations, publication materials | NO | `research/` и `papers/` содержат только заготовки/описания | Нет literature review, derivations, proofs, manuscript и publication-grade tables | P0 |
| Negative results и self-refutation | PARTIAL | `research/negative_results.md`, hypothesis и limitations задают условия самоопровержения | Нет фактического negative-results ledger и системной проверки случаев, где baseline лучше | P0 |
| Privacy boundary | YES | `private/TECHNICAL_SPEC.md` read-only и исключён; publication safety script и archive checks присутствуют | Это процедурная защита, а `git add -f` технически возможно; нужна дисциплина проверок | P1 |
| GitHub readiness | YES | Public repository, CI, LICENSE, CITATION, CONTRIBUTING и audit присутствуют; push history available | Научная публикационная готовность отсутствует, потому что P0 scientific evidence не завершена | P2 |

## Отдельная проверка новых компонентов после `33fdb96`

| Компонент | Фактически подтверждено | Чего он не доказывает |
|---|---|---|
| `inference/metrics.py` | `parameter_rmse`, `likelihood_distortion`, `false_optimum_rate` имеют валидацию входов и unit-тесты | Наличие метрики не означает наличие parameter-fitting, landscape или научных результатов |
| `benchmarks/repeated.py` | Повторы по seeds, одинаковые noisy observations внутри seed, failed trials, failure rate и summaries для nfev/runtime/trajectory RMSE; JSON serialization test | Нет повторного MLE/Bayesian inference, uncertainty intervals, significance tests или ablation |
| `models/config.py` | Serializable `ModelConfig`/`ParameterSpec`, bounds, observations/noise metadata, JSON round-trip и uniqueness validation | Metadata contract не подключён end-to-end к runtime model, solver и inference |
| `controller/temporal.py` | Greedy sensitivity-per-cost interval selection с ограничением total budget и tests | Не является доказанным optimal allocator и не получает sensitivity/error автоматически |
| CLI reproducibility metadata | Oscillator и all-model CLI сохраняют seed, solver settings, package versions и hardware metadata | Не все experiment paths используют metadata; записи времени и machine-dependent cost не гарантируют идентичные отчёты |

## Итоговый вердикт

**PARTIALLY COMPLIANT / NOT SCIENTIFICALLY COMPLETE.**

По software-части NUMERIS заметно продвинулся после `33fdb96`: добавлены проверяемые inference metrics, repeated benchmark orchestration, serializable model metadata, temporal budget-allocation baseline и CLI reproducibility metadata. Эти изменения закрывают отдельные инженерные требования частично или полностью.

Проект всё ещё не является завершённой научной работой и не подтверждает научный вклад NUMERIS-GO. Отсутствуют или не выполнены: literature review и research-gap analysis, Bayesian sampling, mathematical proofs, solver-integrated validated estimator, полноценный equal-budget inference protocol, parameter/posterior experiments, ablation study, reliability calibration, false-optimum experiments и публикационные материалы. `SensitivityAwarePolicy` и temporal allocator следует считать исследовательскими baseline/эвристиками до получения теоретических и экспериментальных доказательств.

Рекомендуемый порядок P0: (1) зафиксировать literature/gap matrix; (2) определить reference и equal-budget protocol; (3) встроить ModelConfig и target metrics в end-to-end inference benchmark; (4) добавить Bayesian sampling или честно сузить scope; (5) провести repeated parameter/posterior experiments, ablation и calibration; (6) опубликовать как положительные, так и отрицательные результаты.
