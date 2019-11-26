"""
File-based cache for text retrieved from URL-based resources.
"""
import os
import pathlib
import sys
import typing

from scrape.url import url_to_filename

PATH = typing.Union[str, pathlib.Path]

MODE_WRITE = 'w'
MODE_READ = 'r'

CACHE_PATH: str = './data/'  # relative to working directory


class WebCache:
    """
    A cache handler with get and put methods, and configurable path for
    storage.
    """

    path: PATH

    class MISSING:
        """ Sentry """
        pass

    def __init__(self, cache_dir: PATH = CACHE_PATH) -> None:
        path_resolved: PATH = pathlib.Path(cache_dir).resolve()
        try:
            os.makedirs(path_resolved, exist_ok=True)
        except FileExistsError:
            # if this causes error, there's a file with the same name already
            print(f"File exists at {path_resolved}.", file=sys.stderr)
        if not os.path.isdir(path_resolved):
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

    def get_stored(self, key: str) -> str:
        """
        Get value if key exists.

        :raise KeyError: `key` is not in cache
        """
        path = self.file_path(key)
        try:
            with open(path, MODE_READ) as file:
                result = file.read()
        except FileNotFoundError:
            raise KeyError('Key does not exist: ', key)
        return result

    def get(self, key: str, default: typing.Any = MISSING) -> typing.Any:
        """
        If key exists, return value, otherwise return `default`.

        :param key: key to lookup
        :param default: value to return if `key` doesn't exist
        :return: value stored with `key`
        """
        if not isinstance(key, str):
            raise TypeError(
                f"`key` should be type `str`, but it's `{type(key)}`.")
        try:
            return self.get_stored(key)
        except KeyError:
            if default is not WebCache.MISSING:
                return default
            raise

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


StringFunction = typing.Callable[[str], str]


def cached(function: StringFunction) -> StringFunction:
    """
    Wrap the decorated function in a cache handler.

    :param function: the URL fetch function to wrap
    :return: Wrapped function
    """
    if not callable(function):
        raise TypeError(
            f'`function` is type {type(function)}, but it must be callable.')
    cache = WebCache()

    # define the wrapped function
    def wrapped(key: str) -> str:
        """
        Attempt to get the value stored in `key`, and if the key doesn't
        exist, store it with the value returned from `function` before
        returning it.

        :param key: URL specifying the document location, which also
        identifies the page in the cache
        :return: Page content
        """
        try:
            return cache.get(key)
        except KeyError:
            text = function(key)
            cache.put(key, text)
        return text

    return wrapped
