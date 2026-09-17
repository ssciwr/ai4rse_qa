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
        return lotka(t, state, alpha, beta, gamma, delta)

    t_eval = np.linspace(0, t_end, n_points)
    sol = solve_ivp(rhs, [0, t_end], [x0, y0], t_eval=t_eval, method="RK45")
    return sol.t, sol.y[0], sol.y[1]


def plot_time(t, x, y):
    import matplotlib.pyplot as plt

    plt.plot(t, x, label="x")
    plt.plot(t, y, label="y")
    plt.legend()
    plt.show()


def plot_phase(x, y):
    import matplotlib.pyplot as plt

    plt.plot(x, y)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()


def lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """

    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[1]]


if __name__ == "__main__":
    import argparse, sys
    if len(sys.argv) <= 1:
        sys.stderr.write("Lotka Volterra equations need parameters alpha, beta, gamma, delta and initial conditions x0, y0\n")
        sys.exit(1)
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, required=True)
    parser.add_argument("--beta", type=float, required=True)
    parser.add_argument("--gamma", type=float, required=True)
    parser.add_argument("--delta", type=float, required=True)
    parser.add_argument("--x0", type=float, required=True)
    parser.add_argument("--y0", type=float, required=True)
    args = parser.parse_args()
    t, x, y = solve_lotkavolterra(
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        delta=args.delta,
        x0=args.x0,
        y0=args.y0,
    )
    plot_time(t, x, y)
    plot_phase(x, y)
