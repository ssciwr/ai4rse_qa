Feature: solve_lotkavolterra
  As a researcher
  I want to pass parameters and initial conditions to lotka.py
  So that I see trajectory plots of the Lotka-Volterra solution

  Scenario: single parameter input produces trajectory plot
    Given the lotka script accepts command line arguments alpha, beta, gamma, delta, x0, y0
    When I run lotka.py with parameters and initial conditions
    Then the trajectory plots are generated without an error

  Scenario: no parameters or initial conditions passed as input
    Given the lotka script accepts command line arguments alpha, beta, gamma, delta, x0, y0
    When I pass no command line arguments
    Then I see an error message 'Lotka Volterra equations need parameters alpha, beta, gamma, delta and initial conditions x0, y0'
    And the program exits with an error code
