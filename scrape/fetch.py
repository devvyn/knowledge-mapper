from typing import Type

import requests

from scrape.file_cache import get, put

URL: Type[str] = str


def get_content(url: URL) -> str:
    """
    High level getter for web page content. Uses ``cache`` module.

        Fetch content from local cache, if possible;
        fetch from web, if not cached.
    """
    try:
        return get(url)
    except FileNotFoundError:
        return put(url, requests.get(url).text)
