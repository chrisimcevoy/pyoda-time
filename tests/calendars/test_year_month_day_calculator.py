# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import itertools
from typing import Final

import pytest

from pyoda_time.calendars import (
    HebrewMonthNumbering,
    IslamicEpoch,
    IslamicLeapYearPattern,
    _CopticYearMonthDayCalculator,
    _GregorianYearMonthDayCalculator,
    _HebrewYearMonthDayCalculator,
    _IslamicYearMonthDayCalculator,
    _JulianYearMonthDayCalculator,
    _PersianYearMonthDayCalculator,
    _UmAlQuraYearMonthDayCalculator,
    _YearMonthDayCalculator,
)

NON_ISLAMIC_CALCULATORS: Final[list[_YearMonthDayCalculator]] = [
    _GregorianYearMonthDayCalculator(),
    _CopticYearMonthDayCalculator(),
    _JulianYearMonthDayCalculator(),
    _HebrewYearMonthDayCalculator(HebrewMonthNumbering.CIVIL),
    _HebrewYearMonthDayCalculator(HebrewMonthNumbering.SCRIPTURAL),
    _PersianYearMonthDayCalculator.Simple(),
    _PersianYearMonthDayCalculator.Arithmetic(),
    _PersianYearMonthDayCalculator.Astronomical(),
    _UmAlQuraYearMonthDayCalculator(),
]

ISLAMIC_CALCULATORS: Final[list[_YearMonthDayCalculator]] = [
    _IslamicYearMonthDayCalculator(leap_year_pattern=leap_year_pattern, epoch=epoch)
    for epoch, leap_year_pattern in itertools.product(IslamicEpoch, IslamicLeapYearPattern)
]

ALL_CALCULATORS: Final[list[_YearMonthDayCalculator]] = NON_ISLAMIC_CALCULATORS + ISLAMIC_CALCULATORS


class TestYearMonthDayCalculator:
    @pytest.mark.parametrize("calculator", ALL_CALCULATORS, ids=lambda x: x.__class__.__name__)
    def test_validate_start_of_year_1_days(self, calculator: _YearMonthDayCalculator) -> None:
        if calculator._min_year > 1 or calculator._max_year < 0:
            return
        assert calculator._get_start_of_year_in_days(1) == calculator._days_at_start_of_year_1

    @pytest.mark.parametrize("calculator", ALL_CALCULATORS)
    def test_get_year_consistent_with_get_year_days(self, calculator: _YearMonthDayCalculator) -> None:
        for year in range(calculator._min_year, calculator._max_year + 1):
            start_of_year_days = calculator._get_start_of_year_in_days(year)
            got_year, day_of_year = calculator._get_year(start_of_year_days)
            assert got_year == year, f"Start of year {year}"
            assert day_of_year == 0  # Zero-based...
            got_year, day_of_year = calculator._get_year(start_of_year_days - 1)
            assert got_year == year - 1, f"End of year {year - 1}"
            assert calculator._get_days_in_year(year - 1) - 1 == day_of_year
