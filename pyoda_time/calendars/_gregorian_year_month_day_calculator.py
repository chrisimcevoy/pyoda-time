# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay
from .._year_month_day_calendar import _YearMonthDayCalendar
from ..utility import _towards_zero_division
from ._g_j_year_month_day_calculator import _GJYearMonthDayCalculator


@typing.final
class _GregorianYearMonthDayCalculator(_GJYearMonthDayCalculator):
    _MIN_GREGORIAN_YEAR: typing.Final[int] = -9998
    _MAX_GREGORIAN_YEAR: typing.Final[int] = 9999

    __FIRST_OPTIMIZED_YEAR: typing.Final[int] = 1900
    __LAST_OPTIMIZED_YEAR: typing.Final[int] = 2100
    __FIRST_OPTIMIZED_DAY: typing.Final[int] = -25567
    __LAST_OPTIMIZED_DAY: typing.Final[int] = 47846
    # The 0-based days-since-unix-epoch for the start of each month
    __MONTH_START_DAYS: typing.Final[list[int]] = list(
        range((__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR) * 12 + 1)
    )
    # The 1-based days-since-unix-epoch for the start of each year
    __YEAR_START_DAYS: typing.Final[list[int]] = list(range(__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR))

    __DAYS_FROM_0000_to_1970: typing.Final[int] = 719527
    __AVERAGE_DAYS_PER_10_YEARS: typing.Final[int] = 3652

    @classmethod
    def _get_gregorian_year_month_day_calendar_from_days_since_epoch(
        cls, days_since_epoch: int
    ) -> _YearMonthDayCalendar:
        from .. import CalendarSystem
        from .._calendar_ordinal import _CalendarOrdinal

        # TODO: unchecked
        if days_since_epoch < cls.__FIRST_OPTIMIZED_DAY or days_since_epoch > cls.__LAST_OPTIMIZED_DAY:
            return CalendarSystem.iso._get_year_month_day_calendar_from_days_since_epoch(days_since_epoch)
        # Divide by more than we need to, in order to guarantee that we only need to move forward.
        # We can still only be out by 1 year.
        year_index = _towards_zero_division(days_since_epoch - cls.__FIRST_OPTIMIZED_DAY, 366)
        index_value = cls.__YEAR_START_DAYS[year_index]
        # Zero-based day of year
        d: int = days_since_epoch - index_value
        year: int = year_index + cls.__FIRST_OPTIMIZED_YEAR
        is_leap: bool = cls.__is_gregorian_leap_year(year)
        days_in_year: int = 366 if is_leap else 365
        if d >= days_in_year:
            year += 1
            d -= days_in_year
            is_leap = cls.__is_gregorian_leap_year(year)

        # The remaining code is copied from GJYearMonthDayCalculator (and tweaked)

        start_of_month: int
        # Perform a hard-coded binary search to get the month.
        if is_leap:
            start_of_month = (
                -1
                if d < 31
                else 30
                if d < 60
                else 59
                if d < 91
                else 90
                if d < 121
                else 120
                if d < 152
                else 151
                if d < 182
                else 181
                if d < 213
                else 212
                if d < 244
                else 243
                if d < 274
                else 273
                if d < 305
                else 304
                if d < 335
                else 334
            )
        else:
            start_of_month = (
                -1
                if d < 31
                else 30
                if d < 59
                else 58
                if d < 90
                else 89
                if d < 120
                else 119
                if d < 151
                else 150
                if d < 181
                else 180
                if d < 212
                else 211
                if d < 243
                else 242
                if d < 273
                else 272
                if d < 304
                else 303
                if d < 334
                else 333
            )
        month: int = _towards_zero_division(start_of_month, 29) + 1
        day_of_month: int = d - start_of_month
        return _YearMonthDayCalendar._ctor(
            year=year,
            month=month,
            day=day_of_month,
            calendar_ordinal=_CalendarOrdinal.ISO,
        )

    def __init__(self) -> None:
        super().__init__(
            self._MIN_GREGORIAN_YEAR,
            self._MAX_GREGORIAN_YEAR,
            self.__AVERAGE_DAYS_PER_10_YEARS,
            -719162,
        )

        # TODO: In Noda Time this is inside a static ctor. Perf? Can we do it once?
        for year in range(self.__FIRST_OPTIMIZED_YEAR, self.__LAST_OPTIMIZED_YEAR + 1):
            year_start = self._calculate_start_of_year_days(year)
            self.__YEAR_START_DAYS[year - self.__FIRST_OPTIMIZED_YEAR] = year_start
            month_start_day = year_start - 1
            year_month_index = (year - self.__FIRST_OPTIMIZED_YEAR) * 12
            for month in range(1, 13):
                year_month_index += 1
                month_length = self._get_days_in_month(year, month)
                self.__MONTH_START_DAYS[year_month_index] = month_start_day
                month_start_day += month_length

    def _get_start_of_year_in_days(self, year: int) -> int:
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super()._get_start_of_year_in_days(year)
        return self.__YEAR_START_DAYS[year - self.__FIRST_OPTIMIZED_YEAR]

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        year = year_month_day._year
        month_of_year = year_month_day._month
        day_of_month = year_month_day._day
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super()._get_days_since_epoch(year_month_day)
        year_month_index = (year - self.__FIRST_OPTIMIZED_YEAR) * 12 + month_of_year
        return self.__MONTH_START_DAYS[year_month_index] + day_of_month

    def _calculate_start_of_year_days(self, year: int) -> int:
        leap_years = _towards_zero_division(year, 100)
        if year < 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers. When the expression is written as
            # (year / 4) - (year / 100) + (year / 400),
            # it works for both positive and negative values, except this optimization
            # eliminates two divisions.
            leap_years = ((year + 3) >> 2) - leap_years + ((leap_years + 3) >> 2) - 1
        else:
            leap_years = (year >> 2) - leap_years + (leap_years >> 2)
            if self._is_leap_year(year):
                leap_years -= 1
        return year * 365 + (leap_years - self.__DAYS_FROM_0000_to_1970)

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self.__is_gregorian_leap_year(year) else 365

    def _is_leap_year(self, year: int) -> bool:
        return self.__is_gregorian_leap_year(year)

    @staticmethod
    def __is_gregorian_leap_year(year: int) -> bool:
        return ((year & 3) == 0) and ((year % 100) != 0 or (year % 400) == 0)
