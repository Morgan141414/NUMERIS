# NUMERIS — Strict Gatekeeper Audit

Дата аудита: 2026-11-03 (Asia/Almaty)
Аудируемый объект: текущий `HEAD`
HEAD: `6d02825b76ae983b3ae3b75a22064c795ffecf42` (`6d02825`, `Add bounded frozen campaign runner`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение публикации: private ТЗ не публикуется, не отслеживается Git и не входит в публичный архив.
Изменения аудита: изменён только этот файл; code, `research/`, `docs/` и private ТЗ не изменялись. Push не выполняется.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD — локально запускаемый исследовательский прототип с 110 passing tests, frozen manifest, evidence ledger, bounded campaign runner, ограниченной Bayesian/calibration диагностикой, hard-budget semantics для bounded orchestration и fail-closed C++ gate. Эти артефакты подтверждают инфраструктурную готовность отдельных проверок, но не доказывают математическую новизну, превосходство NUMERIS-GO, полную воспроизводимость baseline-методов или готовность к публикации.

## Evidence ledger

| Gate | Статус | Фактическое evidence и границы вывода |
|---|---|---|
| Полный тестовый набор | **PASS** | `./.venv/bin/pytest -q` → **110 passed**. |
| Publication safety | **PASS** | `python3 scripts/check_publication_safety.py` → `Publication safety check passed`; private/spec paths не входят в публичный Git/archive. |
| Phase-I evidence ledger | **PASS как контрольный ledger / PARTIAL по научному закрытию** | `PHASE_I_EVIDENCE_LEDGER.md` содержит статусы R1–R3, blockers, checklist и stop conditions. R1–R3 evidence остаётся неполным; reproduction и novelty claims запрещены. |
| Baseline reproduction gate | **PASS для структурного gate / PARTIAL для научного воспроизведения** | `bash research/protocol/check_baseline_reproduction.sh` проходит. Manifest, bibliography, cards и source IDs проверяются. Source-aligned numerical reproductions ADJ-GLOBAL, likelihood-distortion, DALTON и PROB-ODE не завершены. |
| Literature foundation | **PARTIAL** | Есть inclusion/exclusion protocol, bibliography ledger, comparison matrix, baseline manifest и evidence ledger. Нет завершённого overlap/mechanism audit и обоснованного решения о novelty/no-novelty. |
| Frozen experiment protocol | **PASS для freeze / PARTIAL для execution** | Manifest v0.1 фиксирует 5 моделей, параметры, шум, 10 seeds, solver/tolerance grid, budgets, references, endpoints и falsification rule. Полный запуск не выполнен. |
| Bounded frozen campaign | **PASS как bounded infrastructure / BLOCKED как full campaign evidence** | Dry-run на manifest v0.1: `bounded_incomplete`, `3000 planned`, `2 admitted`, `0 solver calls`, `3000 not_started`. Runner сохраняет `success`, `failure`, `over_budget`, `not_started`, но ограниченный run не является полной validation campaign. |
| Bayesian parameter recovery | **PASS как deterministic diagnostic / PARTIAL по ТЗ** | Работает finite-grid Gaussian posterior/recovery helper. Это не MCMC/PyMC/NumPyro и не доказательство posterior reliability. |
| Numerical reliability calibration | **PARTIAL** | Tolerance-sweep calibration сравнивает emitted bound с независимой reference error, считает coverage/overconfidence; Bayesian coverage helper имеет Wilson intervals и Monte Carlo SE. Нет полной declared-workload calibration campaign и установленного отсутствия overconfidence. |
| Reference convergence report | **PASS как utility / PARTIAL как scientific gate** | Есть multi-method consensus, pairwise disagreement, RMSE, max error, nfev и runtime. Полные cross-family reference checks для всех пяти моделей не сохранены как завершённая campaign. Consensus не считается абсолютной истиной. |
| Hard-budget semantics | **PASS для bounded runner / PARTIAL для всей validation stack** | Bounded orchestration выполняет preflight, сохраняет `preflight_rejected`, `completed`, `over_budget`, `not_started` и прекращает последующие запуски после исчерпания бюджета; тесты проходят. Frozen runner сохраняет budget violations, но SciPy solver call не прерывается mid-call, а старый equal-budget comparison остаётся post-hoc. |
| Equal-budget comparison | **PARTIAL** | Paired comparison, same observations/seeds и budget accounting реализованы. Нет полного protocol-wide набора cells, paired confidence intervals и committed scientific results. |
| Ablation | **PARTIAL infrastructure / FAIL as scientific evidence** | Callback path и metadata работают. Полный estimator-only/allocation-only/stopping-only/full-policy набор на всех моделях, seeds и budgets отсутствует. |
| Profiling suite | **PASS как profiling workflow** | `PYTHONPATH=. ./.venv/bin/python scripts/profile_benchmark.py --suite` успешно создал профили для oscillator, FitzHugh–Nagumo и Robertson и автоматически вызвал fail-closed gate. Это не C++ superiority evidence. |
| C++ gate | **PASS как safety decision / KEEP_PYTHON** | При трёх distinct profiles gate возвращает `KEEP_PYTHON`: отсутствуют numerical equivalence, warm-up speedup ≥1.25, comparable memory и reproducibility evidence. Production C++ не разрешён и не требуется. |
| Software laboratory | **PARTIAL** | Models, SciPy adapters, inference diagnostics, budget accounting, reports, profiling, tests и reproducibility helpers присутствуют. Validated NUMERIS-GO controller и complete end-to-end campaign отсутствуют. |
| Git/publication hygiene | **PASS** | Рабочее дерево чистое перед audit commit; private ТЗ read-only и не публикуется. Audit commit локальный, push не выполняется. |

## Phase gates against the private ТЗ

### Phase I — Research Foundation: **PARTIAL**

Evidence ledger, baseline manifest, literature protocol и executable structural gate созданы. Научные R1–R3 reproductions не завершены, поэтому research gap и novelty не установлены.

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty**

Есть target-versus-cost постановка, Gaussian likelihood perturbation baseline и heuristic sensitivity/temporal scaffolding. Нет validated solver-integrated goal-oriented estimator, доказанных convergence/stability/reliability properties или подтверждённой математической новизны.

### Phase III — Software Laboratory: **PARTIAL**

Библиотека, benchmark/reporting utilities, bounded budget semantics, calibration helpers, profiling workflow и тесты работают локально. Полная интеграция validated controller и end-to-end reproducibility package по всем заявленным экспериментам не закрыта.

### Phase IV — Scientific Validation: **FAIL**

Нет завершённого полного frozen campaign для пяти моделей, всех methods/tolerances/seeds/noise/budgets, committed primary endpoint analysis, paired uncertainty intervals, full false-optimum/posterior-distance study, independent reference package и полного scientific ablation.

### Phase V — Publication readiness: **BLOCKED**

Validated scientific contribution, superiority/non-inferiority result, complete figures/tables, manuscript и independent reproduction package не установлены. 110 passing tests не заменяют научную валидацию.

## Required remaining work

1. Завершить source-aligned baseline evidence или зафиксировать каждый blocker как `NOT-REPRODUCED` с artifact-level причиной.
2. Провести независимые convergence/cross-family reference checks для всех пяти benchmark families и сохранить результаты с commit hash.
3. Запустить frozen manifest в полном объявленном объёме либо явно документировать невозможность полного запуска; сохранить все success, failure, over-budget и not-started cases.
4. Рассчитать declared primary endpoints: likelihood distortion и parameter RMSE, paired 95% uncertainty intervals, failure/budget rates и negative-results ledger.
5. Реализовать и проверить реальные estimator/allocation/stopping components NUMERIS-GO; выполнить полный ablation study.
6. Сопоставить emitted numerical-error bounds с независимой фактической ошибкой по всем declared workloads; overconfidence считать gate failure.
7. Разделить post-hoc accounting и истинное прерывание solver call; не расширять hard-budget claim без доказанной interrupt semantics.
8. Для C++ либо предоставить все пять predicates (hotspot, equivalence, warm-up speed, memory, reproducibility), либо сохранить `KEEP_PYTHON`; не добавлять production C++ только из-за профилирования.
9. Подготовить committed negative-results record: baseline-better cases, failures, budget exhaustion, unresolved references и applicability limits.

## Permitted public claim

> NUMERIS HEAD `6d02825` — локально запускаемый, протестированный deterministic research prototype с frozen experiment manifest, Phase-I evidence ledger, bounded campaign runner, numerical-reliability calibration helpers, hard-budget orchestration, representative profiling suite и fail-closed optional C++ gate. Он не является подтверждённо новым методом, доказанно превосходящим стандартные решатели, завершённым Bayesian study или publication-ready результатом.
