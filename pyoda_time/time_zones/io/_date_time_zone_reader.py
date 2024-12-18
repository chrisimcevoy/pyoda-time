# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from collections.abc import Sequence
from typing import BinaryIO, final

from pyoda_time._duration import Duration
from pyoda_time._instant import Instant
from pyoda_time._offset import Offset
from pyoda_time._pyoda_constants import PyodaConstants
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.utility import InvalidPyodaDataError
from pyoda_time.utility._csharp_compatibility import _CsharpConstants, _int64_overflow, _private, _sealed


@final
@_sealed
@_private
class _DateTimeZoneReader(_IDateTimeZoneReader):
    """Implementation of ``_IDateTimeZoneReader`` for the most recent version of the "blob" format of time zone data.

    If the format changes, this class will be renamed (e.g. to _DateTimeZoneReaderV0) and the new implementation will
    replace it.
    """

    __input: BinaryIO
    """Raw stream to read from.

    Be careful before reading from this - you need to take account of bufferedByte as well.
    """
    __string_pool: Sequence[str] | None
    """String pool to use, or null if no string pool is in use."""
    __buffered_byte: int | None
    """Sometimes we need to buffer a byte in memory, e.g. to check if there is any more data.

    Anything reading directly from the stream should check here first.
    """

    @classmethod
    def _ctor(cls, input_: BinaryIO, string_pool: Sequence[str] | None) -> _DateTimeZoneReader:
        self = super().__new__(cls)
        self.__input = input_
        self.__string_pool = string_pool
        self.__buffered_byte = None
        return self

    @property
    def has_more_data(self) -> bool:
        if self.__buffered_byte is not None:
            return True
        next_byte = self.__input.read(1)
        if not next_byte:
            return False
        # Okay, we got a byte - remember it for the next call to read_byte
        self.__buffered_byte = next_byte[0]
        return True

    def read_count(self) -> int:
        """Reads a non-negative integer value from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_count``.

        :return: The integer value from the stream.
        """
        unsigned = self.__read_varint()
        if unsigned > _CsharpConstants.INT_MAX_VALUE:
            raise InvalidPyodaDataError("Count value greater than Int32.MaxValue")
        return unsigned

    def read_signed_count(self) -> int:
        """Reads a (possibly-negative) integer value from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_signed_count``.

        :return: The integer value from the stream.
        """
        value = self.__read_varint()
        return (value >> 1) ^ -(value & 1)  # zigzag encoding

    def __read_varint(self) -> int:
        """Reads a base-128 varint value from the stream.

        The value must have been written by DateTimeZoneWriter.WriteVarint, which documents the format.

        :return: The integer value from the stream.
        """
        # TODO: unchecked
        ret = 0
        shift = 0
        while True:
            next_byte = self.read_byte()
            ret += (next_byte & 0x7F) << shift
            shift += 7
            if next_byte < 0x80:
                return ret

    def read_milliseconds(self) -> int:
        """Reads a number of milliseconds from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_milliseconds``.

        :return: The milliseconds value from the stream.
        """
        # TODO: unchecked
        first_byte = self.read_byte()

        millis: int

        if (first_byte & 0x80) == 0:
            millis = first_byte * (30 * PyodaConstants.MILLISECONDS_PER_MINUTE)
        else:
            flag = first_byte & 0xE0  # The flag parts of the first byte
            first_data = first_byte & 0x1F  # The data parts of the first byte
            match flag:
                case 0x80:  # Minutes
                    minutes = (first_data << 8) + self.read_byte()
                    millis = minutes * PyodaConstants.MILLISECONDS_PER_MINUTE
                case 0xA0:  # Seconds
                    seconds = (first_data << 16) + (self.__read_int16() & 0xFFFF)
                    millis = seconds * PyodaConstants.MILLISECONDS_PER_SECOND
                case 0xC0:  # Milliseconds
                    millis = (first_data << 24) + (self.read_byte() << 16) + (self.__read_int16() & 0xFFFF)
                case _:
                    raise InvalidPyodaDataError(f"Invalid flag in offset: {flag:02x}")
        millis -= PyodaConstants.MILLISECONDS_PER_DAY
        return millis

    def read_offset(self) -> Offset:
        """Reads an offset value from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_offset``.

        :return: The offset value from the stream.
        """
        millis = self.read_milliseconds()
        return Offset.from_milliseconds(millis)

    def read_dictionary(self) -> dict[str, str]:
        """Reads a string to string dictionary value from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_dictionary``.

        :return: The ``dict[TKey,TValue]`` value from the stream.
        """
        results = {}
        count = self.read_count()
        for _ in range(count):
            key = self.read_string()
            value = self.read_string()
            results[key] = value
        return results

    def read_zone_interval_transition(self, previous: Instant | None) -> Instant:
        """Reads an instant representing a zone interval transition from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_zone_interval_transition``.

        :param previous: The previous transition written (usually for a given timezone), or null if there is no
            previous transition
        :return: The instant read from the stream
        """
        # TODO: unchecked (redundant)
        value: int = self.read_count()
        if value < _DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_HOURS_SINCE_PREVIOUS:
            match value:
                case _DateTimeZoneWriter._ZoneIntervalConstants._MARKER_MIN_VALUE:
                    return Instant._before_min_value()
                case _DateTimeZoneWriter._ZoneIntervalConstants._MARKER_MAX_VALUE:
                    return Instant._after_max_value()
                case _DateTimeZoneWriter._ZoneIntervalConstants._MARKER_RAW:
                    return Instant.from_unix_time_ticks(self.__read_int64())
                case _:
                    raise InvalidPyodaDataError(f"Unrecognised marker value: {value}")
        if value < _DateTimeZoneWriter._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH:
            if previous is None:
                raise InvalidPyodaDataError(
                    f"No previous value, so can't interpret value encoded as delta-since-previous: {value}"
                )
            return previous + Duration.from_hours(value)
        return _DateTimeZoneWriter._ZoneIntervalConstants._EPOCH_FOR_MINUTES_SINCE_EPOCH + Duration.from_minutes(value)

    def read_string(self) -> str:
        """Reads a string value from the stream.

        The value must have been written by ``_DateTimeZoneWriter.write_string``.

        :return: The string value from the stream.
        """
        if self.__string_pool is None:
            length = self.read_count()
            data = bytearray()
            while len(data) < length:
                remaining = length - len(data)
                chunk = self.__input.read(remaining)
                if not chunk:
                    raise InvalidPyodaDataError(
                        f"Unexpectedly reached end of data with {remaining} bytes still to read"
                    )
                data.extend(chunk)
            return data.decode()
        else:
            index = self.read_count()
            if index >= len(self.__string_pool) or index < 0:
                raise InvalidPyodaDataError("String pool index out of range")
            return self.__string_pool[index]

    def __read_int16(self) -> int:
        """Reads a signed 16 bit integer value from the stream and returns it as an int.

        :return: The 16 bit int value.
        """
        # TODO: unchecked (redundant)
        high = self.read_byte()
        low = self.read_byte()
        return (high << 8) | low

    def __read_int32(self) -> int:
        """Reads a signed 32 bit integer value from the stream and returns it as an int.

        :return: The 32 bit int value.
        """
        # TODO: unchecked (redundant)
        high = self.__read_int16() & 0xFFFF
        low = self.__read_int16() & 0xFFFF
        return (high << 16) | low

    def __read_int64(self) -> int:
        """Reads a signed 64 bit integer value from the stream and returns it as an long.

        :return: The 64 bit long value.
        """
        high = self.__read_int32() & 0xFFFFFFFF
        low = self.__read_int32() & 0xFFFFFFFF
        return _int64_overflow((high << 32) | low)

    def read_byte(self) -> int:
        """Reads a signed 8 bit integer value from the stream and returns it as an int.

        :return: The 8 bit int value.
        :raises InvalidPyodaDataError: The data in the stream has been exhausted.
        """
        if self.__buffered_byte is not None:
            ret, self.__buffered_byte = self.__buffered_byte, None
            return ret
        value: bytes = self.__input.read(1)
        if not value:
            raise InvalidPyodaDataError("Unexpected end of data stream")
        return value[0]
