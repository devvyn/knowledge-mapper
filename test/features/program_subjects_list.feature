# language: en
# Created by devvyn-70504 at 2019-09-24
Feature: subjects within study levels

  For any given STUDY LEVEL (Undergraduate, etc.), all degree program
  SUBJECTS, with links to degree program pages.

  Scenario Outline: degree program subject list
    Given the UofS program subject list for <study_level>
    Then <subject> is a <study_level> subject
    And there are at least <min_subject_count> subjects

    Examples:
      | study_level             | subject                         | min_subject_count |
      | Undergraduate           | Bioinformatics                  | 130               |
      | Graduate                | Biostatistics                   | 90                |
      | Non-degree Certificates | Certificate in Dental Assisting | 2                 |
