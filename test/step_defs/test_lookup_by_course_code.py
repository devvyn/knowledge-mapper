from pytest_bdd import given, scenario, then
from pytest_bdd.parsers import parse

from courses.courses_by_course_code import fetch_course_details_by_course_code


@scenario('../features/courses_by_course_code.feature',
          'course details by course code')
def test_lookup_by_course_code():
    pass


@given(parse('the lookup for course code "{course_code}"'))
def lookup_by_course_code(course_code):
    print(course_code)
    return fetch_course_details_by_course_code(
        course_code=course_code)


@then(parse('the "{field_name}" text is at least {quantity:d} words long'))
def word_count_in_field(lookup_by_course_code, field_name, quantity):
    text = lookup_by_course_code[field_name]
    assert isinstance(text, str)
    word_list = text.split()
    assert len(word_list) >= quantity


@then(parse('"{subject_code}" is in a "{field_name}" field'))
def prerequisite_membership(lookup_by_course_code,
                            subject_code: str,
                            field_name: str, ):
    assert subject_code in lookup_by_course_code[field_name]
