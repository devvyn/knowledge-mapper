"""
Course data getter. Fetch and parse course descriptions from usask website.
"""

from scrape.fetch import get_content
from scrape.parse import (parse_course, parse_fields, parse_programs,
                          parse_requirements)
from scrape.url import get_course_url, get_fields_url, get_programs_url


def get_fields() -> dict:
    url = get_fields_url()
    return parse_fields(get_content(url), url)


def get_programs(college, field) -> dict:
    url = get_programs_url(college, field)
    return parse_programs(get_content(url), url)


def get_requirements(program_page_url: str) -> dict:
    return parse_requirements(get_content(program_page_url))


def get_course(course_code: str) -> dict:
    return parse_course(get_content(get_course_url(course_code)))
