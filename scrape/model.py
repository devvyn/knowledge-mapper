"""
Course data getter. Fetch and parse course descriptions from usask website.
"""
from itertools import chain

from scrape.fetch import get_content
from scrape.parse import (parse_course, parse_fields, parse_programs,
                          parse_program)
from scrape.url import get_course_url, get_fields_url


def get_all_fields() -> dict:
    """
    Academic fields grouped by program level, each having one or more
    academic program which can be retrieved with `get_programs`.
    """
    base_href = get_fields_url()
    content = get_content(base_href)
    return parse_fields(content, base_href)


def get_programs(content, base_href) -> dict:
    return parse_programs(content, base_href)


def get_programs_page(level, field):
    url = get_programs_url(level, field)
    content = get_content(url)
    return content, url


def program_page_url(field, program):
    # FIXME: lookup from scraped data instead of faking it
    program_page_url = f"https://.../{field}/{program}"
    return program_page_url


def get_program_data(content: str) -> dict:
    return parse_program(content)


def get_program_page(field, program):
    url = program_page_url(field, program)
    content = get_content(url)
    return content


def get_course(course_code: str) -> dict:
    url = get_course_url(course_code)
    content = get_content(url)
    return parse_course(content)


def get_programs_url(level, field):
    all_fields = get_all_fields()
    return all_fields[level][field]
