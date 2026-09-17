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
    """Solve the Lotka--Volterra system and return both population series."""

    model_inputs = (alpha, beta, gamma, delta, x0, y0)
    if any(value < 0 for value in model_inputs):
        raise ValueError(
            "Model parameters and initial populations must be non-negative"
        )

    def rhs(t, state):
        return lotka(t, state, alpha, beta, gamma, delta)

    t_eval = np.linspace(0, t_end, n_points)
    sol = solve_ivp(rhs, [0, t_end], [x0, y0], t_eval=t_eval, method="RK45")
    if not sol.success:
        raise RuntimeError(f"Lotka--Volterra integration failed: {sol.message}")

    return sol.y[0], sol.y[1]


def plot_time(t, x, y):
    """Show the populations as functions of time."""
    import matplotlib.pyplot as plt

    if any(np.asarray(values).size == 0 for values in (t, x, y)):
        raise ValueError("Solution data must not be empty")

    plt.plot(t, x, label="x")
    plt.plot(t, y, label="y")
    plt.legend()
    plt.show()


def plot_phase(x, y):
    """Show the phase-space trajectory."""
    import matplotlib.pyplot as plt

    if any(np.asarray(values).size == 0 for values in (x, y)):
        raise ValueError("Solution data must not be empty")

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


def main(argv=None):
    """Run the solver and plots from command-line arguments."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=0.1)
    parser.add_argument("--gamma", type=float, default=1.5)
    parser.add_argument("--delta", type=float, default=0.075)
    parser.add_argument("--x0", type=float, default=0.0)
    parser.add_argument("--y0", type=float, default=0.0)
    parser.add_argument("--t-end", type=float, default=10.0)
    parser.add_argument("--n-points", type=int, default=100)
    args = parser.parse_args(argv)

    x, y = solve_lotkavolterra(
        alpha=args.alpha,
        beta=args.beta,
        gamma=args.gamma,
        delta=args.delta,
        x0=args.x0,
        y0=args.y0,
        t_end=args.t_end,
        n_points=args.n_points,
    )
    t = np.linspace(0, args.t_end, args.n_points)
    plot_time(t, x, y)
    plot_phase(x, y)


if __name__ == "__main__":
    main()
