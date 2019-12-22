""" Functions for scraping and parsing the program catalogue page for usask. """
import urllib.parse
from typing import Optional, Dict

import cssselect2
import html5lib
from typeguard import typechecked

from devvyn.fetch import get_content
from devvyn.scrape.parse import get_href, clean_whitespace

URL_USASK_PROGRAMS_LIST = "https://programs.usask.ca/programs/list-of-programs.php"


@typechecked
def program_catalogue_data(src: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """
    Academic fields grouped by program level, each having one or more
    academic program which can be retrieved with `get_programs`.
    """
    # @todo: move key params into function signature (see `field.py`)
    if src is None:
        src = URL_USASK_PROGRAMS_LIST
    else:
        src = str(src)
    content = get_content(src)
    return parse_fields(content, src)


@typechecked
def parse_fields(content: str, base_href: str = '') -> Dict[str, Dict[str, str]]:
    """
    Given HTML and base_href, return a nested mapping of course page URLs.

    :param content: HTML of page
    :param base_href: URL of page source
    :return:
    """
    html_root = html5lib.parse(content)
    css_root = cssselect2.ElementWrapper.from_html_root(html_root)
    section_heading_selector = 'section.uofs-section h1'

    data = {
        get_cleaned_text(section): section_data(section, base_href)
        for section in css_root.query_all(section_heading_selector)
    }

    return data


def section_data(section: cssselect2.ElementWrapper, src: str):
    """
    (Temporary) data constructor for the

    :param section:
    :param src:
    :return:
    """
    link_selector = 'li>a'
    data = {
        clean_whitespace(text): urllib.parse.urljoin(src, get_href(link))
        for link in section.parent.query_all(link_selector)
        if (text := link.etree_element.text)
    }
    return data


def get_cleaned_text(node: cssselect2.ElementWrapper):
    """
    Clean text from node by removing all spaces after the first one contiguously.

    :param node:
    :return: element text, extra whitespace removed
    """
    text = node.etree_element.text
    cleaned = clean_whitespace(text)
    return cleaned
