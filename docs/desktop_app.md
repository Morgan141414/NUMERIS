# NUMERIS desktop application

## Current status

The current public NUMERIS revision does **not** contain a `desktop_app/`
implementation or a registered desktop entry point. The repository is a
scientific-computing library and research laboratory, not a finished user
application.

Therefore the desktop UI status is:

```text
DESKTOP UI: NOT IMPLEMENTED
DESKTOP TESTS: HEADLESS CONTRACT ONLY
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

The exact command is provisional until an entry point is added. No command
above should be interpreted as proof that the application currently exists.

## Tkinter and headless CI limitations

Tkinter needs a macOS graphical session and an available display. It should
not be imported or launched during normal unit-test collection on CI, SSH,
or other headless environments. A future implementation should therefore:

- keep GUI imports inside the executable launch path;
- keep non-GUI helpers importable without creating a `Tk()` root;
- avoid opening windows at module import time;
- provide deterministic callbacks that can be tested without a display;
- keep UI tests separate from numerical and scientific validation tests.

The current test file `tests/ui/test_desktop_app_entrypoint.py` performs only
AST/static checks. If no entry point exists, it reports the honest
`NOT IMPLEMENTED` state by skipping the optional checks; it never requires a
display server.

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
