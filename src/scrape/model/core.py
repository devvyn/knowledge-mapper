"""
Unified data model.

Fetches and parses pages to build a dict-like data object.
"""
import collections
from typing import (Any, Iterator, KeysView, ValuesView)

from scrape.model.page.fields_at_levels import get_all_fields


class CourseAndProgramCatalogue(collections.Mapping):
    """
    Represent scraped data, with the root at the list of study levels and
    the leaf nodes as courses
    """
    _map: dict

    def __init__(self) -> None:
        self._map = get_all_fields()

    def keys(self) -> KeysView:
        return self._map.keys()

    def values(self) -> ValuesView:
        return self._map.values()

    def get(self, *args, **kwargs) -> Any:
        return self._map.get(*args, **kwargs)

    def __len__(self) -> int:
        return len(self.keys())

    def __iter__(self) -> Iterator[collections.Hashable]:
        return iter(self.keys())

    def __getitem__(self, k: collections.Hashable) -> Any:
        if not isinstance(k, collections.Hashable):
            raise TypeError(f'"{k:str}" is not hashable')
        return self.get(k)
