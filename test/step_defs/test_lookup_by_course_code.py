from pytest_bdd import given, scenario, then
from pytest_bdd.parsers import parse

from courses.courses_by_course_code import fetch_course_details_by_course_code


@scenario('../features/courses_by_course_code.feature',
          'course details by course code')
def test_lookup_by_course_code():
    pass


@given(parse('course code: "{course_code}"'))
def lookup_by_course_code(course_code):
    print(course_code)
    return fetch_course_details_by_course_code(
        course_code=course_code)


@then('"summary" is at least 2 words long')
def summary_length(lookup_by_course_code):
    assert len(lookup_by_course_code['summary'].split()) >= 2


@then(parse('"{subject_code}" is in a "{field_name}" field'))
def prerequisite_membership(lookup_by_course_code,
                            subject_code: str,
                            field_name: str, ):
    assert subject_code in lookup_by_course_code[field_name]
