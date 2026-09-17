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
    """Solve the Lotka--Volterra system on an evenly spaced time grid.

    Parameters are the four model rates, the initial populations ``x0`` and
    ``y0``, and the end time and number of requested output points.  The
    solution starts at time zero and is sampled through ``t_end``.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        The prey and predator populations, respectively, at each requested
        time point.
    """
    t_eval = np.linspace(0.0, t_end, n_points)

    def rhs(t, state):
        return lotka(t, state, alpha, beta, gamma, delta)

    solution = solve_ivp(
        rhs,
        (0.0, t_end),
        (x0, y0),
        t_eval=t_eval,
        method="RK45",
        rtol=1e-8,
        atol=1e-10,
    )
    if not solution.success:
        raise RuntimeError(f"Lotka--Volterra integration failed: {solution.message}")

    return solution.y[0], solution.y[1]


def lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """

    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[1]]
