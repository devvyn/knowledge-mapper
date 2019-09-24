# Created by devvyn-70504 at 2019-09-24
Feature: programs by subject
  For any given subject, a list of degree programs,
  with corresponding links.

  Scenario Outline: degree program names and links
    Given the UofS program list for <study_level> <subject>
    Then there is at least 1 degree program link

    Examples:
      | study_level   | subject          |
      | Undergraduate | Bioinformatics   |
      | Undergraduate | Computer Science |
