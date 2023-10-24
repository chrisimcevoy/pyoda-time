import pytest

from pyoda_time.calendars import GregorianYearMonthDayCalculator, YearMonthDayCalculator

ALL_CALCULATORS: list[YearMonthDayCalculator] = [
    GregorianYearMonthDayCalculator(),
]


class TestYearMonthDayCalculator:
    @pytest.mark.parametrize(
        "calculator", ALL_CALCULATORS, ids=lambda x: x.__class__.__name__
    )
    def test_validate_start_of_year_1_days(self, calculator):
        if calculator.min_year > 1 or calculator.max_year < 0:
            return
        assert (
            calculator.get_start_of_year_in_days(1)
            == calculator.days_at_start_of_year_1
        )
