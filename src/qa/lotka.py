import argparse

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


TRAJECTORY_PLOT_FILENAME = "lotka_trajectories.pdf"
PHASE_PLOT_FILENAME = "lotka_phase.pdf"


def _positive_int(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _nonnegative_float(value):
    value = float(value)
    if value < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return value


def main(argv=None):
    """Run the Lotka--Volterra solver with command-line options."""
    parser = argparse.ArgumentParser(description="Solve the Lotka--Volterra system.")
    parser.add_argument("--a", type=float, default=1.0, help="prey growth rate (alpha)")
    parser.add_argument("--b", type=float, default=0.1, help="predation rate (beta)")
    parser.add_argument("--c", type=float, default=1.5, help="predator death rate (gamma)")
    parser.add_argument("--d", type=float, default=0.075, help="predator growth rate (delta)")
    parser.add_argument("--x0", type=float, default=0.1, help="initial prey population")
    parser.add_argument("--y0", type=float, default=0.2, help="initial predator population")
    parser.add_argument("--t", type=_nonnegative_float, default=10.0, help="end time")
    parser.add_argument("--n", type=_positive_int, default=100, help="number of output points")
    args = parser.parse_args(argv)

    x, y = solve_lotkavolterra(
        alpha=args.a,
        beta=args.b,
        gamma=args.c,
        delta=args.d,
        x0=args.x0,
        y0=args.y0,
        t_end=args.t,
        n_points=args.n,
    )
    t = np.linspace(0.0, args.t, args.n)
    plot_trajectories(t, x, y, TRAJECTORY_PLOT_FILENAME)
    plot_phase(x, y, PHASE_PLOT_FILENAME)
    plt.show()
    return 0


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


def plot_trajectories(t, x, y, output_path):
    """Plot the prey and predator trajectories over time to a PDF file.

    Returns the Matplotlib figure and axes so callers and tests can inspect
    the plotted data.
    """
    fig, ax = plt.subplots()
    ax.plot(t, x, label="x(t)")
    ax.plot(t, y, label="y(t)")
    ax.set_title("Lotka--Volterra trajectories")
    ax.set_xlabel("t")
    ax.set_ylabel("population")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, format="pdf")
    return fig, ax


def plot_phase(x, y, output_path):
    """Plot the phase trajectory y(x) to a PDF file.

    Returns the Matplotlib figure and axes so callers and tests can inspect
    the plotted data.
    """
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Lotka--Volterra phase plot")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(output_path, format="pdf")
    return fig, ax


def lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """

    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[1]]


if __name__ == "__main__":
    main()
