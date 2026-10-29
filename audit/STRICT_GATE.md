# NUMERIS — Strict Gatekeeper Audit

Дата аудита: 2026-10-30 (Asia/Almaty)
Аудируемый объект: текущий `HEAD`
HEAD: `04aa86a6206a71043aba7b837b820ce310a49c8c` (`04aa86a`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение публикации: private ТЗ не читается в публичный вывод, не отслеживается Git и не входит в Git archive.
Изменения в рамках аудита: изменён только этот файл; код, `research/`, `docs/` и private ТЗ не изменялись. Push не выполняется.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD является локально запускаемым и протестированным исследовательским прототипом. В нём есть замороженный protocol manifest, baseline-reproduction plan, finite-grid Bayesian recovery и calibration diagnostics, reference-convergence report, equal-budget/ablation infrastructure и измеримый optional C++ gate. Однако обязательная scientific validation campaign не выполнена, ближайшие baselines не воспроизведены локально, а NUMERIS-GO не является доказанно новым или превосходящим методом.

## Evidence ledger

| Критерий | Статус | Проверка и честная интерпретация |
|---|---|---|
| Полный тестовый набор | **PASS** | `./.venv/bin/pytest -q` → `92 passed` на текущем HEAD. |
| Publication safety | **PASS** | `python3 scripts/check_publication_safety.py` → `Publication safety check passed`; `git ls-files` и `git archive` не содержат `private/`, `TECHNICAL_SPEC.md` или секретные файлы. |
| Research baseline protocol | **PARTIAL** | Inclusion/exclusion protocol, bibliography ledger, comparison matrix, closest-baseline reproduction plan и Phase-I exit criteria существуют. Статусы ближайших baselines остаются R0/conceptual или reproduction pending; R2/R3 evidence, line-by-line overlap audit и финальное novelty/no-novelty decision отсутствуют. |
| Frozen experiment protocol | **PASS для freeze / PARTIAL для execution** | `PROTOCOL_MANIFEST_v0.1.md` фиксирует модели, параметры, noise, seeds, solver/tolerance grid, budgets, reference policy, endpoints и falsification rule. Полная кампания по всем объявленным ячейкам ещё не выполнена и не заархивирована. |
| Bayesian parameter recovery | **PASS как детерминированный diagnostic** | `run_parameter_recovery` и finite-grid Gaussian posterior работают, сохраняют MAP/mean/RMSE/interval diagnostics и настройки solver. Это не MCMC/PyMC/NumPyro и не доказательство posterior reliability. |
| Bayesian calibration | **PASS как ограниченный calibration helper / PARTIAL по ТЗ** | `calibrate_credible_intervals` воспроизводим; smoke check с повторными seed проходит и выдаёт coverage/Monte Carlo SE. Это конечная grid-диагностика, а не полное Bayesian исследование: нет sampler convergence, posterior predictive checks, независимого posterior reference и separation statistical-vs-numerical uncertainty. |
| Reference report | **PASS как utility / PARTIAL по validation gate** | `build_reference_report` требует минимум два независимых solver methods, сравнивает tolerance levels и явно помечает consensus не абсолютной истиной; smoke check даёт 2 candidates и конечное disagreement. Полный two-level плюс cross-family reference gate для OSC/FHN/LV/LOR/ROB ещё не выполнен и не сохранён как campaign artifact. |
| Equal-budget comparison | **PARTIAL** | Paired runner и smoke comparison работают; 2/2 пары comparable. `BudgetCaps` проверяет расход после завершения solver call, а не прерывает вычисление по hard cap. Нет полного protocol endpoint set, всех seeds/noise/models и paired 95% bootstrap CIs. |
| Ablation | **PARTIAL infrastructure / FAIL as scientific evidence** | Callback path реально выполняется, label/effective config сохраняются; smoke ablation проходит. Но нет интегрированных переключателей отдельных estimator/allocator/stopping components, полного набора arms и committed results, показывающих научный эффект каждого компонента. |
| Profiling | **PASS для software slice / PARTIAL для C++ decision** | `scripts/profile_benchmark.py` запускается с корректным project import path и создаёт structured JSON/profile; текущий run фиксирует hotspot вокруг `solve_ode`, но memory source unavailable и workload одиночный. |
| Optional C++ gate | **BLOCKED — KEEP_PYTHON** | Документированы predicates HOTSPOT, EQUIVALENT, FASTER_AFTER_WARMUP, MEMORY_ACCEPTABLE, REPRODUCIBLE. Есть только предварительный Python hotspot; нет C++ candidate, frozen equivalence corpus, warm-up timing, comparable memory или reproducible build. ТЗ делает C++ условным, поэтому отсутствие C++ реализации само по себе не нарушение; добавлять C++ до прохождения gate нельзя. |
| README/docs honesty | **PASS** | README и performance/limitations docs прямо называют проект prototype, не заявляют novelty/superiority/publication readiness и фиксируют ограничения finite-grid, heuristic controller, reference consensus и optional C++. |
| Git sync | **PASS** | `main` отслеживает `origin/main`; после `git fetch origin main` расхождение `HEAD...origin/main = 0 0`; рабочее дерево чистое до коммита этого аудита. |

## Phase gates against the private ТЗ

### Phase I — Research Foundation: **PARTIAL**

Документы и frozen protocol foundation созданы. Не закрыты source-aligned reproductions ближайших baselines, полный screening handoff, overlap audit и окончательное решение о research gap. До этого запрещены claims `novel`, `first`, `superior`, `publication-ready`.

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty**

Есть формулировка target-versus-cost, Gaussian likelihood perturbation bound и heuristic sensitivity/temporal policy scaffolding. Нет solver-integrated validated goal-oriented estimator, доказательств convergence/stability/reliability и подтверждённой математической новизны. Наличие формулы или контроллера не является доказательством научного вклада.

### Phase III — Software Laboratory: **PARTIAL**

Основной API, пять ODE models, SciPy solver adapters, inference diagnostics, budget accounting, validation orchestration, profiling, tests и reproducibility support присутствуют. Software slice проходит тесты, но полная acceptance по ТЗ не закрыта из-за отсутствия hard-budget semantics, полного end-to-end report и интеграции настоящего научного контроллера.

### Phase IV — Scientific Validation: **FAIL**

В текущем HEAD нет committed evidence полного frozen campaign: пять моделей × 10 seeds × 3 noise levels × 5 methods × 4 tolerance levels, resolved independent references, primary likelihood/parameter endpoints, false-optimum study, posterior-distance study, reliability calibration over declared models, paired bootstrap CIs, negative-results ledger и полного component ablation.

### Phase V — Publication readiness: **BLOCKED**

Не установлены validated scientific contribution, superiority/non-inferiority result, complete figures/tables, manuscript и independent reproduction package. Научная публикация не следует из наличия кода и тестов.

## Required next gates

1. Выполнить и сохранить reference convergence/cross-family checks для всех пяти моделей.
2. Запустить frozen manifest целиком; сохранить failed и over-budget trials, commit hash и machine-readable summaries.
3. Рассчитать likelihood distortion и parameter RMSE, paired differences и заранее определённые two-sided 95% bootstrap CIs.
4. Завершить source-aligned baseline reproduction или явно зафиксировать blockers и допустимую формулировку `NOT-REPRODUCED`.
5. Подключить реальные estimator/allocation/stopping components и провести estimator-only, allocation-only, stopping-only и full-policy ablations.
6. Для reliability claims проверить каждую emitted error estimate против независимой фактической ошибки; systematic overconfidence считать gate failure.
7. До C++ реализации получить representative multi-model profiles; затем пройти equivalence, warm-up speed, memory и reproducibility gates либо сохранить отрицательное решение `KEEP_PYTHON`.
8. Вести committed negative-results record для baseline-better cases, failures, budget exhaustion и ограничений применимости.

## Permitted public claim

> NUMERIS HEAD `04aa86a` — локально запускаемый, протестированный deterministic research prototype с frozen experiment manifest, baseline-reproduction protocol, finite-grid Bayesian diagnostics, reproducible reference/validation helpers и optional C++ gate. Он не является подтверждённо новым методом, доказанно превосходящим стандартные решатели, завершённым Bayesian study или publication-ready результатом.
