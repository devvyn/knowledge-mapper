from scrape.fetch import get_content
from scrape.parse import parse_fields


def get_all_fields(src: str = None) -> dict:
    """
    Academic fields grouped by program level, each having one or more
    academic program which can be retrieved with `get_programs`.
    """
    if src is None:
        base_href = get_fields_url()
    else:
        base_href = str(src)
    content = get_content(base_href)
    return parse_fields(content, base_href)


def get_fields_url():
    fields_url: str = "https://programs.usask.ca/programs/list-of-programs.php"
    return fields_url
