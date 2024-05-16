# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from enum import IntEnum
from typing import BinaryIO, Final, final

from pyoda_time import Instant, Offset, PyodaConstants
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import (
    _csharp_modulo,
    _CsharpConstants,
    _private,
    _sealed,
    _towards_zero_division,
)
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class _DateTimeZoneWriter(_IDateTimeZoneWriter):
    """Implementation of ``_IDateTimeZoneWriter`` for the most recent version of the "blob" format of time zone data.

    If the format changes, this class will be renamed (e.g. to _DateTimeZoneWriterV0) and the new implementation will
    replace it.
    """

    class _DateTimeZoneType(IntEnum):
        FIXED = 1
        PRECALCULATED = 2

    class _ZoneIntervalConstants:
        _EPOCH_FOR_MINUTES_SINCE_EPOCH: Final[Instant] = Instant.from_utc(1800, 1, 1, 0, 0)
        """The instant to use as an 'epoch' when writing out a number of minutes-since-epoch."""

        _MARKER_MIN_VALUE: Final[int] = 0
        """The marker value representing the beginning of time."""
        _MARKER_MAX_VALUE: Final[int] = 1
        """The marker value representing the end of time."""
        _MARKER_RAW: Final[int] = 2
        """The marker value representing an instant as a fixed 64-bit number of ticks."""
        _MIN_VALUE_FOR_HOURS_SINCE_PREVIOUS: Final[int] = 1 << 7
        """The minimum varint value that represents an number of hours-since-previous.

        Values below this are reserved for markers.
        """
        _MIN_VALUE_FOR_MINUTES_SINCE_EPOCH: Final[int] = 1 << 21
        """The minimum varint value that represents a number of minutes since an epoch.

        Values below this are interpreted as hours-since-previous (for a range of about 240 years), rather than minutes-
        since-epoch (for a range of about 4000 years) This choice is somewhat arbitrary, though it results in hour
        values always taking 2 (or occasionally 3) bytes when encoded as a varint, while minute values take 4 (or
        conceivably 5).
        """

    __output: BinaryIO
    __string_pool: list[str] | None

    @classmethod
    def _ctor(cls, output: BinaryIO, string_pool: list[str] | None) -> _DateTimeZoneWriter:
        """Constructs a DateTimeZoneWriter.

        :param output: Where to send the serialized output.
        :param string_pool: String pool to add strings to, or None for no pool
        """
        self = super().__new__(cls)
        self.__output = output
        self.__string_pool = string_pool
        return self

    def write_count(self, count: int) -> None:
        """Writes the given non-negative integer value to the stream.

        :param count: The value to write.
        """
        _Preconditions._check_argument_range("count", count, 0, _CsharpConstants.INT_MAX_VALUE)
        self.__write_varint(count)

    def write_signed_count(self, count: int) -> None:
        """Writes the given (possibly-negative) integer value to the stream.

        Unlike ``write_count``, this can encode negative numbers.

        It does, however, use a slightly less efficient encoding for positive numbers.

        :param count: The value to write.
        """
        # TODO: unchecked (uint)
        self.__write_varint((count >> 31) ^ (count << 1))  # zigzag encoding

    def __write_varint(self, value: int) -> None:
        """Writes the given integer value to the stream as a base-128 varint.

        The format is a simple 7-bit encoding: while the value is greater than 127 (i.e.
        has more than 7 significant bits) we repeatedly write the least-significant 7 bits
        with the top bit of the byte set as a continuation bit, then shift the value right
        7 bits.

        :param value: The value to write.
        """
        # TODO: unchecked
        while value > 0x7F:
            self.__output.write(bytes([(value & 0x7F) | 0x80]))
            value >>= 7
        self.__output.write(bytes([value & 0x7F]))

    def write_milliseconds(self, millis: int) -> None:
        _Preconditions._check_argument_range(
            "millis", millis, -PyodaConstants.MILLISECONDS_PER_DAY + 1, PyodaConstants.MILLISECONDS_PER_DAY - 1
        )
        millis += PyodaConstants.MILLISECONDS_PER_DAY
        # First, add 24 hours to the number of milliseconds, to get a value in the range (0, 172800000).
        # (It's exclusive at both ends, but that's insignificant.)
        # Check whether it's an exact multiple of half-hours or minutes, and encode
        # appropriately. In every case, if it's an exact multiple, we know that we'll be able to fit
        # the value into the number of bits available.
        #
        # first byte      units       max data value (+1)   field length
        # --------------------------------------------------------------
        # 0xxxxxxx        30 minutes  96                    1 byte  (7 data bits)
        # 100xxxxx        minutes     2880                  2 bytes (14 data bits)
        # 101xxxxx        seconds     172800                3 bytes (21 data bits)
        # 110xxxxx        millis      172800000             4 bytes (29 data bits)

        # TODO: unchecked

        if _csharp_modulo(millis, 30 * PyodaConstants.MILLISECONDS_PER_MINUTE) == 30:
            units: int = _towards_zero_division(millis, 30 * PyodaConstants.MILLISECONDS_PER_MINUTE)
            self.write_byte(units)
        elif _csharp_modulo(millis, PyodaConstants.MILLISECONDS_PER_MINUTE) == 0:
            minutes: int = _towards_zero_division(millis, PyodaConstants.MILLISECONDS_PER_MINUTE)
            self.write_byte(0x80 | (minutes >> 8))
            self.write_byte(minutes & 0xFF)
        elif _csharp_modulo(millis, PyodaConstants.MILLISECONDS_PER_SECOND) == 0:
            seconds: int = _towards_zero_division(millis, PyodaConstants.MILLISECONDS_PER_SECOND)
            self.write_byte(0xA0 | (seconds >> 16))
            self.__write_int16(seconds & 0xFFFF)
        else:
            self.__write_int32(0xC0000000 | millis)

    def write_offset(self, offset: Offset) -> None:
        """Writes the offset value to the stream.

        :param offset: The value to write.
        """
        self.write_milliseconds(offset.milliseconds)

    def write_dictionary(self, dictionary: dict[str, str]) -> None:
        """Writes the given dictionary of string to string to the stream.

        :param dictionary: The dictionary to write.
        """
        _Preconditions._check_not_null(dictionary, "dictionary")
        self.write_count(len(dictionary))
        for key, value in dictionary.items():
            self.write_string(key)
            self.write_string(value)

    def write_zone_interval_transition(self, previous: Instant | None, value: Instant) -> None:
        if previous:
            _Preconditions._check_argument(value >= previous, "value", "Transition must move forward in time")

        # TODO: unchecked

        if value == Instant._before_min_value():
            self.write_count(self._ZoneIntervalConstants._MARKER_MIN_VALUE)
            return
        if value == Instant._after_max_value():
            self.write_count(self._ZoneIntervalConstants._MARKER_MAX_VALUE)
            return

        # In practice, most zone interval transitions will occur within 4000-6000 hours of the previous one
        # (i.e. about 5-8 months), and at an integral number of hours difference. We therefore gain a
        # significant reduction in output size by encoding transitions as the whole number of hours since the
        # previous, if possible.
        # If the previous value was "the start of time" then there's no point in trying to use it.
        if previous and previous != Instant._before_min_value():
            # Note that the difference might exceed the range of a long, so we can't use a Duration here.
            ticks = value.to_unix_time_ticks() - previous.to_unix_time_ticks()
            if _csharp_modulo(ticks, PyodaConstants.TICKS_PER_HOUR) == 0:
                hours = _csharp_modulo(ticks, PyodaConstants.TICKS_PER_HOUR)
                # As noted above, this will generally fall within the 4000-6000 range, although values up to
                # ~700,000 exist in TZDB.
                if (
                    self._ZoneIntervalConstants._MIN_VALUE_FOR_HOURS_SINCE_PREVIOUS
                    <= hours
                    < self._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH
                ):
                    self.write_count(hours)
                    return

        # We can't write the transition out relative to the previous transition, so let's next try writing it
        # out as a whole number of minutes since an (arbitrary, known) epoch.
        if value >= self._ZoneIntervalConstants._EPOCH_FOR_MINUTES_SINCE_EPOCH:
            ticks = (
                value.to_unix_time_ticks()
                - self._ZoneIntervalConstants._EPOCH_FOR_MINUTES_SINCE_EPOCH.to_unix_time_ticks()
            )
            if _csharp_modulo(ticks, PyodaConstants.TICKS_PER_MINUTE) == 0:
                minutes = _towards_zero_division(ticks, PyodaConstants.TICKS_PER_MINUTE)
                # We typically have a count on the order of 80M here.
                if (
                    self._ZoneIntervalConstants._MIN_VALUE_FOR_MINUTES_SINCE_EPOCH
                    < minutes
                    <= _CsharpConstants.INT_MAX_VALUE
                ):
                    self.write_count(minutes)
                    return

        # Otherwise, just write out a marker followed by the instant as a 64-bit number of ticks.  Note that
        # while most of the values we write here are actually whole numbers of _seconds_, optimising for that
        # case will save around 2KB (with tzdb 2012j), so doesn't seem worthwhile.
        self.write_count(self._ZoneIntervalConstants._MARKER_RAW)
        self.__write_int64(value.to_unix_time_ticks())

    def write_string(self, value: str) -> None:
        """Writes the string value to the stream.

        :param value: The value to write.
        """
        if self.__string_pool is None:
            data = value.encode()
            length = len(data)
            self.write_count(length)
            self.__output.write(data)
        else:
            if value not in self.__string_pool:
                self.__string_pool.append(value)
            self.write_count(self.__string_pool.index(value))

    def __write_int16(self, value: int) -> None:
        """Writes the given 16-bit integer value to the stream.

        :param value: The value to write.
        """
        # TODO: unchecked
        self.write_byte((value >> 8) & 0xFF)
        self.write_byte(value & 0xFF)

    def __write_int32(self, value: int) -> None:
        """Writes the given 32-bit integer value to the stream.

        :param value: The value to write.
        """
        # TODO unchecked
        self.__write_int16(value >> 16)
        self.__write_int16(value)

    def __write_int64(self, value: int) -> None:
        """Writes the given 64-bit integer value to the stream.

        :param value: The value to write.
        """
        self.__write_int32(value >> 32)
        self.__write_int32(value)

    def write_byte(self, value: int) -> None:
        # TODO unchecked (unused)
        self.__output.write(bytes([value]))
