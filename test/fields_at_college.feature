# Created by devvyn-70504 at 2019-10-08
Feature: colleges have fields of study

  Scenario Outline:
    Given the college of <college>
    Then the field of <field> is listed

    Examples:
      | college          | field          |
      | Arts and Science | Bioinformatics |
