import os
import subprocess
import sys
from pathlib import Path

from pytest_bdd import given, scenarios, then, when


scenarios("solve_lotka.feature")


SCRIPT_PATH = Path(__file__).parents[1] / "src" / "qa" / "lotka.py"
PARAMETERS = [
    "--alpha",
    "1",
    "--beta",
    "0.1",
    "--gamma",
    "1.5",
    "--delta",
    "0.075",
    "--x0",
    "10",
    "--y0",
    "10",
]


@given(
    "the lotka script accepts command line arguments alpha, beta, gamma, delta, x0, y0"
)
def lotka_args():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    for argument in ("--alpha", "--beta", "--gamma", "--delta", "--x0", "--y0"):
        assert argument in result.stdout


@when(
    "I run lotka.py with parameters and initial conditions", target_fixture="run_result"
)
def run_lotka():
    """Run the script with a non-interactive matplotlib backend for testing."""
    environment = {**os.environ, "MPLBACKEND": "Agg"}
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *PARAMETERS],
        capture_output=True,
        text=True,
        env=environment,
    )


@then("the trajectory plots are generated without an error")
def trajectory_plots_generated(run_result):
    assert run_result.returncode == 0, run_result.stderr


@when("I pass no command line arguments", target_fixture="no_args_result")
def run_lotka_no_args():
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
    )


@then(
    "I see an error message 'Lotka Volterra equations need parameters alpha, beta, gamma, delta and initial conditions x0, y0'"
)
def error_message(no_args_result):
    message = no_args_result.stderr + no_args_result.stdout
    assert (
        "Lotka Volterra equations need parameters alpha, beta, gamma, delta and initial conditions x0, y0"
        in message
    )


@then("the program exits with an error code")
def exit_error(no_args_result):
    assert no_args_result.returncode != 0
