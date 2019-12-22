"""
Convenience functions for storing text in files in a data directory,
with a `FileCache` class to allow easy saving and loading.
"""
import collections
import os
import sys
from pathlib import Path
from typing import Iterable, Iterator, AbstractSet, Any, Union, Generator

from typeguard import typechecked

PATH = Union[str, Path]
MODE_WRITE = 'w'
MODE_READ = 'r'
CACHE_PATH: str = './data/'  # default (tail to working directory)


@typechecked
def mkdir_path(path: PATH) -> PATH:
    """
    Check validity of the given _path and create an empty directory if one does not already exist.

    :param path: file system _path for cache directory
    :return: absolute _path to valid and ready cache directory
    """

    resolve = Path(path).resolve()
    try:
        resolve.mkdir(parents=True, exist_ok=True)  # don't raise error if directory exists
    except FileExistsError:
        # there's a file with the same name already
        print(f"File exists at {resolve}.", file=sys.stderr)
    if not os.path.isdir(resolve):
        raise NotADirectoryError(resolve)
    return resolve


@typechecked
def dir_path(path: PATH) -> Generator[Path, None, None]:
    """
    Get an iterator of `Path` objects corresponding to the files in the `path` directory.

    :param path:
    :return:
    """
    path = Path(path)
    assert path.is_dir()
    return path.iterdir()


class FileCache(collections.MutableMapping):
    """
    Get and put files on disk in the host file system in the directory given by `path`.
    """
    _path: Path

    def __contains__(self, item):
        return self.path.joinpath(item).is_file()

    def __setitem__(self, key, v) -> None:
        self.save(key, v)

    def __delitem__(self, key) -> None:
        Path(self.path, key).unlink()

    def __getitem__(self, k) -> str:
        return self.get(key=k)

    def __len__(self) -> int:
        return len(dir(self))

    def __dir__(self) -> Iterable[str]:
        return self.keys()

    def keys(self) -> AbstractSet[PATH]:
        return frozenset(dir_path(self.path))

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
        self.path = cache_dir

    @property
    def path(self) -> Path:
        """
        Cache directory path.

        :return:
        """
        return self._path

    @path.setter
    def path(self, cache_dir: PATH) -> None:
        """
        Set the path to the cache directory after resolving, creating, and validating it.

        :param cache_dir:
        :return:
        """
        self._path = mkdir_path(cache_dir)

    @path.deleter
    def path(self) -> None:
        del self._path

    def load(self, key: str) -> str:
        """
        Get value if key exists.

        :raise KeyError: `key` is not in cache
        """
        path = self.path.joinpath(key)
        try:
            result = path.read_text()
        except FileNotFoundError:
            raise KeyError('Key does not exist: ', key)
        return result

    def save(self, key: str, text: str) -> int:
        """
        Write the given text to a file on local storage.

        :param key: The
        :param text:
        :return: The number of bytes written
        """
        path = Path(self.path, key)
        return path.write_text(text)

    class MISSING:
        """ Sentry """
        pass

    @typechecked
    def get(self, key: str) -> Any:
        """
        If key exists, return value.

        :param key: key to data
        :return: value stored with `key`
        """
        if not isinstance(key, str):
            raise TypeError(
                f"`key` should be type `str`, but it's `{type(key)}`.")
        return self.load(key)
