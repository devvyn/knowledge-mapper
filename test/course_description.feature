# Created by devvyn-70504 at 2019-10-07
Feature: course descriptions
  Retrieve course descriptions.

  Scenario: course descriptions have a summary
    Given the description of CMPT-270
    Then there is a summary
    And the summary is more than just a few words
