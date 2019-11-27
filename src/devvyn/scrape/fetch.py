""" Over-the-wire retrieval of data. """
import requests

from devvyn.cache import cached


@cached
def get_content(url: str) -> str:
    """
    Fetch web page content from given URL.

    :param url:
    :return:
    """
    # @todo: use standard library instead of `requests`
    return requests.get(url).text
