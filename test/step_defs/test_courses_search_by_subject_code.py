from pytest_bdd import (
    scenario,
    given,
    then,
    parsers,
)

from courses import courses_by_subject


@scenario('../features/courses_by_subject_code.feature',
          'courses under a subject code')
def test_courses_search_by_subject_code():
    pass


@given(parsers.parse('a search for subject code "{subject_code}"'))
def subject_code_search_results(subject_code):
    return courses_by_subject.fetch_course_details_by_subject_code(
        subject_code=subject_code)


@then("there are at least 7 courses")
def course_list_length(subject_code_search_results):
    assert len(subject_code_search_results) >= 7


@then('"summary" is always at least 2 words long')
def summary_length_any(subject_code_search_results):
    results_ = list((len(result['summary'].split()) for result in
                     subject_code_search_results))
    assert min(results_) >= 2


@then(parsers.parse('"{subject_code}" is in a "{field_name}" field'))
def prerequisite_membership_any(subject_code_search_results: dict,
                                subject_code: str,
                                field_name: str, ):
    assert subject_code in subject_code_search_results[0][field_name]
