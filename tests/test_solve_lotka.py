import numpy as np

from pytest_bdd import given, scenarios, then, when

from qa.lotka import solve_lotkavolterra


scenarios("solve_lotka.feature")


VALID_INPUTS = {
    "alpha": 1.0,
    "beta": 0.1,
    "gamma": 1.5,
    "delta": 0.075,
    "x0": 10.0,
    "y0": 5.0,
    "t_end": 10.0,
    "n_points": 101,
}


@given(
    "valid model parameters and initial prey and predator populations",
    target_fixture="solver_inputs",
)
def valid_solver_inputs():
    return VALID_INPUTS.copy()


@when(
    "I solve the Lotka-Volterra equations for a requested number of time points",
    target_fixture="solution",
)
def solve_with_valid_inputs(solver_inputs):
    return solve_lotkavolterra(**solver_inputs)


@then(
    "I receive one prey value and one predator value for every requested time point"
)
def solution_contains_two_population_arrays(solution, solver_inputs):
    assert isinstance(solution, tuple)
    assert len(solution) == 2

    prey, predators = solution
    assert isinstance(prey, np.ndarray)
    assert isinstance(predators, np.ndarray)
    assert prey.shape == (solver_inputs["n_points"],)
    assert predators.shape == (solver_inputs["n_points"],)


@then("the first values equal the supplied initial populations")
def solution_starts_at_initial_populations(solution, solver_inputs):
    prey, predators = solution
    assert prey[0] == solver_inputs["x0"]
    assert predators[0] == solver_inputs["y0"]


@given(
    "a negative model parameter or initial population",
    target_fixture="negative_input_cases",
)
def negative_input_cases():
    cases = []
    for input_name in ("alpha", "beta", "gamma", "delta", "x0", "y0"):
        inputs = VALID_INPUTS.copy()
        inputs[input_name] = -1.0
        cases.append((input_name, inputs))
    return cases


@when(
    "I try to solve the Lotka-Volterra equations",
    target_fixture="negative_input_errors",
)
def solve_with_negative_inputs(negative_input_cases):
    errors = {}
    for input_name, inputs in negative_input_cases:
        try:
            solve_lotkavolterra(**inputs)
        except ValueError as error:
            errors[input_name] = error
    return errors


@then("a value error is raised explaining that inputs must be non-negative")
def all_negative_inputs_are_rejected(negative_input_cases, negative_input_errors):
    expected_inputs = {name for name, _ in negative_input_cases}
    assert set(negative_input_errors) == expected_inputs
    for error in negative_input_errors.values():
        assert "non-negative" in str(error).lower()
