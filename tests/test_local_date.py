# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import datetime
from typing import cast

import pytest

from pyoda_time import (
    CalendarSystem,
    DateAdjusters,
    Instant,
    IsoDayOfWeek,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    OffsetDate,
    Period,
    PyodaConstants,
)
from pyoda_time.calendars import Era, IslamicEpoch, IslamicLeapYearPattern
from pyoda_time.calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from pyoda_time.utility._csharp_compatibility import _CsharpConstants, _towards_zero_division
from tests.helpers import assert_overflow


class TestLocalDate:
    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to January 1st 1970, UTC, ISO calendar."""
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


class TestLocalDateBasicProperties:
    def test_epoch_properties(self) -> None:
        date: LocalDate = PyodaConstants.UNIX_EPOCH.in_utc().date
        assert date.year == 1970
        assert date.year_of_era == 1970
        assert date.day == 1
        assert date.day_of_week == IsoDayOfWeek.THURSDAY
        assert date.day_of_year == 1
        assert date.month == 1

    def test_arbitrary_date_properties(self) -> None:
        # This is necessarily different to Noda Time, because it relies on BCL.
        from datetime import datetime

        stdlib_date = datetime(2011, 3, 5, 0, 0, 0)
        stdlib_epoch = datetime(1970, 1, 1, 0, 0, 0)
        stdlib_seconds = (stdlib_date - stdlib_epoch).total_seconds()
        stdlib_days = _towards_zero_division(stdlib_seconds, PyodaConstants.SECONDS_PER_DAY)
        date = LocalDate._ctor(days_since_epoch=stdlib_days, calendar=CalendarSystem.iso)
        assert date.year == 2011
        assert date.year_of_era == 2011
        assert date.day == 5
        assert date.day_of_week == IsoDayOfWeek.SATURDAY
        assert date.day_of_year == 64
        assert date.month == 3

    # TODO: def test_day_of_week_around_epoch(self) -> None: [requires bcl]


class TestLocalDateComparison:
    def test_equals_equal_values(self) -> None:
        calendar: CalendarSystem = CalendarSystem.julian
        date1: LocalDate = LocalDate(2011, 1, 2, calendar)
        date2: LocalDate = LocalDate(2011, 1, 2, calendar)
        # In Noda Time this also tests Object.Equals() and IEquatable.Equals()
        assert date1 == date2
        assert hash(date1) == hash(date2)
        assert not (date1 != date2)

    def test_equals_different_dates(self) -> None:
        calendar: CalendarSystem = CalendarSystem.julian
        date1: LocalDate = LocalDate(2011, 1, 2, calendar)
        date2: LocalDate = LocalDate(2011, 1, 3, calendar)
        # In Noda Time this also tests Object.Equals() and IEquatable.Equals()
        assert date1 != date2
        assert hash(date1) != hash(date2)
        assert not (date1 == date2)

    def test_equals_different_calendars(self) -> None:
        calendar: CalendarSystem = CalendarSystem.julian
        date1: LocalDate = LocalDate(2011, 1, 2, calendar)
        date2: LocalDate = LocalDate(2011, 1, 2, CalendarSystem.iso)
        # In Noda Time this also tests Object.Equals() and IEquatable.Equals()
        assert date1 != date2
        assert hash(date1) != hash(date2)
        assert not (date1 == date2)

    def test_equals_different_to_null(self) -> None:
        date: LocalDate = LocalDate(2011, 1, 2)
        assert not (date == None)  # noqa: E711

    def test_equals_different_to_other_type(self) -> None:
        date: LocalDate = LocalDate(2011, 1, 2)
        assert not (date == Instant.from_unix_time_ticks(0))

    def test_comparison_operators_same_calendar(self) -> None:
        date1: LocalDate = LocalDate(2011, 1, 2)
        date2: LocalDate = LocalDate(2011, 1, 2)
        date3: LocalDate = LocalDate(2011, 1, 5)

        assert not date1 < date2
        assert date1 < date3
        assert not date2 < date1
        assert not date3 < date1

        assert date1 <= date2
        assert date1 <= date3
        assert date2 <= date1
        assert not date3 <= date1

        assert not date1 > date2
        assert not date1 > date3
        assert not date2 > date1
        assert date3 > date1

        assert date1 >= date2
        assert not date1 >= date3
        assert date2 >= date1
        assert date3 >= date1

    def test_comparison_operators_different_calendars_throws(self) -> None:
        date1: LocalDate = LocalDate(2011, 1, 2)
        date2: LocalDate = LocalDate(2011, 1, 2, CalendarSystem.julian)

        with pytest.raises(ValueError):  # TODO: ArgumentException
            _ = date1 < date2
        with pytest.raises(ValueError):  # TODO: ArgumentException
            _ = date1 <= date2
        with pytest.raises(ValueError):  # TODO: ArgumentException
            _ = date1 > date2
        with pytest.raises(ValueError):  # TODO: ArgumentException
            _ = date1 >= date2

    def test_compare_to_same_calendar(self) -> None:
        date1: LocalDate = LocalDate(2011, 1, 2)
        date2: LocalDate = LocalDate(2011, 1, 2)
        date3: LocalDate = LocalDate(2011, 1, 5)

        assert date1.compare_to(date2) == 0
        assert date1.compare_to(date3) < 0
        assert date3.compare_to(date2) > 0

    def test_compare_to_different_calendars_throws(self) -> None:
        islamic: CalendarSystem = CalendarSystem.get_islamic_calendar(
            IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL
        )
        date1: LocalDate = LocalDate(2011, 1, 2)
        date2: LocalDate = LocalDate(1500, 1, 1, islamic)

        with pytest.raises(ValueError):  # TODO: ArgumentException
            date1.compare_to(date2)
        # In Noda Time, IComparable.compare_to() is tested here...

    @pytest.mark.skip("Not applicable to Python")
    def test_icomparable_compare_to_same_calendar(self) -> None:
        pass  # pragma: no cover

    def test_icomparable_compare_to_null_positive(self) -> None:
        """IComparable.CompareTo returns a positive number for a null input."""
        comparable = LocalDate(2012, 3, 5)
        result = comparable.compare_to(None)
        assert result > 0

    def test_icomparable_compare_to_wrong_type_argument_exception(self) -> None:
        """IComparable.CompareTo throws an ArgumentException for non-null arguments that are not a LocalDate."""
        instance = LocalDate(2012, 3, 5)
        arg = LocalDateTime(2012, 3, 6, 15, 42)
        with pytest.raises(TypeError):
            instance.compare_to(arg)  # type: ignore[arg-type]

    def test_min_max_different_calendars_throws(self) -> None:
        date1: LocalDate = LocalDate(2011, 1, 2)
        date2: LocalDate = LocalDate(1500, 1, 1, CalendarSystem.julian)

        with pytest.raises(ValueError):
            LocalDate.max(date1, date2)
        with pytest.raises(ValueError):
            LocalDate.min(date1, date2)

    def test_min_max_same_calendar(self) -> None:
        date1: LocalDate = LocalDate(1500, 1, 2, CalendarSystem.julian)
        date2: LocalDate = LocalDate(1500, 1, 1, CalendarSystem.julian)

        assert LocalDate.max(date1, date2) == date1
        assert LocalDate.max(date2, date1) == date1
        assert LocalDate.min(date1, date2) == date2
        assert LocalDate.min(date2, date1) == date2


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


class TestLocalDateConversion:
    def test_at_midnight(self) -> None:
        date: LocalDate = LocalDate(2011, 6, 29)
        expected: LocalDateTime = LocalDateTime(2011, 6, 29, 0, 0, 0)
        assert date.at_midnight() == expected

    def test_with_calendar(self) -> None:
        iso_epoch: LocalDate = LocalDate(1970, 1, 1)
        julian_epoch = iso_epoch.with_calendar(CalendarSystem.julian)
        assert julian_epoch.year == 1969
        assert julian_epoch.month == 12
        assert julian_epoch.day == 19

    def test_with_offset(self) -> None:
        date = LocalDate(2011, 6, 29)
        offset = Offset.from_hours(5)
        expected = OffsetDate(date, offset)
        assert date.with_offset(offset) == expected

    # TODO: Skipping the following tests as they are not relevant in Python, where `datetime.date` is not a recent
    #  addition to the stdlib (unlike `DateOnly` in dotnet).
    #  - ToDateTimeUnspecified
    #  - ToDateTimeUnspecified_JulianCalendar
    #  - FromDateTime
    #  - FromDateTime_WithCalendar

    def test_with_calendar_out_of_range(self) -> None:
        start: LocalDate = LocalDate(1, 1, 1)
        with pytest.raises(ValueError):
            start.with_calendar(CalendarSystem.persian_simple)

    def test_with_calendar_unchanged(self) -> None:
        iso_epoch: LocalDate = LocalDate(1970, 1, 1)
        unchanged = iso_epoch.with_calendar(CalendarSystem.iso)
        assert unchanged.year == iso_epoch.year
        assert unchanged.month == iso_epoch.month
        assert unchanged.day == iso_epoch.day
        assert unchanged.calendar == iso_epoch.calendar

    def test_to_date_gregorian(self) -> None:
        local_date = LocalDate(2011, 8, 5)
        expected = datetime.date(2011, 8, 5)
        actual = local_date.to_date()
        assert actual == expected

    def test_to_date_non_gregorian(self) -> None:
        # Julian calendar is 13 days behind Gregorian calendar in the 21st century
        local_date = LocalDate(2011, 8, 5, CalendarSystem.julian)
        expected = datetime.date(2011, 8, 18)
        actual = local_date.to_date()
        assert actual == expected
        # Unlike the equivalent test in Pyoda Time, we cannot test the stlib date
        # with different calendars like they do for DateOnly in dotnet.

    def test_to_date_out_of_range(self) -> None:
        local_date = LocalDate(0, 12, 31)
        with pytest.raises(OverflowError):
            # TODO: Noda Time has the following comment:
            #  "While ArgumentOutOfRangeException may not be the absolute ideal exception, it conveys
            #  the right impression, and is consistent with what we do elsewhere."
            #  I'm not sure that is accurate, for instance LocalDate.ToDate and LocalDateTime.ToDateTimeUnspecified both
            #  throw InvalidOperationException...
            #  In any case, LocalDate.ToDateOnly seems to defer to The DateOnly constructor rather than throwing itself.
            #  So we are doing the same thing here, just allowing datetime.date() to raise.
            local_date.to_date()

    def test_from_date(self) -> None:
        date = datetime.date(2011, 8, 18)
        expected = LocalDate(2011, 8, 18)
        actual = LocalDate.from_date(date)
        assert actual == expected


class TestLocalDatePeriodArithmetic:
    def test_addition_with_period(self) -> None:
        start = LocalDate(2010, 6, 19)
        period = Period.from_months(3) + Period.from_days(10)
        expected = LocalDate(2010, 9, 29)
        assert start + period == expected

    def test_addition_truncates_on_short_month(self) -> None:
        start = LocalDate(2010, 1, 30)
        period = Period.from_months(1)
        expected = LocalDate(2010, 2, 28)
        assert start + period == expected

    def test_addition_with_null_period_throws_argument_null_exception(self) -> None:
        date = LocalDate(2010, 1, 1)
        with pytest.raises(TypeError):
            date + cast(Period, None)

    def test_subtraction_with_period(self) -> None:
        start = LocalDate(2010, 9, 29)
        period = Period.from_months(3) + Period.from_days(10)
        expected = LocalDate(2010, 6, 19)
        assert start - period == expected

    def test_subtraction_truncates_on_short_month(self) -> None:
        start = LocalDate(2010, 3, 30)
        period = Period.from_months(1)
        expected = LocalDate(2010, 2, 28)
        assert start - period == expected

    def test_subtraction_with_null_period_throws_argument_null_exception(self) -> None:
        date = LocalDate(2010, 1, 1)
        with pytest.raises(TypeError):
            date - cast(Period, None)

    def test_addition_period_with_time(self) -> None:
        date = LocalDate(2010, 1, 1)
        period = Period.from_hours(1)
        # Use method not operator here to form a valid statement
        with pytest.raises(ValueError):
            LocalDate.add(date, period)

    def test_subtraction_period_with_time(self) -> None:
        date = LocalDate(2010, 1, 1)
        period = Period.from_hours(1)
        # Use method not operator here to form a valid statement
        with pytest.raises(ValueError):
            LocalDate.subtract(date, period)

    def test_period_addition_method_equivalents(self) -> None:
        start = LocalDate(2010, 6, 19)
        period = Period.from_months(3) + Period.from_days(10)
        assert LocalDate.add(start, period) == start + period
        assert start.plus(period) == start + period

    def test_period_subtraction_method_equivalents(self) -> None:
        start = LocalDate(2010, 6, 19)
        period = Period.from_months(3) + Period.from_days(10)
        end = start + period
        assert LocalDate.subtract(start, period) == start - period
        assert start.minus(period) == start - period
        assert end - start == period
        assert LocalDate.subtract(end, start) == period
        assert end.minus(start) == period

    @pytest.mark.parametrize(
        ("year", "month", "day", "months_to_add"),
        [
            (9999, 12, 31, 1),
            (9999, 12, 1, 1),
            (9999, 11, 30, 2),
            (9999, 11, 1, 2),
            (9998, 12, 31, 13),
            (9998, 12, 1, 13),
            (-9998, 1, 1, -1),
            (-9998, 2, 1, -2),
            (-9997, 1, 1, -13),
        ],
    )
    def test_plus_months_overflow(self, year: int, month: int, day: int, months_to_add: int) -> None:
        start = LocalDate(year, month, day)
        with pytest.raises(OverflowError):
            start.plus_months(months_to_add)


class TestLocalDatePseudomutators:
    def test_plus_year_simple(self) -> None:
        start = LocalDate(2011, 6, 26)
        expected = LocalDate(2016, 6, 26)
        assert start.plus_years(5) == expected

        expected = LocalDate(2006, 6, 26)
        assert start.plus_years(-5) == expected

    def test_plus_year_leap_to_non_leap(self) -> None:
        start = LocalDate(2012, 2, 29)
        expected = LocalDate(2013, 2, 28)
        assert start.plus_years(1) == expected

        expected = LocalDate(2011, 2, 28)
        assert start.plus_years(-1) == expected

    def test_plus_year_leap_to_leap(self) -> None:
        start = LocalDate(2012, 2, 29)
        expected = LocalDate(2016, 2, 29)
        assert start.plus_years(4) == expected

    def test_plus_month_simple(self) -> None:
        start = LocalDate(2012, 4, 15)
        expected = LocalDate(2012, 8, 15)
        assert start.plus_months(4) == expected

    def test_plus_month_changing_year(self) -> None:
        start = LocalDate(2012, 10, 15)
        expected = LocalDate(2013, 2, 15)
        assert start.plus_months(4) == expected

    def test_plus_month_truncation(self) -> None:
        start = LocalDate(2011, 1, 30)
        expected = LocalDate(2011, 2, 28)
        assert start.plus_months(1) == expected

    def test_plus_days_same_month(self) -> None:
        start = LocalDate(2011, 1, 15)
        expected = LocalDate(2011, 1, 23)
        assert start.plus_days(8) == expected

        expected = LocalDate(2011, 1, 7)
        assert start.plus_days(-8) == expected

    def test_plus_days_month_boundary(self) -> None:
        start = LocalDate(2011, 1, 26)
        expected = LocalDate(2011, 2, 3)
        assert start.plus_days(8) == expected

        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_year_boundary(self) -> None:
        start = LocalDate(2011, 12, 26)
        expected = LocalDate(2012, 1, 3)
        assert start.plus_days(8) == expected

        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_end_of_february_in_leap_year(self) -> None:
        start = LocalDate(2012, 2, 26)
        expected = LocalDate(2012, 3, 5)
        assert start.plus_days(8) == expected
        # Round-trip back across boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_end_of_february_not_in_leap_year(self) -> None:
        start = LocalDate(2011, 2, 26)
        expected = LocalDate(2011, 3, 6)
        assert start.plus_days(8) == expected

        # Round-trip back across boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_large_value(self) -> None:
        start = LocalDate(2013, 2, 26)
        expected = LocalDate(2015, 2, 26)
        assert start.plus_days(365 * 2) == expected

    def test_plus_weeks_simple(self) -> None:
        start = LocalDate(2011, 4, 2)
        expected_forward = LocalDate(2011, 4, 23)
        expected_backward = LocalDate(2011, 3, 12)
        assert start.plus_weeks(3) == expected_forward
        assert start.plus_weeks(-3) == expected_backward

    @pytest.mark.parametrize(
        ("year", "month", "day", "days"),
        [
            (-9998, 1, 1, -1),
            (-9996, 1, 1, -1000),
            (9999, 12, 31, 1),
            (9997, 12, 31, 1000),
            (2000, 1, 1, _CsharpConstants.INT_MAX_VALUE),
            (1, 1, 1, _CsharpConstants.INT_MIN_VALUE),
        ],
    )
    def test_plus_days_out_of_range(self, year: int, month: int, day: int, days: int) -> None:
        start = LocalDate(year, month, day)
        assert_overflow(start.plus_days, days)

    @pytest.mark.parametrize(
        ("day_of_month", "target_day_of_week", "expected_result"),
        [
            (10, IsoDayOfWeek.WEDNESDAY, 16),
            (10, IsoDayOfWeek.FRIDAY, 11),
            (10, IsoDayOfWeek.THURSDAY, 17),
            (11, IsoDayOfWeek.WEDNESDAY, 16),
            (11, IsoDayOfWeek.THURSDAY, 17),
            (11, IsoDayOfWeek.FRIDAY, 18),
            (11, IsoDayOfWeek.SATURDAY, 12),
            (11, IsoDayOfWeek.SUNDAY, 13),
            (12, IsoDayOfWeek.FRIDAY, 18),
            (13, IsoDayOfWeek.FRIDAY, 18),
        ],
    )
    def test_next(self, day_of_month: int, target_day_of_week: IsoDayOfWeek, expected_result: int) -> None:
        """Each test case gives a day-of-month in November 2011 and a target "next day of week"; the result is the next
        day-of-month in November 2011 with that target day.

        The tests are picked somewhat arbitrarily...
        """
        start = LocalDate(2011, 11, day_of_month)
        target = start.next(target_day_of_week)
        assert target.year == 2011
        assert target.month == 11
        assert target.day == expected_result

    # TODO: Skipping `Next_InvalidArgument` as python enums do not work like C# enums.

    @pytest.mark.parametrize(
        ("day_of_month", "target_day_of_week", "expected_result"),
        [
            (10, IsoDayOfWeek.WEDNESDAY, 9),
            (10, IsoDayOfWeek.FRIDAY, 4),
            (10, IsoDayOfWeek.THURSDAY, 3),
            (11, IsoDayOfWeek.WEDNESDAY, 9),
            (11, IsoDayOfWeek.THURSDAY, 10),
            (11, IsoDayOfWeek.FRIDAY, 4),
            (11, IsoDayOfWeek.SATURDAY, 5),
            (11, IsoDayOfWeek.SUNDAY, 6),
            (12, IsoDayOfWeek.FRIDAY, 11),
            (13, IsoDayOfWeek.FRIDAY, 11),
        ],
    )
    def test_previous(self, day_of_month: int, target_day_of_week: IsoDayOfWeek, expected_result: int) -> None:
        """Each test case gives a day-of-month in November 2011 and a target "next day of week"; the result is the next
        day-of-month in November 2011 with that target day."""
        start = LocalDate(2011, 11, day_of_month)
        target = start.previous(target_day_of_week)
        assert target.year == 2011
        assert target.month == 11
        assert target.day == expected_result

    # TODO: Skipping `Previous_InvalidArgument` because python enums do not work like C# enums

    # No tests for non-ISO-day-of-week calendars as we don't have any yet.

    def test_with(self) -> None:
        start = LocalDate(2014, 6, 27)
        expected = LocalDate(2014, 6, 30)
        assert start.with_date_adjuster(DateAdjusters.end_of_month) == expected
