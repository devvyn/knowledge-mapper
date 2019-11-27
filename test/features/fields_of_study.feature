# Created by devvyn-70504 at 2019-10-08
Feature: all fields of study
  Get names and URLs of program fields

  Scenario Outline:
    Given the web page for the list of all programs
    Given the list of all programs
    Then the field of <field> is listed under <level>

    Examples:
      | level         | field             |
      | Graduate      | Biology           |
      | Graduate      | Chemistry         |
      | Graduate      | Computer Science  |
      | Undergraduate | Astronomy         |
      | Undergraduate | Bioinformatics    |
      | Undergraduate | Biology           |
      | Undergraduate | Business          |
      | Undergraduate | Chemistry         |
      | Undergraduate | Civil Engineering |
      | Undergraduate | Computer Science  |
      | Undergraduate | Geology           |
      | Undergraduate | Linguistics       |
      | Undergraduate | Mathematics       |