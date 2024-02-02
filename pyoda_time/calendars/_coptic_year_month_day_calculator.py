# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from ._fixed_month_year_month_day_calculator import _FixedMonthYearMonthDayCalculator


class _CopticYearMonthDayCalculator(_FixedMonthYearMonthDayCalculator):
    def __init__(self) -> None:
        super().__init__(1, 9715, -615558)

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Unix epoch is 1970-01-01 Gregorian which is 1686-04-23 Coptic.
        # Calculate relative to the nearest leap year and account for the
        # difference later.

        relative_year = year - 1687
        leap_years: int
        if relative_year <= 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers.
            leap_years = (relative_year + 3) >> 2
        else:
            leap_years = relative_year >> 2
            # For post 1687 an adjustment is needed as jan1st is before leap day
            if not self._is_leap_year(year):
                leap_years += 1

        ret: int = relative_year * 365 + leap_years

        # Adjust to account for difference between 1687-01-01 and 1686-04-23.
        return ret + (365 - 112)
