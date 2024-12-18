# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from collections import deque
from collections.abc import Callable
from threading import Lock
from typing import Final, Generic, TypeVar, final

from pyoda_time.utility._csharp_compatibility import _sealed

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")


@_sealed
@final
class _Cache(Generic[TKey, TValue]):
    """Implements a thread-safe cache with a single computation function.

    For simplicity's sake, eviction is currently on a least-recently-added basis (not LRU). This may change in the
    future.
    """

    # TODO: IEqualityComparer?
    def __init__(self, size: int, value_factory: Callable[[TKey], TValue]) -> None:
        self.__size: Final[int] = size
        self.__value_factory: Final[Callable[[TKey], TValue]] = value_factory
        self.__lock: Final[Lock] = Lock()
        self.__key_list: Final[deque[TKey]] = deque()  # For eviction tracking
        self.__dictionary: Final[dict[TKey, TValue]] = {}  # Main storage

    def get_or_add(self, key: TKey) -> TValue:
        """Fetches a value from the cache, populating it if necessary.

        :param key: Key to fetch
        :return: The value associated with the key.
        """
        with self.__lock:
            if key in self.__dictionary:
                return self.__dictionary[key]
            # If not in the dictionary, prepare to add it
            self.__key_list.append(key)
            if key not in self.__dictionary:  # Check again to avoid race conditions
                self.__dictionary[key] = self.__value_factory(key)

            # Evict if necessary
            while len(self.__dictionary) > self.__size:
                evict_key = self.__key_list.popleft()
                if evict_key in self.__dictionary:
                    del self.__dictionary[evict_key]

            return self.__dictionary[key]

    def count(self) -> int:
        """Returns the number of entries currently in the cache, primarily for diagnostic purposes."""
        with self.__lock:
            return len(self.__dictionary)

    def keys(self) -> list[TKey]:
        """Returns a copy of the keys in the cache as a list, for diagnostic purposes."""
        with self.__lock:
            return list(self.__dictionary.keys())

    def clear(self) -> None:
        """Clears the cache.

        This is never surfaced publicly (directly or indirectly) - it's just for testing.
        """
        with self.__lock:
            self.__key_list.clear()
            self.__dictionary.clear()
