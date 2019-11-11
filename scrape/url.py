import re
import urllib.parse
from typing import Iterable

COURSE_URL = "https://catalogue.usask.ca/"

FIELDS_URL: str = "https://programs.usask.ca/programs/list-of-programs.php"


def abs_url(base: str, relative: str) -> str:
    return urllib.parse.urljoin(base, relative)


def fill_url(url: str) -> str:
    return join(parse_url(url))


def join(exploded: Iterable[str]) -> str:
    return ''.join(exploded)


def parse_url(url):
    # @todo: try to refactor out `_asdict`
    # noinspection PyProtectedMember
    return urllib.parse.urlparse(url)._asdict().values()


def get_course_url(course_code):
    """ Course catalogue page URL for given usask course code. """
    return urllib.parse.urljoin(COURSE_URL, course_code.lower())


def get_programs_url(college, field):
    return f'https://programs.usask.ca/{college}/{field}/index.php'


def get_fields_url():
    return FIELDS_URL


def get_requirements_url(field, program):
    url_map = {
        'Bioinformatics': {
            'Bachelor of Science Four-year (B.Sc. Four-year)':
                ('arts-and-science', 'bioinformatics'),
        }
    }
    base_url = 'https://programs.usask.ca/'
    index_slug = 'index.php'
    college_slug, field_slug = url_map[field][program]
    return f"{base_url}{college_slug}/{field_slug}/{index_slug}"


def strip_invalid_characters(filename: str) -> str:
    return re.sub(r'(?u)[^-\w.]', '', filename)


def get_valid_filename(filename: str) -> str:
    """ Fix invalid filename string by changing or removing characters."""
    return strip_invalid_characters(
        filename.strip().replace(' ', '_'))


def url_to_filename(url: str) -> str:
    return get_valid_filename(
        fill_url(url))