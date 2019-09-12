from typing import Generator, Tuple, Any

from lxml import html

from cache import get_page_text_with_cache
import html_helper

DATA_PROGRAMS_LIST_PAGE_URL = "https://programs.usask.ca/programs/list-of-programs.php"


def get_program_dict(programs_list_page_url=DATA_PROGRAMS_LIST_PAGE_URL):
    link_fields = get_programs_links(programs_list_page_url)
    program_dict = dict(_filter_link_fields_for_program_url(link_fields))
    return program_dict


def get_programs_links(programs_list_page_url):
    full_etree = _get_programs_list_page_tree(programs_list_page_url)
    link_fields = html_helper.get_all_link_fields(full_etree)
    return link_fields


def _get_programs_list_page_tree(url: str) -> html.etree.ElementTree:
    page_url = url
    page_html = get_page_text_with_cache(page_url)
    return html.fromstring(page_html)


def _filter_link_fields_for_program_url(dict_items) -> Generator[Tuple[Any, Any], Any, None]:
    return ((key, value) for key, value in dict_items if value[:3] == '../')
