"""
Tests for course catalogue model.

The model must be able to:

- Find official course description online, given only a course code.
- Understand course codes in various formats:
  - PSY 120
  - PSY-120
  - PSY 120.3
  - PSY-120.3
- Parse course prerequisite descriptions, producing:
  - list of course codes mentioned
  - remaining content fragments that could not be parsed
"""
import pytest

from devvyn.scrape.model.course_catalogue import Course


class TestCourseCode:

    def test_course_parse_code_invalid(self):
        with pytest.raises(ValueError):
            assert Course(code='PSY').code != 'PSY'

    def test_course_parse_code_full_hyphen(self):
        course = Course(code='PSY-120.3')
        assert str(course.code) == 'PSY-120.3'
        assert str(course.code.subject) == 'PSY'
        assert int(course.code.number) == 120
        assert int(course.code.credit) == 3

    def test_course_parse_code_full_space(self):
        course = Course(code='PSY 120.3')
        assert str(course.code) == 'PSY-120.3'
        assert str(course.code.subject) == 'PSY'
        assert int(course.code.number) == 120
        assert int(course.code.credit) == 3

    def test_course_parse_code_partial(self):
        course = Course(code='PSY-120')
        assert str(course.code) == 'PSY-120'
        assert str(course.code.subject) == 'PSY'
        assert int(course.code.number) == 120
        assert course.code.credit is None
