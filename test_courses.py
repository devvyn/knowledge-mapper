import courses

URL_SUBJ_CODE_BIOL = 'https://catalogue.usask.ca/?subj_code=BIOL'
COURSE_CODE_BIOL_120 = 'BIOL-120'


def test_courses_single():
    course_details = courses.fetch_course_details_by_course_code(
        COURSE_CODE_BIOL_120)
    assert 'summary' in course_details
    assert len(str(course_details['summary']).split()) > 2
    assert 'prerequisites' in course_details
    assert 'BIOL' in course_details['prerequisites']


def test_course_details_multi():
    course_details = courses.fetch_course_details_by_subject_code(
        URL_SUBJ_CODE_BIOL)
    assert type(course_details) is dict
    assert 'summary' in course_details
    assert len(str(course_details['summary']).split()) > 2
    assert 'prerequisites' in course_details
    assert 'BIOL' in course_details['prerequisites']
