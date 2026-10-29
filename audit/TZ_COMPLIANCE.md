# NUMERIS — итоговая таблица соответствия ТЗ

Дата: 2026-10-30  
Проверка: `41 passed`; privacy-check пройден; приватное ТЗ отсутствует в Git и Git-архиве.

| Requirement | Status | Files | Gap | Priority |
|---|---|---|---|---:|
| Исследовательская identity и фальсифицируемая гипотеза | MUST | `README.md`; `research/hypotheses/HYPOTHESIS.md`; `docs/limitations.md` | Формулировки есть, экспериментального подтверждения нет | P0 |
| ODE scope и Gaussian observations | MUST | `numeris/models/base.py`; `numeris/inference/gaussian.py` | Нет формальной noise-model/schema и model ID | P1 |
| Формальная задача `min E_target` при `C <= B` | PARTIAL | `docs/mathematical_foundation.md`; `numeris/controller/goal_oriented.py` | Есть только эвристика; нет доказательств и temporal budget allocation | P0 |
| Разделение trajectory/likelihood/parameter/posterior/statistical/cost errors | PARTIAL | `numeris/error_analysis/observatory.py`; `numeris/benchmarks/runner.py` | Нет parameter error, posterior benchmark, statistical uncertainty и calibration | P0 |
| Literature review и research-gap analysis | NO | `research/literature_review/README.md` | Нет библиографии, таблицы аналогов и сравнительного анализа DALTON/adjoint/probabilistic methods | P0 |
| Baseline solvers RK45/DOP853/Radau/BDF/LSODA | MUST | `numeris/solvers/scipy_solver.py`; `scripts/run_oscillator_benchmark.py`; `tests/regression/test_public_api.py` | Поддержка есть, полного системного сравнения нет | P1 |
| Пять обязательных benchmark-моделей | MUST | `numeris/benchmarks/*.py`; `tests/unit/test_benchmarks.py` | Фабрики и smoke-тесты есть, научных серий нет | P1 |
| Synthetic data, controlled noise, converged references | PARTIAL | `scripts/run_oscillator_benchmark.py`; `scripts/run_all_benchmarks.py`; `tests/numerical/test_reference_convergence.py` | Независимая reference-проверка не проведена для всех моделей | P0 |
| Equal-budget comparison | PARTIAL | `numeris/budget/ledger.py`; `numeris/benchmarks/runner.py`; `docs/benchmarks.md` | Нет CLI budget matrix; solver выполняется до проверки перерасхода | P0 |
| Repeated runs и uncertainty summaries | PARTIAL | `numeris/benchmarks/statistics.py` | Есть primitive summary, но нет orchestration повторов и отчётов | P1 |
| Ablation study | NO | `docs/benchmarks.md`; `docs/roadmap.md` | Нет сценариев, данных и результатов отключения компонентов | P0 |
| Parameter RMSE | NO | `numeris/inference/gaussian.py`; `numeris/benchmarks/runner.py` | `fit_parameters` есть, benchmark не считает ошибку относительно truth | P0 |
| Likelihood error относительно reference | PARTIAL | `numeris/benchmarks/runner.py`; `numeris/error_analysis/observatory.py` | Сохраняется candidate NLL, но не reference NLL и distortion | P1 |
| Posterior distance | PARTIAL | `numeris/inference/distances.py`; `numeris/inference/grid.py` | Есть примитивы, нет ODE posterior pipeline и экспериментов; Wasserstein упрощён для unequal samples | P1 |
| False-optimum rate | NO | — | Нет multi-start/likelihood-landscape эксперимента и метрики | P0 |
| Runtime/RHS/peak RAM | PARTIAL | `numeris/solvers/scipy_solver.py`; `numeris/benchmarks/runner.py` | RSS — process high-water mark, не изолированная память запуска | P1 |
| Failure rate | NO | `numeris/benchmarks/runner.py` | Есть `success/message`, нет repeated-run failure rate | P1 |
| Reliability calibration | NO | `numeris/controller/goal_oriented.py` | Оценка ошибки подаётся извне, predicted-vs-actual calibration отсутствует | P0 |
| Goal-oriented error estimator | PARTIAL | `numeris/controller/goal_oriented.py` | `SensitivityAwarePolicy` — эвристика, не solver-integrated estimator и не доказанный метод | P0 |
| Budget allocation по временным интервалам | NO | — | Контроллер оценивает один candidate refinement; temporal allocation отсутствует | P0 |
| Reliability stopping criterion | PARTIAL | `numeris/controller/goal_oriented.py` | Есть остановка по tolerance/budget/ratio, но нет фактической calibration/utility проверки | P1 |
| Model Definition: params, bounds, observations, noise, ID, config | PARTIAL | `numeris/models/base.py`; `numeris/inference/gaussian.py` | Нет parameter schema, встроенных bounds/noise/ID/config persistence | P1 |
| Solver interface и instrumentation | MUST | `numeris/solvers/scipy_solver.py`; `numeris/benchmarks/runner.py` | Основной интерфейс выполнен; hard budget interruption отсутствует | P1 |
| Numerical Error Observatory | PARTIAL | `numeris/error_analysis/observatory.py`; `tests/numerical/test_reference_convergence.py` | Нет local error, interval sensitivity, accumulation analysis и tolerance-sweep runner | P1 |
| Inference Engine: MLE, bounds, Gaussian, intervals, multi-start | PARTIAL | `numeris/inference/gaussian.py` | MLE/Gaussian/bounds есть; нет intervals, multi-start orchestration и inference budget | P1 |
| Inference Distortion Detector | PARTIAL | `numeris/error_analysis/observatory.py`; `numeris/benchmarks/runner.py` | Нет автоматического сравнения fitted parameters/maxima/posteriors между tolerances | P0 |
| Bayesian inference | NO | `numeris/inference/grid.py`; `pyproject.toml` | Grid posterior — diagnostic; нет PyMC/NumPyro sampler и posterior protocol | P0 |
| Budget manager RHS/time/runs/memory | PARTIAL | `numeris/budget/ledger.py` | Нет memory limit; runtime/RHS проверяются после полного solve | P1 |
| Benchmark laboratory и JSON | PARTIAL | `numeris/benchmarks/runner.py`; `scripts/run_*.py` | CLI/JSON есть, но нет полного protocol: budgets, repeats, metadata, calibration | P1 |
| Reproducibility engine | PARTIAL | `numeris/reproducibility/metadata.py`; `tests/unit/test_reproducibility.py` | Metadata class есть, но не интегрирована в CLI/reports | P1 |
| Visualization | PARTIAL | `numeris/visualization/plots.py`; `tests/unit/test_visualization.py` | Есть 3 generic plot-а; нет posterior, calibration, parameter-surface и multi-budget views | P2 |
| Unit/integration/numerical/regression tests | MUST | `tests/`; CI | 41 тест проходит; scientific acceptance criteria не покрыты | P1 |
| Local macOS/Apple Silicon и <=8 GB target | PARTIAL | `README.md`; `numeris/solvers/scipy_solver.py`; CI | Нет memory guard/workload policy; CI не проверяет Apple Silicon | P2 |
| Documentation/API/examples/limitations | PARTIAL | `README.md`; `docs/*.md`; `examples/oscillator_demo.py` | Документация честная, но roadmap не синхронизирован с кодом; API неполный | P2 |
| Research notes, derivations, publication materials | NO | `research/`; `papers/` | Есть только шаблоны; нет derivations, статьи и таблиц | P0 |
| Negative results и self-refutation | PARTIAL | `research/negative_results.md`; `research/hypotheses/HYPOTHESIS.md` | Условия заданы, фактический ledger отрицательных результатов пуст | P0 |
| Privacy boundary | MUST | `.gitignore`; `scripts/check_publication_safety.py`; `private/TECHNICAL_SPEC.md` | Текущее состояние чистое; защита процедурная, `git add -f` остаётся возможным | P1 |
| GitHub readiness | MUST | `.github/workflows/ci.yml`; `LICENSE`; `CITATION.cff`; `CONTRIBUTING.md` | CI и public hygiene готовы; научный релиз не готов без P0-результатов | P2 |

## Итоговый вердикт

**PARTIALLY COMPLIANT / NOT SCIENTIFICALLY COMPLETE.**

Готов инженерный прототип ODE-лаборатории. Не готовы и не доказаны: новый математический метод, превосходство над tuned baselines, equal-budget inference advantage, Bayesian validation, ablation, calibration, false-optimum rate, полноценный literature gap и публикационный результат.

Главные следующие задачи: P0 literature review → fixed experimental protocol → reference validation → parameter/inference benchmark → real controller integration → equal-budget/repeated/ablation/calibration experiments → honest negative-results report.
