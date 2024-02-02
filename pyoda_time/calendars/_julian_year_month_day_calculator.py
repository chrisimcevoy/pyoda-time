# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

from ..utility import _sealed
from ._g_j_year_month_day_calculator import _GJYearMonthDayCalculator


@_sealed
class _JulianYearMonthDayCalculator(_GJYearMonthDayCalculator):
    __AVERAGE_DAYS_PER_10_JULIAN_YEARS: _typing.Final[int] = 3653  # Ideally 365.25 per year

    def __init__(self) -> None:
        super().__init__(-9997, 9998, self.__AVERAGE_DAYS_PER_10_JULIAN_YEARS, -719164)

    def _is_leap_year(self, year: int) -> bool:
        return (year & 3) == 0

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Unix epoch is 1970-01-01 Gregorian which is 1969-12-19 Julian.
        # Calculate relative to the nearest leap year and account for the
        # difference later.

        relative_year = year - 1968
        if relative_year <= 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers.
            leap_years = (relative_year + 3) >> 2
        else:
            leap_years = relative_year >> 2
            # For post 1968 an adjustment is needed as jan1st is before leap day
            if not self._is_leap_year(year):
                leap_years += 1

        # Accounts for the difference between January 1st 1968 and December 19th 1969.
        return relative_year * 365 + leap_years - (366 + 352)
