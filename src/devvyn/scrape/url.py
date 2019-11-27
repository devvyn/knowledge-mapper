import re
import urllib.parse

COURSE_URL = "https://catalogue.usask.ca/"


def abs_url(base: str, relative: str) -> str:
    return urllib.parse.urljoin(base, relative)


def get_course_url(course_code):
    """ Course catalogue page URL for given usask course code. """
    return urllib.parse.urljoin(COURSE_URL, course_code.lower())


def get_requirements_url(field, program):
    url_map = {
        "Bioinformatics": {
            "Bachelor of Science Four-year (B.Sc. Four-year)":
                ('arts-and-science', 'bioinformatics'),
        }
    }
    base_url = 'https://programs.usask.ca/'  # @todo: move to usask module
    index_slug = 'index.php'
    college_slug, field_slug = url_map[field][program]
    return f'{base_url}{college_slug}/{field_slug}/{index_slug}'


def url_to_filename(url: str) -> str:
    """ Parse the URL, concatenate the components, and remove any remaining
    characters not used in URL paths or filenames. This includes most
    non-alphanumeric characters, such as whitespace, most punctuation,
    and all symbols. """

    asdict = urllib.parse.urlparse(url)._asdict()
    exploded = asdict.values()
    filename = ''.join(exploded)
    return re.sub(r'(?u)[^-\w.]', '', filename)
