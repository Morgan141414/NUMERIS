"""Native desktop interface for bounded NUMERIS diagnostics.

The application is deliberately a thin UI layer. It calls the existing
``numeris`` benchmark API and does not claim that the research candidate is
implemented or scientifically superior.
"""

from __future__ import annotations

import json
import queue
import sys
import threading
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from numeris.benchmarks import (
    damped_oscillator,
    fitzhugh_nagumo,
    lorenz,
    lotka_volterra,
    robertson,
    run_bounded_benchmark,
)
from numeris.benchmarks.runner import SolverConfig
from numeris.budget import BoundedBenchmarkBudget
from numeris.solvers import solve_ode


MODEL_DEFINITIONS: dict[str, tuple[Callable[[], Any], list[float], str]] = {
    "Damped oscillator": (damped_oscillator, [1.0, 0.1, 0.2], "DOP853"),
    "FitzHugh–Nagumo": (fitzhugh_nagumo, [0.7, 0.8, 0.08, 0.5], "DOP853"),
    "Lotka–Volterra": (lotka_volterra, [1.5, 1.0, 0.75, 1.0], "DOP853"),
    "Lorenz system": (lorenz, [10.0, 28.0, 8.0 / 3.0], "DOP853"),
    "Robertson kinetics": (robertson, [0.04, 3.0e7, 1.0e4], "BDF"),
}
SOLVERS = ("RK45", "DOP853", "Radau", "BDF", "LSODA")
TOLERANCES = {
    "Loose (1e-5 / 1e-7)": (1e-5, 1e-7),
    "Standard (1e-8 / 1e-10)": (1e-8, 1e-10),
    "Tight (1e-10 / 1e-12)": (1e-10, 1e-12),
}


@dataclass(frozen=True)
class RunRequest:
    model_name: str
    solver: str
    rtol: float
    atol: float
    max_rhs_evals: int
    output_path: Path


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def execute_run(request: RunRequest) -> dict[str, Any]:
    """Execute one bounded diagnostic using only the existing benchmark API."""
    factory, params, reference_solver = MODEL_DEFINITIONS[request.model_name]
    model = factory()
    # The reference is diagnostic context only; it is not treated as absolute truth.
    reference = solve_ode(model, np.asarray(params), method=reference_solver, rtol=1e-11, atol=1e-13)
    config = SolverConfig(
        name=f"desktop-{request.solver.lower()}",
        method=request.solver,
        rtol=request.rtol,
        atol=request.atol,
    )
    budget = BoundedBenchmarkBudget(max_rhs_evals=request.max_rhs_evals, max_runs=1)
    report = run_bounded_benchmark(
        model,
        np.asarray(params),
        [config],
        budget=budget,
        reference_states=reference.states,
        name=f"desktop/{request.model_name}",
        estimated_rhs_evals_per_run=500,
    )
    report.update(
        {
            "schema_version": "numeris-desktop-diagnostic-v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "exploratory_bounded_diagnostic",
            "scientific_status": "PROTOTYPE — NO_CONFIRMED_ADVANTAGE",
            "candidate_status": "NOT-IMPLEMENTED",
            "interpretation": (
                "This desktop run exercises existing solver infrastructure only. "
                "It is not evidence of NUMERIS-GO novelty, reliability, or superiority."
            ),
            "reference": {
                "method": reference_solver,
                "rtol": 1e-11,
                "atol": 1e-13,
                "is_absolute_truth": False,
            },
            "request": {
                "model": request.model_name,
                "solver": request.solver,
                "rtol": request.rtol,
                "atol": request.atol,
                "max_rhs_evals": request.max_rhs_evals,
            },
        }
    )
    payload = _json_safe(report)
    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    request.output_path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return payload


class NumerisDesktopApp:
    """Tkinter application with a deliberately small, research-honest UI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("NUMERIS — Inference-Aware Numerical Computing")
        self.root.geometry("920x680")
        self.root.minsize(760, 540)
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.last_report: dict[str, Any] | None = None
        self.last_path: Path | None = None
        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        title = ttk.Label(outer, text="NUMERIS", font=("TkDefaultFont", 20, "bold"))
        title.pack(anchor="w")
        ttk.Label(
            outer,
            text="Native desktop prototype for bounded numerical diagnostics",
        ).pack(anchor="w", pady=(0, 10))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True)
        self.overview_tab = ttk.Frame(self.notebook, padding=16)
        self.run_tab = ttk.Frame(self.notebook, padding=16)
        self.results_tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.run_tab, text="Run Model")
        self.notebook.add(self.results_tab, text="Results")
        self._build_overview()
        self._build_run()
        self._build_results()

    def _build_overview(self) -> None:
        frame = self.overview_tab
        ttk.Label(frame, text="What this application does", font=("TkDefaultFont", 14, "bold")).pack(anchor="w")
        text = (
            "This is a native Tkinter shell around the existing NUMERIS benchmark API.\n\n"
            "It runs one bounded solver diagnostic in a background thread, records the result as JSON, "
            "and exposes solver cost and trajectory error against a diagnostic reference.\n\n"
            "Research honesty: the NUMERIS-GO candidate is currently NOT-IMPLEMENTED. "
            "A run marked completed or reference-resolved is not proof of novelty or superiority. "
            "The app may show over_budget, failed, or not_started outcomes."
        )
        ttk.Label(frame, text=text, justify="left", wraplength=760).pack(anchor="w", pady=(8, 18))
        status_box = ttk.LabelFrame(frame, text="Current scientific status", padding=12)
        status_box.pack(fill="x", anchor="n")
        ttk.Label(
            status_box,
            text="PROTOTYPE  •  CANDIDATE: NOT-IMPLEMENTED  •  NO_CONFIRMED_ADVANTAGE",
            foreground="#8a4b08",
            wraplength=760,
        ).pack(anchor="w")
        ttk.Label(
            frame,
            text="Use Run Model to select one of the five benchmark models and execute a bounded diagnostic.",
        ).pack(anchor="w", pady=(18, 0))

    def _build_run(self) -> None:
        frame = self.run_tab
        frame.columnconfigure(1, weight=1)
        self.model_var = tk.StringVar(value=next(iter(MODEL_DEFINITIONS)))
        self.solver_var = tk.StringVar(value="DOP853")
        self.tolerance_var = tk.StringVar(value="Standard (1e-8 / 1e-10)")
        self.budget_var = tk.StringVar(value="5000")
        self.run_status_var = tk.StringVar(value="Ready — no run started")

        fields = (
            ("Model", ttk.Combobox(frame, textvariable=self.model_var, values=list(MODEL_DEFINITIONS), state="readonly")),
            ("Solver", ttk.Combobox(frame, textvariable=self.solver_var, values=SOLVERS, state="readonly")),
            ("Tolerance", ttk.Combobox(frame, textvariable=self.tolerance_var, values=list(TOLERANCES), state="readonly")),
        )
        for row, (label, widget) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=7)
            widget.grid(row=row, column=1, sticky="ew", pady=7)
        ttk.Label(frame, text="RHS budget").grid(row=3, column=0, sticky="w", padx=(0, 12), pady=7)
        ttk.Entry(frame, textvariable=self.budget_var).grid(row=3, column=1, sticky="ew", pady=7)

        note = ttk.LabelFrame(frame, text="Run semantics", padding=10)
        note.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(16, 12))
        note.columnconfigure(0, weight=1)
        ttk.Label(
            note,
            text=(
                "The selected solver is run through run_bounded_benchmark. "
                "SciPy calls cannot be interrupted mid-call: if measured cost exceeds the cap, "
                "the JSON result explicitly reports over_budget."
            ),
            wraplength=700,
            justify="left",
        ).grid(row=0, column=0, sticky="w")
        self.run_button = ttk.Button(frame, text="Run bounded diagnostic", command=self.start_run)
        self.run_button.grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 8))
        ttk.Label(frame, textvariable=self.run_status_var, wraplength=700).grid(row=6, column=0, columnspan=2, sticky="w")

    def _build_results(self) -> None:
        frame = self.results_tab
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        toolbar = ttk.Frame(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.open_button = ttk.Button(toolbar, text="Open JSON result…", command=self.open_json)
        self.open_button.pack(side="left")
        self.path_var = tk.StringVar(value="No result loaded")
        ttk.Label(toolbar, textvariable=self.path_var).pack(side="left", padx=12)
        self.result_text = tk.Text(frame, wrap="word", height=24, state="disabled")
        self.result_text.grid(row=1, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.result_text.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.result_text.configure(yscrollcommand=scroll.set)

    def start_run(self) -> None:
        try:
            budget = int(self.budget_var.get())
            if budget < 0:
                raise ValueError("RHS budget must be non-negative")
            rtol, atol = TOLERANCES[self.tolerance_var.get()]
        except (KeyError, ValueError) as exc:
            messagebox.showerror("Invalid run settings", str(exc), parent=self.root)
            return
        output = ROOT / "desktop_app" / "results" / "latest.json"
        request = RunRequest(self.model_var.get(), self.solver_var.get(), rtol, atol, budget, output)
        self.run_button.configure(state="disabled")
        self.run_status_var.set("Running in background…")
        self.events.put(("status", "Running — the window remains responsive"))
        threading.Thread(target=self._worker, args=(request,), daemon=True).start()

    def _worker(self, request: RunRequest) -> None:
        try:
            self.events.put(("done", (request.output_path, execute_run(request))))
        except Exception as exc:  # UI must never silently lose a failed run.
            self.events.put(("error", (exc, traceback.format_exc())))

    def _poll_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "status":
                    self.run_status_var.set(payload)
                elif event == "done":
                    path, report = payload
                    self.last_path, self.last_report = path, report
                    self.run_button.configure(state="normal")
                    self.run_status_var.set(f"Finished: {report.get('status', 'unknown')}")
                    self._show_report(path, report)
                    self.notebook.select(self.results_tab)
                elif event == "error":
                    exc, details = payload
                    self.run_button.configure(state="normal")
                    self.run_status_var.set("Run failed — see error dialog")
                    messagebox.showerror("NUMERIS run failed", f"{exc}\n\n{details}", parent=self.root)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _show_report(self, path: Path, report: dict[str, Any]) -> None:
        self.path_var.set(str(path))
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", json.dumps(report, indent=2, ensure_ascii=False))
        self.result_text.configure(state="disabled")

    def open_json(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self.root,
            title="Open NUMERIS JSON result",
            initialdir=str((ROOT / "desktop_app" / "results")),
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if not selected:
            return
        try:
            path = Path(selected)
            report = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(report, dict):
                raise ValueError("JSON root must be an object")
            self.last_path, self.last_report = path, report
            self._show_report(path, report)
            self.notebook.select(self.results_tab)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            messagebox.showerror("Cannot open JSON", str(exc), parent=self.root)


def main() -> int:
    root = tk.Tk()
    NumerisDesktopApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
