"""
Course data getter. Fetch and parse course descriptions from usask website.
"""
import itertools
from typing import Iterable

from scrape.fetch import get_content
from scrape.parse import (parse_course, parse_program, parse_programs,
                          parse_fields)
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


def program_page_url(program):
    all_fields: dict = get_all_fields()
    sections_children: Iterable[dict] = itertools.chain.from_iterable(
        all_fields.values())
    fields_list = (
        value
        for program_pages in sections_children
        for key, value in program_pages.items()
        if key == program
    )
    return next(fields_list)


def get_program_data(content: str) -> dict:
    return parse_program(content)


def get_program_page(program: str) -> str:
    """
    For given program, return the content of the program's page in the
    course catalogue.

    :param program: Program name
    :return:
    """
    url = program_page_url(program)
    content = get_content(url)
    return content


def get_course(course_code: str) -> dict:
    url = get_course_url(course_code)
    content = get_content(url)
    return parse_course(content)


def get_programs_url(level, field):
    all_fields = get_all_fields()
    return all_fields[level][field]
