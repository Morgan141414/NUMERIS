# NUMERIS desktop application

## Current status

The checkout currently contains a native `desktop_app/` Tkinter shell and a
`python -m desktop_app` entry point. This UI is a thin exploratory wrapper
around the existing benchmark API; it is not a separate web service and does
not implement the NUMERIS-GO research candidate. The UI implementation is
kept separate from the numerical library and the UI test/documentation change
does not alter it.

Therefore the desktop UI status is:

```text
DESKTOP UI: EXPLORATORY TKINTER PROTOTYPE
DESKTOP TESTS: HEADLESS STATIC CONTRACT
SCIENTIFIC STATUS: PROTOTYPE — NOT SCIENTIFICALLY COMPLETE
```

The UI is not required to validate the numerical method. It should be added
only as a thin local desktop shell around existing library workflows, without
changing the mathematical claims or the frozen experiment protocols.

## Intended form

If implemented, NUMERIS should be a local macOS desktop application, not a
web site and not a web server. A first version should expose only a small
workflow:

1. choose a model and solver configuration;
2. run a bounded diagnostic or experiment;
3. display trajectory/error/budget results;
4. save the reproducibility record and report.

The desktop shell must call the public Python API. It must not duplicate the
solver, inference, controller, or benchmark logic.

## macOS launch guidance

When a desktop implementation exists, launch it locally from the repository
root with the project environment active:

```bash
cd "/Users/amanatkorgan/Desktop/my projects/NUMERIS"
source .venv/bin/activate
python -m desktop_app
```

The command launches the local Tkinter shell when a graphical macOS session is
available. It does not start a web server. The UI is a convenience layer for
bounded diagnostics, not a proof that the scientific candidate exists.

## Tkinter and headless CI limitations

Tkinter needs a macOS graphical session and an available display. It should
not be imported or launched during normal unit-test collection on CI, SSH,
or other headless environments. A future implementation should therefore:

- keep GUI imports inside the executable launch path;
- keep non-GUI helpers importable without creating a `Tk()` root;
- avoid opening windows at module import time;
- provide deterministic callbacks that can be tested without a display;
- keep UI tests separate from numerical and scientific validation tests.

The test file `tests/ui/test_desktop_app_entrypoint.py` performs only
AST/static checks on the entry point. It never constructs a `Tk()` root and
never requires a display server. If the optional entry point is absent in a
minimal checkout, the checks are skipped with an explicit reason rather than
claiming that the UI was tested.

## Scientific limitations

A desktop interface would improve local usability, but it would not establish
mathematical novelty, solver superiority, reliability, or publication
readiness. The current NUMERIS status remains:

```text
BLOCKED — PARTIALLY COMPLIANT, NOT SCIENTIFICALLY COMPLETE
```

The interface must not present bounded diagnostics as a proof of NUMERIS-GO,
and it must preserve failure, over-budget, unresolved-reference, and negative
result statuses.
