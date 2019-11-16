"""
File-based cache for text retrieved from URL-based resources.
"""
import pathlib
import sys
from os import makedirs
from os.path import isdir
from typing import Callable, Union

from scrape.url import url_to_filename

PATH = Union[str, pathlib.Path]

MODE_WRITE = 'w'
MODE_READ = 'r'

CACHE_PATH: str = './data/'  # relative to working directory


class WebCache:
    """
    A cache handler with get and put methods, and configurable path for
    storage.
    """

    path: PATH

    def __init__(self, cache_dir: PATH = CACHE_PATH) -> None:
        path_resolved: PATH = pathlib.Path(cache_dir).resolve()
        try:
            makedirs(path_resolved, exist_ok=True)
        except FileExistsError:
            # if this causes error, there's a file with the same name already
            print(f"File exists at {path_resolved}.", file=sys.stderr)
        if not isdir(path_resolved):
            raise NotADirectoryError(path_resolved)
        self.path = path_resolved

    def file_path(self, url: str) -> PATH:
        """ Full path for file.
        :param url: A URL, URN, or other string to use as the key for
            storage.
        :return: Path for a hypothetical file corresponding to the local
            storage path plus the file name derived from the key.
        """
        html_file_name: str = url_to_filename(url) + ".html"
        return pathlib.Path(self.path, html_file_name)

    def get(self, key: str) -> str:
        path = self.file_path(key)
        with open(path, MODE_READ) as file:
            return file.read()

    def put(self, key: str, text: str) -> int:
        """
        Write the given text to a file on local storage.

        :param key: The
        :param text:
        :return: The number of bytes written
        """
        path = self.file_path(key)
        with open(path, MODE_WRITE) as file:
            return file.write(text)


def cached(function: Callable) -> Callable:
    """
    Wrap the decorated function in a cache handler.

    :param function:
    :return:
    """

    cache = WebCache()

    def wrapper(url: str) -> str:
        """
        Attempt cache retrieval before calling the wrapped function to fetch
        the content.

        :param url: URL specifying the document location, which also
            identifies the page in the cache
        :return: Page content
        """
        try:
            result = cache.get(url)
        except FileNotFoundError:
            text = function(url)
            cache.put(url, text)
            result = text
        return result

    return wrapper
