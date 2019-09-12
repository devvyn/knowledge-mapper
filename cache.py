import re
from pathlib import Path
from urllib.parse import urlparse

import requests

DATA_PATH = Path('./data/')
DATA_PROGRAMS_LIST_PAGE_URL = "https://programs.usask.ca/programs/list-of-programs.php"


def save_text_to_cache(cache_file_path, text):
    with open(cache_file_path, 'w') as f:
        f.write(text)


def get_text_from_cache(cache_file_path):
    with open(cache_file_path) as f:
        text = f.read()
    return text


def get_page_text_with_cache(page_url: str, cache_file_path: str = DATA_PATH) -> str:
    """
    Fetch text from file if it exists, otherwise fetch text from URL and save to file before returning.
    :param page_url: Full URL to page.
    :param cache_file_path: Full path to file.
    :return: Page text.
    """
    path = get_cache_path(cache_file_path, url=DATA_PROGRAMS_LIST_PAGE_URL)
    try:
        text = get_text_from_cache(path)
    except FileNotFoundError:
        text = requests.get(page_url).text
        save_text_to_cache(path, text)
    return text


def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def get_cache_path(cache_file_path, url):
    parse_result = get_valid_filename(''.join(urlparse(url)._asdict().values()))
    file_name = Path(parse_result)
    #
    path = Path(cache_file_path, file_name)
    return path
