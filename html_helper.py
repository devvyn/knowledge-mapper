from typing import Generator, Tuple, Any

import cssselect2
import lxml.html
from lxml import html as lxml_html

import cache


def get_all_link_fields(full_etree: lxml.html.etree) -> Generator[Tuple[Any, Any], Any, None]:
    wrapped_links = get_all_links_wrapped(full_etree)
    unwrapped_links = unwrap_etree(wrapped_links)
    link_fields = get_link_fields(unwrapped_links)
    return link_fields


def get_all_links_wrapped(tree):
    return cssselect2.ElementWrapper.from_html_root(tree).query_all('li>a')


def unwrap_etree(wrapped_etree):
    unwrapped_etree = (item.etree_element for item in wrapped_etree)
    return unwrapped_etree


def get_link_fields(unwrapped_etree: lxml.html.etree.ElementTree):
    return (
        (item.text.strip(), item.attrib['href'])
        for item in unwrapped_etree
    )


def get_page_etree(page_url: str) -> lxml_html.etree.ElementTree:
    page_html = cache.get_page_text_with_cache(page_url)
    return lxml_html.fromstring(page_html)


def get_links_from_page(page_url):
    """
    Return sequence of tuples of link text and link href from the HTML document found at the given URL.
    :param page_url:
    :return:
    """

    full_etree = get_page_etree(page_url)
    link_fields = get_all_link_fields(full_etree)
    return link_fields
