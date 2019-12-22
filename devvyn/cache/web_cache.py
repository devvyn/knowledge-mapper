import re
import urllib.parse
from typing import Any

from typeguard import typechecked

from devvyn.cache.file_cache import FileCache


class WebCache(FileCache):
    """
    A file cache handler which ensures keys are consistently treated as unambiguous URLs.
    """

    @typechecked
    def get(self, key: str) -> Any:
        """
        Retrieve content at `key` from cache or web.

        :param key: URL used to load content from cache or fetch content from web
        :param default: value to return instead of fetching content if `key` not found
        :return: content retrieved, or `default` if provided and key not found
        """
        html_filename: str = url_to_filename(key) + ".html"
        return super().get(html_filename)


@typechecked
def url_to_filename(url: str) -> str:
    """ Parse the URL, concatenate the components, and remove any remaining
    characters not used in URL paths or filenames. This includes most
    non-alphanumeric characters, such as whitespace, most punctuation,
    and all symbols. """

    as_dict = urllib.parse.urlparse(url)._asdict()
    exploded = as_dict.values()
    filename = ''.join(exploded)
    return re.sub(r'(?u)[^-\w.]', '', filename)
