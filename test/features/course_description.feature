# Created by devvyn-70504 at 2019-10-07
Feature: course descriptions
  Retrieve course descriptions.

  Scenario: CMPT-270 has the expected prerequisites
    Given the description of CMPT-270
    Then there is a prerequisites field
    And the prerequisites include CMPT 115
    And the prerequisites include MATH 110
