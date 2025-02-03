# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import datetime, timedelta, timezone
from typing import Final

import pytest

from pyoda_time import (
    CalendarSystem,
    DateAdjusters,
    DateTimeZone,
    DateTimeZoneProviders,
    Duration,
    Instant,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    OffsetDate,
    OffsetDateTime,
    OffsetTime,
    PyodaConstants,
    TimeAdjusters,
    ZonedDateTime,
)
from tests import helpers
from tests.test_offset_time import get_class_properties


class TestOffsetDateTime:
    @pytest.mark.parametrize(
        "property_name",
        [name for name in get_class_properties(OffsetDateTime) if name in get_class_properties(LocalDateTime)],
    )
    def test_local_date_time_properties(self, property_name: str) -> None:
        local = LocalDateTime(2012, 6, 19, 1, 2, 3, calendar=CalendarSystem.julian).plus_nanoseconds(123456789)
        offset = Offset.from_hours(5)
        odt = OffsetDateTime(local, offset)

        actual = getattr(odt, property_name)
        expected = getattr(local, property_name)

        assert actual == expected

    def test_offset_property(self) -> None:
        offset = Offset.from_hours(5)

        odt = OffsetDateTime(LocalDateTime(2012, 1, 2, 3, 4), offset)
        assert odt.offset == offset

    def test_local_date_time_property(self) -> None:
        local = LocalDateTime(2012, 6, 19, 1, 2, 3, calendar=CalendarSystem.julian).plus_nanoseconds(123456789)
        offset = Offset.from_hours(5)

        odt = OffsetDateTime(local, offset)
        assert odt.local_date_time == local

    def test_to_instant(self) -> None:
        instant = Instant.from_utc(2012, 6, 25, 16, 5, 20)
        local = LocalDateTime(2012, 6, 25, 21, 35, 20)
        offset = Offset.from_hours_and_minutes(5, 30)

        odt = OffsetDateTime(local, offset)
        assert odt.to_instant() == instant

    def test_equality(self) -> None:
        local1 = LocalDateTime(2012, 10, 6, 1, 2, 3)
        local2 = LocalDateTime(2012, 9, 5, 1, 2, 3)
        offset1 = Offset.from_hours(1)
        offset2 = Offset.from_hours(2)

        equal1 = OffsetDateTime(local1, offset1)
        equal2 = OffsetDateTime(local1, offset1)
        unequal_by_offset = OffsetDateTime(local1, offset2)
        unequal_by_local = OffsetDateTime(local2, offset1)

        helpers.test_equals_struct(equal1, equal2, unequal_by_offset)
        helpers.test_equals_struct(equal1, equal2, unequal_by_local)

        helpers.test_operator_equality(equal1, equal2, unequal_by_offset)
        helpers.test_operator_equality(equal1, equal2, unequal_by_local)

    def test_to_date_time_offset(self) -> None:
        local = LocalDateTime(2012, 10, 6, 1, 2, 3)
        offset = Offset.from_hours(1)
        odt = OffsetDateTime(local, offset)

        expected = datetime(2012, 10, 6, 1, 2, 3, tzinfo=timezone(offset=timedelta(hours=1)))
        actual = odt.to_aware_datetime()
        assert actual == expected

    def test_to_date_time_offset_julian_calendar(self) -> None:
        local = LocalDateTime(2012, 10, 6, 1, 2, 3, calendar=CalendarSystem.julian)
        offset = Offset.from_hours(1)
        odt = OffsetDateTime(local, offset)

        # Different to Noda Time:
        # Python's datetime does not support different calendar systems (unlike .NET's DateTime[Offset]),
        # so there is an implicit conversion to the gregorian calendar in Pyoda Time.
        expected = datetime(2012, 10, 19, 1, 2, 3, tzinfo=timezone(offset=timedelta(hours=1)))
        actual = odt.to_aware_datetime()
        assert actual == expected

    @pytest.mark.parametrize(
        ("hours", "minutes", "seconds"),
        [
            (0, 30, 20),
            (-1, -30, -20),
            (0, 30, 55),
            (-1, -30, -55),
        ],
    )
    def test_to_date_time_offset_truncated_offset(self, hours: int, minutes: int, seconds: int) -> None:
        # Different to Noda Time:
        # The Noda Time test documents that conversions to DateTimeOffset in .NET necessarily truncate the offset,
        # because TimeSpan has a resolution of minutes (whereas Noda Time has a resolution of seconds).
        # In Python, the converted offsets use timedelta which has microsecond granularity.
        # For Pyoda Time, this test is just more coverage for the conversion; no truncation takes place.

        ldt = LocalDateTime(2017, 1, 9, 21, 45, 20)
        offset = Offset.from_hours_and_minutes(hours, minutes).plus(Offset.from_seconds(seconds))
        odt = ldt.with_offset(offset)
        dto = odt.to_aware_datetime()

        assert dto == datetime(
            2017, 1, 9, 21, 45, 20, tzinfo=timezone(offset=timedelta(hours=hours, minutes=minutes, seconds=seconds))
        )

    @pytest.mark.xfail(
        reason=(
            "Python's datetime supports offsets of strictly between -24 and 24 hrs (timedelta), "
            "unlike dotnet's DateTimeOffset which supports -14 to 14 (TimeSpan)"
        )
    )
    @pytest.mark.parametrize("hours", [-15, 15])
    def test_to_date_time_offset_offset_out_of_range(self, hours: int) -> None:
        # TODO: This passes in Noda Time because DateTimeOffset supports an offset (TimeSpan) range of -14 and 14 hours.
        #  But in Python, datetime may have an offset (timedelta) of strictly between -24 and 24 hours.
        #  See also: the test directly below this one.
        ldt = LocalDateTime(2017, 1, 9, 21, 45, 20)
        offset = Offset.from_hours(hours)
        odt = ldt.with_offset(offset)

        with pytest.raises(RuntimeError):
            odt.to_aware_datetime()

    @pytest.mark.parametrize("hours", [-14, 14])
    def test_to_date_time_offset_offset_edge_of_range(self, hours: int) -> None:
        # TODO: This is not the "edge of range" for the min/max timedelta in python.
        #  See also: The test directly above this one.
        ldt = LocalDateTime(2017, 1, 9, 21, 45, 20)
        offset = Offset.from_hours(hours)
        odt = ldt.with_offset(offset)
        assert odt.to_aware_datetime().tzinfo.utcoffset(None).total_seconds() / 60 / 60 == hours  # type: ignore[union-attr]

    def test_to_date_time_offset_date_out_of_range(self) -> None:
        # One day before 1st January, 1AD (which is DateTime.MinValue)
        odt = LocalDate(1, 1, 1).plus_days(-1).at_midnight().with_offset(Offset.from_hours(1))
        with pytest.raises(RuntimeError):
            odt.to_aware_datetime()

    @pytest.mark.parametrize("year", [100, 1900, 2900])
    def test_to_date_time_offset_truncate_nanos_toward_start_of_time(self, year: int) -> None:
        # Different to Noda Time:
        # Pyoda Time truncates to the millisecond, not to the tick.
        odt = (
            LocalDateTime(year, 1, 1, 13, 15, 55)
            .plus_nanoseconds(PyodaConstants.NANOSECONDS_PER_SECOND - 1)
            .with_offset(Offset.from_hours(1))
        )
        expected = datetime(year, 1, 1, 13, 15, 55, tzinfo=timezone(timedelta(hours=1))) + timedelta(
            microseconds=PyodaConstants.MICROSECONDS_PER_SECOND - 1
        )
        actual = odt.to_aware_datetime()
        assert actual == expected

    def test_from_date_time_offset(self) -> None:
        local = LocalDateTime(2012, 10, 6, 1, 2, 3)
        offset = Offset.from_hours(1)
        expected = OffsetDateTime(local, offset)

        stdlib = datetime(2012, 10, 6, 1, 2, 3, tzinfo=timezone(offset=timedelta(hours=1)))
        actual = OffsetDateTime.from_aware_datetime(stdlib)
        assert actual == expected

    def test_from_aware_datetime_raises_when_datetime_is_not_aware(self) -> None:
        # This test does not exist in Noda Time, because DateTimeOffset always has an offset/timespan.
        # In Python, we have one type (datetime) which may or may not be "aware".
        dt = datetime(2025, 2, 3)
        with pytest.raises(ValueError) as e:
            OffsetDateTime.from_aware_datetime(dt)
        assert str(e.value) == "aware_datetime must be timezone-aware"

    def test_from_aware_datetime_with_microsecond_granularity_offset(self) -> None:
        # This test does not exist in Noda Time, because DateTimeOffset's offset/timespan has minute granularity.
        # In Python, datetime.tzinfo's offset can have microsecond granularity.
        # (Both Noda Time and Pyoda Time have second granularity)
        dt = datetime(
            2025,
            2,
            3,
            3,
            11,
            30,
            tzinfo=timezone(offset=timedelta(hours=1, minutes=2, seconds=3, milliseconds=4, microseconds=5)),
        )
        actual = OffsetDateTime.from_aware_datetime(dt)
        expected = OffsetDateTime(
            local_date_time=LocalDateTime(2025, 2, 3, 3, 11, 30),
            offset=Offset.from_hours_and_minutes(1, 2)
            + Offset.from_seconds(3)
            + Offset.from_milliseconds(4)
            + Offset.from_ticks(5 * PyodaConstants.TICKS_PER_MICROSECOND),
        )
        assert actual == expected

    def test_in_fixed_zone(self) -> None:
        offset = Offset.from_hours(5)
        local = LocalDateTime(2012, 1, 2, 3, 4)
        odt = OffsetDateTime(local, offset)

        zoned = odt.in_fixed_zone()
        assert zoned == DateTimeZone.for_offset(offset).at_strictly(local)

    # TODO: [requires OffsetDateTimePattern]
    #  def test_to_string_whole_hour_offset(self) -> None:
    #  def test_to_string_part_hour_offset(self) -> None:
    #  def test_to_string_utc(self) -> None:
    #  def test_to_string_with_format(self) -> None:

    # TODO:  [requires OffsetDateTime.Comparer]
    #  def test_local_comparer(self) -> None:
    #  def test_instant_comparer(self) -> None:

    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to January 1st 1970, midnight, UTC, ISO calendar."""
        actual = OffsetDateTime()
        assert actual.local_date_time == LocalDateTime(1, 1, 1, 0, 0)
        assert actual.offset == Offset.zero

    def test_subtraction_duration(self) -> None:
        # Test all three approaches... not bothering to check a different calendar,
        # but we'll use two different offsets.
        end = LocalDateTime(2014, 8, 14, 15, 0).with_offset(Offset.from_hours(1))
        duration = Duration.from_hours(8) + Duration.from_minutes(9)
        expected = LocalDateTime(2014, 8, 14, 6, 51).with_offset(Offset.from_hours(1))
        assert end - duration == expected
        assert end.minus(duration) == expected
        assert OffsetDateTime.subtract(end, duration) == expected

    def test_addition_duration(self) -> None:
        minutes: Final[int] = 23
        hours: Final[int] = 3
        milliseconds: Final[int] = 40000
        seconds: Final[int] = 321
        nanoseconds: Final[int] = 12345
        ticks: Final[int] = 5432112345

        # Test all three approaches... not bothering to check a different calendar,
        # but we'll use two different offsets.
        start = LocalDateTime(2014, 8, 14, 6, 51).with_offset(Offset.from_hours(1))
        duration = Duration.from_hours(8) + Duration.from_minutes(9)
        expected = LocalDateTime(2014, 8, 14, 15, 0).with_offset(Offset.from_hours(1))

        assert start + duration == expected
        assert start.plus(duration) == expected
        assert OffsetDateTime.add(start, duration) == expected

        assert start.plus_hours(hours) == start + Duration.from_hours(hours)
        assert start.plus_hours(-hours) == start + Duration.from_hours(-hours)

        assert start.plus_minutes(minutes) == start + Duration.from_minutes(minutes)
        assert start.plus_minutes(-minutes) == start + Duration.from_minutes(-minutes)

        assert start.plus_seconds(seconds) == start + Duration.from_seconds(seconds)
        assert start.plus_seconds(-seconds) == start + Duration.from_seconds(-seconds)

        assert start.plus_milliseconds(milliseconds) == start + Duration.from_milliseconds(milliseconds)
        assert start.plus_milliseconds(-milliseconds) == start + Duration.from_milliseconds(-milliseconds)

        assert start.plus_ticks(ticks) == start + Duration.from_ticks(ticks)
        assert start.plus_ticks(-ticks) == start + Duration.from_ticks(-ticks)

        assert start.plus_nanoseconds(nanoseconds) == start + Duration.from_nanoseconds(nanoseconds)
        assert start.plus_nanoseconds(-nanoseconds) == start + Duration.from_nanoseconds(-nanoseconds)

    def test_subtraction_offset_date_time(self) -> None:
        # Test all three approaches... not bothering to check a different calendar,
        # but we'll use two different offsets.
        start = LocalDateTime(2014, 8, 14, 6, 51).with_offset(Offset.from_hours(1))
        end = LocalDateTime(2014, 8, 14, 18, 0).with_offset(Offset.from_hours(4))
        expected = Duration.from_hours(8) + Duration.from_minutes(9)
        assert end - start == expected
        assert end.minus(start) == expected
        assert OffsetDateTime.subtract(end, start) == expected

    # TODO:
    #  XmlSerialization_Iso
    #  XmlSerialization_ZeroOffset
    #  XmlSerialization_NonIso
    #  XmlSerialization_Invalid

    def test_with_offset(self) -> None:
        morning = LocalDateTime(2014, 1, 31, 9, 30)
        original = OffsetDateTime(morning, Offset.from_hours(-8))
        evening = LocalDateTime(2014, 1, 31, 19, 30)
        new_offset = Offset.from_hours(2)
        expected = OffsetDateTime(evening, new_offset)
        assert original.with_offset(new_offset) == expected

    def test_with_offset_cross_dates(self) -> None:
        noon = OffsetDateTime(LocalDateTime(2017, 8, 22, 12, 0, 0), Offset.from_hours(0))
        previous_night = noon.with_offset(Offset.from_hours(-14))
        next_morning = noon.with_offset(Offset.from_hours(14))
        assert previous_night.local_date_time == LocalDateTime(2017, 8, 21, 22, 0, 0)
        assert next_morning.local_date_time == LocalDateTime(2017, 8, 23, 2, 0, 0)

    def test_with_offset_two_days_forward_and_back(self) -> None:
        # Go from UTC-18 to UTC+18
        night = OffsetDateTime(LocalDateTime(2017, 8, 21, 18, 0, 0), Offset.from_hours(-18))
        morning = night.with_offset(Offset.from_hours(18))
        assert morning.local_date_time == LocalDateTime(2017, 8, 23, 6, 0, 0)
        back_again = morning.with_offset(Offset.from_hours(-18))
        assert back_again == night

    def test_with_calendar(self) -> None:
        julian_calendar = CalendarSystem.julian
        gregorian_epoch = PyodaConstants.UNIX_EPOCH.with_offset(Offset.zero)

        expected = LocalDate(1969, 12, 19, calendar=julian_calendar).at_midnight().with_offset(Offset.from_hours(0))
        actual = gregorian_epoch.with_calendar(CalendarSystem.julian)
        assert actual == expected

    def test_with_time_adjuster(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = LocalDateTime(2014, 6, 27, 12, 5, 8).with_offset(offset)
        assert start.with_time_adjuster(TimeAdjusters.truncate_to_second) == expected

    def test_with_date_adjuster(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = LocalDateTime(2014, 6, 30, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        assert start.with_date_adjuster(DateAdjusters.end_of_month) == expected

    def test_in_zone(self) -> None:
        offset = Offset.from_hours(-7)
        start = LocalDateTime(2017, 10, 31, 18, 12, 0).with_offset(offset)
        zone = DateTimeZoneProviders.tzdb["Europe/London"]
        zoned = start.in_zone(zone)

        # On October 31st, the UK had already gone back, so the offset is 0.
        # Importantly, it's not the offset of the original OffsetDateTime: we're testing
        # that InZone *doesn't* require that.
        expected = ZonedDateTime._ctor(
            offset_date_time=LocalDateTime(2017, 11, 1, 1, 12, 0).with_offset(Offset.zero), zone=zone
        )
        assert zoned == expected

    # TODO:
    #  Deconstruction
    #  MoreGranularDeconstruction

    def test_to_offset_date(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        odt = LocalDateTime(2014, 6, 27, 12, 15, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = OffsetDate(LocalDate(2014, 6, 27), offset)
        assert odt.to_offset_date() == expected

    def test_to_offset_time(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        odt = LocalDateTime(2014, 6, 27, 12, 15, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = OffsetTime(LocalTime(12, 15, 8).plus_nanoseconds(123456789), offset)
        assert odt.to_offset_time() == expected
