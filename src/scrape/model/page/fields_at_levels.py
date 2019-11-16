from scrape.fetch import get_content
from scrape.parse import parse_fields


def get_all_fields() -> dict:
    """
    Academic fields grouped by program level, each having one or more
    academic program which can be retrieved with `get_programs`.
    """
    base_href = get_fields_url()
    content = get_content(base_href)
    return parse_fields(content, base_href)


FIELDS_URL: str = "https://programs.usask.ca/programs/list-of-programs.php"


def get_fields_url():
    return FIELDS_URL
