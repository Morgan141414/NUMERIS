"""Matplotlib visualizations for trajectories and benchmark trade-offs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

try:  # Matplotlib is an optional visualization dependency.
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
except ImportError:  # pragma: no cover - depends on the environment
    plt = None  # type: ignore[assignment]
    Axes = Any  # type: ignore[assignment,misc]
    Figure = Any  # type: ignore[assignment,misc]


def _require_matplotlib() -> Any:
    if plt is None:
        raise ImportError(
            "Matplotlib is required for NUMERIS visualizations. "
            "Install it with `pip install matplotlib`."
        )
    return plt


def _axes(ax: Axes | None, *, title: str | None) -> tuple[Figure, Axes]:
    plotting = _require_matplotlib()
    if ax is None:
        figure, axis = plotting.subplots()
    else:
        axis = ax
        figure = axis.figure
    if title is not None:
        axis.set_title(title)
    return figure, axis


def _labels(labels: Sequence[str] | None, size: int) -> list[str]:
    if labels is None:
        return [f"state {index}" for index in range(size)]
    result = [str(label) for label in labels]
    if len(result) != size:
        raise ValueError("labels must have one entry per plotted series")
    return result


def plot_trajectory(
    times: Sequence[float],
    states: Sequence[Sequence[float]] | Sequence[float],
    *,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    title: str | None = "ODE trajectory",
    xlabel: str = "Time",
    ylabel: str = "State",
) -> Figure:
    """Plot one or more state components against time and return the figure."""
    time_values = np.asarray(times, dtype=float)
    state_values = np.asarray(states, dtype=float)
    if time_values.ndim != 1:
        raise ValueError("times must be one-dimensional")
    if state_values.ndim == 1:
        state_values = state_values[:, None]
    if state_values.ndim != 2 or state_values.shape[0] != time_values.size:
        raise ValueError("states must have shape (n_times, n_states)")

    figure, axis = _axes(ax, title=title)
    for index, label in enumerate(_labels(labels, state_values.shape[1])):
        axis.plot(time_values, state_values[:, index], label=label)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    if state_values.shape[1] > 1 or labels is not None:
        axis.legend()
    figure.tight_layout()
    return figure


def plot_error_vs_cost(
    costs: Sequence[float],
    errors: Sequence[float],
    *,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    title: str | None = "Error versus computational cost",
    xlabel: str = "Computational cost",
    ylabel: str = "Error",
) -> Figure:
    """Plot error against cost, optionally as multiple labelled series."""
    cost_values = np.asarray(costs, dtype=float)
    error_values = np.asarray(errors, dtype=float)
    if cost_values.shape != error_values.shape:
        raise ValueError("costs and errors must have the same shape")
    if cost_values.ndim not in (1, 2):
        raise ValueError("costs and errors must be one- or two-dimensional")
    if cost_values.ndim == 1:
        cost_values = cost_values[:, None]
        error_values = error_values[:, None]
    if labels is not None and len(labels) != cost_values.shape[1]:
        raise ValueError("labels must have one entry per plotted series")

    figure, axis = _axes(ax, title=title)
    for index in range(cost_values.shape[1]):
        label = str(labels[index]) if labels is not None else None
        axis.plot(cost_values[:, index], error_values[:, index], marker="o", label=label)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    if labels is not None:
        axis.legend()
    figure.tight_layout()
    return figure


def plot_likelihood_budget(
    budgets: Sequence[float],
    likelihoods: Sequence[float],
    *,
    labels: Sequence[str] | None = None,
    ax: Axes | None = None,
    title: str | None = "Likelihood versus computational budget",
    xlabel: str = "Computational budget",
    ylabel: str = "Negative log-likelihood",
) -> Figure:
    """Plot likelihood values against computational budgets."""
    figure = plot_error_vs_cost(
        budgets,
        likelihoods,
        labels=labels,
        ax=ax,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
    )
    return figure
