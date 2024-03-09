# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from .._local_date import LocalDate

from ..utility import _sealed
from ._i_date_period_field import _IDatePeriodField


@_sealed
@typing.final
class _MonthsPeriodField(_IDatePeriodField):
    def add(self, local_date: LocalDate, value: int) -> LocalDate:
        from pyoda_time import LocalDate

        calendar = local_date.calendar
        calculator = calendar._year_month_day_calculator
        year_month_day = calculator._add_months(local_date._year_month_day, value)
        return LocalDate._ctor(year_month_day_calendar=year_month_day._with_calendar(calendar))

    def units_between(self, start: LocalDate, end: LocalDate) -> int:
        return start.calendar._year_month_day_calculator._months_between(start._year_month_day, end._year_month_day)
