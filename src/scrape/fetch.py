import requests

from scrape.file_cache import cached


@cached
def get_content(url: str) -> str:
    """
    Fetch web page content from given URL

    :param url:
    :return:
    """
    return requests.get(url).text
