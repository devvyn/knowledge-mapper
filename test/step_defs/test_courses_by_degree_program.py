import itertools

from pytest_bdd import given, scenario, then

import courses.courses_by_course_code

PROGRAM_PAGE_URL_BS4Y_BINF = "https://programs.usask.ca/arts-and-science/" \
                             "bioinformatics/bsc-4-bioinformatics.php"


@scenario('../features/courses_by_degree_program.feature',
          'courses required by degree program',
          example_converters=dict(
              degree_program=str,
              course_code=str,
          ))
def test_courses_by_degree_program():
    pass


@given("the program: <degree_program>")
def courses_by_section(degree_program):
    bs4y_binf = "Bachelor of Science Four-year (B.Sc. Four-year)" \
                " - Bioinformatics"
    if degree_program == bs4y_binf:
        return courses.courses_by_course_code.fetch_courses_by_section(
            PROGRAM_PAGE_URL_BS4Y_BINF)
    else:
        acceptable_values = tuple(bs4y_binf, )
        raise KeyError(f"Degree_program must be one of: {acceptable_values}")


@then("<course_code> is required")
def course_code_is_required(course_code, courses_by_section):
    # collected_values = (*child.values() for child in
    #                     courses_by_section.values())
    collected_values = itertools.chain.from_iterable(
        courses_by_section.values())
    values = list((course_code in value) for value in collected_values)
    assert any(values)
