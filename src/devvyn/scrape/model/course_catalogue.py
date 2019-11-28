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


class Course:
    """ Course in one or more programs. """
    pass
