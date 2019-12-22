"""
File-based cache for text retrieved from URL-based resources.
"""
import typing

from typeguard import typechecked

from devvyn.cache.web_cache import WebCache

StringFunction = typing.Callable[[str], str]


@typechecked
def cached(function: StringFunction) -> StringFunction:
    """
    Wrap the decorated function in a cache handler.

    Example:

    ```
    import requests

    @cached
    def get_content(url: str) -> str:
        return requests.get(url).text

    content_fresh = get_content('https://example.com/')  # save file to cache after fetching
    content_again = get_content('https://example.com/')  # load file from cache instead of fetching
    ```

    :param function: the URL fetch function to wrap
    :return: Wrapped function
    """
    if not callable(function):
        raise TypeError(
            f'`function` is type {type(function)}, but it must be callable.')
    cache = WebCache()

    def wrapped(key: str) -> str:
        """
        Attempt to get the value stored in `key`, and if the key doesn't
        exist, store it with the value returned from `function` before
        returning it.

        :param key: URL specifying the document location, which also
        identifies the page in the cache
        :return: Page content
        """
        try:
            return cache.get(key)
        except KeyError:
            text = function(key)
            cache.save(key, text)
        return text

    return wrapped
