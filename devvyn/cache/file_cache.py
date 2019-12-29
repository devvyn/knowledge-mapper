"""
Convenience functions for storing text in files in a data directory,
with a `FileCache` class to allow easy saving and loading.
"""
import collections
import os
import re
import sys
from pathlib import Path
from typing import AbstractSet, Any, Generator, Iterable, Iterator, Union

from typeguard import typechecked

PATH = Union[str, Path]
MODE_WRITE = 'w'
MODE_READ = 'r'
CACHE_PATH: str = './data/'  # default (tail to working directory)


@typechecked
def mkdir_path(path: PATH) -> Path:
    """
    Check validity of the given path and create an empty directory if one
    does not already exist.

    :param path: file system path for cache directory
    :return: absolute path to valid and ready cache directory
    """

    resolve = Path(path).resolve()
    try:
        resolve.mkdir(parents=True,
                      exist_ok=True)  # don't raise error if directory exists
    except FileExistsError:
        # there's a file with the same name already
        print(f"File exists at {resolve}.", file=sys.stderr)
    if not os.path.isdir(resolve):
        raise NotADirectoryError(resolve)
    return resolve


@typechecked
def dir_path(path: PATH) -> Generator[Path, None, None]:
    """
    Get an iterator of `Path` objects corresponding to the files in the
    `path` directory.

    :param path:
    :return:
    """
    path = Path(path)
    assert path.is_dir()
    return path.iterdir()


class FileCache(collections.MutableMapping):
    """
    Get and put files on disk in the host file system in the directory given
    by `path`.
    """
    _root: Path

    def __contains__(self, item):
        return self.file_path(item).is_file()

    def file_path(self, item: PATH) -> Path:
        return self.root.joinpath(item)

    def __setitem__(self, key, v) -> None:
        self.save(key, v)

    def __delitem__(self, key) -> None:
        Path(self.root, key).unlink()

    def __getitem__(self, k) -> str:
        """
        Mimic the `__getitem__` method of built-in `dict`.

        :param k: Key
        :raises KeyError: if key does not exist
        :return: Stored value
        """
        try:
            return self.load(k)
        except KeyError:
            raise

    def __len__(self) -> int:
        return len(dir(self))

    def __dir__(self) -> Iterable[str]:
        return self.keys()

    def keys(self) -> AbstractSet[PATH]:
        return frozenset(dir_path(self.root))

    def values(self) -> Generator[str, Any, None]:
        values_generator = (
            Path(filename).read_text()
            for filename in self.keys()
        )
        return values_generator

    def __iter__(self) -> Iterator:
        return iter(dir(self))

    def __init__(self, cache_dir: PATH = CACHE_PATH) -> None:
        """
        Set the storage directory to `cache_dir`.

        :param cache_dir:
        """
        self.root = cache_dir

    @property
    def root(self) -> Path:
        """
        Cache directory path.

        :return:
        """
        return self._root

    @root.setter
    @typechecked
    def root(self, cache_dir: PATH) -> None:
        """
        Set the path to the cache directory after resolving, creating,
        and validating it.

        :param cache_dir:
        :return:
        """
        self._root = mkdir_path(cache_dir)

    @root.deleter
    def root(self) -> None:
        del self._root

    @typechecked
    def load(self, key: str) -> str:
        """
        Get value if key exists.

        :raise KeyError: `key` is not in cache
        """
        path = self.file_path(key)
        try:
            result = path.read_text()
        except FileNotFoundError:
            raise KeyError('Key does not exist: ', key)
        return result

    @typechecked
    def save(self, filename: str, text: str) -> int:
        """
        Write the given text to a file on local storage in the current root.

        :return: The number of bytes written
        """
        file_path = self.file_path(filename)
        return file_path.write_text(text)

    @typechecked
    def set(self, key: str, text: str) -> None:
        """ Store the text in the file cache under the given key. """
        filename = sanitize_filename(key)
        self[filename] = text

    class MISSING:
        """ Sentry """

    @typechecked
    def get(self, key: str) -> Any:
        """
        Given key is normalized and if normalized match exists, return
        stored value.

        :raises KeyError: if key does not exist
        """
        try:
            return self[key]
        except KeyError:
            raise


@typechecked
def sanitize_filename(filename: str) -> str:
    """
    Make the given string into a filename by removing
    non-descriptive characters.

    :param filename:
    :return:
    """
    return re.sub(r'(?u)[^-\w.]', '', filename)
