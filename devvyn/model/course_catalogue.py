"""
Course catalogue model.

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
import re

from devvyn.fetch import get_content
from devvyn.scrape.page.usask.course import get_course_url, parse_course


class Code:
    """ Course code parser. """

    def __init__(self, code: str):
        course_code = parse_course_code(code)
        if not course_code:
            raise ValueError(
                f'`code` value "{code}" is not of format "ABCD-120[.3]" '
                f'or "ABCD 120".')
        groups = course_code.groups()
        self.subject, self.number, self.credit = groups

    def __repr__(self):
        credit = f'.{self.credit}' if self.credit else ''
        return f'{self.subject}-{self.number}{credit}'


class Course:
    """ Course. """

    def __init__(self, code: str):
        self.code = Code(code)


def parse_course_code(code):
    subject_pattern = r'(?P<subject>\w+)'
    credit_pattern = r'(?P<credit>\d)'
    number_pattern = r'(?P<number>\d{2,3})'
    code_pattern = (
        fr'{subject_pattern}[- ]?{number_pattern}'
        fr'(?:(?:[.]){credit_pattern})?')
    r = re.compile(code_pattern)
    return re.match(r, code)


def get_course(course_code: str) -> dict:
    url = get_course_url(course_code)
    content = get_content(url)
    return parse_course(content)