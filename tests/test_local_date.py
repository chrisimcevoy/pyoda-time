# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import CalendarSystem, IsoDayOfWeek, LocalDate, LocalDateTime, LocalTime
from pyoda_time.calendars import Era
from pyoda_time.calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator


class TestLocalDate:
    def test_default_constructor(self) -> None:
        actual = LocalDate()
        assert actual == LocalDate(year=1, month=1, day=1)

    def test_combination_with_time(self) -> None:
        # Test all three approaches in the same test - they're logically equivalent.
        calendar = CalendarSystem.julian
        date = LocalDate(2014, 3, 28, calendar)
        time = LocalTime(20, 17, 30)
        expected = LocalDateTime(2014, 3, 28, 20, 17, 30, calendar=calendar)
        assert date + time == expected
        assert date.at(time) == expected
        assert time.on(date) == expected

    # TODO:
    #  def test_xml_serializtion_iso(self):
    #  def test_xml_serializtion_non_iso(self):
    #  def test_xml_serializtion_invalid(self):

    def test_construction_null_calendar_throws(self) -> None:
        with pytest.raises(TypeError):
            LocalDate(2017, 11, 7, calendar=None)  # type: ignore

        with pytest.raises(TypeError):
            LocalDate(era=Era.common, year_of_era=2017, month=11, day=7, calendar=None)  # type: ignore

    def test_max_iso_value(self) -> None:
        value: LocalDate = LocalDate.max_iso_value
        assert value.calendar == CalendarSystem.iso
        with pytest.raises(OverflowError):
            value.plus_days(1)

    def test_min_iso_value(self) -> None:
        value: LocalDate = LocalDate.min_iso_value
        assert value.calendar == CalendarSystem.iso
        with pytest.raises(OverflowError):
            value.plus_days(-1)

    def test_deconstruction(self) -> None:
        value = LocalDate(2017, 11, 7)
        expected_year = 2017
        expected_month = 11
        expected_day = 7
        actual_year, actual_month, actual_day = value

        assert actual_year == expected_year
        assert actual_month == expected_month
        assert actual_day == expected_day

    # TODO: def test_deconstruction_including_calendar(self) -> None:


class TestLocalDateConstruction:
    @pytest.mark.parametrize(
        "year",
        [
            1620,  # Leap year in non-optimized period
            1621,  # Non-leap year in non-optimized period
            1980,  # Leap year in optimized period
            1981,  # Non-leap year in optimized period
        ],
    )
    def test_constructor_with_days(self, year: int) -> None:
        start = LocalDate(year, 1, 1)
        start_days = start._days_since_epoch
        for i in range(366):
            assert LocalDate._ctor(days_since_epoch=start_days + i) == start.plus_days(i)

    @pytest.mark.parametrize(
        "year",
        [
            1620,  # Leap year in non-optimized period
            1621,  # Non-leap year in non-optimized period
            1980,  # Leap year in optimized period
            1981,  # Non-leap year in optimized period
        ],
    )
    def test_constructor_with_days_and_calendar(self, year: int) -> None:
        start = LocalDate(year, 1, 1)
        start_days = start._days_since_epoch
        for i in range(366):
            assert LocalDate._ctor(days_since_epoch=start_days + i, calendar=CalendarSystem.iso) == start.plus_days(i)

    def test_constructor_calendar_defaults_to_iso(self) -> None:
        date = LocalDate(2000, 1, 1)
        assert date.calendar == CalendarSystem.iso

    def test_constructor_properties_round_trip(self) -> None:
        date = LocalDate(2023, 7, 27)
        assert date.year == 2023
        assert date.month == 7
        assert date.day == 27

    def test_constructor_properties_round_trip_custom_calendar(self) -> None:
        date = LocalDate(2023, 7, 27, CalendarSystem.julian)
        assert date.year == 2023
        assert date.month == 7
        assert date.day == 27

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (_GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR + 1, 1, 1),
            (_GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR - 1, 1, 1),
            (2010, 13, 1),
            (2010, 0, 1),
            (2010, 1, 100),
            (2010, 2, 30),
            (2010, 1, 0),
        ],
    )
    def test_constructor_invalid(self, year: int, month: int, day: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(year, month, day)

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (_GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR + 1, 1, 1),
            (_GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR - 1, 1, 1),
            (2010, 13, 1),
            (2010, 0, 1),
            (2010, 1, 100),
            (2010, 2, 30),
            (2010, 1, 0),
        ],
    )
    def test_constructor_invalid_with_calendar(self, year: int, month: int, day: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(year, month, day, CalendarSystem.iso)

    def test_constructor_invalid_year_of_era(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(0, 1, 1, era=Era.common)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(0, 1, 1, era=Era.before_common)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(10000, 1, 1, era=Era.common)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate(10000, 1, 1, era=Era.before_common)

    def test_constructor_with_year_of_era_bc(self) -> None:
        absolute = LocalDate(-10, 1, 1)
        with_era = LocalDate(11, 1, 1, era=Era.before_common)
        assert with_era == absolute

    def test_constructor_with_year_of_era_ad(self) -> None:
        absolute = LocalDate(50, 6, 19)
        with_era = LocalDate(50, 6, 19, era=Era.common)
        assert with_era == absolute

    def test_constructor_with_year_of_era_non_iso_calendar(self) -> None:
        calendar = CalendarSystem.coptic
        absolute = LocalDate(50, 6, 19, calendar)
        with_era = LocalDate(50, 6, 19, calendar, Era.anno_martyrum)
        assert with_era == absolute

    # Most tests are in IsoBasedWeekYearRuleTest.
    def test_from_week_year_and_day_invalid_week_53(self) -> None:
        # Week year 2005 only has 52 weeks
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalDate.from_week_year_week_and_day(2005, 53, IsoDayOfWeek.SUNDAY)

    @pytest.mark.parametrize(
        "year,month,occurrence,day_of_week,expected_day",
        [
            (2014, 8, 3, IsoDayOfWeek.SUNDAY, 17),
            (2014, 8, 3, IsoDayOfWeek.FRIDAY, 15),
            # Needs "rewind" logic as August 1st 2014 is a Friday
            (2014, 8, 3, IsoDayOfWeek.THURSDAY, 21),
            (2014, 8, 5, IsoDayOfWeek.SUNDAY, 31),
            # Only 4 Mondays in August in 2014.
            (2014, 8, 5, IsoDayOfWeek.MONDAY, 25),
        ],
    )
    def test_from_year_month_week_and_day(
        self, year: int, month: int, occurrence: int, day_of_week: IsoDayOfWeek, expected_day: int
    ) -> None:
        date = LocalDate.from_year_month_week_and_day(year, month, occurrence, day_of_week)
        assert date.year == year
        assert date.month == month
        assert date.day == date.day
