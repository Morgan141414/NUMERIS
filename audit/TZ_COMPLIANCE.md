# NUMERIS — строгий аудит соответствия ТЗ

Дата аудита: 2026-10-30 (Asia/Almaty)  
Проверенный commit: `c1fb735` (`main`, совпадает с `origin/main`)  
Объект: локальный репозиторий `NUMERIS` и локальное read-only ТЗ `private/TECHNICAL_SPEC.md`.

## 1. Итог

**Статус: частичное соответствие, научная работа по ТЗ не завершена.**

Репозиторий является запускаемым инженерным прототипом детерминированной ODE-лаборатории. В нём есть пять benchmark-моделей, SciPy-адаптер, Gaussian likelihood, простая параметрическая оптимизация, диагностическая эвристика NUMERIS-GO, бюджетный ledger, визуализация, CLI и тесты.

Однако обязательные научные результаты ТЗ пока отсутствуют: нет полноценного литературного обзора, доказанной новизны, интегрированного goal-oriented контроллера, equal-budget исследования, Bayesian/MCMC протокола, ablation study, false-optimum/calibration/failure экспериментов, статистического анализа повторных запусков и статьи. Поэтому проект нельзя объявлять соответствующим ТЗ на 100% или доказавшим преимущество NUMERIS.

Фактически проверено локально:

- `./.venv/bin/python -m pytest -q` → **41 passed**;
- `./.venv/bin/python scripts/check_publication_safety.py` → **Publication safety check passed**;
- `git ls-files` не содержит `private`, `TECHNICAL_SPEC`, `confidential`, `secret`;
- `git archive HEAD` не содержит приватных путей;
- рабочее дерево на момент аудита чистое и `main...origin/main`.

`41 passed` подтверждает тестируемое поведение текущего кода, но не подтверждает научную гипотезу и не заменяет экспериментальную валидацию из ТЗ.

## 2. Легенда и приоритеты

- **MUST** — обязательное требование выполнено доказательно.
- **Частично** — есть заготовка или отдельная часть требования, но отсутствует обязательная интеграция, доказательство или покрытие.
- **Нет** — требование не реализовано или не подтверждено.

Приоритеты:

- **P0** — блокирует честное заявление о выполнении ТЗ/научном результате.
- **P1** — обязательно для исследовательского протокола и воспроизводимого сравнения.
- **P2** — важное качество продукта/документации.

## 3. Матрица соответствия внутреннему ТЗ

| Требование ТЗ | Статус | Приоритет | Фактическое свидетельство | Что отсутствует |
|---|---|---:|---|---|
| Исследовательская идентичность: inference-aware лаборатория, гипотеза, возможность отрицательного результата | MUST | P0 | `README.md:5-7,23-40`; `research/hypotheses/HYPOTHESIS.md:1-11`; `docs/limitations.md:1-3` | На уровне формулировок выполнено; экспериментального подтверждения гипотезы нет. |
| Ограничение первой версии детерминированными ODE и Gaussian observation model | MUST | P1 | `numeris/models/base.py:12-35`; `numeris/inference/gaussian.py:10-35` | В коде нет явной декларации/валидации модели шума и идентификатора модели. |
| Формальная задача `min_A E_target(A)` при `C(A) <= B` | Частично | P0 | `docs/mathematical_foundation.md:3-5`; `numeris/controller/goal_oriented.py:44-64` | Реализована эвристика на входных оценках, но нет алгоритма распределения бюджета по временным интервалам и нет теории/гарантий. |
| Разделение trajectory error, likelihood error, parameter error, posterior distance, statistical uncertainty, solver cost | Частично | P0 | `numeris/error_analysis/observatory.py`; `numeris/benchmarks/runner.py:104-119`; `docs/methodology.md:3-7` | Runner не считает parameter error, posterior distance, statistical uncertainty или reliability calibration. |
| Обзор adaptive step-size, local/global error, adjoint/goal-oriented, probabilistic ODE, Bayesian inverse, DALTON, SciPy/SUNDIALS/SciML | Нет | P0 | `research/literature_review/README.md:1-5` прямо говорит, что это ledger, а не завершённый обзор | Нет библиографии, таблицы методов, источников, реализации/условий сравнения и research-gap анализа. |
| Не переименовывать известный алгоритм в новый | Частично | P0 | `README.md:7`; docstring `numeris/controller/goal_oriented.py:1-5,63-64` честно называет метод heuristic | Нет доказательства отличия от существующих методов; нет comparative literature analysis. |
| SciPy RK45, DOP853, Radau, BDF, LSODA | MUST | P1 | `scripts/run_oscillator_benchmark.py:35-40`; `numeris/solvers/scipy_solver.py`; `tests/regression/test_public_api.py:7-14` | Поддержка есть; системное сравнение всех методов на всех применимых моделях не проведено. |
| Модели oscillator, FitzHugh–Nagumo, Lotka–Volterra, Lorenz, Robertson | MUST | P1 | `numeris/benchmarks/*.py`; `tests/unit/test_benchmarks.py`; `scripts/run_all_benchmarks.py:24-30` | Фабрики и smoke-интеграция есть; научные benchmark-серии отсутствуют. |
| Известные параметры, synthetic observations, controlled noise, converged reference | Частично | P0 | `scripts/run_oscillator_benchmark.py:86-110`; `scripts/run_all_benchmarks.py:44-56`; `tests/numerical/test_reference_convergence.py` | References — один tightened solve; независимая проверка есть только как требование/тест для oscillator, не полноценный протокол для всех пяти моделей. |
| Equal-budget comparison | Частично | P0 | `numeris/budget/ledger.py`; `numeris/benchmarks/runner.py:123-153`; `docs/benchmarks.md:7` | Ledger умеет учитывать ресурсы, но CLI не задаёт бюджет, solver не прерывается до выполнения, нет матрицы matched budgets и trade-off анализа. |
| Repeated runs и uncertainty summaries | Частично | P1 | `numeris/benchmarks/statistics.py`; `research/hypotheses/HYPOTHESIS.md:9-11` | Summary primitive есть, но runner/CLI не выполняют повторы и не сохраняют uncertainty summaries. |
| Ablation study каждого компонента controller | Нет | P0 | Только требования в `docs/benchmarks.md:7` и `docs/roadmap.md:16-21` | Нет сценария, данных, таблиц или теста ablation. |
| Parameter RMSE | Нет | P0 | `numeris/inference/gaussian.py:18-35` умеет оптимизацию, но `runner.py:104-119` параметров не оценивает | Нет benchmark-пайплайна fit-vs-truth и метрики RMSE. |
| Likelihood error относительно reference | Частично | P1 | `runner.py:96-114` сохраняет только candidate NLL | Нет reference NLL и `target_distortion` в report; поле `likelihood error` в docs фактически не соответствует output. |
| Posterior distance: Hellinger/Wasserstein | Частично | P1 | `numeris/inference/distances.py`; `numeris/inference/grid.py` | Примитивы есть, но нет построения posterior из ODE inference и benchmark-сравнения. `wasserstein_1d` для неравных размеров использует усечённые сортированные выборки, что не является общей реализацией Wasserstein-1. |
| False optimum rate | Нет | P0 | В репозитории нет реализации/данных | Нет multi-start likelihood landscape и определения/подсчёта ложного оптимума. |
| Runtime, RHS evaluations, peak RAM | Частично | P1 | `numeris/solvers/scipy_solver.py:15-26`; `runner.py:115-119` | `ru_maxrss` — process-wide high-water mark, не память конкретного запуска; нет стандартизованного повторного измерения. |
| Failure rate | Нет | P1 | Есть `success/message` в `runner.py:104-108` | Нет серии повторов/определения знаменателя/отчёта failure rate. |
| Reliability calibration | Нет | P0 | `SensitivityAwarePolicy` принимает оценку ошибки извне | Нет predicted-vs-actual calibration experiment и coverage/графиков. |
| Goal-oriented error estimator | Частично | P0 | `SensitivityAwarePolicy` в `goal_oriented.py:44-124` вычисляет `sensitivity * state_error` | Это локальная эвристика по пользовательским оценкам, не estimator из решателя, не adjoint/variational метод и не интегрированный control loop. |
| Budget allocation rule по временным интервалам | Нет | P0 | Нет модуля/кода, распределяющего tolerance/steps между интервалами | Контроллер принимает один candidate refinement; temporal allocation отсутствует. |
| Reliability stopping criterion | Частично | P1 | `goal_oriented.py:104-123` останавливает по tolerance/budget/ratio | Критерий не получает фактической оценки из численного эксперимента и не проверен на calibration/utility. |
| Assumptions, applicability, failure modes controller | Частично | P1 | Docstring `goal_oriented.py:48-64`; `docs/limitations.md` | Описания есть; систематической матрицы применимости и failure experiments нет. |
| Model Definition: params, constraints, observations, noise, unique ID, config persistence | Частично | P1 | `ODEModel` содержит RHS/state/time/observe; metadata сохраняется отдельно | Нет parameter schema, bounds в model, noise model объекта, unique model ID и сериализуемой model config. `fit_parameters` принимает bounds только на уровне вызова. |
| Solver interface: tolerances, max step, trajectory, nfev, errors, time | MUST | P1 | `scipy_solver.py:29-51`; `SolverConfig`; tests | Основной интерфейс выполнен; budget не предотвращает фактическое перерасходование до solve. |
| Numerical Error Observatory: local/global error, tolerance sweeps, accumulation, sensitive intervals | Частично | P1 | `error_analysis/observatory.py`; `tests/numerical/test_reference_convergence.py` | Есть сравнение массивов и target distortion, нет local error, interval sensitivity, accumulation analysis или sweep runner. |
| Inference Engine: MLE, bounded runs, Gaussian likelihood, intervals, multi-start | Частично | P1 | `fit_parameters` и `gaussian_negative_log_likelihood` | MLE/Gaussian/bounds есть; нет confidence intervals, multi-start orchestration, convergence report и budget accounting inside optimization. |
| Inference Distortion Detector | Частично | P0 | `target_distortion` и candidate NLL | Нет автоматического сравнения tolerances на fitted parameters, maxima, intervals/posteriors и distinction from statistical uncertainty. |
| Bayesian inference | Нет | P0 | `normalized_grid_posterior` — только low-dimensional grid diagnostic; `pyproject.toml:12-13` не содержит PyMC/NumPyro | Нет PyMC/NumPyro sampler, posterior experiment, convergence diagnostics или posterior benchmark. |
| Budget manager: RHS/time/memory/repeats and limits | Частично | P1 | `numeris/budget/ledger.py` | RHS/time/runs есть; memory limit отсутствует; runtime budget проверяется после solve; no hard stop/atomic reservation for actual integration. |
| Benchmark laboratory and JSON reports | Частично | P1 | `runner.py`; `scripts/run_oscillator_benchmark.py`; `scripts/run_all_benchmarks.py` | JSON/CLI есть; all-model script фиксирует один solver matrix, не reference convergence, no full protocol/budget/repeats/metadata. |
| Reproducibility engine integrated into reports | Частично | P1 | `ReproducibilityMetadata` и tests | Класс сериализует metadata, но оба CLI/report runner его не вызывают; отчёты не содержат software versions/hardware context/observation grid fully. |
| Visualization: trajectories, errors, likelihood, posterior, budget, accuracy-cost | Частично | P2 | `numeris/visualization/plots.py`; tests | Есть три generic plot functions; нет posterior, parameter surfaces, uncertainty, reliability calibration, multi-method budget dashboard. |
| Unit/integration/numerical/regression tests | MUST | P1 | `tests/unit`, `integration`, `numerical`, `regression`; 41 passed | Покрытие подтверждает API, но не научные acceptance criteria. |
| Local Apple Silicon/macOS and <=8 GB experiment target | Частично | P2 | `README.md:19`; solver captures platform | Нет explicit memory guard, workload-size policy или platform validation in CI; CI runs Ubuntu, not target Mac. |
| Documentation/API/examples/limitations | Частично | P2 | `docs/*.md`, `README.md`, `examples/oscillator_demo.py` | Документация честная, но public docs содержат roadmap contradictions: budget/controller listed as “next” although code exists; no API reference for all public modules. |
| Research notes, derivations, publication materials | Нет | P0 | `research/` содержит hypothesis/ledger/negative-results; `papers/` пустой | Нет filled derivations, literature results, manuscript, tables or reproducibility package. |
| Negative results and self-refutation | Частично | P0 | `research/negative_results.md`; hypothesis falsification conditions | Ledger пуст/шаблонный; нет фактических failed/baseline-better records. |
| Acceptance: formal contribution, proof/empirical separation, five families, sensitivity, ablation, reproducibility | Частично | P0 | Formal separation documented in README/docs; five factories/tests exist | Scientific acceptance not met: sensitivity/ablation/repeated equal-budget evidence and contribution are missing. |
| Privacy: full TЗ local-only, read-only, excluded from Git and archive | MUST | P1 | `private/TECHNICAL_SPEC.md` mode `0444`; `.gitignore:10`; safety script; archive scan | Current commit/archive clean. This is a process control, not cryptographic protection; `git add -f` remains possible, so checks must run before every push. |
| GitHub readiness: CI, license, citation, contribution docs, clean public archive | MUST | P2 | `.github/workflows/ci.yml`; `LICENSE`; `CITATION.cff`; `CONTRIBUTING.md`; remote `origin` | CI/test/repository hygiene ready; scientific release readiness is not met because results and paper are absent. |

## 4. Критические несоответствия

### P0 — нельзя объявлять ТЗ выполненным

1. Нет доказанного нового метода: `SensitivityAwarePolicy` — прозрачная эвристика, которая получает уже оценённые `state_error_estimate`, sensitivity и candidate reduction (`numeris/controller/goal_oriented.py:44-124`). Она не подключена к solver control loop и не распределяет бюджет по временным интервалам.
2. Нет завершённого обзора литературы и gap analysis; `research/literature_review/README.md` прямо является пустым ledger.
3. Нет equal-budget научного сравнения с tuned baselines, repeated seeds и ablation.
4. Нет parameter RMSE pipeline, false-optimum rate и reliability calibration.
5. Нет Bayesian sampler и контролируемого posterior эксперимента.
6. Reference strategy в CLI — tightened solve, а не доказанно независимый reference для всех пяти моделей (`scripts/run_oscillator_benchmark.py:88-94`, `run_all_benchmarks.py:47-56`).
7. Generated reports не содержат полноценные reproducibility metadata, хотя класс для этого существует.

### P1 — существенно снижает воспроизводимость и соответствие реализации документации

1. `docs/roadmap.md:14-20` не синхронизирован с кодом: budget ledger и controller уже существуют, но перечислены как следующие milestones.
2. `docs/benchmarks.md:3` обещает target likelihood error, но runner сохраняет candidate NLL, а не distortion относительно reference.
3. `run_all_benchmarks.py` не записывает observation grid, parameters, solver configurations, software versions/hardware context в один отчет.
4. Budget ledger не может остановить solver до перерасхода: solve выполняется целиком, затем `charge_rhs` проверяет лимит (`runner.py:83-95`).
5. Memory budget из ТЗ не реализован.

## 5. Что считается готовым сейчас

Можно честно утверждать, что готов следующий scope:

> Локальный Python-прототип для детерминированных ODE benchmark-ов: пять модельных фабрик, SciPy solver adapter для RK45/DOP853/Radau/BDF/LSODA, Gaussian NLL, простая parameter fitting функция, diagnostic sensitivity-aware policy, budget accounting, visualization, CLI, JSON serialization и 41 автоматический тест.

Нельзя утверждать, что готово:

> Новый математический метод, превосходящий существующие методы и доказавший повышение надёжности inference при равном бюджете.

## 6. Приоритизированный план следующих задач

### P0 — научная валидность

1. Заполнить literature review: первичные публикации и implementations; для каждой — objective, estimator, control variable, budget, assumptions, benchmark overlap, exact difference. Отдельно проверить adjoint/goal-oriented methods, probabilistic ODE solvers, likelihood-aware methods, DALTON, SciPy/SUNDIALS/SciML.
2. Зафиксировать protocol до экспериментов: models, parameter truths, observation grids, noise levels, seeds, tolerances, budgets, reference procedure, primary endpoints, exclusion/failure rules.
3. Реализовать реальный inference benchmark: fit parameters from observations, parameter RMSE, NLL distortion against reference, multi-start optimization and convergence metadata.
4. Реализовать reference validation для каждой модели: tolerance sweep plus independent solver; для Robertson — independent stiff method; для Lorenz — target/statistical metrics instead of trajectory-only claims.
5. Подключить controller к измеряемым diagnostics и формализовать хотя бы одну исследуемую contribution line: estimator, budget allocation или stopping criterion. Пока это research prototype, не novelty claim.
6. Реализовать equal-budget matrix across methods/tolerances/noise/seeds and report target error vs RHS/runtime.
7. Провести ablation study: remove estimator, allocation, stopping component separately; record negative results.
8. Добавить false-optimum rate и reliability calibration; определить, как отделяется numerical distortion от statistical uncertainty.

### P1 — inference/reproducibility

9. Добавить controlled low-dimensional posterior experiment; grid posterior можно оставить как diagnostic, но честно обозначить, что это не MCMC. Затем добавить PyMC/NumPyro only if resource budget allows.
10. Интегрировать `ReproducibilityMetadata.capture()` в benchmark reports; включить model ID, params, observation times, noise seed, solver matrix, tolerances, budget, reference provenance, versions and hardware.
11. Исправить benchmark report: добавить reference NLL, absolute/relative likelihood distortion, parameter result/error, failure record, budget limits/consumption and uncertainty summaries.
12. Решить semantics budget enforcement: either implement solver-level budget-aware interruption or explicitly document that ledger is post-run accounting and not a hard execution limit. Add memory accounting/limit if required by scope.
13. Fix or document Wasserstein implementation for unequal sample sizes; current truncation is not a general empirical Wasserstein-1 calculation.

### P2 — release quality

14. Синхронизировать `docs/roadmap.md`, README и фактический status.
15. Добавить API docs for all public modules and a single reproducible experiment command with expected artifacts.
16. Добавить calibration/posterior/budget plots and selected fixtures only after protocol is fixed.
17. После получения результатов заполнить `research/negative_results.md`, `research/derivations/`, `papers/`, and update `CITATION.cff` with research release metadata.

## 7. Решение по аудиту

**Вердикт: PARTIALLY COMPLIANT / NOT SCIENTIFICALLY COMPLETE.**

Инженерное основание и privacy boundary соответствуют заявленному prototype scope. Основная исследовательская цель ТЗ — математически обоснованный, экспериментально проверенный и сравнимый контроллер надёжности inference — ещё не достигнута. Следующий корректный шаг — не заявлять успех, а выполнить P0 protocol and validation work; отрицательный результат должен приниматься как допустимый исход.

