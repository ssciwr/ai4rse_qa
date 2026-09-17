import matplotlib
import numpy as np

from pytest_bdd import given, scenarios, then, when

from qa.lotka import plot_phase, plot_time


matplotlib.use("Agg")

scenarios("lotka_plots.feature")


@given(
    "a non-empty Lotka-Volterra solution with time, prey, and predator values",
    target_fixture="solution_data",
)
def nonempty_solution_data():
    return {
        "t": np.array([0.0, 0.5, 1.0]),
        "x": np.array([10.0, 12.0, 15.0]),
        "y": np.array([5.0, 4.5, 4.0]),
    }


@when(
    "I create the trajectory plot and phase plot",
    target_fixture="shown_plots",
)
def create_both_plots(solution_data, monkeypatch):
    import matplotlib.pyplot as plt

    plt.close("all")
    shown_plots = []

    def capture_current_plot():
        axes = plt.gca()
        shown_plots.append(
            [
                {
                    "x": line.get_xdata().copy(),
                    "y": line.get_ydata().copy(),
                    "label": line.get_label(),
                }
                for line in axes.lines
            ]
        )
        plt.close(plt.gcf())

    monkeypatch.setattr(plt, "show", capture_current_plot)
    plot_time(solution_data["t"], solution_data["x"], solution_data["y"])
    plot_phase(solution_data["x"], solution_data["y"])
    return shown_plots


@then("the prey and predator trajectories are plotted against time")
def trajectories_are_plotted(shown_plots, solution_data):
    assert len(shown_plots) == 2
    trajectory_lines = shown_plots[0]
    assert len(trajectory_lines) == 2
    np.testing.assert_array_equal(trajectory_lines[0]["x"], solution_data["t"])
    np.testing.assert_array_equal(trajectory_lines[0]["y"], solution_data["x"])
    np.testing.assert_array_equal(trajectory_lines[1]["x"], solution_data["t"])
    np.testing.assert_array_equal(trajectory_lines[1]["y"], solution_data["y"])


@then("the predator population is plotted against the prey population")
def phase_trajectory_is_plotted(shown_plots, solution_data):
    phase_lines = shown_plots[1]
    assert len(phase_lines) == 1
    np.testing.assert_array_equal(phase_lines[0]["x"], solution_data["x"])
    np.testing.assert_array_equal(phase_lines[0]["y"], solution_data["y"])


@given(
    "empty time, prey, and predator data",
    target_fixture="empty_solution_data",
)
def empty_solution_data():
    empty = np.array([])
    return {"t": empty, "x": empty, "y": empty}


@when(
    "I try to create the trajectory plot or phase plot",
    target_fixture="empty_plot_errors",
)
def create_plots_with_empty_data(empty_solution_data, monkeypatch):
    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "show", lambda: None)
    plot_calls = {
        "trajectory": lambda: plot_time(
            empty_solution_data["t"],
            empty_solution_data["x"],
            empty_solution_data["y"],
        ),
        "phase": lambda: plot_phase(
            empty_solution_data["x"], empty_solution_data["y"]
        ),
    }
    errors = {}
    for plot_name, plot_call in plot_calls.items():
        try:
            plot_call()
        except ValueError as error:
            errors[plot_name] = error
        finally:
            plt.close("all")
    return errors


@then(
    "a value error is raised explaining that the solution data must not be empty"
)
def empty_data_is_rejected(empty_plot_errors):
    assert set(empty_plot_errors) == {"trajectory", "phase"}
    for error in empty_plot_errors.values():
        assert "must not be empty" in str(error).lower()
