from pytest_bdd import (
    scenario,
    given,
    then,
    parsers,
)

import courses


@scenario('../features/courses_search_by_course_code.feature', 'course code')
def test_courses_search_by_course_code():
    pass


@given(parsers.parse('a search for course code "{course_code}"'))
def course_code_search_results(course_code):
    return courses.fetch_course_details_by_course_code(course_code=course_code)


@then('"summary" is at least 2 words long')
def summary_length(course_code_search_results):
    assert len(course_code_search_results['summary'].split()) >= 2


@then(parsers.parse('"{subject_code}" is in a "{field_name}" field'))
def prerequisite_membership(course_code_search_results: dict,
                            subject_code: str,
                            field_name: str, ):
    assert subject_code in course_code_search_results[field_name]
