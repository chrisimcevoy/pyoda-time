# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from .._local_date import LocalDate

from ..utility._csharp_compatibility import _sealed
from ..utility._preconditions import _Preconditions
from ._i_date_period_field import _IDatePeriodField


@_sealed
@final
class _YearsPeriodField(_IDatePeriodField):
    def add(self, local_date: LocalDate, value: int) -> LocalDate:
        from pyoda_time import LocalDate

        if value == 0:
            return local_date
        year_month_day = local_date._year_month_day
        calendar = local_date.calendar
        calculator = calendar._year_month_day_calculator
        current_year = year_month_day._year
        # Adjust argument range based on current year
        _Preconditions._check_argument_range(
            "value", value, calculator._min_year - current_year, calculator._max_year - current_year
        )
        return LocalDate._ctor(
            year_month_day_calendar=calculator._set_year(year_month_day, current_year + value)._with_calendar_ordinal(
                calendar._ordinal
            )
        )

    def units_between(self, start: LocalDate, end: LocalDate) -> int:
        diff: int = end.year - start.year

        # If we just add the difference in years to subtrahendInstant, what do we get?
        simple_addition = self.add(start, diff)

        if start <= end:
            # Moving forward: if the result of the simple addition is before or equal to the end,
            # we're done. Otherwise, rewind a year because we've overshot.
            return diff if simple_addition <= end else diff - 1
        else:
            # Moving backward: if the result of the simple addition (of a non-positive number)
            # is after or equal to the end, we're done. Otherwise, increment by a year because
            # we've overshot backwards.
            return diff if simple_addition >= end else diff + 1
