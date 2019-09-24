# Created by devvyn-70504 at 2019-09-23
Feature: get course details from list of course details by subject code

  Scenario: subject code
    Given a search for subject code "BIOL"
    Then "summary" is always at least 2 words long
    And "BIOL" is in a "prerequisites" field
    And there are at least 7 courses
