# NUMERIS: минимальный исследовательский каркас

Статус: независимый план первого рабочего прототипа.  
Область v0: детерминированные параметрические ODE, синтетические наблюдения, Gaussian likelihood, MLE и диагностическое goal-oriented управление точностью.  
Цель v0: проверить исследовательскую гипотезу и воспроизводимость измерений, а не заранее заявить научную новизну.

## 1. Границы первого прототипа

Входит:

- Python 3.11+; NumPy, SciPy, pandas, Matplotlib, pytest.
- Единый интерфейс модели и решателя.
- Один полностью реализованный контроллер: `diagnostic/goal-oriented`, который сравнивает несколько точностей и оценивает влияние на выбранную целевую величину.
- MLE для Gaussian observation model.
- Эталонное решение, бюджет RHS-вызовов, runtime и повторяемость.
- Два обязательных теста для вертикального среза: damped oscillator и Lotka–Volterra.
- FitzHugh–Nagumo, Lorenz и Robertson как следующий benchmark-набор после прохождения вертикального среза.

Не входит в v0: полноценный Bayesian MCMC, PyMC/NumPyro, probabilistic ODE solvers, собственная реализация RK/Radau/BDF, GPU, PDE/DAE, веб-интерфейс и утверждение о новизне метода.

## 2. Файлы и модули

```text
NUMERIS/
├── README.md
├── pyproject.toml
├── LICENSE
├── .gitignore
├── CITATION.cff                         # можно добавить после фиксации авторства
├── docs/
│   ├── scope.md                         # границы v0 и критерии самоопровержения
│   ├── methodology.md                   # протокол экспериментов до запуска
│   └── limitations.md
├── research/
│   ├── hypotheses/HYPOTHESIS.md         # H1, нулевая гипотеза, условия проигрыша
│   └── literature_review/README.md      # таблица аналогов; без вывода о новизне
├── numeris/
│   ├── __init__.py
│   ├── types.py                          # Protocol/dataclass: model, solution, metrics
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                       # ODEModel и ObservationModel
│   │   └── builtins.py                   # oscillator, Lotka–Volterra; позже остальные
│   ├── solvers/
│   │   ├── __init__.py
│   │   ├── scipy_backend.py              # solve_ivp adapter
│   │   └── reference.py                  # независимая проверка эталона и сходимости
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── likelihood.py                 # Gaussian log-likelihood
│   │   └── mle.py                        # bounded multi-start optimization
│   ├── error_analysis/
│   │   ├── __init__.py
│   │   ├── trajectory.py                 # ошибки относительно reference
│   │   └── target.py                     # likelihood/parameter distortion
│   ├── controller/
│   │   ├── __init__.py
│   │   ├── baseline.py                   # фиксированная точность / стандартный режим
│   │   └── goal_oriented.py              # v0: pilot ladder + stopping rule
│   ├── budget/
│   │   ├── __init__.py
│   │   └── accounting.py                 # RHS, runtime, memory, hard limits
│   ├── benchmarks/
│   │   ├── __init__.py
│   │   ├── protocol.py                   # единый запуск и конфигурация
│   │   └── metrics.py                    # заранее определённые метрики
│   ├── reproducibility/
│   │   ├── __init__.py
│   │   └── manifest.py                   # seed, версии, конфиг, git revision
│   └── visualization/
│       └── plots.py                      # минимальные графики, без логики расчёта
├── experiments/
│   ├── configs/                          # YAML/JSON конфиги, не код
│   ├── oscillator/run.py
│   ├── lotka_volterra/run.py
│   ├── fitzhugh_nagumo/run.py            # после v0
│   ├── lorenz/run.py                     # после v0
│   └── robertson/run.py                  # после v0
├── tests/
│   ├── unit/
│   ├── numerical/
│   ├── integration/
│   └── regression/
├── results/.gitkeep                      # результаты не коммитить без решения о формате
└── scripts/
    ├── run_benchmark.py
    └── summarize_results.py
```

## 3. Минимальные интерфейсы

`ODEModel`: `rhs(t, y, theta)`, `initial_state(theta)`, `parameter_bounds`, `observation(t, y)`.  
`SolverConfig`: method, `rtol`, `atol`, `max_step`, `t_eval`.  
`Solution`: time grid, state, success/message, `nfev`, runtime, solver config.  
`Target`: функция научной величины и допуск её изменения.  
`Controller`: получает модель, observations, target и бюджет; возвращает solver configuration, estimate, diagnostics и stopping reason.

Важно: v0-контроллер не меняет внутренний шаг SciPy. Он выбирает уровень точности/повторный запуск и распределяет ограниченный бюджет между кандидатами. Это делает гипотезу проверяемой без преждевременной реализации нового ODE solver.

## 4. Baseline-ы

Обязательная матрица сравнения:

1. `RK45`, фиксированные `rtol/atol`.
2. `DOP853`, фиксированные `rtol/atol`.
3. `Radau`, фиксированные `rtol/atol` для stiff/контрольного сравнения.
4. `BDF`, только для Robertson на следующем этапе.
5. `LSODA`, только если доступен в установленной SciPy и воспроизводимо запускается.
6. `tight-reference`: наиболее строгая конфигурация, подтверждённая лестницей сходимости двумя методами; не считать её автоматически истинной.
7. `NUMERIS-GO-v0`: тот же backend и тот же общий бюджет, но выбор точности по целевой величине.

Каждый baseline должен получать одинаковые модель, данные, стартовые точки MLE, бюджет и seed. Отдельно фиксировать случаи, когда метод не уложился в бюджет или завершился неуспешно.

## 5. Benchmark-набор

### Вертикальный срез v0

- Damped driven oscillator: восстановление параметров, гладкая likelihood, низкий риск численной патологии.
- Lotka–Volterra: нелинейная циклическая динамика, длительное интегрирование и параметрическая чувствительность.

Для каждой модели: 2–3 истинных набора параметров, 3 уровня Gaussian noise, минимум 20 фиксированных seeds/replicates, один короткий и один длинный горизонт наблюдений.

### Расширение после v0

- FitzHugh–Nagumo: быстрые/медленные масштабы.
- Lorenz: только статистические/параметрические цели, не raw trajectory на длинном горизонте.
- Robertson: stiff-сравнение `Radau/BDF/LSODA`; не включать в выводы v0 до проверки эталона.

## 6. Метрики и протокол

Основные метрики, заранее зафиксированные в `numeris/benchmarks/metrics.py`:

- parameter RMSE относительно истинных параметров;
- absolute/relative likelihood error относительно reference;
- target distortion при переходе с reference на выбранную точность;
- RHS evaluations, runtime, peak RSS;
- failure rate;
- calibration: заявленный контроллером target error против фактического.

Posterior distance, false optimum rate и Bayesian inference оставить как v1: они требуют отдельного протокола MCMC/плотности и не должны смешиваться с первым MLE-экспериментом.

Для каждого запуска сохранять JSON/CSV manifest: модель, параметры, seed, solver, `rtol/atol`, бюджет, версии, git revision, метрики, статус и причину остановки.

Главное сравнение: одинаковый бюджет, затем кривая `target error` против `RHS evaluations`. Результат считать преимуществом только если улучшение повторяется на заранее объявленной доле сценариев без неприемлемого роста failure rate и стоимости.

## 7. Тесты

### Unit

- известные RHS oscillator/Lotka–Volterra на ручных точках;
- валидация размерностей и границ параметров;
- Gaussian likelihood на аналитическом простом примере;
- корректный подсчёт `nfev`, runtime и budget exhaustion;
- сериализация/десериализация manifest;
- детерминизм при фиксированном seed.

### Numerical

- `rtol/atol` ladder демонстрирует уменьшение ошибки на oscillator;
- эталон сходится при ужесточении допусков и согласуется у двух solver methods;
- `Radau/BDF` не дают ложного преимущества на не-stiff модели только из-за другого бюджета;
- контроллер не объявляет target reliable, если reference-сравнение опровергает его оценку;
- отрицательный тест: при плоской likelihood усиление точности не обязано улучшать parameter RMSE.

### Integration

- полный запуск одной конфигурации oscillator через baseline и NUMERIS-GO;
- полный запуск Lotka–Volterra;
- превышение RHS/time budget корректно завершает эксперимент;
- повторный запуск создаёт сопоставимый manifest и метрики.

### Regression

- фиксированные небольшие smoke-конфигурации с диапазонами, а не хрупкими точными float-значениями;
- проверка, что изменение solver/допуска отражается в manifest и результатах;
- проверка, что неуспешный solver не попадает в таблицу как успешный результат.

## 8. Порядок реализации

1. Зафиксировать `HYPOTHESIS.md`, метрики, budget и протокол до экспериментов.
2. Собрать типы, модели и SciPy adapter.
3. Реализовать reference convergence ladder.
4. Реализовать likelihood, bounded multi-start MLE и accounting.
5. Реализовать baseline benchmark и вертикальный срез oscillator.
6. Добавить Lotka–Volterra, numerical/integration tests и отчётные графики.
7. Реализовать `NUMERIS-GO-v0` как диагностический pilot-ladder controller.
8. Выполнить ablation: без target signal, без budget limit, с неверно заданным target tolerance.
9. Только после этого добавлять FHN, Lorenz, Robertson и Bayesian слой.

## 9. Критерии готовности первого рабочего прототипа

- `pytest` проходит unit, numerical и integration smoke-тесты.
- Один скрипт запускает оба v0 benchmark без ручного редактирования кода.
- Для каждого запуска сохраняются manifest и таблица метрик.
- Reference проверен лестницей сходимости двумя методами.
- Baseline и NUMERIS-GO используют одинаковый бюджет и одинаковые данные.
- Есть минимум один сценарий, где контроллер не выигрывает или корректно отказывается от дополнительной точности.
- Итоговый отчёт явно разделяет измеренные результаты, предположения, ограничения и неподтверждённые гипотезы.

## 10. Что не следует обещать на стадии v0

Не заявлять математическую новизну, универсальное превосходство, posterior reliability или готовность к публикации. В v0 проверяется более узкое утверждение: может ли target-aware выбор точности уменьшить ошибку заранее выбранной MLE/likelihood-цели при сопоставимом бюджете на ограниченном классе ODE.
