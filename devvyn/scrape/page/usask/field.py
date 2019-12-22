"""
Scrape data from field pages.
"""
import re
import urllib.parse
from logging import info, basicConfig, INFO
from typing import Tuple, final

import cssselect2
import html5lib
from typeguard import typechecked

from devvyn.fetch import get_content
from devvyn.scrape.page.usask.program_catalogue import program_catalogue_data
from devvyn.scrape.parse import get_href, clean_whitespace


def field_page(level: str, field: str) -> Tuple[str, str]:
    """


    :param level:
    :param field:
    :return:
    """
    url = field_url(level, field)
    content = get_content(url)
    return content, url


def field_url(level: str, field: str) -> str:
    # @todo: move key params into function signature
    return program_catalogue_data()[level][field]


@typechecked
@final
class ScrapeProgramString:
    """ String parsing functions """

    def __init__(self):
        raise NotImplementedError(f"{self.__class__.__name__} is not instantiable.")

    @staticmethod
    def parse_program_string(program: str) -> dict:
        # @todo: implement tests
        # @todo: make resilience against non-matching strings
        long = r'(?P<name_long>.+)'
        short = r'(?: ?\(|, )?' \
                r'(?P<name_short>[^)]+)' \
                r'(?:\))?'
        field = r'(?: - (?P<field_long>.+))?'
        info(f'{program=}')
        return re.match(
            pattern=''.join((long, short, field)),
            string=program,
        ).groupdict()


def program_url(field, level, program):
    content, url = field_page(level, field)
    programs_data = field_data(content, url)
    program_page_url = next(
        (
            url
            for title, url
            in programs_data.items()
            if program in title
        )
    )
    return program_page_url


def field_data(content: str, base_href: str) -> dict:
    """
    Parse field page and return dict-like summary of academic programs.

    :param content:
    :param base_href:
    :return:
    """
    root = cssselect2.ElementWrapper.from_html_root(
        html5lib.parse(content))
    links_selector = 'section#Programs ul>li>a'
    links = root.query_all(links_selector)
    programs_in_subject = {
        clean_whitespace(element.etree_element.text):
            abs_url(base_href, get_href(element))
        for element in links
    }
    return programs_in_subject


def abs_url(base, href):
    return urllib.parse.urljoin(base, href)


if __name__ == '__main__':
    basicConfig(level=INFO)
