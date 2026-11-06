# NUMERIS Desktop App

Native Tkinter desktop interface for the existing NUMERIS benchmark API.

## Start

From the repository root:

```bash
python3 scripts/launch_numeris_app.py
```

No web server and no additional mandatory dependency are used. NumPy, SciPy,
and Tkinter are supplied by the local Python installation/project environment.

## Tabs

- **Overview** explains the prototype status and research limitations.
- **Run Model** selects one of five models, a SciPy solver, tolerance, and RHS budget.
- **Results** displays the JSON report and opens previously saved JSON files.

The run executes in a background thread through `run_bounded_benchmark`. The
result is saved to `desktop_app/results/latest.json` (a runtime artifact, not a
scientific claim). The application explicitly reports `over_budget`, failed,
and not-started cases. It also labels the research candidate
`NOT-IMPLEMENTED` and does not claim superiority.
