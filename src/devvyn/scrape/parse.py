""" Parse strings. """
import logging
import re
from typing import List, Text, Any, Generator

import cssselect2
from typeguard import typechecked


@typechecked
def get_href(node: cssselect2.ElementWrapper) -> str:
    """ Get the href attribute of parent_node. """
    return get_attrib(node, 'href')


@typechecked
def get_attrib(node: cssselect2.ElementWrapper, attribute: str) -> str:
    """ Get the value of the specified attribute from the parent_node. """
    return node.etree_element.attrib[attribute]


@typechecked
def get_main(root: cssselect2.ElementWrapper) -> cssselect2.ElementWrapper:
    """ Get the ARIA main content node from the given root. """
    selector = '[role="main"]'
    # todo: what if there are multiple nodes?
    return root.query(selector)


@typechecked
def clean_whitespace(text: str) -> str:
    """
    Replace all contiguous whitespace with single space character,
    strip leading and trailing whitespace.
    """
    text = str(text or '')
    stripped = text.strip()
    sub = re.sub(r'\s+', ' ', stripped, )
    return sub


@typechecked
def find_tag_with_text(node: cssselect2.ElementWrapper, tag: str, text: str) -> Generator[Any, str, None]:
    """
    Find all child elements with tag name, and return elements with
    specified text.
    """
    return (
        child_node.etree_element.tail
        for child_node
        in node.query_all(tag)
        if clean_whitespace(child_node.etree_element.text) == text
    )


@typechecked
def get_words(text: Text) -> List[Text]:
    """
    Split text by whitespace.

    :param text: Text to split.
    :return: List of words.
    """
    return re.split(r'\s+', text)


