from scipy.integrate import solve_ivp
import numpy as np
import pytest


def buggy_lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """
    # bug: the last
    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[0]]


def solve_lotkavolterra(
    alpha=1.0,
    beta=0.1,
    gamma=1.5,
    delta=0.075,
    x0=0.0,
    y0=0.0,
    t_end=10.0,
    n_points=100,
):
    """Solve the Lotka-Volterra system and return time series.

    Parameters
    ----------
    alpha, beta, gamma, delta : float
        Model parameters.
    x0, y0 : float
        Initial populations.
    t_end : float
        End time.
    n_points : int
        Number of output points.

    Returns
    -------
    t, x, y : ndarrays
        Time and population arrays.
    """

    def rhs(t, state):
        return buggy_lotka(t, state, alpha, beta, gamma, delta)

    t_eval = np.linspace(0, t_end, n_points)
    sol = solve_ivp(rhs, [0, t_end], [x0, y0], t_eval=t_eval, method="RK45")
    return sol.t, sol.y[0], sol.y[1]
