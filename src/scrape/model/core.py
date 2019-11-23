"""
Unified data model.

Fetches and parses pages to build a dict-like data object.
"""
import collections
from typing import (Any, Iterator, KeysView, ValuesView)


class SourceMapping(collections.MappingView):
    """ Immutable dictionary view of data structure with a source URL for
    the root. """
    data: dict = {}
    src: str = None

    def __init__(self: object, src: str = None, ):
        if src is None:
            raise TypeError(src)
        self.src = str(src)

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

    def get(self, *args, **kwargs) -> Any:
        """
        Get data value by key.

        :param k: Key to look for.
        :param default: Value to return if key is not found.
        :return: Value.
        :raises KeyError: if `k` is not found and no `default` value is
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


class NamedSource(SourceMapping):
    """ Generic web-based data source, with a name for the root. """
    name: str = None

    def __init__(self: object, name: str = None, src: str = None) -> None:
        super().__init__(src)
        if name is None:
            raise TypeError(name)
        self.name = str(name)
