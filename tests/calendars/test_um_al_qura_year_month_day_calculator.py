# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time._year_month_day import _YearMonthDay
from pyoda_time.calendars import _UmAlQuraYearMonthDayCalculator


class TestUmAlQuraYearMonthDayCalculator:
    # TODO: test_bcl_equivalence(self) [requires bcl]

    # TODO def test_get_start_of_year_in_days(self) -> None: [requires bcl]

    def test_get_year_month_day_days_since_epoch(self) -> None:
        calculator = _UmAlQuraYearMonthDayCalculator()
        days_since_epoch = calculator._get_start_of_year_in_days(calculator._min_year)
        for year in range(calculator._min_year, calculator._max_year + 1):
            for month in range(1, 13):
                for day in range(1, calculator._get_days_in_month(year, month) + 1):
                    actual = calculator._get_year_month_day(days_since_epoch=days_since_epoch)
                    expected = _YearMonthDay._ctor(year=year, month=month, day=day)
                    assert actual == expected, f"{days_since_epoch=}"
                    days_since_epoch += 1

    def test_get_year_month_day_year_and_day_of_year(self) -> None:
        calculator = _UmAlQuraYearMonthDayCalculator()
        for year in range(calculator._min_year, calculator._max_year + 1):
            day_of_year = 1
            for month in range(1, 13):
                for day in range(1, calculator._get_days_in_month(year, month) + 1):
                    actual = calculator._get_year_month_day(year=year, day_of_year=day_of_year)
                    expected = _YearMonthDay._ctor(year=year, month=month, day=day)
                    assert actual == expected, f"{year=}, {day_of_year=}"
                    day_of_year += 1

    def test_get_days_from_start_of_year_to_start_of_month(self) -> None:
        calculator = _UmAlQuraYearMonthDayCalculator()
        for year in range(calculator._min_year, calculator._max_year + 1):
            day_of_year = 1
            for month in range(1, 13):
                assert (
                    calculator._get_day_of_year(_YearMonthDay._ctor(year=year, month=month, day=1)) == day_of_year
                ), f"{year=}, {month=}"
                day_of_year += calculator._get_days_in_month(year, month)

    def test_get_year_month_day_invalid_value_for_coverage(self) -> None:
        calculator = _UmAlQuraYearMonthDayCalculator()
        with pytest.raises(ValueError):  # TODO: In Noda Time this is ArgumentOutOfRangeException
            calculator._get_year_month_day(year=calculator._min_year, day_of_year=1000)

    # TODO: test_generate_data()
