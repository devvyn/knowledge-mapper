import re
from typing import AnyStr, List

import cssselect2
import html5lib

from scrape.url import abs_url, get_course_url


def get_text(node: cssselect2.ElementWrapper) -> str:
    """ Get inner text from parent_node with clean whitespace. """
    return clean_whitespace(node.etree_element.text)


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
        text.strip(),
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
            get_text(description_node.query(selector_first_p)),
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
        if get_text(child_node) == text
    )


def locate_main_results_nodes(cssselect2_root):
    return get_main(cssselect2_root).query_all('h3#results ~ div')


def get_prerequisites(
        description_node: cssselect2.ElementWrapper) -> str:
    """ Text after <b>Prerequisite(s):</b>" in the given parent_node. """
    # @todo:
    #     implement semantic parsing
    #     conjunctive expression
    #     <subject_code>(<conjunction><subject_code>)*
    #     <subject_code> = (\w+ \d{2,3})
    #     <conjunction> = ( (?:or|and|,) )
    tag = 'b'
    text = "Prerequisite(s):"
    return next(find_tag_with_text(description_node, tag, text))


def parse_requirements(content):
    content_root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    selector_section_heading = 'section.uofs-section h1'
    section_headings = content_root.query_all(selector_section_heading)
    return {
        get_text(heading):
            {
                code:
                    get_course_url(code)
                for code in
                (
                    get_text(list_item_node)
                    for list_item_node in
                    query_parent(heading, 'ul>li')
                )
            }
        for heading in section_headings
    }


def query_parent(node, selectors):
    return node.parent.query_all(selectors)


def parse_fields(content, url):
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    section_headers = root.query_all('section.uofs-section h1')
    subjects = {
        get_text(match): {
            get_text(sub_match):
                abs_url(url,
                        get_href(sub_match))
            for sub_match in query_parent(match, 'li>a')}
        for match in section_headers}
    return subjects


def parse_programs(content, base_href):
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    links_selector = 'section#Programs ul>li>a'
    links = root.query_all(links_selector)
    programs_in_subject = {
        get_text(element):
            abs_url(base_href,
                    get_href(element))
        for element in links
    }
    return programs_in_subject


def parse_course(content):
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    description_node = root.query('section#Description'
                                  '>div#Description-subsection-0')
    return description_dict(description_node)


def get_words(text: AnyStr) -> List[AnyStr]:
    """
    Split text by whitespace.

    :param text: Text to split.
    :return: List of words.
    """
    return re.split(r'\s+', text)
