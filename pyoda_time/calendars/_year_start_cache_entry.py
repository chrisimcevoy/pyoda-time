# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Final


class _YearStartCacheEntry:
    """Type containing as much logic as possible for how the cache of "start of year" data works."""

    __CACHE_INDEX_BITS: Final[int] = 10
    __CACHE_SIZE: Final[int] = 1 << __CACHE_INDEX_BITS
    __CACHE_INDEX_MASK: Final[int] = __CACHE_SIZE - 1
    __ENTRY_VALIDATION_BITS: Final[int] = 7
    __ENTRY_VALIDATION_MASK: Final[int] = (1 << __ENTRY_VALIDATION_BITS) - 1
    _INVALID_ENTRY_YEAR: Final[int] = (__ENTRY_VALIDATION_MASK >> 1) << __CACHE_INDEX_BITS

    def __init__(self, year: int, days: int) -> None:
        self.__value = (days << self.__ENTRY_VALIDATION_BITS) | self.__get_validator(year)

    @classmethod
    def __get_validator(cls, year: int) -> int:
        """Returns the validator to use for a given year, a non-negative number containing at most
        __ENTRY_VALIDATION_BITS bits."""
        return (year >> cls.__CACHE_INDEX_BITS) & cls.__ENTRY_VALIDATION_MASK

    @classmethod
    def _get_cache_index(cls, year: int) -> int:
        """Returns the cache index, in [0, CacheSize), that should be used to store the given year's cache entry."""
        return year & cls.__CACHE_INDEX_MASK

    @classmethod
    def _create_cache(cls) -> dict[int, _YearStartCacheEntry]:
        cache = {i: _YearStartCacheEntry.__invalid() for i in range(cls.__CACHE_SIZE)}
        return cache

    @classmethod
    def __invalid(cls) -> _YearStartCacheEntry:
        """Entry which is guaranteed to be obviously invalid for any real date, by having a validation value which is
        larger than any valid year number."""
        return _YearStartCacheEntry(cls._INVALID_ENTRY_YEAR, 0)

    def _is_valid_for_year(self, year: int) -> bool:
        """Returns whether this cache entry is valid for the given year, and so is safe to use.

        (We assume that we have located this entry via the correct cache index.)
        """
        return self.__get_validator(year) == (self.__value & self.__ENTRY_VALIDATION_MASK)

    @property
    def _start_of_year_days(self) -> int:
        """Returns the (signed) number of days since the Unix epoch for the cache entry."""
        return self.__value >> self.__ENTRY_VALIDATION_BITS
