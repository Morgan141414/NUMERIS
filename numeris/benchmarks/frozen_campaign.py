"""Bounded execution of the frozen v0.1 validation campaign.

The frozen manifest is a protocol input, not a result.  This module parses
the small, declarative manifest table and executes only an explicitly bounded
subset of its Cartesian product.  A bounded run is never labelled as a full
campaign: planned, executed and not-started cells are reported separately.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

import numpy as np

from numeris.inference.gaussian import gaussian_negative_log_likelihood
from numeris.solvers.scipy_solver import solve_ode

from .fitzhugh_nagumo import fitzhugh_nagumo
from .lorenz import lorenz
from .lotka_volterra import lotka_volterra
from .oscillator import damped_oscillator
from .robertson import robertson


@dataclass(frozen=True)
class FrozenModelSpec:
    """One model/data row from the frozen manifest."""

    model_id: str
    factory: str
    time_kind: str
    time_args: tuple[float, ...]
    truth: tuple[float, ...]
    sigmas: tuple[float, ...]
    budget_rhs: int

    def build(self) -> Any:
        builders = {
            "damped_oscillator": damped_oscillator,
            "fitzhugh_nagumo": fitzhugh_nagumo,
            "lotka_volterra": lotka_volterra,
            "lorenz": lorenz,
            "robertson": robertson,
        }
        try:
            factory = builders[self.factory]
        except KeyError as exc:
            raise ValueError(f"unsupported frozen model factory: {self.factory}") from exc
        if self.time_kind == "linspace":
            times = np.linspace(self.time_args[0], self.time_args[1], int(self.time_args[2]))
        elif self.time_kind == "geomspace":
            times = np.geomspace(self.time_args[0], self.time_args[1], int(self.time_args[2]))
        else:
            raise ValueError(f"unsupported frozen time grid: {self.time_kind}")
        return factory(times)

    def as_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "factory": self.factory,
            "time_kind": self.time_kind,
            "time_args": list(self.time_args),
            "truth": list(self.truth),
            "sigmas": list(self.sigmas),
            "budget_rhs": self.budget_rhs,
        }


@dataclass(frozen=True)
class FrozenCampaignFactors:
    """Explicit factors accepted instead of a manifest file.

    Supplying factors is useful for tests and small exploratory runs.  Such a
    run is still marked as ``explicit_factors`` and cannot be mistaken for a
    frozen-manifest result.
    """

    models: tuple[FrozenModelSpec, ...]
    methods: tuple[str, ...]
    tolerance_levels: tuple[tuple[float, float], ...]
    seeds: tuple[int, ...]
    reference_method: Mapping[str, str]
    manifest_version: str = "explicit-factors"

    def as_dict(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "models": [model.as_dict() for model in self.models],
            "methods": list(self.methods),
            "tolerance_levels": [list(item) for item in self.tolerance_levels],
            "seeds": list(self.seeds),
            "reference_method": dict(self.reference_method),
        }


def _numbers(text: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in text.strip("[] ").split(","))


def _time_expression(text: str) -> tuple[str, tuple[float, ...]]:
    match = re.fullmatch(r"(linspace|geomspace)\(([^)]*)\)", text.strip())
    if match is None:
        raise ValueError(f"unsupported time expression: {text}")
    values = tuple(float(item.strip()) for item in match.group(2).split(","))
    if len(values) != 3:
        raise ValueError("time expression must contain start, stop and count")
    return match.group(1), values


def load_frozen_manifest(path: str | Path) -> FrozenCampaignFactors:
    """Parse the exact model/configuration factors from manifest v0.1.

    Parsing is intentionally strict and limited to the manifest table.  It
    does not execute arbitrary Python expressions and rejects an altered row
    rather than silently inventing defaults.
    """
    manifest_path = Path(path)
    text = manifest_path.read_text(encoding="utf-8")
    if "NUMERIS frozen experiment manifest v0.1" not in text:
        raise ValueError("manifest is not NUMERIS frozen experiment manifest v0.1")
    row_pattern = re.compile(
        r"\|\s*(OSC|FHN|LV|LOR|ROB)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|"
        r"\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|"
    )
    rows = row_pattern.findall(text)
    if len(rows) != 5:
        raise ValueError(f"expected five frozen model rows, found {len(rows)}")
    models: list[FrozenModelSpec] = []
    for model_id, factory, initial_state, grid, truth, sigmas, budget in rows:
        del initial_state  # Initial states are part of the canonical factories.
        time_kind, time_args = _time_expression(grid)
        sigma_values = tuple(float(item.strip().strip("`")) for item in sigmas.split(","))
        models.append(
            FrozenModelSpec(
                model_id=model_id,
                factory=factory,
                time_kind=time_kind,
                time_args=time_args,
                truth=_numbers(truth),
                sigmas=sigma_values,
                    budget_rhs=int(budget.strip().strip("`").replace(",", "")),
            )
        )
    return FrozenCampaignFactors(
        models=tuple(models),
        methods=("RK45", "DOP853", "Radau", "BDF", "LSODA"),
        tolerance_levels=((1e-4, 1e-6), (1e-6, 1e-8), (1e-8, 1e-10), (1e-10, 1e-12)),
        seeds=tuple(range(10)),
        reference_method={"OSC": "DOP853", "FHN": "DOP853", "LV": "DOP853", "LOR": "DOP853", "ROB": "BDF"},
        manifest_version="v0.1",
    )


def _digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(array, dtype=np.float64).tobytes()).hexdigest()


def _normalise_factors(factors: FrozenCampaignFactors | Mapping[str, Any]) -> FrozenCampaignFactors:
    if isinstance(factors, FrozenCampaignFactors):
        return factors
    raw = dict(factors)
    models = tuple(item if isinstance(item, FrozenModelSpec) else FrozenModelSpec(**item) for item in raw["models"])
    return FrozenCampaignFactors(
        models=models,
        methods=tuple(str(item) for item in raw["methods"]),
        tolerance_levels=tuple(tuple(float(value) for value in pair) for pair in raw["tolerance_levels"]),
        seeds=tuple(int(item) for item in raw["seeds"]),
        reference_method=dict(raw["reference_method"]),
        manifest_version=str(raw.get("manifest_version", "explicit-factors")),
    )


def run_frozen_campaign(
    *,
    manifest_path: str | Path | None = None,
    factors: FrozenCampaignFactors | Mapping[str, Any] | None = None,
    mode: str = "dry-run",
    model_ids: Sequence[str] | None = None,
    seeds: Sequence[int] | None = None,
    sigmas: Sequence[float] | None = None,
    methods: Sequence[str] | None = None,
    tolerance_levels: Sequence[Sequence[float]] | None = None,
    max_cells: int = 25,
    root_seed: int = 0,
) -> dict[str, Any]:
    """Run a bounded subset of the frozen Cartesian campaign.

    ``mode="dry-run"`` performs no ODE solves.  ``mode="real"`` is still a
    bounded campaign and defaults to at most 25 cells.  Cells not admitted by
    ``max_cells`` are retained as ``not_started``; failures and budget
    violations are retained rather than dropped from denominators.
    """
    if (manifest_path is None) == (factors is None):
        raise ValueError("provide exactly one of manifest_path or factors")
    if mode not in {"dry-run", "real"}:
        raise ValueError("mode must be 'dry-run' or 'real'")
    if not isinstance(max_cells, (int, np.integer)) or max_cells <= 0:
        raise ValueError("max_cells must be a positive integer")
    loaded = load_frozen_manifest(manifest_path) if manifest_path is not None else _normalise_factors(factors)
    selected_models = tuple(model for model in loaded.models if model_ids is None or model.model_id in set(model_ids))
    if not selected_models:
        raise ValueError("model_ids selected no frozen models")
    selected_seeds = tuple(loaded.seeds if seeds is None else (int(item) for item in seeds))
    sigma_values = (
        sigmas
        if sigmas is not None
        else [sigma for model in selected_models for sigma in model.sigmas]
    )
    selected_sigmas = tuple(sorted({float(item) for item in sigma_values}))
    selected_methods = tuple(loaded.methods if methods is None else (str(item) for item in methods))
    selected_levels = tuple(
        loaded.tolerance_levels
        if tolerance_levels is None
        else tuple(tuple(float(value) for value in pair) for pair in tolerance_levels)
    )
    if not selected_seeds or not selected_sigmas or not selected_methods or not selected_levels:
        raise ValueError("selected campaign factors must be non-empty")
    if any(len(pair) != 2 or pair[0] <= 0 or pair[1] <= 0 for pair in selected_levels):
        raise ValueError("tolerance levels must be positive (rtol, atol) pairs")

    planned: list[dict[str, Any]] = []
    for model in selected_models:
        for seed in selected_seeds:
            for sigma in selected_sigmas:
                if sigma not in model.sigmas:
                    continue
                for method in selected_methods:
                    for level_index, (rtol, atol) in enumerate(selected_levels):
                        planned.append({
                            "model_id": model.model_id,
                            "seed": int(seed),
                            "sigma": float(sigma),
                            "method": method,
                            "tolerance_level": level_index,
                            "rtol": float(rtol),
                            "atol": float(atol),
                            "pair_id": f"{model.model_id}:seed={seed}:sigma={sigma:g}",
                        })

    if not planned:
        raise ValueError("selected factors produce no campaign cells")
    admitted = planned[: int(max_cells)]
    admitted_keys = {id(item) for item in admitted}
    seed_sequence = np.random.SeedSequence(int(root_seed)).spawn(len(selected_models))
    model_seed_map = {
        model.model_id: int(child.generate_state(1, dtype=np.uint64)[0] % np.iinfo(np.int64).max)
        for model, child in zip(selected_models, seed_sequence)
    }
    model_by_id = {model.model_id: model for model in selected_models}
    observations: dict[tuple[str, int, float], tuple[np.ndarray, float]] = {}
    rows: list[dict[str, Any]] = []
    for cell in planned:
        if id(cell) not in admitted_keys:
            rows.append({**cell, "status": "not_started", "execution_mode": mode, "failure_reason": "bounded_limit"})
            continue
        base = {**cell, "execution_mode": mode, "failure_reason": None}
        if mode == "dry-run":
            rows.append({**base, "status": "not_started", "failure_reason": "dry_run_no_solver_calls"})
            continue
        model_spec = model_by_id[cell["model_id"]]
        key = (cell["model_id"], cell["seed"], cell["sigma"])
        try:
            if key not in observations:
                model = model_spec.build()
                reference = solve_ode(
                    model,
                    np.asarray(model_spec.truth),
                    method=loaded.reference_method[model_spec.model_id],
                    rtol=1e-12,
                    atol=1e-14,
                )
                if not reference.success:
                    raise RuntimeError(f"reference_failure: {reference.message}")
                rng = np.random.default_rng(int(cell["seed"]) + model_seed_map[cell["model_id"]])
                observations[key] = (
                    model.observe(reference.states) + rng.normal(0.0, cell["sigma"], size=reference.states.shape),
                    float(gaussian_negative_log_likelihood(model.observe(reference.states), model.observe(reference.states), cell["sigma"])),
                )
            model = model_spec.build()
            result = solve_ode(
                model,
                np.asarray(model_spec.truth),
                method=cell["method"],
                rtol=cell["rtol"],
                atol=cell["atol"],
            )
            if not result.success:
                rows.append({**base, "status": "failure", "failure_reason": str(result.message), "nfev": int(result.nfev)})
                continue
            if result.nfev > model_spec.budget_rhs:
                rows.append({**base, "status": "over_budget", "failure_reason": "rhs_budget_exceeded", "nfev": int(result.nfev)})
                continue
            observations_array, reference_nll = observations[key]
            nll = gaussian_negative_log_likelihood(model.observe(result.states), observations_array, cell["sigma"])
            rows.append({
                **base,
                "status": "success",
                "failure_reason": None,
                "nfev": int(result.nfev),
                "runtime_s": float(result.runtime_s),
                "likelihood_error": float(abs(nll - reference_nll)),
                "seed_metadata": {
                    "seed": int(cell["seed"]),
                    "model_seed_offset": model_seed_map[cell["model_id"]],
                    "observation_digest": _digest(observations_array),
                    "paired_observation_key": ":".join(str(item) for item in key),
                },
            })
        except Exception as exc:  # failures are part of the validation denominator
            rows.append({**base, "status": "failure", "failure_reason": f"{type(exc).__name__}: {exc}"})

    counts = {status: sum(row["status"] == status for row in rows) for status in ("success", "failure", "over_budget", "not_started")}
    report = {
        "schema_version": "frozen-campaign-v1",
        "campaign_status": "bounded_incomplete" if len(admitted) < len(planned) or mode == "dry-run" else "bounded_real_run",
        "complete": False,
        "mode": mode,
        "manifest": {
            "source": str(manifest_path) if manifest_path is not None else None,
            "version": loaded.manifest_version,
            "factors": loaded.as_dict(),
        },
        "limits": {"max_cells": int(max_cells), "planned_cells": len(planned), "admitted_cells": len(admitted)},
        "counts": counts,
        "cells": rows,
        "negative_results": {
            "no_confirmed_advantage": True,
            "superiority_tested": False,
            "full_campaign_completed": False,
            "unstarted_cells_retained": True,
            "failed_cells_retained": True,
            "over_budget_cells_retained": True,
            "reason": "A bounded validation run is diagnostic evidence only; it cannot establish superiority or a complete-manifest result.",
        },
    }
    json.dumps(report, allow_nan=False, sort_keys=True)
    return report


__all__ = ["FrozenCampaignFactors", "FrozenModelSpec", "load_frozen_manifest", "run_frozen_campaign"]
