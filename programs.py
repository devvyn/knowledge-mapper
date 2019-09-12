import cssselect2
import lxml.html

from cache import get_page_text_with_cache

DATA_PROGRAMS_LIST_PAGE_URL = "https://programs.usask.ca/programs/list-of-programs.php"


def get_program_dict():
    wrapped_etree = _get_all_links_wrapped()
    unwrapped_etree = _unwrap_etree(wrapped_etree)
    dict_items = _get_link_fields(unwrapped_etree)
    program_dict = _filter_link_fields(dict_items)
    return program_dict


def _get_programs_list_page_tree():
    page_url = DATA_PROGRAMS_LIST_PAGE_URL
    html = get_page_text_with_cache(page_url)
    return lxml.html.fromstring(html)


def _filter_link_fields(dict_items):
    return {
        key: value
        for key, value in dict_items if value[:3] == '../'
    }


def _get_link_fields(unwrapped_etree):
    return (
        (item.text.strip(), item.attrib['href'])
        for item in unwrapped_etree
    )


def _unwrap_etree(wrapped_etree):
    unwrapped_etree = (item.etree_element for item in wrapped_etree)
    return unwrapped_etree


def _get_all_links_wrapped():
    return (
        cssselect2.ElementWrapper.from_html_root(
            _get_programs_list_page_tree()
        ).query_all('li>a')
    )
