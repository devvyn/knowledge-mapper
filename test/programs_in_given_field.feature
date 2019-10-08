# Created by devvyn-70504 at 2019-10-08
Feature: any given field has one or more programs

  Scenario Outline: an expect program is associated with the field of study
    Given the field of <field> at the college of <college>
    Then <program> is listed as a program

    Examples:
      | college          | field          | program                                     |
      | Arts and Science | Bioinformatics | Bachelor of Science Honours (B.Sc. Honours) |
