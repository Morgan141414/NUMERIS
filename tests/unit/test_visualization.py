import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

import numpy as np

from numeris.visualization import (
    plot_error_vs_cost,
    plot_likelihood_budget,
    plot_trajectory,
)


def test_plot_trajectory_returns_figure_with_state_lines():
    figure = plot_trajectory([0.0, 1.0, 2.0], [[1.0, 2.0], [2.0, 3.0], [3.0, 5.0]])
    assert figure.__class__.__name__ == "Figure"
    assert len(figure.axes) == 1
    assert len(figure.axes[0].lines) == 2


def test_error_vs_cost_and_likelihood_budget_return_figures():
    costs = [10.0, 20.0, 40.0]
    values = [1.0, 0.5, 0.2]
    error_figure = plot_error_vs_cost(costs, values)
    likelihood_figure = plot_likelihood_budget(costs, values, labels=["RK45"])
    assert len(error_figure.axes[0].lines) == 1
    assert likelihood_figure.axes[0].get_xlabel() == "Computational budget"


def test_visualizations_do_not_show_or_require_matching_shapes():
    with pytest.raises(ValueError):
        plot_trajectory([0.0, 1.0], np.ones((3, 1)))
    with pytest.raises(ValueError):
        plot_error_vs_cost([1.0, 2.0], [1.0])
