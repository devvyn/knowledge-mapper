import pathlib
import re
import sys
from os import makedirs
from os.path import isdir
from typing import Union

from scrape.url import fill_url

MODE_WRITE = 'w'
MODE_READ = 'r'

CACHE_PATH: str = './data/'  # relative to working directory
PATH = Union[pathlib.Path, str]


def get(key: str) -> str:
    with open(get_cache_path(key), MODE_READ) as f:
        return f.read()


def getdefault(key: str, text: str) -> str:
    with open(get_cache_path(key), MODE_WRITE) as file:
        file.write(text)
    return text


def get_valid_filename(filename: str) -> str:
    """ Fix invalid filename string by changing or removing characters."""
    return strip_invalid_characters(
        replace_spaces(filename))


def get_cache_path(url: str, cache_dir: PATH = CACHE_PATH) -> PATH:
    """ Full path for file. """
    return pathlib.Path(cache_dir, f'{url_to_filename(url)}.html')


def url_to_filename(url: str) -> str:
    return get_valid_filename(
        fill_url(url))


def strip_invalid_characters(filename: str) -> str:
    return re.sub(r'(?u)[^-\w.]', '', filename)


def replace_spaces(string: str) -> str:
    return string.strip().replace(' ', '_')


def init_cache(cache_dir: str) -> str:
    resolved_path = pathlib.Path(cache_dir).resolve()
    try:
        makedirs(resolved_path, exist_ok=True)
    except FileExistsError:
        # if this causes error, there's a file with the same name already
        print(f"File exists at {resolved_path}.", file=sys.stderr)
    if not isdir(resolved_path):
        raise NotADirectoryError(resolved_path)
    return resolved_path


class WebCache:
    dir: Union[str, pathlib.Path]
    def __init__(self, cache_dir: str = CACHE_PATH):
        self.dir = init_cache(cache_dir)

    def get(self, *args, **kwargs):
        return get(*args, **kwargs)

    def getdefault(self, *args, **kwargs):
        return getdefault(*args, **kwargs)

    def get_valid_filename(self, *args, **kwargs):
        return get_valid_filename(*args, **kwargs)

    def get_cache_path(self, *args, **kwargs):
        return get_cache_path(*args, **kwargs)

    def url_to_filename(self, *args, **kwargs):
        return url_to_filename(*args, **kwargs)

    def strip_invalid_characters(self, *args, **kwargs):
        return strip_invalid_characters(*args, **kwargs)

    def replace_spaces(self, *args, **kwargs):
        return replace_spaces(*args, **kwargs)
