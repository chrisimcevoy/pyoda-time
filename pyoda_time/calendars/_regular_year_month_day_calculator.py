# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay
from ..utility._csharp_compatibility import _towards_zero_division
from ._year_month_day_calculator import _YearMonthDayCalculator


class _RegularYearMonthDayCalculator(_YearMonthDayCalculator, abc.ABC):
    """Subclass of YearMonthDayCalculator for calendars with the following attributes:
    - A fixed number of months
    - Occasional leap years which are always 1 day longer than non-leap years
    - The year starting with month 1, day 1 (i.e. naive YearMonthDay comparisons work)
    """

    def __init__(
        self,
        min_year: int,
        max_year: int,
        months_in_year: int,
        aveage_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(min_year, max_year, aveage_days_per_10_years, days_at_start_of_year_1)
        self.__months_in_year = months_in_year

    def _get_months_in_year(self, year: int) -> int:
        return self.__months_in_year

    def _set_year(self, year_month_day: _YearMonthDay, year: int) -> _YearMonthDay:
        """Implements a simple year-setting policy, truncating the day if necessary."""
        # If this ever becomes a bottleneck due to GetDaysInMonth, it can be overridden in subclasses.
        current_month: int = year_month_day._month
        current_day: int = year_month_day._day
        new_day: int = self._get_days_in_month(year, current_month)
        from .._year_month_day import _YearMonthDay

        return _YearMonthDay._ctor(year=year, month=current_month, day=min(current_day, new_day))

    def _add_months(self, year_month_day: _YearMonthDay, months: int) -> _YearMonthDay:
        if months == 0:
            return year_month_day
        # Get the year and month
        this_year = year_month_day._year
        this_month = year_month_day._month

        # Do not refactor without careful consideration.
        # Order of calculation is important.

        year_to_use: int
        # Initially, monthToUse is zero-based
        month_to_use = this_month - 1 + months
        if month_to_use >= 0:
            year_to_use = this_year + _towards_zero_division(month_to_use, self.__months_in_year)
            month_to_use = (month_to_use % self.__months_in_year) + 1
        else:
            year_to_use = this_year + _towards_zero_division(month_to_use, self.__months_in_year) - 1
            month_to_use = abs(month_to_use)
            rem_month_to_use = month_to_use % self.__months_in_year
            # Take care of the boundary condition
            if rem_month_to_use == 0:
                rem_month_to_use = self.__months_in_year
            month_to_use = self.__months_in_year - rem_month_to_use + 1
            # Take care of the boundary condition
            if month_to_use == 1:
                year_to_use += 1
        # End of do not refactor

        # Quietly force DOM to nearest sane value.
        day_to_use = year_month_day._day
        max_day = self._get_days_in_month(year_to_use, month_to_use)
        day_to_use = min(day_to_use, max_day)
        if (year_to_use < self._min_year) or (year_to_use > self._max_year):
            raise OverflowError("Date computation would overflow calendar bounds.")
        from .._year_month_day import _YearMonthDay

        return _YearMonthDay._ctor(year=year_to_use, month=month_to_use, day=day_to_use)

    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        start_month: int = start._month
        start_year: int = start._year
        end_month: int = end._month
        end_year: int = end._year

        diff: int = (end_year - start_year) * self.__months_in_year + end_month - start_month

        # If we just add the difference in months to start, what do we get?
        simple_addition: _YearMonthDay = self._add_months(start, diff)

        # Note: this relies on naive comparison of year/month/date values.
        if start <= end:
            # Moving forward: if the result of the simple addition is before or equal to the end,
            # we're done. Otherwise, rewind a month because we've overshot.
            return diff if simple_addition <= end else diff - 1
        else:
            # Moving backward: if the result of the simple addition (of a non-positive number)
            # is after or equal to the end, we're done. Otherwise, increment by a month because
            # we've overshot backwards.
            return diff if simple_addition >= end else diff + 1
