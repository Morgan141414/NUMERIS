"""Plotting helpers for NUMERIS benchmark results.

The plotting dependency is optional.  Importing :mod:`numeris.visualization`
therefore remains safe when Matplotlib is not installed; plotting functions
raise a clear :class:`ImportError` only when they are called.
"""

try:
    from .plots import plot_error_vs_cost, plot_likelihood_budget, plot_trajectory
except ImportError as exc:  # pragma: no cover - exercised when matplotlib is absent
    if "matplotlib" not in str(exc).lower():
        raise

    plot_trajectory = None  # type: ignore[assignment]
    plot_error_vs_cost = None  # type: ignore[assignment]
    plot_likelihood_budget = None  # type: ignore[assignment]

__all__ = ["plot_error_vs_cost", "plot_likelihood_budget", "plot_trajectory"]
