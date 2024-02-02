# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc as _abc
import typing as _typing

from ..utility import _towards_zero_division
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator

if _typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay


class _FixedMonthYearMonthDayCalculator(_RegularYearMonthDayCalculator, _abc.ABC):
    """Abstract implementation of a year/month/day calculator based around months which always have 30 days.

    As the month length is fixed various calculations can be optimised. This implementation assumes any additional days
    after twelve months fall into a thirteenth month.
    """

    __DAYS_IN_MONTH: _typing.Final[int] = 30

    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = 3653  # Ideally 365.25 days per year...

    def __init__(self, min_year: int, max_year: int, days_at_start_of_year_1: int) -> None:
        super().__init__(min_year, max_year, 13, self.__AVERAGE_DAYS_PER_10_YEARS, days_at_start_of_year_1)

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        # Just inline the arithmetic that would be done via various methods.
        return (
            self._get_start_of_year_in_days(year_month_day._year)
            + (year_month_day._month - 1) * self.__DAYS_IN_MONTH
            + (year_month_day._day - 1)
        )

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return (month - 1) * self.__DAYS_IN_MONTH

    def _is_leap_year(self, year: int) -> bool:
        return (year & 3) == 3

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self._is_leap_year(year) else 365

    def _get_days_in_month(self, year: int, month: int) -> int:
        return self.__DAYS_IN_MONTH if month != 13 else 6 if self._is_leap_year(year) else 5

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        zero_based_day_of_year = day_of_year - 1
        month = _towards_zero_division(zero_based_day_of_year, self.__DAYS_IN_MONTH) + 1
        day = zero_based_day_of_year % self.__DAYS_IN_MONTH + 1
        return _YearMonthDay._ctor(year=year, month=month, day=day)
