import re
from pathlib import Path
from urllib.parse import urlparse

import requests

DATA_PATH = Path('./data/')


def save_text_to_cache(cache_file_path, text):
    with open(cache_file_path, 'w') as f:
        f.write(text)


def get_text_from_cache(cache_file_path):
    with open(cache_file_path) as f:
        text = f.read()
    return text


def get_page_text_with_cache(page_url: str, cache_dir: str = DATA_PATH) -> str:
    text = get_or_fetch_page_text_via_cache(cache_dir, page_url)
    return text


def get_or_fetch_page_text_via_cache(cache_dir, page_url):
    """
    Fetch text from file if it exists, otherwise fetch text from URL and save to file before returning.
    :param page_url: Full URL to page.
    :param cache_dir: Full path to file.
    :return: Page text.
    """
    path = get_cache_path(cache_dir, url=page_url)
    try:
        text = get_text_from_cache(path)
    except FileNotFoundError:
        text = get_page_text(page_url)  # @todo refactor: decorate around here
        save_text_to_cache(path, text)
    return text


def get_page_text(page_url):  # @todo refactor: decorate this definition with caching wrapper
    # return requests.get(page_url).content  # @todo: try this instead of .text, research benefits
    return requests.get(page_url).text


def get_valid_filename(string: str) -> str:
    string = str(string).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', string)


def get_cache_path(cache_dir: str, url: str) -> Path:
    file_name = f'{url_to_filename(url)}.html'
    path = Path(cache_dir, file_name)
    return path


def url_to_filename(url: str) -> str:
    parse_results = urlparse(url)
    # noinspection PyProtectedMember
    asdict = parse_results._asdict()
    url_segments_joined = ''.join(asdict.values())
    return get_valid_filename(url_segments_joined)
