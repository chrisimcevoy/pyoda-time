# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time import Duration, Instant, Offset
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

from .dtz_io_helper import _DtzIoHelper


class TestReadWrite:
    def test_count(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()

        for i in range(16):
            dio.test_count(i)

        dio.test_count(0x0F)
        dio.test_count(0x10)
        dio.test_count(0x7F)
        dio.test_count(0x80)
        dio.test_count(0x81)
        dio.test_count(0x3FFF)
        dio.test_count(0x4000)
        dio.test_count(0x4001)
        dio.test_count(0x1FFFFF)
        dio.test_count(0x200000)
        dio.test_count(0x200001)
        dio.test_count(_CsharpConstants.INT_MAX_VALUE)
        dio.test_count(0, bytes([0x00]))
        dio.test_count(1, bytes([0x01]))
        dio.test_count(127, bytes([0x7F]))
        dio.test_count(128, bytes([0x80, 0x01]))
        dio.test_count(300, bytes([0xAC, 0x02]))

    def test_signed_count(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()

        for i in range(-16, 16):
            dio.test_signed_count(i)

        dio.test_signed_count(0x4000000)
        dio.test_signed_count(-0x4000000)
        dio.test_signed_count(_CsharpConstants.INT_MIN_VALUE)
        dio.test_signed_count(_CsharpConstants.INT_MIN_VALUE + 1)
        dio.test_signed_count(_CsharpConstants.INT_MAX_VALUE - 1)
        dio.test_signed_count(_CsharpConstants.INT_MAX_VALUE)
        dio.test_signed_count(0, bytes([0x00]))
        dio.test_signed_count(-1, bytes([0x01]))
        dio.test_signed_count(1, bytes([0x02]))
        dio.test_signed_count(-2, bytes([0x03]))
        dio.test_signed_count(64, bytes([0x80, 0x01]))
        dio.test_signed_count(-65, bytes([0x81, 0x01]))
        dio.test_signed_count(128, bytes([0x80, 0x02]))

    def test_dictionary(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        expected: dict[str, str] = {}
        dio.test_dictionary(expected)

        expected["Able"] = "able"
        dio.test_dictionary(expected)

        expected["Baker"] = "baker"
        expected["Charlie"] = "charlie"
        expected["Delta"] = "delta"
        dio.test_dictionary(expected)

    def test_zone_interval_transition(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        dio.test_zone_interval_transition(None, Instant._before_min_value())
        dio.test_zone_interval_transition(None, Instant.min_value)
        # No test for Instant.MaxValue, as it's not on a tick boundary.
        dio.test_zone_interval_transition(None, Instant._after_max_value())

        dio.test_zone_interval_transition(None, Instant.min_value.plus_ticks(1))
        # The ZoneIntervalTransition has precision to the tick (with no real need to change that).
        # Round to the tick just lower than Instant.MaxValue...
        tick_before_max_instant = Instant.from_unix_time_ticks(Instant.max_value.to_unix_time_ticks())
        dio.test_zone_interval_transition(None, tick_before_max_instant)

        # Encoding as hours-since-previous.
        previous = Instant.from_utc(1990, 1, 1, 11, 30)  # arbitrary
        dio.test_zone_interval_transition(previous, previous)
        dio.test_zone_interval_transition(
            previous,
            previous
            + Duration.from_hours(_DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_HOURS_SINCE_PREVIOUS),
        )
        dio.test_zone_interval_transition(
            previous,
            previous
            + Duration.from_hours(_DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_HOURS_SINCE_PREVIOUS - 1),
        )
        dio.test_zone_interval_transition(previous, previous + Duration.from_hours(1))
        dio.test_zone_interval_transition(
            previous,
            previous
            + Duration.from_hours(_DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH - 1),
        )
        dio.test_zone_interval_transition(
            previous,
            previous
            + Duration.from_hours(_DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH),
        )
        dio.test_zone_interval_transition(Instant.min_value.plus_ticks(1), tick_before_max_instant)

        # Encoding as minutes-since-epoch
        epoch = _DateTimeZoneWriter._ZoneIntervalConstants._EPOCH_FOR_MINUTES_SINCE_EPOCH
        dio.test_zone_interval_transition(None, epoch)
        dio.test_zone_interval_transition(
            None,
            epoch
            + Duration.from_minutes(_DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH),
        )
        dio.test_zone_interval_transition(None, epoch + Duration.from_minutes(_CsharpConstants.INT_MAX_VALUE))

        # Out of range cases, or not a multiple of minutes since the epoch.
        dio.test_zone_interval_transition(None, epoch + Duration.from_hours(1))
        dio.test_zone_interval_transition(None, epoch + Duration.from_minutes(1))
        dio.test_zone_interval_transition(None, epoch + Duration.from_seconds(1))
        dio.test_zone_interval_transition(None, epoch + Duration.from_milliseconds(1))
        dio.test_zone_interval_transition(None, epoch - Duration.from_hours(1))
        dio.test_zone_interval_transition(None, epoch + Duration.from_minutes(_CsharpConstants.INT_MAX_VALUE + 1))

        # Example from Pacific/Auckland which failed at one time, and a similar one with seconds.
        dio.test_zone_interval_transition(None, Instant.from_utc(1927, 11, 5, 14, 30))
        dio.test_zone_interval_transition(None, Instant.from_utc(1927, 11, 5, 14, 30, 5))

    def test_offset(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        dio.test_offset(Offset.min_value)
        dio.test_offset(Offset.max_value)
        dio.test_offset(Offset.from_hours(0))
        dio.test_offset(Offset.from_hours(5))
        dio.test_offset(Offset.from_hours(-5))
        dio.test_offset(Offset.from_hours_and_minutes(5, 15))
        dio.test_offset(Offset.from_hours_and_minutes(5, 30))
        dio.test_offset(Offset.from_hours_and_minutes(5, 45))
        dio.test_offset(Offset.from_hours_and_minutes(-5, -15))
        dio.test_offset(Offset.from_hours_and_minutes(-5, -30))
        dio.test_offset(Offset.from_hours_and_minutes(-5, -45))
        dio.test_offset(Offset.from_seconds(1))
        dio.test_offset(Offset.from_seconds(-1))
        dio.test_offset(Offset.from_seconds(1000))
        dio.test_offset(Offset.from_seconds(-1000))

    def test_string_no_pool(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        dio.test_string("")
        dio.test_string("This is a test string")

    def test_string_with_pool(self) -> None:
        dio = _DtzIoHelper._create_with_string_pool()
        dio.test_string("")
        dio.test_string("This is a test string")

    def test_read_byte_after_has_more_data(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        dio._writer.write_byte(5)

        assert dio._reader.has_more_data
        assert dio._reader.read_byte() == 5

    def test_read_string_after_has_more_data(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        dio._writer.write_string("foo")

        assert dio._reader.has_more_data
        assert dio._reader.read_string() == "foo"
