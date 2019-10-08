# Created by devvyn-70504 at 2019-10-08
Feature: list of courses required by any given program

  Scenario Outline: an expected course code is associated with the program
    Given the <program> program in the field of <field>
    Then <code> is listed as a requirement

    Examples:
      | field          | program                                         | code     |
      | Bioinformatics | Bachelor of Science Four-year (B.Sc. Four-year) | BIOL 120 |
      | Bioinformatics | Bachelor of Science Honours (B.Sc. Honours)     | BIOL 120 |
