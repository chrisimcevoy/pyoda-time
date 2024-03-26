# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from .._year_month_day_calendar import _YearMonthDayCalendar

if typing.TYPE_CHECKING:
    from .._local_date import LocalDate

from ..utility._csharp_compatibility import _sealed, _towards_zero_division
from ._i_date_period_field import _IDatePeriodField


@_sealed
@typing.final
class _FixedLengthDatePeriodField(_IDatePeriodField):
    """Date period field for fixed-length periods (weeks and days)."""

    def __init__(self, unit_days: int) -> None:
        self.__unit_days = unit_days

    def add(self, local_date: LocalDate, value: int) -> LocalDate:
        from .. import LocalDate

        if value == 0:
            return local_date
        days_to_add = value * self.__unit_days
        calendar = local_date.calendar
        # If we know it will be in this year, next year, or the previous year...
        if 300 > days_to_add > -300:
            calculator = calendar._year_month_day_calculator
            year_month_day = local_date._year_month_day
            year = local_date.year
            month = local_date.month
            day = local_date.day
            new_day_of_month = day + days_to_add
            if 1 <= new_day_of_month <= calculator._get_days_in_month(year, month):
                return LocalDate._ctor(
                    year_month_day_calendar=_YearMonthDayCalendar._ctor(
                        year=year, month=month, day=new_day_of_month, calendar_ordinal=calendar._ordinal
                    )
                )
            day_of_year = calculator._get_day_of_year(year_month_day)
            new_day_of_year = day_of_year + days_to_add

            if new_day_of_year < 1:
                new_day_of_year += calculator._get_days_in_year(year - 1)
                year -= 1
                if year < calculator._min_year:
                    raise OverflowError("Date computation would underflow the minimum year of the calendar")
            else:
                days_in_year = calculator._get_days_in_year(year)
                if new_day_of_year > days_in_year:
                    new_day_of_year -= days_in_year
                    year += 1
                    if year > calculator._max_year:
                        raise OverflowError("Date computation would overflow the maximum year of the calendar")
            return LocalDate._ctor(
                year_month_day_calendar=calculator._get_year_month_day(
                    year=year, day_of_year=new_day_of_year
                )._with_calendar_ordinal(calendar._ordinal)
            )
        # LocalDate constructor will validate
        days = local_date._days_since_epoch + days_to_add
        return LocalDate._ctor(days_since_epoch=days, calendar=calendar)

    def units_between(self, start: LocalDate, end: LocalDate) -> int:
        from .. import Period

        return _towards_zero_division(Period._internal_days_between(start, end), self.__unit_days)
