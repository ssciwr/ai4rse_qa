import numpy as np

from qa.lotka import solve_lotkavolterra


def test_origin_equilibrium_stays():
    t, x, y = solve_lotkavolterra(
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
    assert len(t) == 1000


def test_nontrivial_equilibrium_stays():
    alpha, beta, gamma, delta = 1.0, 0.1, 1.5, 0.075
    x0 = gamma / delta
    y0 = alpha / beta
    t, x, y = solve_lotkavolterra(
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
    assert len(t) == 1000
