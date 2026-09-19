import runpy
import sys
from types import SimpleNamespace

import matplotlib.pyplot as plt
import numpy as np
import pytest

import qa.lotka as lotka_module
from qa.lotka import plot_phase, plot_time, solve_lotkavolterra


def test_solution_returns_one_value_per_requested_time_and_initial_conditions():
    t, x, y = solve_lotkavolterra(
        alpha=1.0,
        beta=0.1,
        gamma=1.5,
        delta=0.075,
        x0=12.0,
        y0=8.0,
        t_end=10.0,
        n_points=101,
    )

    assert isinstance(t, np.ndarray)
    assert isinstance(x, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert t.ndim == x.ndim == y.ndim == 1
    assert t.shape == x.shape == y.shape == (101,)
    assert t[0] == pytest.approx(0.0)
    assert x[0] == pytest.approx(12.0)
    assert y[0] == pytest.approx(8.0)


def test_origin_equilibrium_stays():
    _, x, y = solve_lotkavolterra(
        alpha=1.0,
        beta=0.1,
        gamma=1.5,
        delta=0.075,
        x0=0.0,
        y0=0.0,
        t_end=100,
        n_points=1000,
    )

    assert np.allclose(x, 0.0)
    assert np.allclose(y, 0.0)


def test_nontrivial_equilibrium_stays():
    alpha, beta, gamma, delta = 1.0, 0.1, 1.5, 0.075
    x0 = gamma / delta
    y0 = alpha / beta
    _, x, y = solve_lotkavolterra(
        alpha=alpha,
        beta=beta,
        gamma=gamma,
        delta=delta,
        x0=x0,
        y0=y0,
        t_end=100,
        n_points=1000,
    )

    assert np.allclose(x, x0)
    assert np.allclose(y, y0)


def test_predator_free_solution_matches_exponential_prey_growth():
    alpha = 0.7
    x0 = 3.5
    t_end = 3.0
    n_points = 61
    expected_time = np.linspace(0.0, t_end, n_points)

    t, x, y = solve_lotkavolterra(
        alpha=alpha,
        beta=0.2,
        gamma=1.1,
        delta=0.1,
        x0=x0,
        y0=0.0,
        t_end=t_end,
        n_points=n_points,
    )

    np.testing.assert_allclose(t, expected_time)
    np.testing.assert_allclose(x, x0 * np.exp(alpha * t), rtol=1e-5, atol=1e-8)
    np.testing.assert_allclose(y, 0.0, atol=1e-12)


def test_prey_free_solution_matches_exponential_predator_decay():
    gamma = 1.1
    y0 = 4.0
    t_end = 3.0
    n_points = 61
    expected_time = np.linspace(0.0, t_end, n_points)

    t, x, y = solve_lotkavolterra(
        alpha=0.7,
        beta=0.2,
        gamma=gamma,
        delta=0.1,
        x0=0.0,
        y0=y0,
        t_end=t_end,
        n_points=n_points,
    )

    np.testing.assert_allclose(t, expected_time)
    np.testing.assert_allclose(x, 0.0, atol=1e-12)
    np.testing.assert_allclose(y, y0 * np.exp(-gamma * t), rtol=1e-5, atol=1e-8)


def test_solver_raises_runtime_error_when_integrator_fails(monkeypatch):
    def failing_solve_ivp(*args, **kwargs):
        return SimpleNamespace(success=False, message="synthetic integration failure")

    monkeypatch.setattr(lotka_module, "solve_ivp", failing_solve_ivp)

    with pytest.raises(RuntimeError, match="synthetic integration failure"):
        solve_lotkavolterra(x0=1.0, y0=1.0)


def test_plot_functions_return_independent_figures():
    plt.close("all")
    t = np.array([0.0, 1.0, 2.0])
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([3.0, 2.0, 1.0])

    time_figure = plot_time(t, x, y)
    phase_figure = plot_phase(x, y)

    assert time_figure is not phase_figure
    assert len(time_figure.axes[0].lines) == 2
    assert len(phase_figure.axes[0].lines) == 1

    plt.close("all")


def test_cli_without_arguments_exits_with_usage_message(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lotka.py"])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path("src/qa/lotka.py", run_name="__main__")

    assert excinfo.value.code == 1
    assert "need parameters alpha, beta, gamma, delta" in capsys.readouterr().err


def test_cli_help_describes_parameters(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["lotka.py", "--h"])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path("src/qa/lotka.py", run_name="__main__")

    help_text = capsys.readouterr().out
    assert excinfo.value.code == 0
    assert "--alpha ALPHA" in help_text
    assert "Prey growth rate." in help_text
    assert "--y0 Y0" in help_text
    assert "Initial predator population." in help_text
    assert "--n N" in help_text
    assert "Number of output time points." in help_text


def test_cli_writes_trajectory_and_phase_plots(monkeypatch, tmp_path):
    output_files = []
    solve_kwargs = {}

    class DummyAxes:
        def plot(self, *args, **kwargs):
            pass

        def legend(self):
            pass

        def set_xlabel(self, label):
            pass

        def set_ylabel(self, label):
            pass

    class DummyFigure:
        def savefig(self, path):
            output_files.append(path.name)
            tmp_path.joinpath(path.name).write_text("saved")

    def fake_solve_lotkavolterra(**kwargs):
        solve_kwargs.update(kwargs)
        return np.array([0.0, 1.0]), np.array([10.0, 11.0]), np.array([5.0, 4.0])

    monkeypatch.setattr(lotka_module, "solve_lotkavolterra", fake_solve_lotkavolterra)
    monkeypatch.setattr(
        lotka_module.plt, "subplots", lambda: (DummyFigure(), DummyAxes())
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lotka.py",
            "--alpha",
            "1.0",
            "--beta",
            "0.1",
            "--gamma",
            "1.5",
            "--delta",
            "0.075",
            "--x0",
            "10.0",
            "--y0",
            "5.0",
            "--t",
            "1.0",
            "--n",
            "3",
        ],
    )

    lotka_module.main()

    assert output_files == ["trajectory.pdf", "phase.pdf"]
    assert tmp_path.joinpath("trajectory.pdf").read_text() == "saved"
    assert tmp_path.joinpath("phase.pdf").read_text() == "saved"


def test_positive_populations_remain_finite_and_nonnegative():
    _, x, y = solve_lotkavolterra(
        alpha=1.0,
        beta=0.1,
        gamma=1.5,
        delta=0.075,
        x0=10.0,
        y0=5.0,
        t_end=20.0,
        n_points=401,
    )

    assert np.isfinite(x).all()
    assert np.isfinite(y).all()
    assert (x >= 0.0).all()
    assert (y >= 0.0).all()
