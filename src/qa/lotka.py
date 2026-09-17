import numpy as np
from scipy.integrate import solve_ivp


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
    """Solve the Lotka--Volterra system and return its time series."""

    def rhs(t, state):
        return lotka(t, state, alpha, beta, gamma, delta)

    t_eval = np.linspace(0, t_end, n_points)
    sol = solve_ivp(rhs, [0, t_end], [x0, y0], t_eval=t_eval, method="RK45")
    return sol.t, sol.y[0], sol.y[1]


def lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """

    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[1]]
