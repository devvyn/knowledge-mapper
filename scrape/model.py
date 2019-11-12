"""
Course data getter. Fetch and parse course descriptions from usask website.
"""

from scrape.fetch import get_content
from scrape.parse import (parse_course, parse_fields, parse_programs,
                          parse_requirements)
from scrape.url import get_course_url, get_fields_url, get_programs_url


def get_all_fields() -> dict:
    """
    Academic fields, each having one or more academic program which can be
    retrieved with `get_programs`.
    """
    list_of_programs_page = get_list_of_program_page()
    return parse_fields(**list_of_programs_page)


def get_list_of_program_page() -> dict:
    base_href = get_fields_url()
    content = get_content(base_href)
    return locals()


def get_programs(college, field) -> dict:
    url = get_programs_url(college, field)
    return parse_programs(get_content(url), url)


def program_page_url(field, program):
    program_page_url = f"https://.../{field}/{program}"  # FIXME
    return program_page_url


def get_program_data(field: str, program: str) -> dict:
    url = program_page_url(field, program)
    content = get_content(url)
    return parse_requirements(content)


def get_course(course_code: str) -> dict:
    return parse_course(get_content(get_course_url(course_code)))
