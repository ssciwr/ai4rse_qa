import os
import subprocess
import sys

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pytest

import qa.lotka as lotka
from qa.lotka import solve_lotkavolterra


def test_solution_returns_one_value_per_requested_time_and_initial_conditions():
    x, y = solve_lotkavolterra(
        alpha=1.0,
        beta=0.1,
        gamma=1.5,
        delta=0.075,
        x0=12.0,
        y0=8.0,
        t_end=10.0,
        n_points=101,
    )

    assert isinstance(x, np.ndarray)
    assert isinstance(y, np.ndarray)
    assert x.ndim == y.ndim == 1
    assert x.shape == y.shape == (101,)
    assert x[0] == pytest.approx(12.0)
    assert y[0] == pytest.approx(8.0)


def test_origin_equilibrium_stays():
    x, y = solve_lotkavolterra(
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
    x, y = solve_lotkavolterra(
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
    t = np.linspace(0.0, t_end, n_points)

    x, y = solve_lotkavolterra(
        alpha=alpha,
        beta=0.2,
        gamma=1.1,
        delta=0.1,
        x0=x0,
        y0=0.0,
        t_end=t_end,
        n_points=n_points,
    )

    np.testing.assert_allclose(x, x0 * np.exp(alpha * t), rtol=1e-5, atol=1e-8)
    np.testing.assert_allclose(y, 0.0, atol=1e-12)


def test_prey_free_solution_matches_exponential_predator_decay():
    gamma = 1.1
    y0 = 4.0
    t_end = 3.0
    n_points = 61
    t = np.linspace(0.0, t_end, n_points)

    x, y = solve_lotkavolterra(
        alpha=0.7,
        beta=0.2,
        gamma=gamma,
        delta=0.1,
        x0=0.0,
        y0=y0,
        t_end=t_end,
        n_points=n_points,
    )

    np.testing.assert_allclose(x, 0.0, atol=1e-12)
    np.testing.assert_allclose(y, y0 * np.exp(-gamma * t), rtol=1e-5, atol=1e-8)


def test_positive_populations_remain_finite_and_nonnegative():
    x, y = solve_lotkavolterra(
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


def test_plot_trajectories_writes_nonempty_pdf(tmp_path):
    t = np.linspace(0.0, 1.0, 5)
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    output = tmp_path / "trajectories.pdf"

    lotka.plot_trajectories(t, x, y, output)

    assert output.is_file()
    assert output.stat().st_size > 0
    assert output.read_bytes().startswith(b"%PDF")


def test_plot_phase_writes_nonempty_pdf(tmp_path):
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    output = tmp_path / "phase.pdf"

    lotka.plot_phase(x, y, output)

    assert output.is_file()
    assert output.stat().st_size > 0
    assert output.read_bytes().startswith(b"%PDF")


def test_plot_trajectories_contains_x_and_y_lines(tmp_path):
    t = np.linspace(0.0, 1.0, 5)
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([5.0, 4.0, 3.0, 2.0, 1.0])

    fig, ax = lotka.plot_trajectories(t, x, y, tmp_path / "trajectories.pdf")

    assert len(ax.lines) == 2
    np.testing.assert_allclose(ax.lines[0].get_xdata(), t)
    np.testing.assert_allclose(ax.lines[0].get_ydata(), x)
    np.testing.assert_allclose(ax.lines[1].get_xdata(), t)
    np.testing.assert_allclose(ax.lines[1].get_ydata(), y)


def test_plot_phase_contains_y_as_function_of_x(tmp_path):
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([5.0, 4.0, 3.0, 2.0, 1.0])

    fig, ax = lotka.plot_phase(x, y, tmp_path / "phase.pdf")

    assert len(ax.lines) == 1
    np.testing.assert_allclose(ax.lines[0].get_xdata(), x)
    np.testing.assert_allclose(ax.lines[0].get_ydata(), y)


def run_lotka_cli(*args):
    """Run the module exactly as a user would from a terminal."""
    return subprocess.run(
        [sys.executable, "-m", "qa.lotka", *args],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "MPLBACKEND": "Agg"},
    )


def test_cli_writes_expected_pdf_plots_to_calling_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_lotka_cli(
        "--x0", "10", "--y0", "5", "--t", "5", "--n", "50",
    )

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "lotka_trajectories.pdf").is_file()
    assert (tmp_path / "lotka_phase.pdf").is_file()


def test_cli_plot_outputs_are_nonempty_pdfs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_lotka_cli(
        "--x0", "10", "--y0", "5", "--t", "5", "--n", "50",
    )

    assert result.returncode == 0, result.stderr
    for filename in ["lotka_trajectories.pdf", "lotka_phase.pdf"]:
        pdf = tmp_path / filename
        assert pdf.stat().st_size > 0
        assert pdf.read_bytes().startswith(b"%PDF")


def test_cli_accepts_explicit_parameters_and_initial_conditions():
    result = run_lotka_cli(
        "--a", "3.0", "--b", "2.0", "--c", "1.0", "--d", "0.4",
        "--x0", ".03", "--y0", "0.5", "--t", "100", "--n", "10",
    )

    assert result.returncode == 0, result.stderr


def test_cli_uses_defaults_when_no_options_are_given():
    result = run_lotka_cli()

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "argv",
    [
        ("--a", "not-a-number"),
        ("--n", "0"),
        ("--n", "-2"),
        ("--t", "-1"),
    ],
)
def test_cli_rejects_invalid_numeric_inputs(argv):
    result = run_lotka_cli(*argv)

    assert result.returncode == 2


def test_cli_help_lists_all_supported_options():
    result = run_lotka_cli("--help")

    assert result.returncode == 0
    for option in ("--a", "--b", "--c", "--d", "--x0", "--y0", "--t", "--n"):
        assert option in result.stdout
