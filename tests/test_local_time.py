# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import datetime, timedelta
from typing import cast

import pytest

from pyoda_time import CalendarSystem, LocalDate, LocalDateTime, LocalTime, Offset, OffsetTime, Period, PyodaConstants
from pyoda_time._time_adjusters import TimeAdjusters
from pyoda_time.utility._csharp_compatibility import _CsharpConstants


class TestLocalTime:
    def test_min_value_equal_to_midnight(self) -> None:
        assert LocalTime.min_value == LocalTime.midnight

    def test_max_value(self) -> None:
        assert LocalTime.max_value.nanosecond_of_day == PyodaConstants.NANOSECONDS_PER_DAY - 1

    def test_clock_hour_of_half_day(self) -> None:
        assert LocalTime(0, 0).clock_hour_of_half_day == 12
        assert LocalTime(1, 0).clock_hour_of_half_day == 1
        assert LocalTime(12, 0).clock_hour_of_half_day == 12
        assert LocalTime(13, 0).clock_hour_of_half_day == 1
        assert LocalTime(23, 0).clock_hour_of_half_day == 11

    def test_default_constructor(self) -> None:
        actual = LocalTime()
        assert actual == LocalTime.midnight

    # TODO:
    #  def test_xml_serialization(self):
    #  def test_xml_serialization_invalid(self):

    def test_max(self) -> None:
        x = LocalTime(5, 10)
        y = LocalTime(6, 20)
        assert LocalTime.max(x, y) == y
        assert LocalTime.max(y, x) == y
        assert LocalTime.max(x, LocalTime.min_value) == x
        assert LocalTime.max(LocalTime.min_value, x) == x
        assert LocalTime.max(LocalTime.max_value, x) == LocalTime.max_value
        assert LocalTime.max(x, LocalTime.max_value) == LocalTime.max_value

    def test_min(self) -> None:
        x = LocalTime(5, 10)
        y = LocalTime(6, 20)
        assert LocalTime.min(x, y) == x
        assert LocalTime.min(y, x) == x
        assert LocalTime.min(x, LocalTime.min_value) == LocalTime.min_value
        assert LocalTime.min(LocalTime.min_value, x) == LocalTime.min_value
        assert LocalTime.min(LocalTime.max_value, x) == x
        assert LocalTime.min(x, LocalTime.max_value) == x

    def test_deconstruction(self) -> None:
        value = LocalTime(15, 8, 20)
        expected_hour = 15
        expected_minute = 8
        expected_second = 20

        actual_hour, actual_minute, actual_second = value

        assert actual_hour == expected_hour
        assert actual_minute == expected_minute
        assert actual_second == expected_second

    def test_with_offset(self) -> None:
        time = LocalTime(3, 45, 12, 34)
        offset = Offset.from_hours(5)
        expected = OffsetTime(time, offset)
        assert time.with_offset(offset) == expected


class TestLocalTimeConstruction:
    @pytest.mark.parametrize(
        "hour,minute",
        [
            (-1, 0),
            (24, 0),
            (0, -1),
            (0, 60),
        ],
    )
    def test_invalid_construction_to_minute(self, hour: int, minute: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime(hour, minute)

    @pytest.mark.parametrize(
        "hour,minute,second",
        [
            (-1, 0, 0),
            (24, 0, 0),
            (0, -1, 0),
            (0, 60, 0),
            (0, 0, 60),
            (0, 0, -1),
        ],
    )
    def test_invalid_construction_to_second(self, hour: int, minute: int, second: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime(hour, minute, second)

    @pytest.mark.parametrize(
        "hour,minute,second,millisecond",
        [
            (-1, 0, 0, 0),
            (24, 0, 0, 0),
            (0, -1, 0, 0),
            (0, 60, 0, 0),
            (0, 0, 60, 0),
            (0, 0, -1, 0),
            (0, 0, 0, -1),
            (0, 0, 0, 1000),
        ],
    )
    def test_invalid_construction_to_millisecond(self, hour: int, minute: int, second: int, millisecond: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime(hour, minute, second, millisecond)

    @pytest.mark.parametrize(
        "hour,minute,second,millisecond,tick",
        [
            (-1, 0, 0, 0, 0),
            (24, 0, 0, 0, 0),
            (0, -1, 0, 0, 0),
            (0, 60, 0, 0, 0),
            (0, 0, 60, 0, 0),
            (0, 0, -1, 0, 0),
            (0, 0, 0, -1, 0),
            (0, 0, 0, 1000, 0),
            (0, 0, 0, 0, -1),
            (0, 0, 0, 0, PyodaConstants.TICKS_PER_MILLISECOND),
        ],
    )
    def test_from_hour_minute_second_millisecond_tick_invalid(
        self, hour: int, minute: int, second: int, millisecond: int, tick: int
    ) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_hour_minute_second_millisecond_tick(hour, minute, second, millisecond, tick)

    @pytest.mark.parametrize(
        "hour,minute,second,tick",
        [
            (-1, 0, 0, 0),
            (24, 0, 0, 0),
            (0, -1, 0, 0),
            (0, 60, 0, 0),
            (0, 0, 60, 0),
            (0, 0, -1, 0),
            (0, 0, 0, -1),
            (0, 0, 0, PyodaConstants.TICKS_PER_SECOND),
        ],
    )
    def test_from_hour_minute_second_tick_invalid(self, hour: int, minute: int, second: int, tick: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_hour_minute_second_tick(hour, minute, second, tick)

    def test_from_hour_minute_second_tick_valid(self) -> None:
        result = LocalTime.from_hour_minute_second_tick(1, 2, 3, PyodaConstants.TICKS_PER_SECOND - 1)
        assert result.hour == 1
        assert result.minute == 2
        assert result.second == 3
        assert result.tick_of_second == PyodaConstants.TICKS_PER_SECOND - 1

    @pytest.mark.parametrize(
        "hour,minute,second,nanosecond",
        [
            (-1, 0, 0, 0),
            (24, 0, 0, 0),
            (0, -1, 0, 0),
            (0, 60, 0, 0),
            (0, 0, 60, 0),
            (0, 0, -1, 0),
            (0, 0, 0, -1),
            (0, 0, 0, PyodaConstants.NANOSECONDS_PER_SECOND),
        ],
    )
    def test_from_hour_minute_second_nanosecond_invalid(
        self, hour: int, minute: int, second: int, nanosecond: int
    ) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_hour_minute_second_nanosecond(hour, minute, second, nanosecond)

    def test_from_nanoseconds_since_midnight_valid(self) -> None:
        assert LocalTime.from_nanoseconds_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_nanoseconds_since_midnight(
            PyodaConstants.NANOSECONDS_PER_DAY - 1
        ) == LocalTime.midnight.plus_nanoseconds(-1)

    def test_from_nanoseconds_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_nanoseconds_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_nanoseconds_since_midnight(PyodaConstants.NANOSECONDS_PER_DAY)

    def test_from_ticks_since_midnight_valid(self) -> None:
        assert LocalTime.from_ticks_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_ticks_since_midnight(
            PyodaConstants.TICKS_PER_DAY - 1
        ) == LocalTime.midnight - Period.from_ticks(1)

    def test_from_ticks_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_ticks_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_ticks_since_midnight(PyodaConstants.TICKS_PER_DAY)

    def test_from_milliseconds_since_midnight_valid(self) -> None:
        assert LocalTime.from_milliseconds_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_milliseconds_since_midnight(
            PyodaConstants.MILLISECONDS_PER_DAY - 1
        ) == LocalTime.midnight - Period.from_milliseconds(1)

    def test_from_milliseconds_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_milliseconds_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_milliseconds_since_midnight(PyodaConstants.MILLISECONDS_PER_DAY)

    def test_from_seconds_since_midnight_valid(self) -> None:
        assert LocalTime.from_seconds_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_seconds_since_midnight(
            PyodaConstants.SECONDS_PER_DAY - 1
        ) == LocalTime.midnight - Period.from_seconds(1)

    def test_from_seconds_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_seconds_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_seconds_since_midnight(PyodaConstants.SECONDS_PER_DAY)

    def test_from_minutes_since_midnight_valid(self) -> None:
        assert LocalTime.from_minutes_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_minutes_since_midnight(
            PyodaConstants.MINUTES_PER_DAY - 1
        ) == LocalTime.midnight - Period.from_minutes(1)

    def test_from_minutes_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_minutes_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_minutes_since_midnight(PyodaConstants.MINUTES_PER_DAY)

    def test_from_hours_since_midnight_valid(self) -> None:
        assert LocalTime.from_hours_since_midnight(0) == LocalTime.midnight
        assert LocalTime.from_hours_since_midnight(
            PyodaConstants.HOURS_PER_DAY - 1
        ) == LocalTime.midnight - Period.from_hours(1)

    def test_from_hours_since_midnight_range_checks(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_hours_since_midnight(-1)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            LocalTime.from_hours_since_midnight(PyodaConstants.HOURS_PER_DAY)


class TestLocalTimeConversion:
    def test_to_time_on_microsecond_boundary(self) -> None:
        local_time = LocalTime(12, 34, 56).plus_microseconds(4567)
        expected = (datetime(1, 1, 1, 12, 34, 56) + timedelta(microseconds=4567)).time()
        actual = local_time.to_time()
        assert actual == expected

    def test_to_time_rounds_down(self) -> None:
        local_time = LocalTime(12, 34, 56).plus_microseconds(4567).plus_nanoseconds(89)
        expected = (datetime(1, 1, 1, 12, 34, 56) + timedelta(microseconds=4567)).time()
        actual = local_time.to_time()
        assert actual == expected

    def test_from_time(self) -> None:
        time_ = (datetime(1, 1, 1, 12, 34, 56) + timedelta(microseconds=4567)).time()
        expected = LocalTime(12, 34, 56).plus_microseconds(4567)
        actual = LocalTime.from_time(time_)
        assert actual == expected


class TestLocalTimeOperators:
    def test_addition_with_period(self) -> None:
        start = LocalTime(3, 30)
        period = Period.from_hours(2) + Period.from_seconds(1)
        expected = LocalTime(5, 30, 1)
        assert start + period == expected

    def test_addition_wraps_at_midnight(self) -> None:
        start = LocalTime(22, 0)
        period = Period.from_hours(3)
        expected = LocalTime(1, 0)
        assert start + period == expected

    def test_addition_with_null_period_raises_type_error(self) -> None:
        start = LocalTime(12, 0)
        with pytest.raises(TypeError):
            start + cast(Period, None)

    def test_subtraction_with_period(self) -> None:
        start = LocalTime(5, 30, 1)
        period = Period.from_hours(2) + Period.from_seconds(1)
        expected = LocalTime(3, 30, 0)
        assert start - period == expected

    def test_subtraction_wraps_at_midnight(self) -> None:
        start = LocalTime(1, 0, 0)
        period = Period.from_hours(3)
        expected = LocalTime(22, 0, 0)
        assert start - period == expected

    def test_subtraction_with_null_period_raises_type_error(self) -> None:
        start = LocalTime(12, 0)
        with pytest.raises(TypeError):
            start - cast(Period, None)

    def test_addition_period_with_date(self) -> None:
        time = LocalTime(20, 30)
        period = Period.from_days(1)
        with pytest.raises(ValueError):
            LocalTime.add(time, period)

    def test_subtraction_period_with_time(self) -> None:
        time = LocalTime(20, 30)
        period = Period.from_days(1)
        with pytest.raises(ValueError):
            LocalTime.subtract(time, period)

    def test_period_addition_method_equivalents(self) -> None:
        start = LocalTime(20, 30)
        period = Period.from_hours(3) + Period.from_minutes(10)
        assert LocalTime.add(start, period) == start + period
        assert start.plus(period) == start + period

    def test_period_subtraction_method_equivalents(self) -> None:
        start = LocalTime(20, 30)
        period = Period.from_hours(3) + Period.from_minutes(10)
        end = start + period
        assert LocalTime.subtract(start, period) == start - period
        assert start.minus(period) == start - period

        assert end - start == period
        assert LocalTime.subtract(end, start) == period
        assert end.minus(start) == period

    def test_comparison_operators(self) -> None:
        time_1 = LocalTime(10, 30, 45)
        time_2 = LocalTime(10, 30, 45)
        time_3 = LocalTime(10, 30, 50)

        assert time_1 == time_2
        assert not time_1 == time_3
        assert not time_1 != time_2
        assert time_1 != time_3

        assert not time_1 < time_2
        assert time_1 < time_3
        assert not time_2 < time_1
        assert not time_3 < time_1

        assert time_1 <= time_2
        assert time_1 <= time_3
        assert time_2 <= time_1
        assert not time_3 <= time_1

        assert not time_1 > time_2
        assert not time_1 > time_3
        assert not time_2 > time_1

        assert time_1 >= time_2
        assert not time_1 >= time_3
        assert time_2 >= time_1
        assert time_3 >= time_1

    def test_comparison_ignores_original_calendar(self) -> None:
        date_time_1 = LocalDateTime(1900, 1, 1, 10, 30, 0)
        date_time_2 = date_time_1.with_calendar(CalendarSystem.julian)

        # Calendar information is propagated into LocalDate, but not into LocalTime
        assert not date_time_1.date == date_time_2.date
        assert date_time_1.time_of_day == date_time_2.time_of_day

    def test_compare_to(self) -> None:
        time_1 = LocalTime(10, 30, 45)
        time_2 = LocalTime(10, 30, 45)
        time_3 = LocalTime(10, 30, 50)

        assert time_1.compare_to(time_2) == 0
        assert time_1.compare_to(time_3) < 0
        assert time_3.compare_to(time_2) > 0

    # TODO: This one is redundant in pyoda time:
    #  `public void IComparableCompareTo()`

    def test_i_comparable_to_null_positive(self) -> None:
        instance = LocalTime(10, 30, 45)
        result = instance.compare_to(None)
        assert result > 0

    def test_i_comparable_compare_to_wrong_type_argument_exception(self) -> None:
        # TODO: This is necessarily different to Noda Time, but still worth doing.
        instance = LocalTime(10, 30, 45)
        arg = LocalDate(2012, 3, 6)
        with pytest.raises(TypeError) as e:
            instance.compare_to(arg)  # type: ignore
        assert str(e.value) == "LocalTime cannot be compared to LocalDate"


class TestLocalTimePseudomutators:
    def test_plus_hours_simple(self) -> None:
        start = LocalTime(12, 15, 8)
        expected_forward = LocalTime(14, 15, 8)
        expected_backward = LocalTime(10, 15, 8)
        assert start.plus_hours(2) == expected_forward
        assert start.plus_hours(-2) == expected_backward

    def test_plus_hours_crossing_day_boundary(self) -> None:
        start = LocalTime(12, 15, 8)
        expected = LocalTime(8, 15, 8)
        assert start.plus_hours(20) == expected
        assert start.plus_hours(20).plus_hours(-20) == start

    def test_plus_hours_crossing_several_days_boundary(self) -> None:
        # Christmas day + 10 days and 1 hour
        start = LocalTime(12, 15, 8)
        expected = LocalTime(13, 15, 8)
        assert start.plus_hours(241) == expected
        assert start.plus_hours(241).plus_hours(-241) == start

    # Having tested that hours cross boundaries correctly, the other time unit
    # tests are straightforward
    def test_plus_minutes_simple(self) -> None:
        start = LocalTime(12, 15, 8)
        expected_forward = LocalTime(12, 17, 8)
        expected_backward = LocalTime(12, 13, 8)
        assert start.plus_minutes(2) == expected_forward
        assert start.plus_minutes(-2) == expected_backward

    def test_plus_seconds_simple(self) -> None:
        start = LocalTime(12, 15, 8)
        expected_forward = LocalTime(12, 15, 18)
        expected_backward = LocalTime(12, 14, 58)
        assert start.plus_seconds(10) == expected_forward
        assert start.plus_seconds(-10) == expected_backward

    def test_plus_milliseconds_simple(self) -> None:
        start = LocalTime(12, 15, 8, 300)
        expected_forward = LocalTime(12, 15, 8, 700)
        expected_backward = LocalTime(12, 15, 7, 900)
        assert start.plus_milliseconds(400) == expected_forward
        assert start.plus_milliseconds(-400) == expected_backward

    def test_plus_ticks_simple(self) -> None:
        start = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 7500)
        expected_forward = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 301, 1500)
        expected_backward = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 300, 3500)
        assert start.plus_ticks(4000) == expected_forward
        assert start.plus_ticks(-4000) == expected_backward

    def test_plus_ticks_long(self) -> None:
        assert PyodaConstants.TICKS_PER_DAY > _CsharpConstants.INT_MAX_VALUE
        start = LocalTime(12, 15, 8)
        expected_forward = LocalTime(12, 15, 9)
        expected_backward = LocalTime(12, 15, 7)
        assert start.plus_ticks(PyodaConstants.TICKS_PER_DAY + PyodaConstants.TICKS_PER_SECOND) == expected_forward
        assert start.plus_ticks(-PyodaConstants.TICKS_PER_DAY - PyodaConstants.TICKS_PER_SECOND) == expected_backward

    def test_with(self) -> None:
        start = LocalTime.from_hour_minute_second_millisecond_tick(12, 15, 8, 100, 1234)
        expected = LocalTime(12, 15, 8)
        assert start.with_(TimeAdjusters.truncate_to_second) == expected

    def test_plus_minutes_would_overflow_naively(self) -> None:
        start = LocalTime(12, 34, 56)
        # Very big value, which just wraps round a *lot* and adds one minute.
        # There's no way we could compute that many nanoseconds.
        value = (PyodaConstants.NANOSECONDS_PER_DAY << 15) + 1
        expected = LocalTime(12, 35, 56)
        actual = start.plus_minutes(value)
        assert actual == expected
