import xml.etree

import cssselect2
import html5lib

import cache


def wrap_tree_cssselect2(tree):
    root = cssselect2.ElementWrapper.from_html_root(tree)
    return root


def get_page_html(page_url):
    page_html = cache.get_page_text_with_cache(page_url)
    return page_html


def get_page_etree(page_html: str):
    # return xml.etree.ElementTree.fromstring(page_html)
    return html5lib.parse(page_html)
