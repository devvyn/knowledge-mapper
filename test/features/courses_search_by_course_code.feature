# language: en
# Created by devvyn-70504 at 2019-09-20
Feature: course details are indexed by course code

  Scrape course details from an INDIVIDUAL course details page,
  and confirm that usable data can be extracted.

  The scraped page is found by COURSE CODE.

  Scenario: course details by course code
    Given a search for course code "BIOL-120"
    Then "summary" is at least 2 words long
    And "BIOL" is in a "prerequisites" field
