# language: en
# Created by devvyn-70504 at 2019-09-24
Feature: courses required by degree programs

  All COURSES required by a DEGREE PROGRAM.

  Scenario Outline: courses required by degree program
  For a given degree program, I want to see the course codes
  for all the courses required by a degree program.

    Given the program: <degree_program>
    Then <course_code> is required

    Examples:
      | degree_program                                                   | course_code |
      | Bachelor of Science Four-year (B.Sc. Four-year) - Bioinformatics | BIOL 120.3  |
      | Bachelor of Science Four-year (B.Sc. Four-year) - Bioinformatics | MATH 110.3  |
