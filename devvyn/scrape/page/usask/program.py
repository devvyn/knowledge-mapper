""" Scrape program page for course data. """
from typing import Generator, Any

import cssselect2
import html5lib
from cssselect2 import ElementWrapper
from typeguard import typechecked

from devvyn.fetch import get_content
from devvyn.scrape.page.usask.course import get_course_url
from devvyn.scrape.page.usask.field import program_url
from devvyn.scrape.parse import clean_whitespace


def program_page(program: str, field: str, level: str) -> str:
    """
    For given program, return the content of the program's page in the
    course catalogue. Lookup is done on data returned by sibling methods
    until a match is found, or the search is exhausted.

    :param program: Program name
    :param field: Field of study
    :param level: Level of study (Undergraduate, Graduate, Non-degree)
    :return: HTML content from first found page
    """
    # FIXME circular import!
    program_page_url = program_url(field, level, program)
    content = get_content(program_page_url)
    return content


def parse_program(content: str) -> dict:
    """
    Parse HTML content and return a dict-like collection of data.

    :param content:
    :return: dict of course names and course data
    """
    content_root = cssselect2.ElementWrapper.from_html_root(html5lib.parse(content))
    selector_section_heading = 'section.uofs-section h1'
    section_headings = content_root.query_all(selector_section_heading)
    return {
        clean_whitespace(heading.etree_element.text): course_dict(heading)
        for heading in section_headings
    }


@typechecked
def course_dict(heading: cssselect2.ElementWrapper) -> dict:
    """
    Collect course codes and page URLs from the parent of the given node.

    :param heading:
    :return:
    """
    parent = heading.parent
    selector = 'ul>li'
    return {
        code: get_course_url(code)
        for code in course_codes(parent, selector)
    }


@typechecked
def course_codes(parent: ElementWrapper, selector: str) -> Generator[str, Any, None]:
    """
    Generate course code strings from elements in given node.

    :param parent:
    :param selector:
    :return:
    """
    query: ElementWrapper = parent.query_all(selector)
    children: Generator[str, Any, None] = (
        clean_whitespace(list_item_node.etree_element.text)
        for list_item_node in query
    )
    return children
