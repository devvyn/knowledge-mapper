"""
Course data getter. Fetch and parse course descriptions from usask website.
"""
from devvyn.scrape.fetch import get_content
from devvyn.scrape.parse import parse_course
from devvyn.scrape.url import get_course_url


def get_course(course_code: str) -> dict:
    url = get_course_url(course_code)
    content = get_content(url)
    return parse_course(content)