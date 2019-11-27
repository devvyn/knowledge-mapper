from scrape.cache import WebCache
from scrape.parse import parse_course, parse_fields


def test_parse_course():
    cache_instance = WebCache()
    url = ...
    content: str = cache_instance.get_stored(url)
    expected = [...]
    actual = parse_course(content)
    assert False


def test_parse_fields():
    # @todo: copy example to dedicated testing directory

    # get already cached content
    cache_instance = WebCache()
    list_of_programs_url = "https://" \
                           "programs.usask.ca" \
                           "/programs/list-of-programs.php"
    content: str = cache_instance.get_stored(list_of_programs_url)
    expected = [...]
    actual = parse_fields(content=content)
    assert False
