"""
Course data getter. Fetch and parse course descriptions from usask website.
"""
import urllib.parse
from typing import Text, Dict, Any

import html5lib
from cssselect2 import ElementWrapper
from typeguard import typechecked

from devvyn.scrape.parse import find_tag_with_text, clean_whitespace

COURSE_URL = "https://catalogue.usask.ca/"


@typechecked
def get_course_url(course_code: str) -> str:
    """ Course dictionary page URL for given usask course code. """
    return urllib.parse.urljoin(COURSE_URL, course_code.lower())


@typechecked
def course_data(
        description_node: ElementWrapper) -> str:
    """ Text after <b>Prerequisite(s):</b>" in the given parent_node. """
    # @todo:
    #     implement better parsing
    #     conjunctive expression
    #     <subject_code>(<conjunction><subject_code>)*
    #     <subject_code> = (\w+ \d{2,3})
    #     <conjunction> = ( (?:or|and|,) )
    tag = 'b'
    text = "Prerequisite(s):"
    return next(find_tag_with_text(description_node, tag, text))


@typechecked
def parse_course(content: Text) -> Dict[Text, Any]:
    """
    Parse HTML markup of course page.

    :param content:
    :return: dict-like collection of data
    """
    root: ElementWrapper = ElementWrapper.from_html_root(
        html5lib.parse(content))
    description_node = root.query('section#Description'
                                  '>div#Description-subsection-0')
    selector_second_p = 'p:nth-child(2)'
    selector_first_p = 'p:nth-child(1)'
    prerequisites_node: ElementWrapper = description_node.query(selector_second_p)
    node: ElementWrapper = description_node.query(selector_first_p)
    text = node.etree_element.text
    data = generate_mapping(prerequisites_node, text)
    return data


@typechecked
def generate_mapping(prerequisites_node: ElementWrapper, text: str) -> Dict[str, Any]:
    """
    Assemble given data into a mapping collection.
    """
    data = {
        "prerequisites":
            course_data(prerequisites_node),
        "summary":
            clean_whitespace(text),
    }
    return data
