"""
Unified data model.

Fetches and parses pages to build a dict-like data object.
"""
import collections
from dataclasses import dataclass
from typing import (Any, Iterator, KeysView, ValuesView, ItemsView, ClassVar)


@dataclass
class SourceMapping(collections.MappingView):
    """ Immutable dictionary view of data structure with a source URL for
    the root. The `src` parameter is required because `data` may be generated
    after initialization."""

    src: str
    data: ClassVar[dict] = {}

    def keys(self) -> KeysView:
        """
        Keys from data.

        :return: KeysView
        """
        return self.data.keys()

    def values(self) -> ValuesView:
        """
        Values from data.

        :return: ValuesView
        """
        return self.data.values()

    def items(self) -> ItemsView:
        """
        Get key, value tuples from data.

        :return: ItemsView
        """
        return self.data.items()

    def get(self, *args, **kwargs) -> Any:
        """
        Get data value by key.

        :param k: Key to look for.
        :param default: Value to return if key is not found.
        :return: Value.
        :raises KeyError: if `key` is not found and no `default` value is
            provided.
        """
        return self.data.get(*args, **kwargs)

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> Iterator[collections.Hashable]:
        return iter(self.keys())

    def __getitem__(self, k: collections.Hashable) -> Any:
        if not isinstance(k, collections.Hashable):
            raise TypeError(f'"{k:repr}" is not hashable')
        return self.get(k)

    def __repr__(self) -> str:
        return repr(self.data)


@dataclass
class NamedSource(SourceMapping):
    """ Generic web-based data source, with a name for the root. """
    name: str
