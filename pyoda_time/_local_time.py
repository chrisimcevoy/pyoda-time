# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import functools as _functools
import typing as _typing

from ._pyoda_constants import PyodaConstants
from .utility import _csharp_modulo, _int32_overflow, _Preconditions, _sealed, _towards_zero_division

if _typing.TYPE_CHECKING:
    from . import LocalDateTime
    from ._local_date import LocalDate

__all__ = ["LocalTime"]


class _LocalTimeMeta(type):
    @property
    @_functools.cache
    def midnight(self) -> LocalTime:
        """Local time at midnight, i.e. 0 hours, 0 minutes, 0 seconds."""
        return LocalTime(hour=0, minute=0, second=0)

    @property
    def min_value(cls) -> LocalTime:
        """The minimum value of this type; equivalent to ``Midnight``."""
        return cls.midnight

    @property
    @_functools.cache
    def noon(self) -> LocalTime:
        """Local time at noon, i.e. 12 hours, 0 minutes, 0 seconds."""
        return LocalTime(hour=12, minute=0, second=0)

    @property
    @_functools.cache
    def max_value(cls) -> LocalTime:
        """The maximum value of this type, one nanosecond before midnight.

        This is useful if you have to use an inclusive upper bound for some reason. In general, it's better to use an
        exclusive upper bound, in which case use midnight of the following day.
        """
        return LocalTime._ctor(nanoseconds=PyodaConstants.NANOSECONDS_PER_DAY - 1)


@_typing.final
@_sealed
class LocalTime(metaclass=_LocalTimeMeta):
    """LocalTime is an immutable struct representing a time of day, with no reference to a particular calendar, time
    zone or date."""

    @_typing.overload
    def __init__(self, *, hour: int, minute: int) -> None: ...

    @_typing.overload
    def __init__(self, *, hour: int, minute: int, second: int) -> None: ...

    @_typing.overload
    def __init__(self, *, hour: int, minute: int, second: int, millisecond: int) -> None: ...

    def __init__(self, *, hour: int, minute: int, second: int = 0, millisecond: int = 0):
        if (
            hour < 0
            or hour > PyodaConstants.HOURS_PER_DAY - 1
            or minute < 0
            or minute > PyodaConstants.MINUTES_PER_HOUR - 1
            or second < 0
            or second > PyodaConstants.SECONDS_PER_MINUTE - 1
            or millisecond < 0
            or millisecond > PyodaConstants.MILLISECONDS_PER_SECOND - 1
        ):
            _Preconditions._check_argument_range("hour", hour, 0, PyodaConstants.HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range("minute", minute, 0, PyodaConstants.MINUTES_PER_HOUR - 1)
            _Preconditions._check_argument_range("second", second, 0, PyodaConstants.SECONDS_PER_MINUTE - 1)
            _Preconditions._check_argument_range(
                "millisecond", millisecond, 0, PyodaConstants.MILLISECONDS_PER_SECOND - 1
            )
        self.__nanoseconds = (
            hour * PyodaConstants.NANOSECONDS_PER_HOUR
            + minute * PyodaConstants.NANOSECONDS_PER_MINUTE
            + second * PyodaConstants.NANOSECONDS_PER_SECOND
            + millisecond * PyodaConstants.NANOSECONDS_PER_MILLISECOND
        )

    @classmethod
    def _ctor(cls, *, nanoseconds: int) -> LocalTime:
        """Constructor only called from other parts of Noda Time - trusted to be the range [0, NanosecondsPerDay)."""
        # TODO: _Preconditions._check_debug_argument_range()
        self = super().__new__(cls)
        self.__nanoseconds = nanoseconds
        return self

    @classmethod
    def from_hour_minute_second_millisecond_tick(
        cls, hour: int, minute: int, second: int, millisecond: int, tick_within_millisecond: int
    ) -> LocalTime:
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if (
            hour < 0
            or hour > PyodaConstants.HOURS_PER_DAY - 1
            or minute < 0
            or minute > PyodaConstants.MINUTES_PER_HOUR - 1
            or second < 0
            or second > PyodaConstants.SECONDS_PER_MINUTE - 1
            or millisecond < 0
            or millisecond > PyodaConstants.MILLISECONDS_PER_SECOND - 1
            or tick_within_millisecond < 0
            or tick_within_millisecond > PyodaConstants.TICKS_PER_MILLISECOND - 1
        ):
            _Preconditions._check_argument_range("hour", hour, 0, PyodaConstants.HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range("minute", minute, 0, PyodaConstants.MINUTES_PER_HOUR - 1)
            _Preconditions._check_argument_range("second", second, 0, PyodaConstants.SECONDS_PER_MINUTE - 1)
            _Preconditions._check_argument_range(
                "millisecond", millisecond, 0, PyodaConstants.MILLISECONDS_PER_SECOND - 1
            )
            _Preconditions._check_argument_range(
                "tick_within_millisecond", tick_within_millisecond, 0, PyodaConstants.TICKS_PER_MILLISECOND - 1
            )
        nanoseconds = (
            hour * PyodaConstants.NANOSECONDS_PER_HOUR
            + minute * PyodaConstants.NANOSECONDS_PER_MINUTE
            + second * PyodaConstants.NANOSECONDS_PER_SECOND
            + millisecond * PyodaConstants.NANOSECONDS_PER_MILLISECOND
            + tick_within_millisecond * PyodaConstants.NANOSECONDS_PER_TICK
        )
        return LocalTime._ctor(nanoseconds=nanoseconds)

    @classmethod
    def from_nanoseconds_since_midnight(cls, nanoseconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of nanoseconds which have elapsed since midnight.

        :param nanoseconds: The number of nanoseconds, in the range [0, 86,399,999,999,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if nanoseconds < 0 or nanoseconds > PyodaConstants.NANOSECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range("nanoseconds", nanoseconds, 0, PyodaConstants.NANOSECONDS_PER_DAY - 1)
        return LocalTime._ctor(nanoseconds=nanoseconds)

    @classmethod
    def from_ticks_since_midnight(cls, ticks: int) -> LocalTime:
        """Factory method for creating a local time from the number of ticks which have elapsed since midnight.

        :param ticks: The number of ticks, in the range [0, 863,999,999,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if ticks < 0 or ticks > PyodaConstants.TICKS_PER_DAY - 1:
            _Preconditions._check_argument_range("ticks", ticks, 0, PyodaConstants.TICKS_PER_DAY - 1)
        return LocalTime._ctor(nanoseconds=_int32_overflow(ticks * PyodaConstants.NANOSECONDS_PER_TICK))

    @classmethod
    def from_milliseconds_since_midnight(cls, milliseconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of milliseconds which have elapsed since midnight.

        :param milliseconds: The number of milliseconds, in the range [0, 86,399,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if milliseconds < 0 or milliseconds > PyodaConstants.MILLISECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range(
                "milliseconds", milliseconds, 0, PyodaConstants.MILLISECONDS_PER_DAY - 1
            )
        return cls._ctor(nanoseconds=_int32_overflow(milliseconds * PyodaConstants.NANOSECONDS_PER_MILLISECOND))

    @classmethod
    def from_seconds_since_midnight(cls, seconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of seconds which have elapsed since midnight.

        :param seconds: The number of seconds, in the range [0, 86,399]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if seconds < 0 or seconds > PyodaConstants.SECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range("seconds", seconds, 0, PyodaConstants.SECONDS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(seconds * PyodaConstants.NANOSECONDS_PER_SECOND))

    @classmethod
    def from_minutes_since_midnight(cls, minutes: int) -> LocalTime:
        """Factory method for creating a local time from the number of minutes which have elapsed since midnight.

        :param minutes: The number of minutes, in the range [0, 1439]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if minutes < 0 or minutes > PyodaConstants.MINUTES_PER_DAY - 1:
            _Preconditions._check_argument_range("minutes", minutes, 0, PyodaConstants.MINUTES_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(minutes * PyodaConstants.NANOSECONDS_PER_MINUTE))

    @classmethod
    def from_hours_since_midnight(cls, hours: int) -> LocalTime:
        """Factory method for creating a local time from the number of hours which have elapsed since midnight.

        :param hours: The number of hours, in the range [0, 23]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if hours < 0 or hours > PyodaConstants.HOURS_PER_DAY - 1:
            _Preconditions._check_argument_range("hours", hours, 0, PyodaConstants.HOURS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(hours * PyodaConstants.NANOSECONDS_PER_HOUR))

    @property
    def hour(self) -> int:
        """The hour of day of this local time, in the range 0 to 23 inclusive."""
        # Effectively nanoseconds / NanosecondsPerHour, but apparently rather more efficient.
        return _towards_zero_division((self.__nanoseconds >> 13), 439453125)

    @property
    def clock_hour_of_half_day(self) -> int:
        """The hour of the half-day of this local time, in the range 1 to 12 inclusive."""
        # TODO: unchecked
        hour_of_half_day = _int32_overflow(_csharp_modulo(self.hour, 12))
        return 12 if hour_of_half_day == 0 else hour_of_half_day

    @property
    def minute(self) -> int:
        """The minute of this local time, in the range 0 to 59 inclusive."""
        # TODO: unchecked
        # Effectively nanoseconds / NanosecondsPerMinute, but apparently rather more efficient.
        minute_of_day = _towards_zero_division((self.__nanoseconds >> 11), 29296875)
        return _csharp_modulo(minute_of_day, PyodaConstants.MINUTES_PER_HOUR)

    @property
    def second(self) -> int:
        """The second of this local time within the minute, in the range 0 to 59 inclusive."""
        # TODO: unchecked
        second_of_day = _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND)
        return _csharp_modulo(second_of_day, PyodaConstants.SECONDS_PER_MINUTE)

    @property
    def millisecond(self) -> int:
        """The millisecond of this local time within the second, in the range 0 to 999 inclusive."""
        # TODO: unchecked
        millisecond_of_day = _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_MILLISECOND)
        return _csharp_modulo(millisecond_of_day, PyodaConstants.MILLISECONDS_PER_SECOND)

    @property
    def tick_of_second(self) -> int:
        """The tick of this local time within the second, in the range 0 to 9,999,999 inclusive."""
        # TODO: unchecked
        return _int32_overflow(_csharp_modulo(self.tick_of_day, PyodaConstants.TICKS_PER_SECOND))

    @property
    def tick_of_day(self) -> int:
        """The tick of this local time within the day, in the range 0 to 863,999,999,999 inclusive.

        If the value does not fall on a tick boundary, it will be truncated towards zero.
        """
        return _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_TICK)

    @property
    def nanosecond_of_second(self) -> int:
        """The nanosecond of this local time within the second, in the range 0 to 999,999,999 inclusive."""
        # TODO: unchecked
        return _int32_overflow(_csharp_modulo(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND))

    @property
    def nanosecond_of_day(self) -> int:
        """The nanosecond of this local time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__nanoseconds

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LocalTime):
            return self.__nanoseconds == other.__nanoseconds
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __lt__(self, other: LocalTime) -> bool:
        return self.__nanoseconds < other.__nanoseconds

    def __le__(self, other: LocalTime) -> bool:
        return self.__nanoseconds <= other.__nanoseconds

    def __gt__(self, other: LocalTime) -> bool:
        return self.__nanoseconds > other.__nanoseconds

    def __ge__(self, other: LocalTime) -> bool:
        return self.__nanoseconds >= other.__nanoseconds

    def compare_to(self, other: LocalTime) -> int:
        return self.__nanoseconds - other.__nanoseconds

    def on(self, date: LocalDate) -> LocalDateTime:
        """Combines this ``LocalTime`` with the given ``LocalDate`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param date: The date to combine with this time
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return date + self
