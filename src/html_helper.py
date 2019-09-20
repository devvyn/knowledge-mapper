import xml

import cssselect2
import html5lib

from src import cache


def wrap_tree_cssselect2(tree):
    root = cssselect2.ElementWrapper.from_html_root(tree)
    return root


def get_page_html(page_url):
    page_html = cache.get_page_text_with_cache(page_url)
    return page_html


def parse_html(page_html: str) -> xml.etree.ElementTree:
    return html5lib.parse(page_html)


def fetch_page_etree(page_url) -> xml.etree.ElementTree:
    return parse_html(get_page_html(page_url))


def wrap_etree_cssselect2(page_etree):
    root = cssselect2.ElementWrapper.from_html_root(page_etree)
    return root


def fetch_cssselect2_root(url):
    root = wrap_etree_cssselect2(fetch_page_etree(url))
    return root
