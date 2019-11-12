# Created by devvyn-70504 at 2019-10-08
Feature: any given field has one or more programs

  Scenario Outline: an expect program is associated with the field of study
    Given the web page for the list of <level> programs in <field>
    And the list of programs
    Then <program> is listed as a program in <field>

    Examples:
      | level         | field          | program                                                      |
      | Undergraduate | Bioinformatics | Bachelor of Science Honours (B.Sc. Honours) - Bioinformatics |
      | Undergraduate | Biology        | Bachelor of Science Four-year (B.Sc. Four-year) - Biology    |
      | Graduate      | Biology        | Master of Science (M.Sc.)                                    |

