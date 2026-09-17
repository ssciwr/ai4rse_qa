Feature: Solve the Lotka-Volterra equations
  As a researcher
  I want to solve the Lotka-Volterra equations for chosen parameters and initial conditions
  So that I can analyse the prey and predator populations over time

  Scenario: Solve with valid parameters and initial conditions
    Given valid model parameters and initial prey and predator populations
    When I solve the Lotka-Volterra equations for a requested number of time points
    Then I receive one prey value and one predator value for every requested time point
    And the first values equal the supplied initial populations

  Scenario: Reject negative inputs
    Given a negative model parameter or initial population
    When I try to solve the Lotka-Volterra equations
    Then a value error is raised explaining that inputs must be non-negative
