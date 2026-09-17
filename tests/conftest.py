import pytest


def buggy_lotka(t, x, alpha, beta, gamma, delta):
    """
    right hand side of lotka-volterra equations
    t = time scalar
    x = state vector [x, y]
    """
    # bug: the last x[0] should be x[1]
    return [alpha * x[0] - beta * x[0] * x[1], delta * x[0] * x[1] - gamma * x[0]]


@pytest.fixture
def run_pi_session_for_bugfix():
    # TODO