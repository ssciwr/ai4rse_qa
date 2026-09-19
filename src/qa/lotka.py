"""Solve and plot the two-species Lotka-Volterra predator-prey model."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp


def lotka(t, x, alpha, beta, gamma, delta):
    """Evaluate the Lotka-Volterra right-hand side.

    Args:
        t: Current time. The autonomous system does not use this value, but
            SciPy's ODE solver passes it to the derivative function.
        x: State vector ``[prey, predator]`` at time ``t``.
        alpha: Prey growth rate.
        beta: Predation rate coefficient.
        gamma: Predator death rate.
        delta: Predator growth rate per prey eaten.

    Returns:
        The derivatives ``[dprey_dt, dpredator_dt]``.
    """

    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[1]]


def solve_lotkavolterra(
    alpha=1.0,
    beta=0.1,
    gamma=1.5,
    delta=0.075,
    x0=0.0,
    y0=0.0,
    t_end=10.0,
    n_points=100,
    function=lotka,
):
    """Solve the Lotka-Volterra system and return population time series.

    Args:
        alpha: Prey growth rate.
        beta: Predation rate coefficient.
        gamma: Predator death rate.
        delta: Predator growth rate per prey eaten.
        x0: Initial prey population.
        y0: Initial predator population.
        t_end: End time for the simulation interval, starting from zero.
        n_points: Number of evenly spaced output time points.
        function: Derivative function with the same call signature as
            :func:`lotka`. This is mainly useful for tests or experimentation.

    Returns:
        A tuple ``(t, x, y)`` containing NumPy arrays for the output times,
        prey population, and predator population.

    Raises:
        RuntimeError: If SciPy's ODE integrator reports a failure.
    """

    def rhs(t, state):
        return function(t, state, alpha, beta, gamma, delta)

    t_eval = np.linspace(0.0, t_end, n_points)
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

    return solution.t, solution.y[0], solution.y[1]


def plot_time(t, x, y):
    """Create a time-series plot for prey and predator populations.

    Args:
        t: Time points for the simulation output.
        x: Prey population values at each time point.
        y: Predator population values at each time point.

    Returns:
        The Matplotlib figure containing the trajectory plot.
    """

    fig, ax = plt.subplots()
    ax.plot(t, x, label="x")
    ax.plot(t, y, label="y")
    ax.legend()
    return fig


def plot_phase(x, y):
    """Create a phase plot of predator population against prey population.

    Args:
        x: Prey population values.
        y: Predator population values.

    Returns:
        The Matplotlib figure containing the phase plot.
    """

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig


def main():
    """Run the command-line interface and save solution plots.

    Parses Lotka-Volterra parameters from the command line, solves the model,
    and writes ``trajectory.pdf`` and ``phase.pdf`` to the project root.
    """

    import argparse
    import sys

    if len(sys.argv) <= 1:
        sys.stderr.write(
            "Lotka Volterra equations need parameters alpha, beta, gamma, delta and initial conditions x0, y0\n"
        )
        sys.exit(1)
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, required=True, help="Prey growth rate.")
    parser.add_argument(
        "--beta", type=float, required=True, help="Predation rate coefficient."
    )
    parser.add_argument(
        "--gamma", type=float, required=True, help="Predator death rate."
    )
    parser.add_argument(
        "--delta",
        type=float,
        required=True,
        help="Predator growth rate per prey eaten.",
    )
    parser.add_argument(
        "--x0", type=float, required=True, help="Initial prey population."
    )
    parser.add_argument(
        "--y0", type=float, required=True, help="Initial predator population."
    )
    parser.add_argument(
        "--t",
        type=float,
        required=False,
        default=10.0,
        help="End time for the simulation.",
    )
    parser.add_argument(
        "--n",
        type=int,
        required=False,
        default=100,
        help="Number of output time points.",
    )
    args = parser.parse_args()
    t, x, y = solve_lotkavolterra(
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        delta=args.gamma,
        x0=args.x0,
        y0=args.y0,
        t_end=args.t,
        n_points=args.n,
    )
    trajectory = plot_time(t, x, y)
    phase = plot_phase(x, y)

    trajectory.savefig(Path(__file__).parents[2] / "trajectory.pdf")
    phase.savefig(Path(__file__).parents[2] / "phase.pdf")


if __name__ == "__main__":
    main()
