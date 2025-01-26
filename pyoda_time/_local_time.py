# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
import functools
from typing import TYPE_CHECKING, final, overload

from ._pyoda_constants import PyodaConstants
from .utility._csharp_compatibility import (
    _csharp_modulo,
    _int32_overflow,
    _int64_overflow,
    _sealed,
    _towards_zero_division,
)
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from . import LocalDateTime, Offset, OffsetTime, Period
    from ._local_date import LocalDate

__all__ = ["LocalTime"]


class _LocalTimeMeta(type):
    @property
    @functools.cache
    def midnight(self) -> LocalTime:
        """Local time at midnight, i.e. 0 hours, 0 minutes, 0 seconds."""
        return LocalTime(hour=0, minute=0, second=0)

    @property
    def min_value(cls) -> LocalTime:
        """The minimum value of this type; equivalent to ``Midnight``."""
        return cls.midnight

    @property
    @functools.cache
    def noon(self) -> LocalTime:
        """Local time at noon, i.e. 12 hours, 0 minutes, 0 seconds."""
        return LocalTime(hour=12, minute=0, second=0)

    @property
    @functools.cache
    def max_value(cls) -> LocalTime:
        """The maximum value of this type, one nanosecond before midnight.

        This is useful if you have to use an inclusive upper bound for some reason. In general, it's better to use an
        exclusive upper bound, in which case use midnight of the following day.
        """
        return LocalTime._ctor(nanoseconds=PyodaConstants.NANOSECONDS_PER_DAY - 1)


@final
@_sealed
class LocalTime(metaclass=_LocalTimeMeta):
    """LocalTime is an immutable struct representing a time of day, with no reference to a particular calendar, time
    zone or date."""

    def __init__(self, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0) -> None:
        """Initialises a ``LocalTime`` at the given hour, minute, second and millisecond.

        :param hour: The hour of day.
        :param minute: The minute of the hour.
        :param second: The second of the minute.
        :param millisecond: The millisecond of the second.
        :raises ValueError: The parameters do not form a valid time.
        """
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
    def from_hour_minute_second_millisecond_tick(
        cls, hour: int, minute: int, second: int, millisecond: int, tick_within_millisecond: int
    ) -> LocalTime:
        """Factory method to create a local time at the given hour, minute, second, millisecond and tick within
        millisecond.

        :param hour: The hour of day.
        :param minute: The minute of the hour.
        :param second: The second of the minute.
        :param millisecond: The millisecond of the second.
        :param tick_within_millisecond: The tick within the millisecond.
        :return: The resulting time.
        :raises ValueError: The parameters do not form a valid time.
        """
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
    def from_hour_minute_second_tick(cls, hour: int, minute: int, second: int, tick_within_second: int) -> LocalTime:
        """Factory method for creating a local time from the hour of day, minute of hour, second of minute, and tick of
        second.

        :param hour: The hour of day in the desired time, in the range [0, 23].
        :param minute: The minute of hour in the desired time, in the range [0, 59].
        :param second: The second of minute in the desired time, in the range [0, 59].
        :param tick_within_second: The tick within the second in the desired time, in the range [0, 9999999].
        :return: The resulting time.
        :raises ValueError: The parameters do not form a valid time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if (
            hour < 0
            or hour > PyodaConstants.HOURS_PER_DAY - 1
            or minute < 0
            or minute > PyodaConstants.MINUTES_PER_HOUR - 1
            or second < 0
            or second > PyodaConstants.SECONDS_PER_MINUTE - 1
            or tick_within_second < 0
            or tick_within_second > PyodaConstants.TICKS_PER_SECOND - 1
        ):
            _Preconditions._check_argument_range("hour", hour, 0, PyodaConstants.HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range("minute", minute, 0, PyodaConstants.MINUTES_PER_HOUR - 1)
            _Preconditions._check_argument_range("second", second, 0, PyodaConstants.SECONDS_PER_MINUTE - 1)
            _Preconditions._check_argument_range(
                "tick_within_second", tick_within_second, 0, PyodaConstants.TICKS_PER_SECOND - 1
            )

        nanoseconds = (
            hour * PyodaConstants.NANOSECONDS_PER_HOUR
            + minute * PyodaConstants.NANOSECONDS_PER_MINUTE
            + second * PyodaConstants.NANOSECONDS_PER_SECOND
            + tick_within_second * PyodaConstants.NANOSECONDS_PER_TICK
        )
        return LocalTime._ctor(nanoseconds=nanoseconds)

    @classmethod
    def from_hour_minute_second_nanosecond(
        cls, hour: int, minute: int, second: int, nanosecond_within_second: int
    ) -> LocalTime:
        """Factory method for creating a local time from the hour of day, minute of hour, second of minute, and
        nanosecond of second.

        :param hour: The hour of day in the desired time, in the range [0, 23].
        :param minute: The minute of hour in the desired time, in the range [0, 59].
        :param second: The second of minute in the desired time, in the range [0, 59].
        :param nanosecond_within_second: The nanosecond within the second in the desired time, in the range [0,
            999999999].
        :return: The resulting time.
        :raises ValueError: The parameters do not form a valid time.
        """
        if (
            hour < 0
            or hour > PyodaConstants.HOURS_PER_DAY - 1
            or minute < 0
            or minute > PyodaConstants.MINUTES_PER_HOUR - 1
            or second < 0
            or second > PyodaConstants.SECONDS_PER_MINUTE - 1
            or nanosecond_within_second < 0
            or nanosecond_within_second > PyodaConstants.NANOSECONDS_PER_SECOND - 1
        ):
            _Preconditions._check_argument_range("hour", hour, 0, PyodaConstants.HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range("minute", minute, 0, PyodaConstants.MINUTES_PER_HOUR - 1)
            _Preconditions._check_argument_range("second", second, 0, PyodaConstants.SECONDS_PER_MINUTE - 1)
            _Preconditions._check_argument_range(
                "nanoseconds_within_second", nanosecond_within_second, 0, PyodaConstants.NANOSECONDS_PER_SECOND - 1
            )
        return cls._from_hour_minute_second_nanosecond_trusted(hour, minute, second, nanosecond_within_second)

    @classmethod
    def _from_hour_minute_second_nanosecond_trusted(
        cls,
        hour: int,
        minute: int,
        second: int,
        nanosecond_within_second: int,
    ) -> LocalTime:
        """Factory method for creating a local time from the hour of day, minute of hour, second of minute, and
        nanosecond of second where the values have already been validated."""
        return cls._ctor(
            nanoseconds=hour * PyodaConstants.NANOSECONDS_PER_HOUR
            + minute * PyodaConstants.NANOSECONDS_PER_MINUTE
            + second * PyodaConstants.NANOSECONDS_PER_SECOND
            + nanosecond_within_second
        )

    @classmethod
    def _ctor(cls, *, nanoseconds: int) -> LocalTime:
        """Constructor only called from other parts of Noda Time - trusted to be the range [0, NanosecondsPerDay)."""
        # TODO: _Preconditions._check_debug_argument_range()
        self = super().__new__(cls)
        self.__nanoseconds = nanoseconds
        return self

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
        # TODO: unchecked
        return LocalTime._ctor(nanoseconds=_int64_overflow(ticks * PyodaConstants.NANOSECONDS_PER_TICK))

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
        return cls._ctor(nanoseconds=_int64_overflow(milliseconds * PyodaConstants.NANOSECONDS_PER_MILLISECOND))

    @classmethod
    def from_seconds_since_midnight(cls, seconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of seconds which have elapsed since midnight.

        :param seconds: The number of seconds, in the range [0, 86,399]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if seconds < 0 or seconds > PyodaConstants.SECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range("seconds", seconds, 0, PyodaConstants.SECONDS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int64_overflow(seconds * PyodaConstants.NANOSECONDS_PER_SECOND))

    @classmethod
    def from_minutes_since_midnight(cls, minutes: int) -> LocalTime:
        """Factory method for creating a local time from the number of minutes which have elapsed since midnight.

        :param minutes: The number of minutes, in the range [0, 1439]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if minutes < 0 or minutes > PyodaConstants.MINUTES_PER_DAY - 1:
            _Preconditions._check_argument_range("minutes", minutes, 0, PyodaConstants.MINUTES_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int64_overflow(minutes * PyodaConstants.NANOSECONDS_PER_MINUTE))

    @classmethod
    def from_hours_since_midnight(cls, hours: int) -> LocalTime:
        """Factory method for creating a local time from the number of hours which have elapsed since midnight.

        :param hours: The number of hours, in the range [0, 23]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if hours < 0 or hours > PyodaConstants.HOURS_PER_DAY - 1:
            _Preconditions._check_argument_range("hours", hours, 0, PyodaConstants.HOURS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int64_overflow(hours * PyodaConstants.NANOSECONDS_PER_HOUR))

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
    def microsecond(self) -> int:
        """The microsecond of this local time within the second, in the range 0 to 999,999 inclusive."""
        # TODO: unchecked
        microsecond_of_day = _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_MICROSECOND)
        return _csharp_modulo(microsecond_of_day, PyodaConstants.MICROSECONDS_PER_SECOND)

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

    def __add__(self, other: Period) -> LocalTime:
        """Creates a new local time by adding a period to an existing time.

        The period must not contain any date-related units (days etc.) with non-zero values.

        :param other: The period to add
        :return: The result of adding the period to the time, wrapping via midnight if necessary
        """
        from ._period import Period

        if not isinstance(other, Period):
            return NotImplemented  # type: ignore[unreachable]

        _Preconditions._check_not_null(other, "other")
        _Preconditions._check_argument(
            not other.has_date_component, "other", "Cannot add a period with a date component to a time"
        )
        return (
            self.plus_hours(other.hours)
            .plus_minutes(other.minutes)
            .plus_seconds(other.seconds)
            .plus_milliseconds(other.milliseconds)
            .plus_ticks(other.ticks)
            .plus_nanoseconds(other.nanoseconds)
        )

    @staticmethod
    def add(time: LocalTime, period: Period) -> LocalTime:
        """Adds the specified period to the time. Friendly alternative to ``+``.

        :param time: The time to add the period to
        :param period: The period to add. Must not contain any (non-zero) date units.
        :return: The sum of the given time and period
        """
        return time + period

    def plus(self, period: Period) -> LocalTime:
        """Adds the specified period to this time. Fluent alternative to ``+``.

        :param period: The period to add. Must not contain any (non-zero) date units.
        :return: The sum of this time and the given period
        """
        return self + period

    @overload
    def __sub__(self, local_time: LocalTime) -> Period: ...

    @overload
    def __sub__(self, period: Period) -> LocalTime: ...

    def __sub__(self, other: LocalTime | Period) -> LocalTime | Period:
        from ._period import Period

        if isinstance(other, Period):
            _Preconditions._check_not_null(other, "other")
            _Preconditions._check_argument(
                not other.has_date_component, "other", "Cannot subtract a period with a date component from a time"
            )
            return (
                self.plus_hours(-other.hours)
                .plus_minutes(-other.minutes)
                .plus_seconds(-other.seconds)
                .plus_milliseconds(-other.milliseconds)
                .plus_ticks(-other.ticks)
                .plus_nanoseconds(-other.nanoseconds)
            )

        if isinstance(other, LocalTime):
            return Period.between(other, self)

        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    @overload
    def subtract(time: LocalTime, period: Period, /) -> LocalTime:
        """Subtracts the specified period from the time. Friendly alternative to ``-``.

        :param time: The time to subtract the period from
        :param period: The period to subtract. Must not contain any (non-zero) date units.
        :return: The result of subtracting the given period from the time.
        """

    @staticmethod
    @overload
    def subtract(lhs: LocalTime, rhs: LocalTime, /) -> Period:
        """Subtracts one time from another, returning the result as a ``Period`` with units of years, months and days.

        This is simply a convenience method for calling ``Period.between(LocalTime,LocalTime)``.

        :param lhs: The time to subtract from
        :param rhs: The time to subtract
        :return: The result of subtracting one time from another.
        """

    @staticmethod
    def subtract(lhs: LocalTime, rhs: LocalTime | Period, /) -> LocalTime | Period:
        return lhs - rhs

    @overload
    def minus(self, period: Period, /) -> LocalTime:
        """Subtracts the specified period from this time. Fluent alternative to ``-``.

        :param period: The period to subtract. Must not contain any (non-zero) date units.
        :return: The result of subtracting the given period from this time.
        """

    @overload
    def minus(self, time: LocalTime, /) -> Period:
        """Subtracts the specified time from this time, returning the result as a ``Period``. Fluent alternative to
        ``-``.

        :param time: The time to subtract from this
        :return: The difference between the specified time and this one
        """

    def minus(self, period_or_time: Period | LocalTime, /) -> Period | LocalTime:
        return self - period_or_time

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented
        return self.__nanoseconds == other.__nanoseconds

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented
        return not (self == other)

    def __lt__(self, other: LocalTime) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented  # type: ignore[unreachable]
        return self.__nanoseconds < other.__nanoseconds

    def __le__(self, other: LocalTime) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented  # type: ignore[unreachable]
        return self.__nanoseconds <= other.__nanoseconds

    def __gt__(self, other: LocalTime) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented  # type: ignore[unreachable]
        return self.__nanoseconds > other.__nanoseconds

    def __ge__(self, other: LocalTime) -> bool:
        if not isinstance(other, LocalTime):
            return NotImplemented  # type: ignore[unreachable]
        return self.__nanoseconds >= other.__nanoseconds

    def compare_to(self, other: LocalTime | None) -> int:
        if other is None:
            return 1
        if not isinstance(other, LocalTime):
            raise TypeError(f"{self.__class__.__name__} cannot be compared to {other.__class__.__name__}")
        return self.__nanoseconds - other.__nanoseconds

    def __hash__(self) -> int:
        return hash(self.__nanoseconds)

    def plus_hours(self, hours: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of hours added.

        If the value goes past the start or end of the day, it wraps - so 11pm plus two hours is 1am, for example.

        :param hours: The number of hours to add
        :return: The current value plus the given number of hours.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._hours._add_local_time(self, hours)

    def plus_minutes(self, minutes: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of minutes added.

        If the value goes past the start or end of the day, it wraps - so 11pm plus 120 minutes is 1am, for example.

        :param minutes: The number of minutes to add
        :return: The current value plus the given number of minutes.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._minutes._add_local_time(self, minutes)

    def plus_seconds(self, seconds: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of seconds added.

        If the value goes past the start or end of the day, it wraps - so 11:59pm plus 120 seconds is
        12:01am, for example.

        :param seconds: The number of seconds to add
        :return: The current value plus the given number of seconds.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._seconds._add_local_time(self, seconds)

    def plus_milliseconds(self, milliseconds: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of milliseconds added.

        :param milliseconds: The number of milliseconds to add
        :return: The current value plus the given number of milliseconds.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._milliseconds._add_local_time(self, milliseconds)

    def plus_microseconds(self, microseconds: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of microseconds added.

        :param microseconds: The number of microseconds to add
        :return: The current value plus the given number of microseconds.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._microseconds._add_local_time(self, microseconds)

    def plus_ticks(self, ticks: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of ticks added.

        :param ticks: The number of ticks to add
        :return: The current value plus the given number of ticks.
        """
        from pyoda_time.fields._time_period_field import _TimePeriodField

        return _TimePeriodField._ticks._add_local_time(self, ticks)

    def plus_nanoseconds(self, nanoseconds: int) -> LocalTime:
        """Returns a new LocalTime representing the current value with the given number of nanoseconds added.

        :param nanoseconds: The number of nanoseconds to add
        :return: The current value plus the given number of ticks.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._nanoseconds._add_local_time(self, nanoseconds)

    def with_time_adjuster(self, adjuster: Callable[[LocalTime], LocalTime]) -> LocalTime:
        return _Preconditions._check_not_null(adjuster, "adjuster")(self)

    def with_offset(self, offset: Offset) -> OffsetTime:
        """Returns an ``OffsetTime`` for this time-of-day with the given offset.

        This method is purely a convenient alternative to calling the ``OffsetTime`` constructor directly.

        :param offset: The offset to apply.
        :return: The result of this time-of-day offset by the given amount.
        """
        from ._offset_time import OffsetTime

        return OffsetTime(self, offset)

    def on(self, date: LocalDate) -> LocalDateTime:
        """Combines this ``LocalTime`` with the given ``LocalDate`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param date: The date to combine with this time
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return date + self

    def __iter__(self) -> Iterator[int]:
        """Deconstruct this time into its components.

        :return: An iterator of integers representing the hour, minute, and second components of the time.
        """
        yield self.hour
        yield self.minute
        yield self.second

    @staticmethod
    def max(x: LocalTime, y: LocalTime) -> LocalTime:
        """Returns the later time of the given two.

        :param x: The first time to compare.
        :param y: The second time to compare.
        :return: The later time of ``x`` or ``y``.
        """
        return max(y, x)

    @staticmethod
    def min(x: LocalTime, y: LocalTime) -> LocalTime:
        """Returns the earlier time of the given two.

        :param x: The first time to compare.
        :param y: The second time to compare.
        :return: The earlier time of ``x`` or ``y``.
        """
        return min(y, x)

    # region Formatting

    def __repr__(self) -> str:
        from pyoda_time._compatibility._culture_info import CultureInfo
        from pyoda_time.text import LocalTimePattern

        return LocalTimePattern._bcl_support.format(self, None, CultureInfo.current_culture)

    def __format__(self, format_spec: str) -> str:
        from pyoda_time._compatibility._culture_info import CultureInfo
        from pyoda_time.text import LocalTimePattern

        return LocalTimePattern._bcl_support.format(self, format_spec, CultureInfo.current_culture)

    # endregion

    def to_time(self) -> datetime.time:
        """Converts this value to an equivalent ``datetime.time``.

        If the value does not fall on a microsecond boundary, it will be truncated to the earlier microsecond boundary.

        :return: The equivalent ``datetime.time``.
        """
        return datetime.time(
            hour=self.hour,
            minute=self.minute,
            second=self.second,
            microsecond=_towards_zero_division(self.nanosecond_of_second, PyodaConstants.NANOSECONDS_PER_MICROSECOND),
        )

    @classmethod
    def from_time(cls, time: datetime.time) -> LocalTime:
        """Constructs a ``LocalTime`` from a ``datetime.time``.

        :param time: The time of day to convert.
        :return: The ``LocalTime`` equivalent.
        """
        return cls.from_ticks_since_midnight(
            time.hour * PyodaConstants.TICKS_PER_HOUR
            + time.minute * PyodaConstants.TICKS_PER_MINUTE
            + time.second * PyodaConstants.TICKS_PER_SECOND
            + time.microsecond * PyodaConstants.TICKS_PER_MICROSECOND
        )
