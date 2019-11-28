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
from devvyn.scrape.parse import parse_course_code


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


class Course:
    """ Course. """

    def __init__(self, code: str):
        self.code = Code(code)
