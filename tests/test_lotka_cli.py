import numpy as np
import pytest

from pytest_bdd import given, scenarios, then, when

from qa import lotka


scenarios("lotka_cli.feature")


DEFAULT_INPUTS = {
    "alpha": 1.0,
    "beta": 0.1,
    "gamma": 1.5,
    "delta": 0.075,
    "x0": 0.0,
    "y0": 0.0,
    "t_end": 10.0,
    "n_points": 100,
}


@pytest.fixture
def cli_calls(monkeypatch):
    calls = {"solver": [], "trajectory_plot": [], "phase_plot": []}

    def fake_solver(
        alpha=1.0,
        beta=0.1,
        gamma=1.5,
        delta=0.075,
        x0=0.0,
        y0=0.0,
        t_end=10.0,
        n_points=100,
    ):
        calls["solver"].append(
            {
                "alpha": alpha,
                "beta": beta,
                "gamma": gamma,
                "delta": delta,
                "x0": x0,
                "y0": y0,
                "t_end": t_end,
                "n_points": n_points,
            }
        )
        return np.full(n_points, x0), np.full(n_points, y0)

    def fake_plot_time(t, x, y):
        calls["trajectory_plot"].append((t, x, y))

    def fake_plot_phase(x, y):
        calls["phase_plot"].append((x, y))

    monkeypatch.setattr(lotka, "solve_lotkavolterra", fake_solver)
    monkeypatch.setattr(lotka, "plot_time", fake_plot_time)
    monkeypatch.setattr(lotka, "plot_phase", fake_plot_phase)
    return calls


@given(
    "valid model parameters and initial populations as command-line arguments",
    target_fixture="cli_case",
)
def explicit_cli_inputs():
    expected = {
        **DEFAULT_INPUTS,
        "alpha": 0.8,
        "beta": 0.2,
        "gamma": 1.2,
        "delta": 0.05,
        "x0": 12.0,
        "y0": 4.0,
    }
    arguments = [
        "--alpha",
        "0.8",
        "--beta",
        "0.2",
        "--gamma",
        "1.2",
        "--delta",
        "0.05",
        "--x0",
        "12",
        "--y0",
        "4",
    ]
    return {"arguments": arguments, "expected_inputs": expected}


@given(
    "no model parameters or initial populations as command-line arguments",
    target_fixture="cli_case",
)
def default_cli_inputs():
    return {"arguments": [], "expected_inputs": DEFAULT_INPUTS}


@when(
    "I run the Lotka-Volterra command-line application",
    target_fixture="cli_run",
)
def run_cli(cli_case, cli_calls):
    result = lotka.main(cli_case["arguments"])
    return {
        "result": result,
        "calls": cli_calls,
        "expected_inputs": cli_case["expected_inputs"],
    }


@then("the trajectory plot and phase plot are shown")
def both_plots_are_shown(cli_run):
    calls = cli_run["calls"]
    assert calls["solver"] == [cli_run["expected_inputs"]]
    assert len(calls["trajectory_plot"]) == 1
    assert len(calls["phase_plot"]) == 1

    t, trajectory_x, trajectory_y = calls["trajectory_plot"][0]
    phase_x, phase_y = calls["phase_plot"][0]
    assert len(t) == cli_run["expected_inputs"]["n_points"]
    np.testing.assert_array_equal(trajectory_x, phase_x)
    np.testing.assert_array_equal(trajectory_y, phase_y)


@then("the default model parameters and initial populations are used")
def solver_uses_defaults(cli_run):
    assert cli_run["calls"]["solver"] == [DEFAULT_INPUTS]
