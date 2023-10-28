import pytest

from pyoda_time.calendars import (
    _GregorianYearMonthDayCalculator,
    _YearMonthDayCalculator,
)

ALL_CALCULATORS: list[_YearMonthDayCalculator] = [
    _GregorianYearMonthDayCalculator(),
]


class TestYearMonthDayCalculator:
    @pytest.mark.parametrize("calculator", ALL_CALCULATORS, ids=lambda x: x.__class__.__name__)
    def test_validate_start_of_year_1_days(self, calculator):
        if calculator._min_year > 1 or calculator._max_year < 0:
            return
        assert calculator._get_start_of_year_in_days(1) == calculator._days_at_start_of_year_1
