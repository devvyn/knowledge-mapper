import urllib.parse
from typing import Any

from typeguard import typechecked

from devvyn.cache.file_cache import FileCache

SEP_DOT: str = '.'  # URL component separator string


@typechecked
def filename_from_url(key: str) -> str:
    """ Parse the URL, concatenate the components, and remove any remaining
    characters not used in URL paths or filenames. This includes most
    non-alphanumeric characters, such as whitespace, most punctuation,
    and all symbols. """
    as_dict = urllib.parse.urlparse(key)._asdict()
    exploded = as_dict.values()
    base_name = SEP_DOT.join(exploded)
    filename = f"{base_name}.html"
    return filename


class WebCache(FileCache):
    """
    A file cache handler which ensures keys are consistently treated as
    unambiguous URLs.
    """

    @typechecked
    def get(self, url: str) -> Any:
        """
        Retrieve content at `key` from cache or web.

        :param url: URL used to load content from cache or fetch content
        from web not found
        :return: content retrieved
        """
        filename = filename_from_url(url)
        return super().get(filename)

    @typechecked
    def set(self, url: str, text: str) -> None:
        """
        Save with the key converted from a URL string to a plain string.

        :param url:
        :param text:
        """
        filename = filename_from_url(url)
        super().set(filename, text)
