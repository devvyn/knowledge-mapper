import requests

from scrape.file_cache import cached


@cached
def get_content(url: str) -> str:
    return requests.get(url).text
