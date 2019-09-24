# Created by devvyn-70504 at 2019-09-24
Feature: list of subjects
  Programs grouped by subject, with URLs

  Scenario Outline: get subject list
    Given the UofS program subject list
    Then there are at least <subject_count> <study_level> subjects
    And <subject> is a <study_level> subject

    Examples:
      | study_level             | subject_count | subject                         |
      | Undergraduate           | 130           | Bioinformatics                  |
      | Graduate                | 90            | Biostatistics                   |
      | Non-degree Certificates | 2             | Certificate in Dental Assisting |
