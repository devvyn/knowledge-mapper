from pytest_bdd import (given, scenario, then)
from pytest_bdd.parsers import parse

import courses.courses_by_subject


@scenario('../features/courses_by_subject_code.feature',
          'courses under a subject code')
def test_courses_search_by_subject_code():
    pass


@given(parse('search results for subject code {subject_code}'))
def subject_code_search_results(subject_code):
    course_details = (
        courses.courses_by_subject.fetch_course_details_by_subject_code(
            subject_code=subject_code))
    assert isinstance(course_details, dict)
    return course_details


@then(parse("there are at least {quantity} courses"))
def course_list_length(subject_code_search_results, quantity):
    assert len(subject_code_search_results) >= quantity


@then('"summary" is always at least 2 words long')
def summary_length_any(subject_code_search_results):
    print(subject_code_search_results)
    results_list = list((len(result['summary'].split()) for result in
                         subject_code_search_results))
    assert min(results_list) >= 2


@then(parse('"{subject_code}" is in a "{field_name}" field'))
def prerequisite_membership_any(subject_code_search_results: dict,
                                subject_code: str,
                                field_name: str, ):
    subject_code_is_in_each_search_result = (
        subject_code in item[field_name]
        for item in subject_code_search_results
    )
    assert any(subject_code_is_in_each_search_result)
