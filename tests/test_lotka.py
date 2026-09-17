from qa.lotka import solve_lotkavolterra
import numpy as np

"""
Known solution structure of Lotka-Volterra model gives us test cases to check correctness against:

Equillibrium points of lotak volterra equations:
x*,y* = (0, 0)
x*,y* = (gamma/delta, alpha/beta)

For (x0=0, y0>0): y = y0 exp(-gamma t)
For (x0>0, y0=0): x = x0 exp(alpha t)
so if one species is 0, the other follows an exponential with the birth rate alpha or death rate gamma, respectively.

For all initials (x0 > 0, y0 > 0) we have stable oscillations around x*,y* = (gamma/delta, alpha/beta).

So if the model is initialized to the fixpoint, they should stay there forever,
and if both species are initialized to nonzero values, it oscialtes forever,
and one species is zero, the other follows an exponential
"""


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
