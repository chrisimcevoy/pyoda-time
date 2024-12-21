# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Final, final, overload

from ._local_time import LocalTime
from ._offset import Offset
from ._offset_date_time import OffsetDateTime
from ._pyoda_constants import PyodaConstants

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["OffsetTime"]

from .utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from .utility._hash_code_helper import _hash_code_helper

if TYPE_CHECKING:
    from ._local_date import LocalDate


@final
@_sealed
class OffsetTime:
    """A combination of a ``LocalTime`` and an ``Offset``, to represent a time-of-day at a specific offset from UTC but
    without any date information.

    Equality is defined in a component-wise fashion: two values are the same if they represent equal time-of-day values
    and equal offsets from UTC. Ordering between offset time values is not defined.

    The default value of this type is midnight with a UTC offset of zero.
    """

    __NANOSECONDS_BITS: Final[int] = 47
    __NANOSECONDS_MASK: Final[int] = (1 << __NANOSECONDS_BITS) - 1

    __nanoseconds_and_offset: int
    """Bottom NanosecondsBits bits are the nanosecond-of-day; top 17 bits are the offset (in seconds).

    This has a slight execution-time cost (masking for each component) but the logical benefit of saving 4 bytes per
    value actually ends up being 8 bytes per value on a 64-bit CLR due to alignment.
    """

    def __init__(self, time: LocalTime, offset: Offset) -> None:
        """Constructs an instance of the specified time and offset.

        :param time: The time part of the value.
        :param offset: The offset part of the value.
        """
        nanosecond_of_day = time.nanosecond_of_day
        offset_seconds = offset.seconds
        self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)

    @classmethod
    @overload
    def _ctor(cls, *, nanosecond_of_day_zero_offset: int) -> OffsetTime:
        """Constructor only used in specialist cases where we know the offset will be 0."""

    @classmethod
    @overload
    def _ctor(cls, *, nanosecond_of_day: int, offset_seconds: int) -> OffsetTime: ...

    @classmethod
    def _ctor(
        cls,
        *,
        nanosecond_of_day_zero_offset: int | None = None,
        nanosecond_of_day: int | None = None,
        offset_seconds: int | None = None,
    ) -> OffsetTime:
        self = super().__new__(cls)
        if nanosecond_of_day_zero_offset is not None:
            # Constructor only used in specialist cases where we know the offset will be 0.
            # TODO: Preconditions.DebugCheckArgument
            self.__nanoseconds_and_offset = nanosecond_of_day_zero_offset
        elif nanosecond_of_day is not None and offset_seconds is not None:
            self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)
        else:
            raise ValueError
        return self

    @property
    def time_of_day(self) -> LocalTime:
        """Gets the time-of-day represented by this value.

        :return: The time-of-day represented by this value.
        """
        return LocalTime._ctor(nanoseconds=self.nanosecond_of_day)

    @property
    def offset(self) -> Offset:
        """Gets the offset from UTC of this value.

        :return: The offset from UTC of this value.
        """
        return Offset._ctor(seconds=self._offset_seconds)

    @property
    def _offset_seconds(self) -> int:
        """Returns the number of seconds in the offset, without going via an Offset."""
        return self.__nanoseconds_and_offset >> self.__NANOSECONDS_BITS

    @property
    def _offset_nanoseconds(self) -> int:
        """Returns the number of nanoseconds in the offset, without going via an Offset."""
        return (self.__nanoseconds_and_offset >> self.__NANOSECONDS_BITS) * PyodaConstants.NANOSECONDS_PER_SECOND

    @property
    def hour(self) -> int:
        """Gets the hour of day of this offset time, in the range 0 to 23 inclusive.

        :return: The hour of day of this offset time, in the range 0 to 23 inclusive.
        """
        # Effectively nanoseconds / NanosecondsPerHour, but apparently rather more efficient.
        return _towards_zero_division((self.nanosecond_of_day >> 13), 439453125)

    @property
    def clock_hour_of_half_day(self) -> int:
        """Gets the hour of the half-day of this offset time, in the range 1 to 12 inclusive.

        :return: The hour of the half-day of this offset time, in the range 1 to 12 inclusive.
        """
        # TODO: unchecked (redundant?)
        hour_of_half_day = _csharp_modulo(self.hour, 12)
        return 12 if hour_of_half_day == 0 else hour_of_half_day

    @property
    def minute(self) -> int:
        """Gets the minute of this offset time, in the range 0 to 59 inclusive.

        :return: The minute of this offset time, in the range 0 to 59 inclusive.
        """
        # Effectively NanosecondOfDay / NanosecondsPerMinute, but apparently rather more efficient.
        # TODO: unchecked
        minute_of_day = _towards_zero_division(self.nanosecond_of_day >> 11, 29296875)
        return _csharp_modulo(minute_of_day, PyodaConstants.MINUTES_PER_HOUR)

    @property
    def second(self) -> int:
        """Gets the second of this offset time within the minute, in the range 0 to 59 inclusive.

        :return: The second of this offset time within the minute, in the range 0 to 59 inclusive.
        """
        # TODO: unchecked
        second_of_day = _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_SECOND)
        return _csharp_modulo(second_of_day, PyodaConstants.SECONDS_PER_MINUTE)

    @property
    def millisecond(self) -> int:
        """Gets the millisecond of this offset time within the second, in the range 0 to 999 inclusive.

        :return: The millisecond of this offset time within the second, in the range 0 to 999 inclusive.
        """
        # TODO: unchecked
        millisecond_of_day = _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_MILLISECOND)
        return _csharp_modulo(millisecond_of_day, PyodaConstants.MILLISECONDS_PER_SECOND)

    @property
    def tick_of_second(self) -> int:
        """Gets the tick of this offset time within the second, in the range 0 to 9,999,999 inclusive.

        :return: The tick of this offset time within the second, in the range 0 to 9,999,999 inclusive.
        """
        # TODO: unchecked
        return _csharp_modulo(self.tick_of_day, PyodaConstants.TICKS_PER_SECOND)

    @property
    def tick_of_day(self) -> int:
        """Gets the tick of this offset time within the day, in the range 0 to 863,999,999,999 inclusive.

        If the value does not fall on a tick boundary, it will be truncated towards zero.

        :return: The tick of this offset time within the day, in the range 0 to 863,999,999,999 inclusive.
        """
        return _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_TICK)

    @property
    def nanosecond_of_second(self) -> int:
        """Gets the nanosecond of this offset time within the second, in the range 0 to 999,999,999 inclusive.

        :return: The nanosecond of this offset time within the second, in the range 0 to 999,999,999 inclusive.
        """
        # TODO: unchecked
        return _csharp_modulo(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_SECOND)

    @property
    def nanosecond_of_day(self) -> int:
        """Gets the nanosecond of this offset time within the day, in the range 0 to 86,399,999,999,999 inclusive.

        :return: The nanosecond of this offset time within the day, in the range 0 to 86,399,999,999,999 inclusive.
        """
        return self.__nanoseconds_and_offset & self.__NANOSECONDS_MASK

    def with_offset(self, offset: Offset) -> OffsetTime:
        """Creates a new ``OffsetTime`` for the same time-of-day, but with the specified UTC offset.

        :param offset: The new UTC offset.
        :return: A new ``OffsetTime`` for the same date, but with the specified UTC offset.
        """
        return OffsetTime(self.time_of_day, offset)

    def with_(self, adjuster: Callable[[LocalTime], LocalTime]) -> OffsetTime:
        """Returns this offset time-of-day, with the given date adjuster applied to it, maintaining the existing offset.

        If the adjuster attempts to construct an invalid time-of-day, any exception thrown by that construction attempt
        will be propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted offset date.
        """
        return OffsetTime(self.time_of_day.with_(adjuster), self.offset)

    def on(self, date: LocalDate) -> OffsetDateTime:
        """Combines this ``OffsetTime`` with the given ``LocalDate`` into an ``OffsetDateTime``.

        :param date: The date to combine with this time-of-day.
        :return: The ``OffsetDateTime`` representation of this time-of-day on the given date.
        """
        return OffsetDateTime(date.at(self.time_of_day), self.offset)

    def __hash__(self) -> int:
        """Returns a hash code for this offset time. See the type documentation for a description of equality semantics.

        :return: A hash code for this offset time.
        """
        return _hash_code_helper(self.time_of_day, self.offset)

    def equals(self, other: OffsetTime) -> bool:
        """Compares two ``OffsetTime`` values for equality.

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset time with.
        :return: True if the given value is another offset time equal to this one; false otherwise.
        """
        return self == other

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset time with.
        :return: True if the given value is another offset time equal to this one; false otherwise.
        """
        if not isinstance(other, OffsetTime):
            return NotImplemented
        return self.time_of_day == other.time_of_day and self.offset == other.offset

    def __ne__(self, other: object) -> bool:
        """Implements the operator ``!=`` (inequality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset time with.
        :return: True if values are not equal to each other, otherwise False.
        """
        return not self == other

    # TODO: [requires OffsetTimePattern]
    #  def __repr__(self) -> str:
    #  def __format__(self, format_spec: str) -> str:
    #  deconstructor..?
