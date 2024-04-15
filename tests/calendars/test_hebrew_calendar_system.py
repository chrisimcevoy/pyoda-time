# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time import CalendarSystem, LocalDate, LocalDateTime, Period, PeriodUnits
from pyoda_time._year_month_day import _YearMonthDay
from pyoda_time.calendars import HebrewMonthNumbering
from pyoda_time.calendars._hebrew_scriptural_calculator import _HebrewScripturalCalculator
from pyoda_time.calendars._hebrew_year_month_day_calculator import _HebrewYearMonthDayCalculator
from pyoda_time.text import LocalDatePattern

from .. import helpers

ADD_AND_SUBTRACT_MONTH_CASES: list[tuple[str, int, str]] = [
    ("5502-02-13", 3, "5502-05-13"),  # Simple
    ("5502-02-13", 238, "5521-05-13"),  # Simple after a 19-year cycle
    ("5502-05-13", -3, "5502-02-13"),  # Simple (negative)
    ("5521-05-13", -238, "5502-02-13"),  # Simple after a 19-year cycle (negative)
    ("5501-02-13", 12, "5502-02-13"),  # Not a leap year
    ("5502-02-13", 13, "5503-02-13"),  # Leap year
    ("5501-02-13", 26, "5503-03-13"),  # Traversing both (and then an extra month)
    ("5502-02-13", -12, "5501-02-13"),  # Not a leap year (negative)
    ("5503-02-13", -13, "5502-02-13"),  # Leap year (negative)
    ("5503-03-13", -26, "5501-02-13"),  # Traversing both (and then an extra month) (negative)
    ("5507-01-30", 1, "5507-02-30"),  # Long Heshvan
    ("5506-01-30", 1, "5506-02-29"),  # Short Heshvan
    ("5505-01-30", 2, "5505-03-30"),  # Long Kislev
    ("5506-01-30", 2, "5506-03-29"),  # Short Kislev
]

MONTH_BETWEEN_CASES: list[tuple[str, int, str]] = [
    ("5502-02-13", 1, "5502-03-15"),
    ("5502-02-13", 0, "5502-03-05"),
    ("5502-02-13", 0, "5502-02-15"),
    ("5502-02-13", 0, "5502-02-05"),
    ("5502-02-13", 0, "5502-01-15"),
    ("5502-02-13", -1, "5502-01-05"),
]


class TestHebrewCalendarSystem:
    # TODO: def test_is_leap_year (requires BCL)
    # TODO: def test_bcl_through_history_civil (requires BCL)
    # TODO: def test_bcl_through_history_scriptural (requires BCL)

    # Test cases are in scriptural month numbering, but we check both. This is
    # mostly testing the behaviour of SetYear, via LocalDate.PlusYears.
    @pytest.mark.parametrize(
        "start_text,years,expected_end_text",
        [
            # Simple case
            ("5405-02-10", 1, "5406-02-10"),
            # Adar mapping - Adar from non-leap maps to Adar II in leap;
            # Adar I and Adar II both map to Adar in a non-leap, except for the 30th of Adar I
            # which maps to the 1st of Nisan.
            ("5402-12-05", 1, "5403-12-05"),  # Mapping from Adar I to Adar
            ("5402-13-05", 1, "5403-12-05"),  # Mapping from Adar II to Adar
            ("5402-12-30", 1, "5403-01-01"),  # Mapping from 30th of Adar I to 1st of Nisan
            ("5401-12-05", 1, "5402-13-05"),  # Mapping from Adar to Adar II
            # Transfer to another leap year
            ("5402-12-05", 2, "5404-12-05"),  # Adar I to Adar I
            ("5402-12-30", 2, "5404-12-30"),  # 30th of Adar I to 30th of Adar I
            ("5402-13-05", 2, "5404-13-05"),  # Adar II to Adar II
            # Rollover of 30th of Kislev and Heshvan to the 1st of the next month.
            ("5402-08-30", 1, "5403-09-01"),  # Rollover from 30th Heshvan to 1st Kislev
            ("5400-09-30", 1, "5401-10-01"),  # Rollover from 30th Kislev to 1st Tevet
            # No rollover required (target year has 30 days in as well)
            ("5402-08-30", 3, "5405-08-30"),  # No truncation in Heshvan (both 5507 and 5509 are long)
            ("5400-09-30", 2, "5402-09-30"),  # No truncation in Kislev (both 5503 and 5504 are long)
        ],
    )
    def test_set_year(self, start_text: str, years: int, expected_end_text: str) -> None:
        civil = CalendarSystem.hebrew_civil
        scriptural = CalendarSystem.hebrew_scriptural
        pattern = LocalDatePattern.create_with_invariant_culture("uuuu-MM-dd").with_template_value(
            LocalDate(year=5774, month=1, day=1, calendar=scriptural)
        )  # Sample value in 2014 ISO

        start = pattern.parse(start_text).value
        expected_end = pattern.parse(expected_end_text).value
        assert start.plus_years(years) == expected_end

        # Check civil as well... the date should be the same (year, month, day) even though
        # the numbering is different.
        assert start.with_calendar(civil).plus_years(years) == expected_end.with_calendar(civil)

    @pytest.mark.parametrize("start_text,months,expected_end_text", ADD_AND_SUBTRACT_MONTH_CASES)
    def test_add_months_months_between(self, start_text: str, months: int, expected_end_text: str) -> None:
        civil = CalendarSystem.hebrew_civil
        pattern = LocalDatePattern.create_with_invariant_culture("uuuu-MM-dd").with_template_value(
            LocalDate(year=5774, month=1, day=1, calendar=civil)
        )  # Sample value in 2014 ISO

        start = pattern.parse(start_text).value
        expected_end = pattern.parse(expected_end_text).value
        assert start.plus_months(months) == expected_end

    @pytest.mark.parametrize("start_text,expected_months,end_text", ADD_AND_SUBTRACT_MONTH_CASES + MONTH_BETWEEN_CASES)
    def test_months_between(self, start_text: str, expected_months: int, end_text: str) -> None:
        civil = CalendarSystem.hebrew_civil
        pattern = LocalDatePattern.create_with_invariant_culture("uuuu-MM-dd").with_template_value(
            LocalDate(year=5774, month=1, day=1, calendar=civil)
        )  # Sample value in 2014 ISO

        start = pattern.parse(start_text).value
        end = pattern.parse(end_text).value
        assert Period.between(start, end, PeriodUnits.MONTHS).months == expected_months

    def test_months_between_time_of_day(self) -> None:
        civil = CalendarSystem.hebrew_civil
        start = LocalDateTime(5774, 5, 10, 15, 0, calendar=civil)  # 3pm
        end = LocalDateTime(5774, 7, 10, 5, 0, calendar=civil)  # 5am
        # Would be 2, but the start time is later than the end time.
        assert Period.between(start, end, PeriodUnits.MONTHS).months == 1

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

    @pytest.mark.parametrize(
        "earlier,later",
        [
            ("5502-01-01", "5503-01-01"),
            pytest.param("5502-01-01", "5502-02-01", id="Months in same half of year"),
            # This is the test that looks odd...
            pytest.param("5502-12-01", "5502-02-01", id="Months in opposite half of year"),
            ("5502-03-10", "5502-03-12"),
        ],
    )
    def test_scriptural_compare(self, earlier: str, later: str) -> None:
        pattern = LocalDatePattern.iso.with_calendar(CalendarSystem.hebrew_scriptural)
        earlier_date = pattern.parse(earlier).value
        later_date = pattern.parse(later).value

        helpers.test_compare_to_struct(earlier_date, earlier_date, later_date)

    def test_scriptural_get_days_from_start_of_year_to_start_of_month_invalid_for_coverage(self) -> None:
        with pytest.raises(ValueError):
            _HebrewScripturalCalculator._get_days_from_start_of_year_to_start_of_month(5502, 0)

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
