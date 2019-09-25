# language: en
# Created by devvyn-70504 at 2019-09-24
Feature: programs on subjects

  For any given SUBJECT, all DEGREE PROGRAMS, with corresponding links
  to degree program pages.

  Scenario Outline: degree program names and links
    Given the UofS <study_level> programs for <subject>
    Then there is at least 1 degree program
    And all degree programs have at least 1 link

    Examples:
      | study_level   | subject          |
      | Undergraduate | Bioinformatics   |
      | Undergraduate | Computer Science |
