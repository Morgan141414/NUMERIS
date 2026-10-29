# NUMERIS — Strict Gatekeeper Audit

Дата аудита: 2026-10-30 (Asia/Almaty)
Аудируемый объект: текущий `HEAD`
HEAD: `22e1f8725d3c126b20b24c6ed520f333d2645db8` (`22e1f87`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение публикации: private ТЗ не публикуется, не отслеживается Git и не входит в публичный архив.
Изменения аудита: изменён только этот файл; code, `research/`, `docs/` и private ТЗ не изменялись. Push не выполняется.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD — локально запускаемый и протестированный исследовательский прототип. Последние изменения добавили воспроизводимые интервалы Bayesian coverage, multi-model validation orchestration, executable closest-baseline reproduction gate и fail-closed C++ gate. Это закрывает инфраструктурные проверки, но не доказывает математическую новизну, превосходство NUMERIS-GO или готовность к публикации.

## Evidence ledger

| Критерий | Статус | Фактическая проверка и интерпретация |
|---|---|---|
| Полный тестовый набор | **PASS** | `./.venv/bin/pytest -q` → **95 passed**. |
| Publication safety | **PASS** | `python3 scripts/check_publication_safety.py` → `Publication safety check passed`; private/spec paths не входят в публичный Git/archive. |
| Baseline reproduction gate | **PASS для структурного gate / PARTIAL для научного воспроизведения** | `bash research/protocol/check_baseline_reproduction.sh` проходит; manifest, ledger, baseline cards, статусы и controls присутствуют. Научные R1–R3 evidence и source-aligned reproductions ещё не выполнены. |
| Literature foundation | **PARTIAL** | Есть inclusion/exclusion protocol, bibliography ledger, comparison matrix и reproduction plan. Нет завершённого overlap audit и итогового решения о novelty/no-novelty. |
| Frozen experiment protocol | **PASS для freeze / PARTIAL для execution** | Версионированный manifest фиксирует модели, параметры, шум, seeds, методы, tolerance grid, budgets, reference policy и falsification rule. Полная кампания по manifest не выполнена и не заархивирована. |
| Bayesian parameter recovery | **PASS как deterministic diagnostic / PARTIAL по ТЗ** | Работает finite-grid Gaussian posterior и recovery summary. Это не MCMC/PyMC/NumPyro и не доказательство posterior reliability. |
| Bayesian calibration intervals | **PASS как ограниченный helper / PARTIAL по ТЗ** | Coverage, Wilson interval, counts, mean width, Monte Carlo SE и reproducible seeds реализованы и покрыты тестами. Нет полноценной sampler convergence диагностики, posterior predictive checks, независимого Bayesian reference и разделения statistical-vs-numerical uncertainty. |
| Reference convergence report | **PASS как utility / PARTIAL как scientific gate** | `reference_report` требует минимум два solver methods, считает consensus, disagreement, RMSE, max error, nfev и runtime; consensus явно не объявляется абсолютной истиной. Полные cross-family reference checks для всех пяти моделей не выполнены как committed campaign. |
| Multi-model validation report | **PASS как orchestration / PARTIAL как evidence** | `run_validation_suite` поддерживает несколько моделей, reference report, calibration, limits и JSON summary. Наличие orchestration не заменяет фактическую полную frozen campaign с результатами и отрицательными случаями. |
| Equal-budget comparison | **PARTIAL** | Paired comparison и smoke checks работают. Budget caps являются проверкой результата после solver call, а не гарантированным interrupt hard cap; нет полного набора protocol cells, paired confidence intervals и committed scientific results. |
| Ablation | **PARTIAL infrastructure / FAIL as scientific evidence** | Callback path реально исполняется и сохраняет metadata. Нет полного estimator-only, allocation-only, stopping-only и full-policy набора на всех объявленных моделях и бюджетах. |
| Reliability calibration | **PARTIAL** | Bayesian coverage helper и общие error-bound metrics существуют. Нет полного сравнения emitted numerical-error bounds с независимой фактической ошибкой по всем declared workloads; систематическая overconfidence не исследована. |
| C++ fail-closed gate | **PASS как safety decision / KEEP_PYTHON** | `python3 scripts/check_cpp_gate.py` выдаёт `KEEP_PYTHON`: отсутствуют hotspot corpus, equivalence, warm-up speed, memory и reproducibility evidence. C++ не требуется автоматически; production C++ не добавлять до прохождения всех predicates. |
| Software laboratory | **PARTIAL** | Models, SciPy solver adapters, inference diagnostics, budget accounting, reports, profiling, tests и reproducibility support присутствуют. Полная end-to-end acceptance по ТЗ не закрыта из-за отсутствия validated controller и complete campaign artifacts. |
| Git/publication hygiene | **PASS** | Рабочее дерево было чистым до изменения аудита; private ТЗ не копируется в публичные материалы. Этот audit commit выполняется локально, без push. |

## Phase gates against the private ТЗ

### Phase I — Research Foundation: **PARTIAL**

Структура обзора, ledger, comparison matrix, protocol и baseline-reproduction gate созданы. Не завершены source-aligned reproductions, line-by-line mechanism/overlap audit и окончательная фиксация research gap. Claims `novel`, `first`, `superior` и `publication-ready` запрещены.

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty**

Есть target-versus-cost постановка, Gaussian likelihood perturbation baseline и heuristic sensitivity/temporal policy scaffolding. Нет validated solver-integrated goal-oriented estimator, доказанных convergence/stability/reliability свойств и подтверждённой математической новизны.

### Phase III — Software Laboratory: **PARTIAL**

Основные программные модули и тестируемые отчёты работают локально. Не закрыты hard-budget semantics, production-level controller integration и полный end-to-end reproducibility package для всех заявленных экспериментов.

### Phase IV — Scientific Validation: **FAIL**

Нет committed evidence полного frozen campaign для пяти моделей, всех seeds/noise/method/tolerance/budget combinations, независимых reference checks, primary endpoint analysis, false-optimum study, posterior-distance study, paired confidence intervals, negative-results ledger и полного component ablation.

### Phase V — Publication readiness: **BLOCKED**

Validated scientific contribution, superiority/non-inferiority result, complete figures/tables, manuscript и independent reproduction package не установлены. Публикация не следует из наличия кода и 95 passing tests.

## Required remaining gates

1. Выполнить и сохранить convergence/cross-family reference checks для всех пяти benchmark families.
2. Запустить frozen manifest целиком; сохранить success, failed и over-budget trials, commit hash и machine-readable summaries.
3. Рассчитать likelihood distortion, parameter RMSE, posterior distance и false-optimum endpoints с заранее заданными paired uncertainty intervals.
4. Завершить source-aligned baseline reproduction либо зафиксировать blockers с допустимым статусом `NOT-REPRODUCED`.
5. Подключить реальные estimator/allocation/stopping components и провести полный ablation study.
6. Проверить emitted error estimates против независимой фактической ошибки; overconfidence считать gate failure.
7. Реализовать hard-budget semantics или явно ограничить claim post-hoc accounting.
8. Провести representative multi-model profiling; затем пройти C++ equivalence, warm-up speed, memory и reproducibility gates либо сохранить отрицательное решение `KEEP_PYTHON`.
9. Вести committed negative-results record: baseline-better cases, failures, budget exhaustion и ограничения применимости.

## Permitted public claim

> NUMERIS HEAD `22e1f87` — локально запускаемый, протестированный deterministic research prototype с frozen experiment manifest, baseline-reproduction protocol, finite-grid Bayesian diagnostics, reproducible reference/validation helpers и fail-closed optional C++ gate. Он не является подтверждённо новым методом, доказанно превосходящим стандартные решатели, завершённым Bayesian study или publication-ready результатом.
