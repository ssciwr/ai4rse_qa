Feature: Plot a Lotka-Volterra solution
  As a researcher
  I want to visualize a Lotka-Volterra solution
  So that I can inspect the population trajectories and their phase relationship

  Scenario: Plot a non-empty solution
    Given a non-empty Lotka-Volterra solution with time, prey, and predator values
    When I create the trajectory plot and phase plot
    Then the prey and predator trajectories are plotted against time
    And the predator population is plotted against the prey population

  Scenario: Reject empty solution data
    Given empty time, prey, and predator data
    When I try to create the trajectory plot or phase plot
    Then a value error is raised explaining that the solution data must not be empty
