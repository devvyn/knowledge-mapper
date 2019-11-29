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

from devvyn.scrape.model.course_catalogue import Code


class TestCourseCode:

    def test_course_parse_code_invalid(self):
        with pytest.raises(ValueError):
            assert str(Code(code='PSY')) != 'PSY'

    def test_course_parse_code_full_hyphen(self):
        code = Code(code='PSY-120.3')
        assert str(code) == 'PSY-120.3'
        assert str(code.subject) == 'PSY'
        assert int(code.number) == 120
        assert int(code.credit) == 3

    def test_course_parse_code_full_space(self):
        code = Code(code='PSY 120.3')
        assert str(code) == 'PSY-120.3'
        assert str(code.subject) == 'PSY'
        assert int(code.number) == 120
        assert int(code.credit) == 3

    def test_course_parse_code_partial(self):
        code = Code(code='PSY-120')
        assert str(code) == 'PSY-120'
        assert str(code.subject) == 'PSY'
        assert int(code.number) == 120
        assert code.credit is None
