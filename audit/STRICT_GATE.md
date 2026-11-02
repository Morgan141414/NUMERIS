# NUMERIS — Strict Gatekeeper Audit

Дата аудита: 2026-11-03 (Asia/Almaty)
Аудируемый объект: текущий `HEAD`
HEAD: `4786700ca6f4805cc0103ab81cd0eb76550871a2` (`4786700`, `Add bounded primary endpoint validation report`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение публикации: private ТЗ не публикуется, не отслеживается Git и не входит в публичный архив.

## Проверки этого аудита

- `./.venv/bin/pytest -q` → **130 passed**.
- `python3 scripts/check_publication_safety.py` → **PASS**.
- `bash research/protocol/check_baseline_reproduction.sh` → **PASS** как структурный gate.
- Фактический bounded reference diagnostic:
  - `campaign_status=complete_bounded_diagnostic`;
  - 5 моделей;
  - 20 запланированных solver runs;
  - `OSC`, `FHN`, `LV`, `LOR`, `ROB` → **REFERENCE-RESOLVED**;
  - `resolved=5`, `unresolved=0`.
- Profiling/C++ workflow: **KEEP_PYTHON** без candidate C++ evidence.
- Primary endpoint helper: **PASS как fail-closed infrastructure / PARTIAL как scientific evidence**.
- Paired bootstrap helper: **PASS как uncertainty infrastructure / PARTIAL как scientific evidence**.
- До изменения этого файла рабочее дерево было чистым; изменяется только `audit/STRICT_GATE.md`.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD — локально запускаемый исследовательский прототип с проходящими тестами, frozen protocol, evidence ledgers, bounded budget/campaign infrastructure, ограниченной Bayesian/reliability diagnostics, provenance-aware profiling, paired uncertainty helpers, fail-closed primary-endpoint report и fail-closed C++ gate. Он не доказывает математическую новизну, превосходство NUMERIS-GO, полную воспроизводимость baseline-методов или готовность к публикации.

## Evidence ledger

| Gate | Статус | Фактическое evidence и границы вывода |
|---|---|---|
| Полный тестовый набор | **PASS** | `./.venv/bin/pytest -q` → **130 passed**. |
| Publication safety | **PASS** | Скрипт publication safety завершился успешно; private/spec paths не входят в публичный Git/archive. |
| Negative-results evidence ledger | **PASS как сохранение статусов** | Зафиксированы `REFERENCE-UNRESOLVED`, `NOT-REPRODUCED`, `BLOCKED`, `baseline-better — NOT-ESTABLISHED`, `BUDGET-EXHAUSTED/INCOMPLETE`, ограничения пяти моделей и C++ gate. Это не заменяет завершённые эксперименты. |
| Phase-I evidence ledger | **PASS как контрольный ledger / PARTIAL по научному закрытию** | R1–R3 evidence, source-aligned reproductions и overlap audit остаются незавершёнными; novelty claims запрещены. |
| Baseline reproduction gate | **PASS для структурного gate / PARTIAL для научного воспроизведения** | Manifest, bibliography, cards, source IDs и stop conditions проходят проверку. ADJ-GLOBAL, GO-FUNCTIONAL, likelihood-distortion, DALTON и PROB-ODE не воспроизведены как полные source-aligned baselines. |
| Frozen experiment protocol | **PASS для freeze / PARTIAL для execution** | Manifest v0.1 фиксирует модели, параметры, шум, seeds, solver/tolerance grid, budgets, references, endpoints и falsification rule. Полный protocol-wide запуск не выполнен. |
| Bounded five-model reference campaign | **PASS как bounded diagnostic / PARTIAL как scientific evidence** | Фактический run дал `5/5 REFERENCE-RESOLVED`, 20 solver runs, два tolerance levels и DOP853/Radau либо BDF/Radau по моделям. `REFERENCE-RESOLVED` означает только прохождение объявленных bounded convergence/cross-family checks; это не exact truth, не full campaign и не доказательство superiority. |
| Primary endpoint report | **PASS как fail-closed infrastructure / PARTIAL как scientific evidence** | Helper считает paired likelihood distortion, parameter RMSE, failure/budget rates и bootstrap intervals, по умолчанию возвращает `NO_CONFIRMED_ADVANTAGE`. Наличие helper и unit-тестов не является фактическим full-campaign result и не подтверждает superiority/non-inferiority. |
| Paired bootstrap CI | **PASS как uncertainty infrastructure / PARTIAL по фактическому evidence** | Реализована воспроизводимая seed-wise paired bootstrap-оценка неопределённости. Она не заменяет запуск declared workloads, не создаёт отсутствующие samples и не является доказательством научного преимущества. |
| Bounded frozen campaign | **PASS как bounded infrastructure / BLOCKED как full campaign evidence** | Предыдущий bounded record: `3000 planned`, `2 admitted`, `bounded_incomplete`; это не полный validation campaign и не numerical result. |
| Bayesian parameter recovery | **PASS как deterministic diagnostic / PARTIAL по ТЗ** | Работает finite-grid Gaussian posterior/recovery helper. Это не полноценный MCMC/PyMC/NumPyro study и не доказательство posterior reliability. |
| Numerical reliability calibration | **PARTIAL** | Есть tolerance-sweep calibration с independent reference error, coverage/overconfidence, а также bounded multi-model reliability helper и Wilson/Monte Carlo uncertainty. Нет полной declared-workload calibration campaign и доказанного отсутствия overconfidence. |
| Reference convergence utility | **PASS как utility / PARTIAL как scientific gate** | Сохраняются within-family convergence, cross-family disagreement, RMSE, max error, `nfev` и runtime. Согласие двух solver families — ограниченный diagnostic, не абсолютный эталон. |
| Hard-budget semantics | **PASS для bounded runner / PARTIAL для всей validation stack** | Есть preflight, `preflight_rejected`, `completed`, `over_budget`, `not_started` и остановка последующих запусков. SciPy solver call не прерывается mid-call; старый equal-budget comparison остаётся post-hoc. |
| Equal-budget comparison | **PARTIAL** | Pairing, same observations/seeds и accounting реализованы. Нет полного protocol-wide набора cells, paired uncertainty intervals и committed primary endpoint analysis. |
| Ablation | **PARTIAL infrastructure / FAIL как scientific evidence** | Callback path и metadata работают. Полный estimator/allocation/stopping/full-policy ablation на всех моделях, seeds и budgets отсутствует. |
| Profiling provenance | **PASS как workflow** | Representative suite сохраняет exact command, workload, solver/options, runtime/platform metadata, profiles, suite manifest и C++ gate decision. Это не evidence пользы C++. |
| C++ gate | **PASS как safety decision / KEEP_PYTHON** | Profiling не сопровождается numerical equivalence, warm-up speedup ≥1.25, comparable memory и reproducibility evidence. Production C++ не разрешён и не требуется по текущим данным. |
| Software laboratory | **PARTIAL** | Models, SciPy adapters, inference diagnostics, budget accounting, reports, calibration, primary-endpoint/uncertainty infrastructure, profiling, provenance и tests присутствуют. Validated NUMERIS-GO controller и complete end-to-end campaign отсутствуют. |
| Git/publication hygiene | **PASS** | Private ТЗ не менялось и не публикуется; этот audit commit не должен включать code, research, docs или private. |

## Phase gates against the private ТЗ

### Phase I — Research Foundation: **PARTIAL**

Evidence ledgers, baseline manifest, literature protocol и executable structural gate созданы. Научные R1–R3 reproductions и окончательный research-gap/novelty decision не завершены.

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty**

Есть target-versus-cost постановка, Gaussian likelihood perturbation baseline и heuristic sensitivity/temporal scaffolding. Нет validated solver-integrated goal-oriented estimator, доказанных convergence/stability/reliability properties или подтверждённой математической новизны.

### Phase III — Software Laboratory: **PARTIAL**

Библиотека, пять benchmark factories, solver adapters, bounded budget semantics, calibration helpers, reference diagnostic, profiling provenance и tests работают локально. Полная интеграция validated controller и end-to-end reproducibility package по всем заявленным экспериментам не закрыта.

### Phase IV — Scientific Validation: **FAIL**

Пять моделей имеют `REFERENCE-RESOLVED` только в bounded numerical diagnostic. Нет полного frozen campaign для всех methods/tolerances/seeds/noise/budgets, фактического primary endpoint evidence, full false-optimum/posterior-distance study и полного scientific ablation. Primary endpoint report и paired bootstrap — только infrastructure; они не являются результатами full campaign. Bounded reference diagnostic не может быть назван full campaign.

### Phase V — Publication readiness: **BLOCKED**

Validated scientific contribution, superiority/non-inferiority result, complete figures/tables, manuscript и independent reproduction package не установлены. 130 passing tests, primary-endpoint/bootstrap infrastructure и 5/5 bounded reference statuses не заменяют научную валидацию.

## Required remaining gates

1. Завершить source-aligned baseline evidence или зафиксировать каждый blocker как `NOT-REPRODUCED` с artifact-level причиной.
2. Сохранить machine-readable artifact фактического five-model bounded diagnostic с commit hash; не переименовывать его в full campaign и не расширять вывод `REFERENCE-RESOLVED`.
3. Запустить frozen manifest в полном объявленном объёме либо явно документировать невозможность полного запуска; сохранить все success, failure, over-budget и not-started cases.
4. Рассчитать declared primary endpoints: likelihood distortion и parameter RMSE, paired uncertainty intervals, failure/budget rates и negative-results ledger.
5. Реализовать и проверить реальные estimator/allocation/stopping components NUMERIS-GO; выполнить полный ablation study.
6. Сопоставить emitted numerical-error bounds с независимой фактической ошибкой по всем declared workloads; overconfidence считать gate failure.
7. Разделить post-hoc accounting и истинное прерывание solver call; не расширять hard-budget claim без доказанной interrupt semantics.
8. Для C++ либо предоставить все predicates (hotspot, numerical equivalence, warm-up speed, memory, reproducibility), либо сохранить `KEEP_PYTHON`; не добавлять production C++ только из-за профилирования.
9. Подготовить committed analysis отрицательных результатов: baseline-better cases, failures, budget exhaustion, unresolved references и applicability limits.

## Permitted public claim

> NUMERIS HEAD `4786700` — локально запускаемый, протестированный deterministic research prototype с frozen experiment manifest, evidence ledgers, bounded five-model reference diagnostic (`5/5 REFERENCE-RESOLVED`), bounded campaign/budget infrastructure, reliability-calibration helpers, paired bootstrap and primary-endpoint fail-closed infrastructure, provenance-aware profiling и fail-closed optional C++ gate. Five-model result является bounded diagnostic, не full campaign; primary-endpoint и bootstrap helpers не являются фактическими full-campaign results; проект не является подтверждённо новым методом, доказанно превосходящим стандартные решатели, завершённым Bayesian study или publication-ready результатом. Novelty, superiority и publication claims запрещены.
