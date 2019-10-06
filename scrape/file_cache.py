import pathlib
import re
from typing import Union

from scrape.fetch import URL
from scrape.url import fill_url

MODE_WRITE = 'w'
MODE_READ = 'r'

CACHE_PATH: str = './data/'  # relative to working directory
PATH = Union[pathlib.Path, str]


def get(key: str):
    with open(get_cache_path(key), MODE_READ) as f:
        return f.read()


def put(key: str, text: str) -> str:
    """
    Caching setter implementation.
    """
    with open(get_cache_path(key), MODE_WRITE) as file:
        file.write(text)
    return text


def get_valid_filename(filename: str) -> str:
    """ Fix invalid filename string by changing or removing characters."""
    return strip_invalid_characters(
        replace_spaces(filename))


def get_cache_path(key: str, cache_dir: PATH = CACHE_PATH) -> PATH:
    return pathlib.Path(cache_dir, get_cache_filename(key))


def get_cache_filename(url: URL) -> str:
    return pathlib.Path(f'{url_to_filename(url)}.html')


def url_to_filename(url: str) -> str:
    return (
        strip_invalid_characters(
            replace_spaces(
                fill_url(
                    url
                )
            )
        )
    )


def strip_invalid_characters(filename: str) -> str:
    return re.sub(r'(?u)[^-\w.]', '', filename)


def replace_spaces(string: str) -> str:
    return string.strip().replace(' ', '_')
