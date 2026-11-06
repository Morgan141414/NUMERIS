"""Headless-safe checks for the optional NUMERIS desktop entry point.

These tests intentionally do not import or launch Tkinter.  The desktop
application is optional while the research prototype is being developed.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENTRY_POINT_CANDIDATES = (
    PROJECT_ROOT / "desktop_app" / "__main__.py",
    PROJECT_ROOT / "desktop_app" / "main.py",
    PROJECT_ROOT / "desktop_app" / "entrypoint.py",
)


def _entry_point() -> Path | None:
    return next((path for path in ENTRY_POINT_CANDIDATES if path.is_file()), None)


def test_desktop_entry_point_is_not_imported_during_headless_collection() -> None:
    """Collection must remain safe on CI workers without a display server."""

    entry_point = _entry_point()
    if entry_point is None:
        pytest.skip("desktop_app entry point is not implemented in this revision")

    tree = ast.parse(entry_point.read_text(encoding="utf-8"), filename=str(entry_point))
    imported_modules = {
        node.module
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported_modules.update(
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
    )

    # GUI imports must be delayed until the executable path is invoked.  This
    # keeps non-GUI helpers and test collection usable in headless CI.
    assert "tkinter" not in imported_modules


def test_desktop_entry_point_has_a_guarded_main_call() -> None:
    """A future entry point must expose a conventional, inspectable launch."""

    entry_point = _entry_point()
    if entry_point is None:
        pytest.skip("desktop_app entry point is not implemented in this revision")

    source = entry_point.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(entry_point))
    function_names = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "main" in function_names
    assert 'if __name__ == "__main__"' in source or "if __name__ == '__main__'" in source
