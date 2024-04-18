# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay
from ..utility._csharp_compatibility import _towards_zero_division
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator


class _GJYearMonthDayCalculator(_RegularYearMonthDayCalculator, abc.ABC):
    _NON_LEAP_DAYS_PER_MONTH: Final[list[int]] = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    _LEAP_DAYS_PER_MONTH: Final[list[int]] = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    @staticmethod
    def __generate_total_days_by_month(*month_lengths: int) -> list[int]:
        ret = [0]
        for i in range(len(month_lengths)):
            ret.append(ret[i] + month_lengths[i])
        return ret

    __NON_LEAP_TOTAL_DAYS_BY_MONTH: Final[list[int]] = __generate_total_days_by_month(*_NON_LEAP_DAYS_PER_MONTH)
    __LEAP_TOTAL_DAYS_BY_MONTH: Final[list[int]] = __generate_total_days_by_month(*_LEAP_DAYS_PER_MONTH)

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(min_year, max_year, 12, average_days_per_10_years, days_at_start_of_year_1)

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, d: int) -> _YearMonthDay:
        is_leap: bool = self._is_leap_year(year)

        start_of_month: int
        # Perform a hard-coded binary search to get the 0-based start day of the month. We can
        # then use that to work out the month... without ever hitting the heap. The values
        # are still MinTotalDaysPerMonth and MaxTotalDaysPerMonth (-1 for convenience), just hard-coded.
        if is_leap:
            start_of_month = (
                (0 if d < 32 else 31 if d < 61 else 60)
                if d < 92
                else (91 if d < 122 else 121 if d < 153 else 152)
                if d < 183
                else (182 if d < 214 else 213 if d < 245 else 244)
                if d < 275
                else (274 if d < 306 else 305 if d < 336 else 335)
            )
        else:
            start_of_month = (
                (0 if d < 32 else 31 if d < 60 else 59)
                if d < 91
                else (90 if d < 121 else 120 if d < 152 else 151)
                if d < 182
                else (181 if d < 213 else 212 if d < 244 else 243)
                if d < 274
                else (273 if d < 305 else 304 if d < 335 else 334)
            )

        day_of_month: int = d - start_of_month
        from .._year_month_day import _YearMonthDay

        return _YearMonthDay._ctor(year=year, month=_towards_zero_division(start_of_month, 29) + 1, day=day_of_month)

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self._is_leap_year(year) else 365

    @final
    def _get_days_in_month(self, year: int, month: int) -> int:
        # February is awkward
        if month == 2:
            if self._is_leap_year(year):
                return 29
            return 28
        # The lengths of months alternate between 30 and 31, but skip a beat for August.
        # By dividing the month by 8, we effectively handle that skip.
        return 30 + ((month + (month >> 3)) & 1)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return (
            self.__LEAP_TOTAL_DAYS_BY_MONTH[month]
            if self._is_leap_year(year)
            else self.__NON_LEAP_TOTAL_DAYS_BY_MONTH[month]
        )
