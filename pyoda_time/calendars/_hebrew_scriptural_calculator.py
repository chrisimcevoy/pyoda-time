# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

from ..utility import _csharp_modulo, _Preconditions, _towards_zero_division
from ._year_start_cache_entry import _YearStartCacheEntry

if _typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay


class _HebrewScripturalCalculator:
    """Implementation of the algorithms described in
    https://www.cs.tau.ac.il/~nachum/calendar-book/papers/calendar.ps, using scriptural
    month numbering.
    """

    _MAX_YEAR: _typing.Final[int] = 9999
    _MIN_YEAR: _typing.Final[int] = 1
    # Use the bottom two bits of the day value to indicate Heshvan/Kislev.
    # Using the top bits causes issues for negative day values (only relevant for
    # invalid years, but still problematic in general).
    __IS_HESHVAN_LONG_CACHE_BIT: _typing.Final[int] = 1 << 0
    __IS_KISLEV_SHORT_CACHE_BIT: _typing.Final[int] = 1 << 1
    # Number of bits to shift the elapsed days in order to get the cache value.
    __ELAPSED_DAYS_CACHE_SHIFT: _typing.Final[int] = 2

    # Cache of when each year starts (in  terms of absolute days). This is the heart of
    # the algorithm, so just caching this is highly effective.
    # Each entry additionally encodes the length of Heshvan and Kislev. We could encode
    # more information too, but those are the tricky bits.
    __YEAR_CACHE: _typing.Final[dict[int, _YearStartCacheEntry]] = _YearStartCacheEntry._create_cache()

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        return ((year * 7) + 1) % 19 < 7

    @classmethod
    def _get_year_month_day(cls, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        # TODO: unchecked

        # Work out everything about the year in one go.
        cache: int = cls.__get_or_populate_cache(year)
        heshvan_length: int = 30 if (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0 else 29
        kislev_length: int = 29 if (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0 else 30
        is_leap: bool = cls._is_leap_year(year)
        first_adar_length = 30 if is_leap else 29

        if day_of_year < 31:
            # Tishri
            return _YearMonthDay._ctor(year=year, month=7, day=day_of_year)
        if day_of_year < 31 + heshvan_length:
            # Heshvan
            return _YearMonthDay._ctor(year=year, month=8, day=day_of_year - 30)
        # Now "day of year without Heshvan"...
        day_of_year -= heshvan_length
        if day_of_year < 31 + kislev_length:
            # Kislev
            return _YearMonthDay._ctor(year=year, month=9, day=day_of_year - 30)
        # Now "day of year without Heshvan or Kislev"...
        day_of_year -= kislev_length
        if day_of_year < 31 + 29:
            # Tevet
            return _YearMonthDay._ctor(year=year, month=10, day=day_of_year - 30)
        if day_of_year < 31 + 29 + 30:
            # Shevat
            return _YearMonthDay._ctor(year=year, month=11, day=day_of_year - (30 + 29))
        if day_of_year < 31 + 29 + 30 + first_adar_length:
            # Adar / Adar I
            return _YearMonthDay._ctor(year=year, month=12, day=day_of_year - (30 + 29 + 30))
        # Now "day of year without first month of Adar"
        day_of_year -= first_adar_length
        if is_leap:
            if day_of_year < 31 + 29 + 30 + 29:
                return _YearMonthDay._ctor(year=year, month=13, day=day_of_year - (30 + 29 + 30))
            # Now "day of year without any Adar"
            day_of_year -= 29
        # We could definitely do a binary search from here, but it would only
        # a few comparisons at most, and simplicity trumps optimization.
        if day_of_year < 31 + 29 + 30 + 30:
            # Nisan
            return _YearMonthDay._ctor(year=year, month=1, day=day_of_year - (30 + 29 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29:
            # Iyar
            return _YearMonthDay._ctor(year=year, month=2, day=day_of_year - (30 + 29 + 30 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30:
            # Sivan
            return _YearMonthDay._ctor(year=year, month=3, day=day_of_year - (30 + 29 + 30 + 30 + 29))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30 + 29:
            # Tamuz
            return _YearMonthDay._ctor(year=year, month=4, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30 + 29 + 30:
            # Av
            return _YearMonthDay._ctor(year=year, month=5, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30 + 29))
        # Elul
        return _YearMonthDay._ctor(year=year, month=6, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30 + 29 + 30))

    @classmethod
    def _get_days_from_start_of_year_to_start_of_month(cls, year: int, month: int) -> int:  # type: ignore[return]
        # Work out everything about the year in one go. (Admittedly we don't always need it all... but for
        # anything other than Tishri and Heshvan, we at least need the length of Heshvan...)

        # TODO: unchecked

        cache: int = cls.__get_or_populate_cache(year)
        heshvan_length = 30 if (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0 else 29
        kislev_length = 29 if (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0 else 30
        is_leap = cls._is_leap_year(year)
        first_adar_length = 30 if is_leap else 29
        second_adar_length = 29 if is_leap else 0
        match month:
            case 1:  # Nisan
                return 30 + heshvan_length + kislev_length + (29 + 30) + first_adar_length + second_adar_length
            case 2:  # Iyar
                return 30 + heshvan_length + kislev_length + (29 + 30) + first_adar_length + second_adar_length + 30
            case 3:  # Sivan
                return (
                    30 + heshvan_length + kislev_length + 29 + 30 + first_adar_length + second_adar_length + (30 + 29)
                )
            case 4:  # Tamuz
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30)
                )
            case 5:  # Av
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30 + 29)
                )
            case 6:  # Elul
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30 + 29 + 30)
                )
            case 7:  # Tishri
                return 0
            case 8:  # Heshvan
                return 30
            case 9:  # Kislev
                return 30 + heshvan_length
            case 10:  # Tevet
                return 30 + heshvan_length + kislev_length
            case 11:  # Shevet
                return 30 + heshvan_length + kislev_length + 29
            case 12:  # Adar / Adar I
                return 30 + heshvan_length + kislev_length + 29 + 30
            case 13:  # Adar II
                return 30 + heshvan_length + kislev_length + 29 + 30 + first_adar_length

        _Preconditions._throw_argument_out_of_range_exception("month", month, 1, 13)

    @classmethod
    def _days_in_month(cls, year: int, month: int) -> int:
        match month:
            case 2 | 4 | 6 | 10 | 13:
                return 29
            case 8:
                return 30 if cls.__is_heshvan_long(year) else 29
            case 9:
                return 29 if cls.__is_kislev_short(year) else 30
            case 12:
                return 30 if cls._is_leap_year(year) else 29
            case _:  # 1, 3, 5, 7, 11
                return 30

    @classmethod
    def __is_heshvan_long(cls, year: int) -> bool:
        cache: int = cls.__get_or_populate_cache(year)
        return (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0

    @classmethod
    def __is_kislev_short(cls, year: int) -> bool:
        cache: int = cls.__get_or_populate_cache(year)
        return (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0

    @classmethod
    def _elapsed_days(cls, year: int) -> int:
        cache: int = cls.__get_or_populate_cache(year)
        return cache >> cls.__ELAPSED_DAYS_CACHE_SHIFT

    @classmethod
    def __elapsed_days_no_cache(cls, year: int) -> int:
        months_elapsed: int = (
            # Months in complete cycles so far
            (235 * _towards_zero_division((year - 1), 19))
            # Regular months in this cycle
            + (12 * _csharp_modulo((year - 1), 19))
            # Leap months this cycle
            + (_towards_zero_division(_csharp_modulo((year - 1), 19) * 7 + 1, 19))
        )
        # Second option in the paper, which keeps values smaller
        parts_elapsed: int = 204 + (793 * _csharp_modulo(months_elapsed, 1080))
        hours_elapsed: int = (
            5
            + (12 * months_elapsed)
            + (793 * _towards_zero_division(months_elapsed, 1080))
            + _towards_zero_division(parts_elapsed, 1080)
        )
        day: int = 1 + (29 * months_elapsed) + _towards_zero_division(hours_elapsed, 24)
        parts: int = (_csharp_modulo(hours_elapsed, 24) * 1080) + _csharp_modulo(parts_elapsed, 1080)
        postpone_rosh_ha_shanah: bool = (
            (parts >= 19440)
            or (_csharp_modulo(day, 7) == 2 and parts >= 9924 and not cls._is_leap_year(year))
            or (_csharp_modulo(day, 7) == 1 and parts >= 16789 and cls._is_leap_year(year - 1))
        )
        alternative_day: int = 1 + day if postpone_rosh_ha_shanah else day
        alternative_day_mod_7: int = _csharp_modulo(alternative_day, 7)
        return alternative_day + 1 if alternative_day_mod_7 in (0, 3, 5) else alternative_day

    @classmethod
    def __get_or_populate_cache(cls, year: int) -> int:
        """Returns the cached "elapsed day at start of year / IsHeshvanLong / IsKislevShort" combination, populating the
        cache if necessary.

        Bits 2-24 are the "elapsed days start of year"; bit 0 is "is Heshvan long"; bit 1 is "is Kislev short". If the
        year is out of the range for the cache, the value is populated but not cached.
        """
        if year < cls._MIN_YEAR or year > cls._MAX_YEAR:
            return cls.__compute_cache_entry(year)
        cache_index: int = _YearStartCacheEntry._get_cache_index(year)
        cache_entry: _YearStartCacheEntry = cls.__YEAR_CACHE[cache_index]
        if not cache_entry._is_valid_for_year(year):
            days: int = cls.__compute_cache_entry(year)
            cache_entry = _YearStartCacheEntry(year, days)
            cls.__YEAR_CACHE[cache_index] = cache_entry
        return cache_entry._start_of_year_days

    @classmethod
    def __compute_cache_entry(cls, year: int) -> int:
        """Computes the cache entry value for the given year, but without populating the cache."""
        days: int = cls.__elapsed_days_no_cache(year)
        # We want the elapsed days for the next year as well. Check the cache if possible.
        next_year = year + 1
        next_year_days: int
        if next_year < cls._MAX_YEAR:
            cache_index: int = _YearStartCacheEntry._get_cache_index(next_year)
            cache_entry: _YearStartCacheEntry = cls.__YEAR_CACHE[cache_index]
            next_year_days = (
                cache_entry._start_of_year_days >> cls.__ELAPSED_DAYS_CACHE_SHIFT
                if cache_entry._is_valid_for_year(next_year)
                else cls.__elapsed_days_no_cache(next_year)
            )
        else:
            next_year_days = cls.__elapsed_days_no_cache(year + 1)
        days_in_year = next_year_days - days
        is_heshvan_long = _csharp_modulo(days_in_year, 10) == 5
        is_kislev_short = _csharp_modulo(days_in_year, 10) == 3
        return (
            (days << cls.__ELAPSED_DAYS_CACHE_SHIFT)
            | (cls.__IS_HESHVAN_LONG_CACHE_BIT if is_heshvan_long else 0)
            | (cls.__IS_KISLEV_SHORT_CACHE_BIT if is_kislev_short else 0)
        )

    @classmethod
    def _days_in_year(cls, year: int) -> int:
        return cls._elapsed_days(year + 1) - cls._elapsed_days(year)
