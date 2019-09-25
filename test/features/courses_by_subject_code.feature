# language: en
# Created by devvyn-70504 at 2019-09-23
Feature: courses under a subject code

  Get course DETAILS from list of COURSES by SUBJECT CODE.

  Scenario: courses under a subject code
    Given a search for subject code "BIOL"
    Then "summary" is always at least 2 words long
    And "BIOL" is in a "prerequisites" field
    And there are at least 7 courses
