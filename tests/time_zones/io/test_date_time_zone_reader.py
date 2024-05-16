# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import io

import pytest

from pyoda_time import PyodaConstants
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.utility import InvalidPyodaDataError


class TestDateTimeZoneReader:
    def test_has_more_data_buffers(self) -> None:
        stream = io.BytesIO(b"\x01\x02")
        reader = _DateTimeZoneReader._ctor(stream, None)

        # has_more_data reads a byte and buffers it
        assert stream.tell() == 0
        assert reader.has_more_data
        assert stream.tell() == 1
        assert reader.has_more_data
        assert stream.tell() == 1

        # Consume the buffered byte
        assert reader.read_byte() == 1
        assert stream.tell() == 1

        # has_more_data reads the next byte
        assert reader.has_more_data
        assert stream.tell() == 2
        assert reader.has_more_data
        assert stream.tell() == 2

        # Consume the buffered byte
        assert reader.read_byte() == 2
        assert stream.tell() == 2

        # No more data
        assert not reader.has_more_data

    def test_read_count_out_of_range(self) -> None:
        # Int32.MaxValue + 1 (as a uint) is 10000000_00000000_00000000_00000000
        # So only bit 31 is set.
        # Divided into 7 bit chunks (reverse order), with top bit set for continuation, this is:
        # 10000000 - bits 0-6
        # 10000000 - bits 7-13
        # 10000000 - bits 14-20
        # 10000000 - bits 21-27
        # 00001000 - bits 28-34
        data = bytes([0x80, 0x80, 0x80, 0x80, 0b00001000])
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            reader.read_count()

    def test_read_milliseconds_invalid_flag(self) -> None:
        # Top 3 bits are the flag. Valid flag values are 0b100 (minutes), 0b101 (seconds)  and 0b110 (milliseconds)
        data = bytes([0xE0, 0, 0, 0, 0, 0])  # Invalid flag (followed by 0s to check that it's not just out of data)
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            reader.read_milliseconds()

    def test_read_zone_interval_transition_invalid_marker_value(self) -> None:
        data = bytes((4, 0, 0, 0, 0, 0))  # Marker value of 4 (followed by 0s to check that it's not just out of data)
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            reader.read_zone_interval_transition(previous=PyodaConstants.UNIX_EPOCH)

    def test_read_zone_interval_transition_no_previous_value(self) -> None:
        # Count value between 1 << 7 and 1 << 21 (followed by 0s to check that it's not just out of data)
        data = bytes((0xFF, 0x7F, 0, 0, 0, 0))
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            reader.read_zone_interval_transition(previous=None)

        # Validate that when we *do* provide a previous value, it doesn't throw
        stream.seek(0)
        reader = _DateTimeZoneReader._ctor(stream, None)
        reader.read_zone_interval_transition(previous=PyodaConstants.UNIX_EPOCH)

    def test_read_string_not_enough_data(self) -> None:
        # We say there are 5 bytes, but there are only 4 left...
        data = bytes([0x05, 0x40, 0x40, 0x40, 0x40])
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            reader.read_string()

    def test_read_byte_not_enough_data(self) -> None:
        data = bytes([0x05])
        stream = io.BytesIO(data)
        reader = _DateTimeZoneReader._ctor(stream, None)
        # Just check we can read the first byte, then fail on the second
        assert reader.read_byte() == 5
        with pytest.raises(InvalidPyodaDataError):
            reader.read_byte()
