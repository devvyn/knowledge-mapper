# language: en
# Created by devvyn-70504 at 2019-09-20
Feature: get course details from individual course details page by course code

  Scenario: course code
    Given a search for course code "BIOL-120"
    Then "summary" is at least 2 words long
    And "BIOL" is in a "prerequisites" field

