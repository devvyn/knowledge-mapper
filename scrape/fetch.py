from typing import Type

import requests

from scrape.file_cache import get, getdefault, WebCache


def get_content(url: str) -> str:
    """
    High level getter for web page content. Uses ``cache`` module.

        Fetch content from local cache, if possible;
        fetch from web, if not cached.
    """
    cache = WebCache()
    try:
        return cache.get(url)
    except FileNotFoundError:
        return cache.getdefault(url, requests.get(url).text)
