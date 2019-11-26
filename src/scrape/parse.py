""" Parse strings. """
import re
from typing import Any, Dict, List, Text, Type

import cssselect2
import html5lib

from scrape.url import abs_url, get_course_url


def get_clean_text(node: cssselect2.ElementWrapper) -> str:
    """ Get inner text from parent_node with clean whitespace. """
    text = get_text(node)
    clean_text = clean_whitespace(text)
    return clean_text


def get_text(node: cssselect2.ElementWrapper) -> str:
    """ Get inner text from parent_node with clean whitespace. """
    text = node.etree_element.text
    return text


def get_href(node: cssselect2.ElementWrapper) -> str:
    """ Get the href attribute of parent_node. """
    return get_attrib(node, 'href')


def get_attrib(node: cssselect2.ElementWrapper, attribute: str) -> str:
    """ Get the value of the specified attribute from the parent_node. """
    return node.etree_element.attrib[attribute]


def get_main(root: cssselect2.ElementWrapper) -> cssselect2.ElementWrapper:
    """ Get the main content parent_node from the given root. """
    selector = '[role="main"]'
    return root.query(selector)


def clean_whitespace(text: str) -> str:
    """
    Replace all contiguous whitespace with single space character,
    strip leading and trailing whitespace.
    """
    return re.sub(
        r'\s+',
        ' ',
        (text or '').strip(),
    )


def description_dict(description_node: cssselect2.ElementWrapper) -> dict:
    """
    Parse data fields from the given course description parent_node of a usask
    course catalogue page.
    """
    selector_second_p = 'p:nth-child(2)'
    selector_first_p = 'p:nth-child(1)'
    prerequisites_node = description_node.query(selector_second_p)
    return {
        "prerequisites":
            get_prerequisites(prerequisites_node),
        "summary":
            get_clean_text(description_node.query(selector_first_p)),
    }


def find_tag_with_text(node, tag, text):
    """
    Find all child elements with tag name, and return elements with
    specified text.
    """
    return (
        child_node.etree_element.tail
        for child_node
        in node.query_all(tag)
        if get_clean_text(child_node) == text
    )


def locate_main_results_nodes(cssselect2_root):
    return get_main(cssselect2_root).query_all('h3#results ~ div')


def get_prerequisites(
        description_node: cssselect2.ElementWrapper) -> str:
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


def parse_program(content):
    content_root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    selector_section_heading = 'section.uofs-section h1'
    section_headings = content_root.query_all(selector_section_heading)
    return {
        get_clean_text(heading): course_dict(heading)
        for heading in section_headings
    }


def course_dict(heading: cssselect2.ElementWrapper) -> dict:
    return {
        code: get_course_url(code)
        for code in (
            get_clean_text(list_item_node)
            for list_item_node in heading.parent.query_all('ul>li')
        )
    }


GROUPED_URL_DICT: Type = Dict[str, Dict[str, str]]


def parse_fields(content: str = None, base_href: str = '') -> GROUPED_URL_DICT:
    """
    Given HTML and base_href, return a nested mapping of course page URLs.

    :param content: HTML of page
    :param base_href: URL of page source
    :return:
    """
    html_root = html5lib.parse(content)
    css_root = cssselect2.ElementWrapper.from_html_root(html_root)
    section_heading_selector = 'section.uofs-section h1'
    sections = css_root.query_all(section_heading_selector)
    link_selector = 'li>a'
    subjects = {
        get_clean_text(section): {
            get_clean_text(sub_match): abs_url(base_href, get_href(sub_match))
            for sub_match in section.parent.query_all(link_selector)
            if get_text(sub_match)}
        for section in sections
    }
    return subjects


def parse_programs(content, base_href):
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    links_selector = 'section#Programs ul>li>a'
    links = root.query_all(links_selector)
    programs_in_subject = {
        get_clean_text(element):
            abs_url(base_href, get_href(element))
        for element in links
    }
    return programs_in_subject


def parse_course(content: Text) -> Dict[Text, Any]:
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    description_node = root.query('section#Description'
                                  '>div#Description-subsection-0')
    return description_dict(description_node)


def get_words(text: Text) -> List[Text]:
    """
    Split text by whitespace.

    :param text: Text to split.
    :return: List of words.
    """
    return re.split(r'\s+', text)


def get_program_data(content: str) -> dict:
    return parse_program(content)
