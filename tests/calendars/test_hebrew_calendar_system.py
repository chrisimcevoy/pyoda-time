import pytest

from pyoda_time import CalendarSystem, LocalDate, _YearMonthDay
from pyoda_time.calendars import HebrewMonthNumbering, _HebrewScripturalCalculator, _HebrewYearMonthDayCalculator


class TestHebrewCalendarSystem:
    # TODO: def test_is_leap_year (requires BCL)
    # TODO: def test_bcl_through_history_civil (requires BCL)
    # TODO: def test_bcl_through_history_scriptural (requires BCL)
    # TODO: def test_set_year (requires LocalDatePattern)
    # TODO: def test_add_months_months_between (requires LocalDatePattern)
    # TODO: def test_months_between (requires LocalDatePattern)
    # TODO: def test_months_between_time_of_day(self) -> None:  (requires Period.Between())

    @pytest.mark.parametrize(
        "numbering",
        (
            HebrewMonthNumbering.CIVIL,
            HebrewMonthNumbering.SCRIPTURAL,
        ),
        ids=lambda x: x.name,
    )
    def test_day_of_year_and_reverse(self, numbering: HebrewMonthNumbering) -> None:
        calculator = _HebrewYearMonthDayCalculator(numbering)
        for year in range(5400, 5420):
            days_in_year = calculator._get_days_in_year(year)
            for day_of_year in range(1, days_in_year + 1):
                ymd = calculator._get_year_month_day(year=year, day_of_year=day_of_year)
                assert calculator._get_day_of_year(ymd) == day_of_year

    def test_get_days_since_epoch(self) -> None:
        calculator = _HebrewYearMonthDayCalculator(HebrewMonthNumbering.SCRIPTURAL)
        unix_epoch = _YearMonthDay._ctor(year=5730, month=10, day=23)
        assert calculator._get_days_since_epoch(unix_epoch) == 0

    def test_days_at_start_of_year(self) -> None:
        calculator = _HebrewYearMonthDayCalculator(HebrewMonthNumbering.SCRIPTURAL)
        assert calculator._get_start_of_year_in_days(5730) == -110
        assert calculator._get_start_of_year_in_days(5731) == 273
        assert calculator._get_start_of_year_in_days(5345) == -140735
        assert calculator._get_year_month_day(days_since_epoch=-140529) == _YearMonthDay._ctor(
            year=5345, month=1, day=1
        )

    def test_days_in_year_cross_check(self) -> None:
        calculator = _HebrewYearMonthDayCalculator(HebrewMonthNumbering.CIVIL)
        for year in range(calculator._min_year, calculator._max_year + 1):
            sum_ = sum(
                calculator._get_days_in_month(year, month)
                for month in range(1, calculator._get_months_in_year(year) + 1)
            )
            assert calculator._get_days_in_year(year) == sum_, f"Days in {year}"

    # TODO: def test_scriptural_compare(self): (requires LocalDatePattern)

    def test_scriptural_get_days_from_start_of_year_to_start_of_month_invalid_for_coverage(self) -> None:
        with pytest.raises(ValueError):
            _HebrewScripturalCalculator._get_days_from_start_of_year_to_start_of_month(5502, 0)

    # TODO: requires LocalDate.plus_months()
    @pytest.mark.parametrize(
        "month_numbering",
        (
            HebrewMonthNumbering.CIVIL,
            HebrewMonthNumbering.SCRIPTURAL,
        ),
    )
    def test_plus_months_overflow(self, month_numbering: HebrewMonthNumbering) -> None:
        calendar = CalendarSystem.get_hebrew_calendar(month_numbering)
        # TODO: It would be nice to have an easy way of getting the smallest/largest LocalDate for
        #  a calendar. Or possibly FromDayOfYear as well... instead, we'll just add/subtract 8 months instead
        early_date = LocalDate(year=calendar.min_year, month=1, day=1, calendar=calendar)
        late_date = LocalDate(year=calendar.max_year, month=12, day=1, calendar=calendar)

        with pytest.raises(OverflowError):
            early_date.plus_months(-7)
        with pytest.raises(OverflowError):
            late_date.plus_months(7)
