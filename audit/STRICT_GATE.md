# NUMERIS — Strict Compliance Gate

Дата аудита: 2026-10-30 (Asia/Almaty)
Аудируемый диапазон: `9fc3163..d634249`
Текущий HEAD: `d6342491be38cad68c2b33e5491a504763021aca` (`d634249`)
Источник требований: локальный read-only `private/TECHNICAL_SPEC.md`
Ограничение аудита: изменён только этот файл; код, ТЗ и GitHub не изменялись.

## Итоговый verdict

**BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE.**

Текущий HEAD заметно продвинулся относительно `9fc3163`: protocol manifest заморожен, literature ledger получил статусы проверки, Bayesian parameter-recovery helper добавлен, validation callbacks теперь реально вызываются, а profiling/C++ gate стал измеримым. Это подтверждает зрелость программной инфраструктуры, но не завершает исследование по ТЗ. Наличие API, unit-тестов или smoke-run не считается scientific evidence.

## Фактические проверки HEAD

| Проверка | Статус | Основание |
|---|---|---|
| Git HEAD | **PASS** | `d634249`; `main...origin/main`; расхождение с origin = `0 0` |
| Полный тестовый набор | **PASS** для software slice | `.venv/bin/python -m pytest -q` → `86 passed` |
| Компиляция | **PASS** | публичные модули импортируются; compileall ранее проходил |
| Public API | **PASS** для API-контракта | benchmark factories, solver methods, Bayesian recovery, validation, memory schema экспортируются и покрыты тестами |
| Frozen protocol manifest | **PASS** | `research/protocol/PROTOCOL_MANIFEST_v0.1.md`, статус `FROZEN`, фиксированные модели/seed/noise/solver/tolerance/budget/reference/decision rule |
| Literature ledger | **PARTIAL** | источники и verification status/date есть, но нет complete systematic screening и reproduction ближайших baseline |
| Bayesian recovery | **PARTIAL** | работает finite-grid Gaussian recovery; сам модуль запрещает трактовать single-run coverage как calibration и не выполняет MCMC |
| Validation callbacks | **PARTIAL** | callback реально меняет effective solver configuration, но это ещё не estimator/allocation/stopping ablation NUMERIS-GO |
| Equal-budget evidence | **FAIL** как научный результат | orchestration есть, committed five-model result matrix и primary endpoints отсутствуют |
| Memory profiling | **PARTIAL** | cross-platform schema и CLI есть; representative multi-model evidence не сохранено |
| C++ gate | **BLOCKED** | hot spot может быть отмечен, но нет C++ kernel, numerical equivalence и measured speed/memory benefit |
| Privacy | **PASS** | `private/TECHNICAL_SPEC.md` не tracked, mode `0444`, archive не содержит private/spec/secret/confidential; publication safety check passed |
| Scientific completion | **FAIL/BLOCKED** | отсутствуют доказательства superiority/novelty, calibration, complete ablation и publication package |

## Аудит изменений после `9fc3163`

### Protocol manifest — PASS for freeze, not for results

`research/protocol/PROTOCOL_MANIFEST_v0.1.md` фиксирует:

- пять моделей и их параметры/гриды наблюдений;
- `sigma ∈ {0.01, 0.05, 0.10}`;
- методы RK45, DOP853, Radau, BDF, LSODA;
- четыре уровня `rtol/atol`;
- seeds `0..9`;
- per-model RHS caps;
- reference solver policy and two-level convergence requirement;
- primary/secondary endpoints;
- paired mean differences and 95% bootstrap CI;
- explicit no-advantage decision rule;
- rule for retaining failures and deviations.

Это удовлетворяет exit criterion **protocol freeze**. Сам manifest не является выполненным экспериментом: в репозитории нет committed result package, подтверждающего, что все заявленные cells действительно были рассчитаны и прошли reference quality gate.

**Exit criterion:** PASS для freeze; NOT MET для validation campaign until references and all declared runs are executed and archived.

### Literature foundation — PARTIAL

В `research/literature_review/` присутствуют inclusion/exclusion protocol, bibliography ledger, comparison matrix и verification dates/statuses. Рассмотрены Cao–Petzold, Lang–Verwer, probabilistic ODE solvers, Bayesian inverse problems, likelihood distortion, DALTON, SciPy, SUNDIALS и SciML.

Корректно зафиксировано, что adjoint/global error control, probabilistic ODE, likelihood-aware inference и solver-induced likelihood distortion уже существуют. Но остаются незакрытыми:

- полный воспроизводимый search/screening record;
- source-level reproduction ближайшего inference-distortion baseline;
- line-by-line comparison зафиксированного NUMERIS-GO mechanism с adjoint/goal-oriented/probabilistic/DALTON mechanisms;
- final novelty decision после фиксации реального алгоритма.

**Phase I:** **PARTIAL**.
**Exit criteria:** completed screening ledger, closest-baseline reproduction, mechanism-level equivalence analysis, explicit novelty/no-novelty decision. Пока не выполнены — novelty claim запрещён.

### Bayesian inference and parameter recovery — PARTIAL

`numeris/inference/bayesian_grid.py` и `run_parameter_recovery(...)` действительно предоставляют:

- deterministic finite-grid Gaussian posterior;
- reproducible synthetic observations via seed;
- MAP/mode, posterior mean, RMSE;
- credible intervals and per-parameter coverage indicator;
- solver settings and JSON-friendly summary;
- Hellinger/total-variation diagnostics.

Ограничения явно указаны в коде и protocol manifest: это не MCMC/PyMC/NumPyro, нет convergence diagnostics, posterior predictive checks, repeated coverage calibration или posterior scientific claim. Поэтому API и 86 тестов подтверждают корректность baseline implementation, но не posterior reliability и не superiority NUMERIS-GO.

**Phase III Bayesian slice:** **PARTIAL**.
**Exit criteria:** separately frozen Bayesian protocol, converged grid/sampler check, repeated seeds, statistical-vs-numerical uncertainty separation, posterior comparison against an independently converged reference. Не выполнены.

### Validation callbacks and ablation — PARTIAL

`numeris/benchmarks/validation.py` теперь передаёт `policy_callback` в trial, сохраняет callback label и effective configuration, а тест подтверждает реальное прохождение callback path. Это исправляет прежний дефект, когда `disabled_components` могли быть только metadata.

Однако callback API всё ещё позволяет произвольным образом заменить `SolverConfig`; он не доказывает, что отключены именно отдельные NUMERIS-GO components:

- goal-oriented estimator;
- temporal budget allocator;
- reliability stopping criterion;
- full policy.

Также `BudgetCaps` проверяет расход после solver call, а не прерывает вычисление при исчерпании hard budget. Текущий runner в основном считает trajectory RMSE; он не выполняет полный protocol endpoint set для parameter RMSE, likelihood distortion, posterior distance, false-optimum rate и calibration.

**Ablation status:** **PARTIAL infrastructure / FAIL as scientific evidence**.
**Exit criteria:** actual estimator/allocation/stopping switches, hard budget enforcement or declared equivalent accounting, all primary endpoints, paired CIs, preserved baseline-better cases, and committed result artifacts.

### Memory profiling and C++ — PARTIAL infrastructure / BLOCKED evidence

`ProfileResult`, `ProfilingSummary`, RSS/peak-memory fallbacks и `scripts/profile_benchmark.py` работают и безопасно представляют unavailable measurements as `None`. Profiling summary records top cumulative functions and a measured hot-spot decision. Это PASS для profiling software slice.

Но public tree не содержит C++ kernel, pybind/nanobind binding, equivalence test или benchmark comparison. Текущий CLI профилирует один oscillator workload/один solver invocation, а `numerical_equivalence_verified` остаётся `False`. Windows `ctypes` fallback — memory API, не C++ implementation.

**C++ gate:** **BLOCKED**, не FAIL: ТЗ делает C++ условным и допускает его только после доказанного hot spot.
**Exit criteria:** representative multi-model profiles; isolated hot spot; specified Python/C++ interface; numerical equivalence on declared tolerances; wall-time/RHS/memory comparison on same machine; measured benefit exceeding build and reproducibility cost. До этого C++ не должен быть добавлен формально ради соответствия.

## Phase gate против ТЗ

### Phase I — Research Foundation: **PARTIAL**

Protocol freeze и initial verified bibliography выполнены. Complete systematic review, closest-baseline reproduction и final gap/novelty decision отсутствуют.

### Phase II — Mathematical Core: **PARTIAL / BLOCKED for novelty claim**

Есть constrained target/cost formulation, sensitivity-aware policy prototype, temporal allocation и Gaussian likelihood perturbation bound. Но текущая реализация остаётся heuristic/baseline; нет solver-integrated validated goal-oriented estimator и доказательств новизны, convergence, stability или reliability coverage. Gaussian bound сам по себе не является новым результатом.

### Phase III — Software Laboratory: **PARTIAL**

Основные модели, solver interface, error observatory, inference, finite-grid Bayesian diagnostic, budget, validation callbacks, profiling, reproducibility, visualization, CLI и тесты присутствуют. Software acceptance для текущего API — **PASS** (`86 passed`), но полная acceptance по ТЗ не закрыта из-за отсутствия hard-budget semantics, complete experiment reporting и end-to-end scientific integration.

### Phase IV — Scientific Validation: **FAIL**

В HEAD отсутствуют committed evidence для:

- пяти моделей × объявленных noise/seed/solver/tolerance/budget cells;
- independently converged references;
- likelihood distortion and parameter-recovery result tables;
- posterior-distance study under a frozen Bayesian protocol;
- false-optimum experiment;
- actual NUMERIS-GO component ablation;
- reliability calibration coverage/mean excess over repeated runs;
- paired confidence intervals and statistical decision;
- populated negative-results ledger.

### Phase V — Publication readiness: **BLOCKED**

Нет установленного scientific contribution, validated superiority/non-inferiority result, publication-quality figures/tables, manuscript или independent reproduction package. Публикация не следует автоматически из успешных тестов.

## Точные exit criteria для следующего gate

1. **Research Foundation:** complete dated screening ledger; reproduce nearest likelihood-distortion baseline; compare the frozen mechanism line-by-line with adjoint/goal-oriented, probabilistic ODE and DALTON; record novelty decision, including no-novelty outcome.
2. **Reference quality:** for each of OSC/FHN/LV/LOR/ROB, pass the manifest’s two-level tolerance convergence and independent solver-family check; otherwise label model `REFERENCE-UNRESOLVED` and exclude it from superiority claims.
3. **Frozen campaign:** execute the exact manifest over all declared models, 10 seeds, 3 noise levels, 5 methods and 4 tolerance levels; retain failures and out-of-budget trials; commit machine-readable result summaries and manifest commit hash.
4. **Primary endpoints:** report likelihood distortion and parameter RMSE per paired cell; include RHS evaluations, runtime, peak RSS, failure rate and budget violations.
5. **Statistics:** compute predeclared paired mean differences with two-sided 95% bootstrap CIs over seeds; do not select seeds/factors after observing outcomes.
6. **Controller integration:** connect the actual estimator, allocator and stopping components to the validation runner; expose effective decisions and costs; enforce or explicitly justify budget accounting.
7. **Ablation:** execute estimator-only, allocation-only, stopping-only and full-policy arms; show that each arm changes behavior, not just metadata; preserve baseline-better and failed cases.
8. **Bayesian evidence:** if claiming posterior results, add a separate frozen protocol, grid/sampler convergence checks, repeated coverage calibration, posterior distance to an independently converged reference, and statistical-vs-numerical uncertainty separation. Otherwise keep posterior claims excluded.
9. **Reliability:** evaluate every emitted error estimate against independent actual error; report coverage and mean excess; reject reliability claims on systematic overconfidence.
10. **C++ decision:** run representative profiles; implement C++ only if all C++ gate criteria pass; otherwise commit a negative profiling decision and keep Python.
11. **Negative results:** populate `research/negative_results.md` with every failure, budget exhaustion, calibration failure, baseline-better case and applicability limitation.
12. **Publication:** only after Phases I–IV close, prepare manuscript, figures/tables, limitations, code/data reproduction instructions and independent rerun evidence.

## Final public claim permitted by this audit

> NUMERIS HEAD `d634249` is a locally runnable, tested deterministic research prototype with a frozen experiment manifest, verified literature ledger, finite-grid Bayesian parameter-recovery diagnostics, validation callback infrastructure, and memory profiling. It is not yet a validated novel method, not evidence of superiority over existing solvers, not a completed Bayesian scientific study, and not publication-ready.
