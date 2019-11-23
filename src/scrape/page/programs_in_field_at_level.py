from scrape.fetch import get_content
from scrape.model.core import get_all_fields
from scrape.parse import parse_programs


def get_programs(content, base_href) -> dict:
    return parse_programs(content, base_href)


def get_programs_page(level, field):
    url = get_programs_url(level, field)
    content = get_content(url)
    return content, url


def get_programs_url(level, field):
    all_fields = get_all_fields()
    return all_fields[level][field]
