# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from pyoda_time import (
    AmbiguousTimeError,
    CalendarSystem,
    DateAdjusters,
    DateTimeZone,
    DateTimeZoneProviders,
    IsoDayOfWeek,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    Period,
    PeriodBuilder,
    PyodaConstants,
    SkippedTimeError,
    TimeAdjusters,
)
from pyoda_time.calendars import IslamicEpoch, IslamicLeapYearPattern
from pyoda_time.calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from pyoda_time.time_zones import Resolvers
from pyoda_time.utility._csharp_compatibility import _CsharpConstants
from tests import helpers

PACIFIC: DateTimeZone = DateTimeZoneProviders.tzdb["America/Los_Angeles"]


class TestLocalDateTime:
    def test_to_naive_datetime(self) -> None:
        """Equivalent to ``LocalDateTime.ToDateTimeUnspecified()`` in Noda Time."""
        ldt = LocalDateTime(2011, 3, 5, 1, 0, 0)
        expected = datetime(2011, 3, 5, 1, 0, 0)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    def test_to_naive_datetime_julian_calendar(self) -> None:
        # In Noda Time, `expected` is also in the Julian calendar.
        # Not possible with Python's datetime module.
        ldt = LocalDateTime(2011, 3, 5, 1, 0, 0, calendar=CalendarSystem.julian)
        expected = datetime(2011, 3, 18, 1, 0, 0)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    @pytest.mark.parametrize("year", (100, 1900, 2900))
    def test_to_naive_datetime_truncates_towards_start_of_time(self, year: int) -> None:
        ldt = LocalDateTime(year, 1, 1, 13, 15, 55).plus_nanoseconds(PyodaConstants.NANOSECONDS_PER_SECOND - 1)
        expected = datetime(year, 1, 1, 13, 15, 55) + timedelta(microseconds=PyodaConstants.MICROSECONDS_PER_SECOND - 1)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    def test_to_naive_datetime_out_of_range(self) -> None:
        ldt = LocalDate(datetime.min.year, datetime.min.month, datetime.min.day).plus_days(-1).at_midnight()
        with pytest.raises(RuntimeError) as e:
            ldt.to_naive_datetime()
        assert str(e.value) == "LocalDateTime out of range of datetime"

    def test_from_naive_datetime(self) -> None:
        expected = LocalDateTime(2011, 8, 18, 20, 53)
        actual = LocalDateTime.from_naive_datetime(datetime(2011, 8, 18, 20, 53))
        assert actual == expected

    def test_from_naive_datetime_with_calendar(self) -> None:
        # Julian calendar is 13 days behind Gregorian calendar in the 21st century
        expected = LocalDateTime(2011, 8, 5, 20, 53, calendar=CalendarSystem.julian)
        actual = LocalDateTime.from_naive_datetime(datetime(2011, 8, 18, 20, 53), CalendarSystem.julian)
        assert actual == expected

    @pytest.mark.parametrize("tzinfo", (UTC, ZoneInfo("UTC"), ZoneInfo("Europe/London")))
    def test_from_naive_datetime_raises_for_aware_datetime(self, tzinfo: timezone | ZoneInfo) -> None:
        """This test doesn't exist in Noda Time, becase in C# DateTime does not have a tzinfo equivalent."""
        dt = datetime(2024, 6, 4, 23, 5, tzinfo=tzinfo)
        with pytest.raises(ValueError) as e:
            LocalDateTime.from_naive_datetime(dt)
        assert str(e.value) == "Invalid datetime.tzinfo for LocalDateTime.from_datetime_utc"
        assert e.value.__notes__ == ["Parameter name: datetime"]

    def test_time_properties_after_epoch(self) -> None:
        # Use the largest valid year as part of validating against overflow
        ldt = LocalDateTime(_GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR, 1, 2, 15, 48, 25).plus_nanoseconds(
            123456789
        )
        assert ldt.hour == 15
        assert ldt.clock_hour_of_half_day == 3
        assert ldt.minute == 48
        assert ldt.second == 25
        assert ldt.millisecond == 123
        assert ldt.microsecond == 123456
        assert ldt.tick_of_second == 1234567
        assert (
            ldt.tick_of_day
            == 15 * PyodaConstants.TICKS_PER_HOUR
            + 48 * PyodaConstants.TICKS_PER_MINUTE
            + 25 * PyodaConstants.TICKS_PER_SECOND
            + 1234567
        )
        assert (
            ldt.nanosecond_of_day
            == 15 * PyodaConstants.NANOSECONDS_PER_HOUR
            + 48 * PyodaConstants.NANOSECONDS_PER_MINUTE
            + 25 * PyodaConstants.NANOSECONDS_PER_SECOND
            + 123456789
        )
        assert ldt.nanosecond_of_second == 123456789

    def test_time_properties_before_epoch(self) -> None:
        # Use the smallest valid year number as part of validating against overflow
        ldt = LocalDateTime(_GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR, 1, 2, 15, 48, 25).plus_nanoseconds(
            123456789
        )
        assert ldt.hour == 15
        assert ldt.clock_hour_of_half_day == 3
        assert ldt.minute == 48
        assert ldt.second == 25
        assert ldt.millisecond == 123
        assert ldt.microsecond == 123456
        assert ldt.tick_of_second == 1234567
        assert (
            ldt.tick_of_day
            == 15 * PyodaConstants.TICKS_PER_HOUR
            + 48 * PyodaConstants.TICKS_PER_MINUTE
            + 25 * PyodaConstants.TICKS_PER_SECOND
            + 1234567
        )
        assert (
            ldt.nanosecond_of_day
            == 15 * PyodaConstants.NANOSECONDS_PER_HOUR
            + 48 * PyodaConstants.NANOSECONDS_PER_MINUTE
            + 25 * PyodaConstants.NANOSECONDS_PER_SECOND
            + 123456789
        )
        assert ldt.nanosecond_of_second == 123456789

    # TODO: DateTime_Roundtrip_OtherCalendarInBcl

    def test_with_calendar(self) -> None:
        iso_epoch = LocalDateTime(1970, 1, 1, 0, 0, 0)
        julian_epoch = iso_epoch.with_calendar(CalendarSystem.julian)
        assert julian_epoch.year == 1969
        assert julian_epoch.month == 12
        assert julian_epoch.day == 19
        assert julian_epoch.time_of_day == iso_epoch.time_of_day

    def test_time_of_day_before_1970(self) -> None:
        """Verifies that negative local instant ticks don't cause a problem with the date."""
        date_time = LocalDateTime(1965, 11, 8, 12, 5, 23)
        expected = LocalTime(12, 5, 23)
        assert date_time.time_of_day == expected

    def test_time_of_day_after_1970(self) -> None:
        """Verifies that positive local instant ticks don't cause a problem with the date."""
        date_time = LocalDateTime(1975, 11, 8, 12, 5, 23)
        expected = LocalTime(12, 5, 23)
        assert date_time.time_of_day == expected

    def test_date_before_1970(self) -> None:
        """Verifies that negative local instant ticks don't cause a problem with the date."""
        date_time = LocalDateTime(1965, 11, 8, 12, 5, 23)
        expected = LocalDate(1965, 11, 8)
        assert date_time.date == expected

    def test_date_after_1970(self) -> None:
        """Verifies that positive local instant ticks don't cause a problem with the date."""
        date_time = LocalDateTime(1975, 11, 8, 12, 5, 23)
        expected = LocalDate(1975, 11, 8)
        assert date_time.date == expected

    # TODO: def test_day_of_week_around_epoch(self) -> None: [requires bcl]

    def test_clock_hour_of_half_day(self) -> None:
        assert LocalDateTime(1975, 11, 8, 0, 0, 0).clock_hour_of_half_day == 12
        assert LocalDateTime(1975, 11, 8, 1, 0, 0).clock_hour_of_half_day == 1
        assert LocalDateTime(1975, 11, 8, 12, 0, 0).clock_hour_of_half_day == 12
        assert LocalDateTime(1975, 11, 8, 13, 0, 0).clock_hour_of_half_day == 1
        assert LocalDateTime(1975, 11, 8, 23, 0, 0).clock_hour_of_half_day == 11

    def test_operators_same_calendar(self) -> None:
        value1 = LocalDateTime(2011, 1, 2, 10, 30, 0)
        value2 = LocalDateTime(2011, 1, 2, 10, 30, 0)
        value3 = LocalDateTime(2011, 1, 2, 10, 45, 0)
        helpers.test_operator_comparison_equality(value1, value2, value3)

    def test_operator_different_calendars_throws(self) -> None:
        value1 = LocalDateTime(2011, 1, 2, 10, 30)
        value2 = LocalDateTime(2011, 1, 2, 10, 30, calendar=CalendarSystem.julian)

        assert not value1 == value2
        assert value1 != value2

        with pytest.raises(ValueError):  # ArgumentException in Noda Time
            value1 < value2
        with pytest.raises(ValueError):
            value1 <= value2
        with pytest.raises(ValueError):
            value1 > value2
        with pytest.raises(ValueError):
            value1 >= value2

    def test_compare_to_same_calendar(self) -> None:
        value1 = LocalDateTime(2011, 1, 2, 10, 30)
        value2 = LocalDateTime(2011, 1, 2, 10, 30)
        value3 = LocalDateTime(2011, 1, 2, 10, 45)

        assert value1.compare_to(value2) == 0
        assert value1.compare_to(value3) < 0
        assert value3.compare_to(value2) > 0

    def test_compare_to_different_calendars_throws(self) -> None:
        islamic = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL)
        value1 = LocalDateTime(2011, 1, 2, 10, 30)
        value2 = LocalDateTime(2011, 1, 2, 10, 30, calendar=islamic)

        with pytest.raises(ValueError):  # ArgumentException in Noda Time
            value1.compare_to(value2)

    # The `IComparableCompareTo_SameCalendar` test is redundant here.

    def test_icomparable_compare_to_null_positive(self) -> None:
        instance = LocalDateTime(2012, 3, 5, 10, 45)
        result = instance.compare_to(None)
        assert result > 0

    def test_icomparable_compare_to_wrong_type_argument_exception(self) -> None:
        instance = LocalDateTime(2012, 3, 5, 10, 45)
        arg = LocalDate(2012, 3, 6)
        with pytest.raises(TypeError):
            instance.compare_to(arg)  # type: ignore[arg-type]

    def test_with_offset(self) -> None:
        offset = Offset.from_hours_and_minutes(5, 10)
        local_date_time = LocalDateTime(2009, 12, 22, 21, 39, 30)
        offset_date_time = local_date_time.with_offset(offset)
        assert offset_date_time.local_date_time == local_date_time

    def test_in_utc(self) -> None:
        local = LocalDateTime(2009, 12, 22, 21, 39, 30)
        zoned = local.in_utc()
        assert zoned.local_date_time == local
        assert zoned.offset == Offset.zero
        assert zoned.zone is DateTimeZone.utc

    def test_in_zone_strictly_in_winter(self) -> None:
        local = LocalDateTime(2009, 12, 22, 21, 39, 30)
        zoned = local.in_zone_strictly(PACIFIC)
        assert zoned.local_date_time == local
        assert zoned.offset == Offset.from_hours(-8)

    def test_in_zone_strictly_in_summer(self) -> None:
        local = LocalDateTime(2009, 6, 22, 21, 39, 30)
        zoned = local.in_zone_strictly(PACIFIC)
        assert zoned.local_date_time == local
        assert zoned.offset == Offset.from_hours(-7)

    def test_in_zone_strictly_throws_when_ambiguous(self) -> None:
        """Pacific time changed from -7 to -8 at 2am wall time on November 2nd 2009, so 2am became 1am."""
        local = LocalDateTime(2009, 11, 1, 1, 30, 0)
        with pytest.raises(AmbiguousTimeError):
            local.in_zone_strictly(PACIFIC)

    def test_in_zone_strictly_throws_when_skipped(self) -> None:
        """Pacific time changed from -8 to -7 at 2am wall time on March 8th 2009, so 2am became 3am.

        This means that 2.30am doesn't exist on that day.
        """
        local = LocalDateTime(2009, 3, 8, 2, 30, 0)
        with pytest.raises(SkippedTimeError):
            local.in_zone_strictly(PACIFIC)

    def test_in_zone_leniently_ambiguous_time_returns_earlier_mapping(self) -> None:
        """Pacific time changed from -7 to -8 at 2am wall time on November 2nd 2009, so 2am became 1am.

        We'll return the earlier result, i.e. with the offset of -7
        """
        local = LocalDateTime(2009, 11, 1, 1, 30, 0)
        zoned = local.in_zone_leniently(PACIFIC)
        assert zoned.local_date_time == local
        assert zoned.offset == Offset.from_hours(-7)

    def test_in_zone_leniently_returns_start_of_second_interval(self) -> None:
        """Pacific time changed from -8 to -7 at 2am wall time on March 8th 2009, so 2am became 3am.

        This means that 2:30am doesn't exist on that day. We'll return 3:30am, the forward-shifted value.
        """
        local = LocalDateTime(2009, 3, 8, 2, 30, 0)
        zoned = local.in_zone_leniently(PACIFIC)
        assert zoned.local_date_time == LocalDateTime(2009, 3, 8, 3, 30, 0)
        assert zoned.offset == Offset.from_hours(-7)

    def test_in_zone(self) -> None:
        # Don't need much for this - it only delegates.
        ambiguous = LocalDateTime()
        skipped = LocalDateTime()
        assert ambiguous.in_zone(PACIFIC, Resolvers.lenient_resolver) == PACIFIC.at_leniently(ambiguous)
        assert skipped.in_zone(PACIFIC, Resolvers.lenient_resolver) == PACIFIC.at_leniently(skipped)

    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to January 1st 1970, midnight, UTC, ISO calendar."""
        actual = LocalDateTime()
        assert actual == LocalDateTime(1, 1, 1, 0, 0)

    # TODO:
    #  XmlSerialization_Iso
    #  XmlSerialization_NonIso
    #  XmlSerialization_Invalid
    #  XmlSerialization_Invalid

    def test_min_max_different_calendars_throws(self) -> None:
        ldt1 = LocalDateTime(2011, 1, 2, 2, 20)
        ldt2 = LocalDateTime(1500, 1, 1, 5, 10, calendar=CalendarSystem.julian)

        with pytest.raises(ValueError):
            LocalDateTime.max(ldt1, ldt2)
        with pytest.raises(ValueError):
            LocalDateTime.min(ldt1, ldt2)

    def test_min_max_same_calendar(self) -> None:
        ldt1 = LocalDateTime(1500, 1, 1, 7, 20, calendar=CalendarSystem.julian)
        ldt2 = LocalDateTime(1500, 1, 1, 5, 10, calendar=CalendarSystem.julian)

        assert LocalDateTime.max(ldt1, ldt2) == ldt1
        assert LocalDateTime.max(ldt2, ldt1) == ldt1
        assert LocalDateTime.min(ldt1, ldt2) == ldt2
        assert LocalDateTime.min(ldt2, ldt1) == ldt2

    # TODO: Deconstruction (see Pyoda Time issue 248)

    def test_equality(self) -> None:
        value = LocalDateTime(2017, 10, 15, 21, 30, 0, 0, calendar=CalendarSystem.iso)
        equal_value = LocalDateTime(2017, 10, 15, 21, 30, 0, 0, calendar=CalendarSystem.iso)
        unequal_values = [
            LocalDateTime(2018, 10, 15, 21, 30, 0, 0, CalendarSystem.iso),
            LocalDateTime(2017, 11, 15, 21, 30, 0, 0, CalendarSystem.iso),
            LocalDateTime(2017, 10, 16, 21, 30, 0, 0, CalendarSystem.iso),
            LocalDateTime(2017, 10, 15, 22, 30, 0, 0, CalendarSystem.iso),
            LocalDateTime(2017, 10, 15, 21, 31, 0, 0, CalendarSystem.iso),
            LocalDateTime(2017, 10, 15, 21, 30, 1, 0, CalendarSystem.iso),
            LocalDateTime(2017, 10, 15, 21, 30, 0, 1, CalendarSystem.iso),
            LocalDateTime(2017, 10, 15, 21, 30, 0, 0, CalendarSystem.gregorian),
        ]
        helpers.test_equals_struct(
            value,
            equal_value,
            *unequal_values,
        )

    def test_max_iso_value(self) -> None:
        value = LocalDateTime.max_iso_value
        assert value.calendar == CalendarSystem.iso
        with pytest.raises(OverflowError):
            value.plus_nanoseconds(1)

    def test_min_iso_value(self) -> None:
        value = LocalDateTime.min_iso_value
        assert value.calendar == CalendarSystem.iso
        with pytest.raises(OverflowError):
            value.plus_nanoseconds(-1)


class TestLocalDateTimePseudomutators:
    def test_plus_year_simple(self) -> None:
        start = LocalDateTime(2011, 6, 26, 12, 15, 8)
        expected = LocalDateTime(2016, 6, 26, 12, 15, 8)
        assert start.plus_years(5) == expected

        expected = LocalDateTime(2006, 6, 26, 12, 15, 8)
        assert start.plus_years(-5) == expected

    def test_assert_plus_year_leap_to_non_leap(self) -> None:
        start = LocalDateTime(2012, 2, 29, 12, 15, 8)
        expected = LocalDateTime(2013, 2, 28, 12, 15, 8)
        assert start.plus_years(1) == expected

        expected = LocalDateTime(2011, 2, 28, 12, 15, 8)
        assert start.plus_years(-1) == expected

    def test_plus_year_leap_to_leap(self) -> None:
        start = LocalDateTime(2012, 2, 29, 12, 15, 8)
        expected = LocalDateTime(2016, 2, 29, 12, 15, 8)
        assert start.plus_years(4) == expected

    def test_plus_month_simple(self) -> None:
        start = LocalDateTime(2012, 4, 15, 12, 15, 8)
        expected = LocalDateTime(2012, 8, 15, 12, 15, 8)
        assert start.plus_months(4) == expected

    def test_plus_month_changing_year(self) -> None:
        start = LocalDateTime(2012, 10, 15, 12, 15, 8)
        expected = LocalDateTime(2013, 2, 15, 12, 15, 8)
        assert start.plus_months(4) == expected

    def test_plus_month_with_truncation(self) -> None:
        start = LocalDateTime(2011, 1, 30, 12, 15, 8)
        expected = LocalDateTime(2011, 2, 28, 12, 15, 8)
        assert start.plus_months(1) == expected

    def test_plus_days_simple(self) -> None:
        start = LocalDateTime(2011, 1, 15, 12, 15, 8)
        expected = LocalDateTime(2011, 1, 23, 12, 15, 8)
        assert start.plus_days(8) == expected

        expected = LocalDateTime(2011, 1, 7, 12, 15, 8)
        assert start.plus_days(-8) == expected

    def test_plus_days_month_boundary(self) -> None:
        start = LocalDateTime(2011, 1, 26, 12, 15, 8)
        expected = LocalDateTime(2011, 2, 3, 12, 15, 8)
        assert start.plus_days(8) == expected

        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_year_boundary(self) -> None:
        start = LocalDateTime(2011, 12, 26, 12, 15, 8)
        expected = LocalDateTime(2012, 1, 3, 12, 15, 8)
        assert start.plus_days(8) == expected

        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_end_of_february_in_leap_year(self) -> None:
        start = LocalDateTime(2012, 2, 26, 12, 15, 8)
        expected = LocalDateTime(2012, 3, 5, 12, 15, 8)
        assert start.plus_days(8) == expected
        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_days_end_of_february_not_in_leap_year(self) -> None:
        start = LocalDateTime(2011, 2, 26, 12, 15, 8)
        expected = LocalDateTime(2011, 3, 6, 12, 15, 8)
        assert start.plus_days(8) == expected

        # Round-trip back across the boundary
        assert start.plus_days(8).plus_days(-8) == start

    def test_plus_weeks_simple(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 23, 12, 15, 8)
        expected_backward = LocalDateTime(2011, 3, 12, 12, 15, 8)
        assert start.plus_weeks(3) == expected_forward
        assert start.plus_weeks(-3) == expected_backward

    def test_plus_hours_simple(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 2, 14, 15, 8)
        expected_backward = LocalDateTime(2011, 4, 2, 10, 15, 8)
        assert start.plus_hours(2) == expected_forward
        assert start.plus_hours(-2) == expected_backward

    def test_plus_hours_crossing_day_boundary(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected = LocalDateTime(2011, 4, 3, 8, 15, 8)
        assert start.plus_hours(20) == expected
        assert start.plus_hours(20).plus_hours(-20) == start

    def test_plus_hours_crossing_year_boundary(self) -> None:
        # Christmas day + 10 days and 1 hour
        start = LocalDateTime(2011, 12, 25, 12, 15, 8)
        expected = LocalDateTime(2012, 1, 4, 13, 15, 8)
        assert start.plus_hours(241) == expected
        assert start.plus_hours(241).plus_hours(-241) == start

    def test_plus_minutes_simple(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 2, 12, 17, 8)
        expected_backward = LocalDateTime(2011, 4, 2, 12, 13, 8)
        assert start.plus_minutes(2) == expected_forward
        assert start.plus_minutes(-2) == expected_backward

    def test_plus_seconds_simple(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 2, 12, 15, 18)
        expected_backward = LocalDateTime(2011, 4, 2, 12, 14, 58)
        assert start.plus_seconds(10) == expected_forward
        assert start.plus_seconds(-10) == expected_backward

    def test_plus_milliseconds_simple(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8, 300)
        expected_forward = LocalDateTime(2011, 4, 2, 12, 15, 8, 700)
        expected_backward = LocalDateTime(2011, 4, 2, 12, 15, 7, 900)
        assert start.plus_milliseconds(400) == expected_forward
        assert start.plus_milliseconds(-400) == expected_backward

    def test_plus_ticks_simple(self) -> None:
        date = LocalDate(2011, 4, 2)
        start_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 7500)
        expected_forward_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 301, 1500)
        expected_backward_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 3500)
        assert (date + start_time).plus_ticks(4000) == date + expected_forward_time
        assert (date + start_time).plus_ticks(-4000) == date + expected_backward_time

    def test_plus_ticks_long(self) -> None:
        assert PyodaConstants.TICKS_PER_DAY > _CsharpConstants.INT_MAX_VALUE
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 3, 12, 15, 8)
        expected_backward = LocalDateTime(2011, 4, 1, 12, 15, 8)

        assert start.plus_ticks(PyodaConstants.TICKS_PER_DAY) == expected_forward
        assert start.plus_ticks(-PyodaConstants.TICKS_PER_DAY) == expected_backward

    def test_plus_nanoseconds_simple(self) -> None:
        # Just use the ticks values
        date = LocalDate(2011, 4, 2)
        start_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 7500)
        expected_forward_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 7540)
        expected_backward_time = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 7460)
        assert (date + start_time).plus_nanoseconds(4000) == date + expected_forward_time
        assert (date + start_time).plus_nanoseconds(-4000) == date + expected_backward_time

    def test_plus_ticks_crossing_day(self) -> None:
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        expected_forward = LocalDateTime(2011, 4, 3, 12, 15, 8)
        expected_backward = LocalDateTime(2011, 4, 1, 12, 15, 8)
        assert start.plus_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY) == expected_forward
        assert start.plus_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY) == expected_backward

    def test_plus_full_period(self) -> None:
        # Period deliberately chosen to require date rollover
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        period = PeriodBuilder(
            years=1, months=2, weeks=3, days=4, hours=15, minutes=6, seconds=7, milliseconds=8, ticks=9, nanoseconds=11
        ).build()
        actual = start.plus(period)
        expected = LocalDateTime(2012, 6, 28, 3, 21, 15).plus_nanoseconds(8000911)
        assert actual == expected, f"{expected:uuuu-MM-dd HH:mm:ss.fffffffff} != {actual:uuuu-MM-dd HH:mm:ss.fffffffff}"

    def test_minus_full_period(self) -> None:
        # Period deliberately chosen to require date rollover
        start = LocalDateTime(2011, 4, 2, 12, 15, 8)
        period = PeriodBuilder(
            years=1, months=2, weeks=3, days=4, hours=15, minutes=6, seconds=7, milliseconds=8, ticks=9, nanoseconds=11
        ).build()
        actual = start.minus(period)
        expected = LocalDateTime(2010, 1, 7, 21, 9, 0).plus_nanoseconds(991999089)
        assert actual == expected, f"{expected:uuuu-MM-dd HH:mm:ss.fffffffff} != {actual:uuuu-MM-dd HH:mm:ss.fffffffff}"

    @pytest.mark.parametrize(
        ("day_of_month", "target_day_of_week", "expected"),
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
    def test_next(self, day_of_month: int, target_day_of_week: IsoDayOfWeek, expected: int) -> None:
        """Each test case gives a day-of-month in November 2011 and a target "next day of week"; the result is the next
        day-of-month in November 2011 with that target day.

        The tests are picked somewhat arbitrarily...
        """
        start = LocalDateTime(2011, 11, day_of_month, 15, 25, 30).plus_nanoseconds(123456789)
        target = start.next(target_day_of_week)
        assert target.year == 2011
        assert target.month == 11
        assert target.time_of_day == start.time_of_day
        assert target.day == expected

    # TODO: def test_next_invalid_argument(self, target_day_of_week: IsoDayOfWeek) -> None:

    @pytest.mark.parametrize(
        ("day_of_month", "target_day_of_week", "expected"),
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
    def test_previous(self, day_of_month: int, target_day_of_week: IsoDayOfWeek, expected: int) -> None:
        """Each test case gives a day-of-month in November 2011 and a target "next day of week"; the result is the next
        day-of-month in November 2011 with that target day."""
        start = LocalDateTime(2011, 11, day_of_month, 15, 25, 30).plus_nanoseconds(123456789)
        target = start.previous(target_day_of_week)
        assert target.year == 2011
        assert target.month == 11
        assert target.time_of_day == start.time_of_day
        assert target.day == expected

    # TODO: def test_previous_invalid_argument(self, target_day_of_week: IsoDayOfWeek) -> None:

    # No tests for non-ISO-day-of-week calendars as we don't have any yet.

    def test_operator_method_equivalents(self) -> None:
        start = LocalDateTime(2011, 1, 1, 15, 25, 30).plus_nanoseconds(123456789)
        period = Period.from_hours(1) + Period.from_days(1)
        end: LocalDateTime = start + period
        assert LocalDateTime.add(start, period) == start + period
        assert start.plus(period) == start + period
        assert LocalDateTime.subtract(start, period) == start - period
        assert start.minus(period) == start - period
        assert end - start == period
        assert LocalDateTime.subtract(end, start) == period
        assert end.minus(start) == period

    def test_with_time_adjuster(self) -> None:
        start = LocalDateTime(2014, 6, 27, 12, 15, 8).plus_nanoseconds(123456789)
        expected = LocalDateTime(2014, 6, 27, 12, 15, 8)
        assert start.with_time_adjuster(TimeAdjusters.truncate_to_second) == expected

    def test_with_date_adjuster(self) -> None:
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789)
        expected = LocalDateTime(2014, 6, 30, 12, 5, 8).plus_nanoseconds(123456789)
        assert start.with_date_adjuster(DateAdjusters.end_of_month) == expected

    @pytest.mark.parametrize(
        ("year", "month", "day", "hours"),
        [
            (-9998, 1, 1, -1),
            (9999, 12, 31, 24),
            (1970, 1, 1, _CsharpConstants.LONG_MAX_VALUE),
            (1970, 1, 1, _CsharpConstants.LONG_MIN_VALUE),
        ],
    )
    def test_plus_hours_overflow(self, year: int, month: int, day: int, hours: int) -> None:
        helpers.assert_overflow(LocalDateTime(year, month, day, 0, 0).plus_hours, hours)
