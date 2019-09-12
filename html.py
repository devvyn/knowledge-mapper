from typing import Generator, Tuple, Any

import cssselect2
import lxml.html


def _get_all_link_fields(full_etree: lxml.html.etree) -> Generator[Tuple[Any, Any], Any, None]:
    wrapped_links = _get_all_links_wrapped(full_etree)
    unwrapped_links = _unwrap_etree(wrapped_links)
    link_fields = _get_link_fields(unwrapped_links)
    return link_fields


def _get_all_links_wrapped(tree):
    return cssselect2.ElementWrapper.from_html_root(tree).query_all('li>a')


def _unwrap_etree(wrapped_etree):
    unwrapped_etree = (item.etree_element for item in wrapped_etree)
    return unwrapped_etree


def _get_link_fields(unwrapped_etree: lxml.html.etree.ElementTree):
    return (
        (item.text.strip(), item.attrib['href'])
        for item in unwrapped_etree
    )
