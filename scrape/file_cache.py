import pathlib
import re
from typing import Union

from scrape.url import fill_url

MODE_WRITE = 'w'
MODE_READ = 'r'

CACHE_PATH: str = './data/'  # relative to working directory
PATH = Union[pathlib.Path, str]


def get(key: str):
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
