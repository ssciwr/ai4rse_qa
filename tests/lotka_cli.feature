Feature: Run the Lotka-Volterra model from the command line
  As a researcher
  I want to run the Lotka-Volterra model from a terminal
  So that I can inspect its results without writing Python code

  Scenario: Run with parameters and initial conditions
    Given valid model parameters and initial populations as command-line arguments
    When I run the Lotka-Volterra command-line application
    Then the trajectory plot and phase plot are shown

  Scenario: Run without command-line input
    Given no model parameters or initial populations as command-line arguments
    When I run the Lotka-Volterra command-line application
    Then the default model parameters and initial populations are used
    And the trajectory plot and phase plot are shown
