import numpy as np
import pytest

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
