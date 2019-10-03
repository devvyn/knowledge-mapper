from pytest_bdd import given, scenario, then

from subjects import fetch_subjects_by_study_level


@scenario('../features/subjects_by_study_level.feature',
          'subjects by study level',
          example_converters={
              'study_level': str,
              'subject_count': int,
              'subject': str,
          })
def test_program_subjects_list():
    pass


@given("the UofS program subject list for <study_level>")
def subjects(study_level: str) -> dict:
    assert isinstance(study_level, str)
    subjects_dict = fetch_subjects_by_study_level()
    assert isinstance(subjects_dict, dict)
    return subjects_dict[study_level]


@then("there are at least <subject_count> subjects")
def subject_count_min(subject_count, subjects):
    assert isinstance(subject_count, int)
    assert len(subjects) >= subject_count


@then("<subject> is a <study_level> subject")
def subject_is_in_study_level(subject, subjects, study_level):
    assert isinstance(subject, str)
    assert subject in subjects
