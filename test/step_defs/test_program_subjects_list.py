import re

from pytest_bdd import scenario, given, then

from programs import fetch_subjects_by_study_level


@scenario('../features/program_subjects_list.feature', 'get subject list',
          example_converters={
              'study_level': str,
              'subject_count': int,
              'subject': str,
          })
def test_program_subjects_list():
    pass


@given("the UofS program subject list")
def subject_dict() -> dict:
    return fetch_subjects_by_study_level()


@then("there are at least <subject_count> <study_level> subjects")
def subject_count_min(subject_count, study_level, subject_dict):
    assert isinstance(subject_count, int)
    assert len(subject_dict[study_level]) >= subject_count


@then("<subject> is a <study_level> subject")
def subject_is_in_study_level(subject: str, study_level: str,
                              subject_dict: dict, ):
    assert re.sub(r'\s+', ' ', subject) in subject_dict[study_level]
