import pathlib
import sys
from os import makedirs
from os.path import isdir
from typing import Union

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

    dir: PATH

    def __init__(self, cache_dir: PATH = CACHE_PATH) -> None:
        resolved_path: PATH = pathlib.Path(cache_dir).resolve()
        try:
            makedirs(resolved_path, exist_ok=True)
        except FileExistsError:
            # if this causes error, there's a file with the same name already
            print(f"File exists at {resolved_path}.", file=sys.stderr)
        if not isdir(resolved_path):
            raise NotADirectoryError(resolved_path)
        self.dir = resolved_path

    def file_path(self, url: str) -> PATH:
        """ Full path for file.
        :param url: A URL, URN, or other string to use as the key for
            storage.
        :return: Path for a hypothetical file corresponding to the local
            storage path plus the file name derived from the key.
        """
        html_file_name: str = url_to_filename(url) + ".html"
        return pathlib.Path(self.dir, html_file_name)

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
