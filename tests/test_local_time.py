# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import LocalTime, Offset, OffsetTime, Period, PyodaConstants


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
