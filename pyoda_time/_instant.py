# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
import functools
from typing import TYPE_CHECKING, Final, Self, final, overload

from ._duration import Duration
from ._pyoda_constants import PyodaConstants

if TYPE_CHECKING:
    from . import (
        CalendarSystem,
        DateTimeZone,
        Offset,
        ZonedDateTime,
    )
    from ._local_instant import _LocalInstant

from ._local_date import LocalDate
from ._local_time import LocalTime
from .utility._csharp_compatibility import _sealed, _to_ticks, _towards_zero_division
from .utility._preconditions import _Preconditions
from .utility._tick_arithmetic import _TickArithmetic


class _InstantMeta(type):
    """Metaclass for Instant.

    This serves two purposes:
    - Provide "class properties" to emulate C# static properties.
    - Provide a way to avoid circular imports by redefining static members as class properties.
    """

    @property
    @functools.cache
    def min_value(cls) -> Instant:
        """Represents the smallest possible Instant.

        This value is equivalent to -9998-01-01T00:00:00Z
        """
        return Instant._ctor(days=Instant._MIN_DAYS, nano_of_day=0)

    @property
    @functools.cache
    def max_value(cls) -> Instant:
        """Represents the largest possible Instant.

        This value is equivalent to 9999-12-31T23:59:59.999999999Z
        """
        from . import PyodaConstants

        return Instant._ctor(days=Instant._MAX_DAYS, nano_of_day=PyodaConstants.NANOSECONDS_PER_DAY - 1)


@final
@_sealed
class Instant(metaclass=_InstantMeta):
    """Represents an instant on the global timeline, with nanosecond resolution.

    An Instant has no concept of a particular time zone or calendar: it simply represents a point in
    time that can be globally agreed-upon.
    Equality and ordering comparisons are defined in the natural way, with earlier points on the timeline
    being considered "less than" later points.
    """

    # These correspond to -9998-01-01 and 9999-12-31 respectively.
    _MIN_DAYS: Final[int] = -4371222
    _MAX_DAYS: Final[int] = 2932896

    __MIN_TICKS: Final[int] = _MIN_DAYS * PyodaConstants.TICKS_PER_DAY
    __MAX_TICKS: Final[int] = (_MAX_DAYS + 1) * PyodaConstants.TICKS_PER_DAY - 1
    __MIN_MILLISECONDS: Final[int] = _MIN_DAYS * PyodaConstants.MILLISECONDS_PER_DAY
    __MAX_MILLISECONDS: Final[int] = (_MAX_DAYS + 1) * PyodaConstants.MILLISECONDS_PER_DAY - 1
    __MIN_SECONDS: Final[int] = _MIN_DAYS * PyodaConstants.SECONDS_PER_DAY
    __MAX_SECONDS: Final[int] = (_MAX_DAYS + 1) * PyodaConstants.SECONDS_PER_DAY - 1

    @classmethod
    def _before_min_value(cls) -> Self:
        """Instant which is invalid *except* for comparison purposes; it is earlier than any valid value.

        This must never be exposed.
        """
        return cls.__ctor(days=Duration._MIN_DAYS, deliberately_invalid=True)

    @classmethod
    def _after_max_value(cls) -> Self:
        """Instant which is invalid *except* for comparison purposes; it is later than any valid value.

        This must never be exposed.
        """
        return cls.__ctor(days=Duration._MAX_DAYS, deliberately_invalid=True)

    def __init__(self) -> None:
        self.__duration = Duration.zero

    @classmethod
    def _ctor(cls, *, days: int, nano_of_day: int) -> Instant:
        self = super().__new__(cls)
        self.__duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        return self

    @classmethod
    @overload
    def __ctor(cls, *, duration: Duration) -> Instant:
        """Constructor which constructs a new instance with the given duration, which is trusted to be valid.

        Should only be called from FromTrustedDuration and FromUntrustedDuration.
        """
        ...

    @classmethod
    @overload
    def __ctor(cls, *, days: int, deliberately_invalid: bool) -> Instant:
        """Constructor which should *only* be used to construct the invalid instances."""
        ...

    @classmethod
    def __ctor(
        cls, duration: Duration | None = None, days: int | None = None, deliberately_invalid: bool | None = None
    ) -> Instant:
        """Private constructors implementation."""
        self = super().__new__(cls)
        if duration is not None and days is None and deliberately_invalid is None:
            self.__duration = duration
        elif duration is None and days is not None and deliberately_invalid is not None:
            self.__duration = Duration._ctor(days=days, nano_of_day=0)
        else:
            raise TypeError
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented
        return self.__duration == other.__duration

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented
        return not (self.__duration == other.__duration)

    def __lt__(self, other: Instant) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration < other.__duration

    def __le__(self, other: Instant) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration <= other.__duration

    def __gt__(self, other: Instant) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration > other.__duration

    def __ge__(self, other: Instant) -> bool:
        if not isinstance(other, Instant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration >= other.__duration

    def __add__(self, other: Duration) -> Instant:
        if isinstance(other, Duration):
            return self._from_untrusted_duration(self.__duration + other)
        return NotImplemented  # type: ignore[unreachable]

    @overload
    def minus(self, duration: Duration, /) -> Instant: ...

    @overload
    def minus(self, instant: Instant, /) -> Duration: ...

    def minus(self, other: Instant | Duration, /) -> Instant | Duration:
        return self - other

    @staticmethod
    @overload
    def subtract(left: Instant, right: Instant, /) -> Duration: ...

    @staticmethod
    @overload
    def subtract(left: Instant, right: Duration, /) -> Instant: ...

    @staticmethod
    def subtract(left: Instant, right: Instant | Duration, /) -> Instant | Duration:
        return left - right

    @overload
    def __sub__(self, other: Instant) -> Duration: ...

    @overload
    def __sub__(self, other: Duration) -> Instant: ...

    def __sub__(self, other: Instant | Duration) -> Instant | Duration:
        if isinstance(other, Instant):
            return self.__duration - other.__duration
        if isinstance(other, Duration):
            return self._from_untrusted_duration(self.__duration - other)
        return NotImplemented  # type: ignore[unreachable]

    @property
    def _time_since_epoch(self) -> Duration:
        """Get the elapsed time since the Unix epoch, to nanosecond resolution.

        :return: The elapsed time since the Unix epoch.
        """
        return self.__duration

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.__duration._floor_days

    @classmethod
    def from_unix_time_ticks(cls, ticks: int) -> Instant:
        """Initializes a new Instant based on a number of ticks since the Unix epoch."""
        _Preconditions._check_argument_range("ticks", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Instant._from_trusted_duration(Duration.from_ticks(ticks))

    @classmethod
    def _from_trusted_duration(cls, duration: Duration) -> Instant:
        """Creates an Instant with the given duration, with no validation (in release mode)."""
        # TODO Preconditions.DebugCheckArgumentRange
        return Instant.__ctor(duration=duration)

    @classmethod
    def _from_untrusted_duration(cls, duration: Duration) -> Instant:
        """Creates an Instant with the given duration, validating that it has a suitable "day" part.

        (It is assumed that the nanoOfDay is okay.)
        """
        days = duration._floor_days
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            raise OverflowError("Operation would overflow range of Instant")
        return Instant.__ctor(duration=duration)

    def to_unix_time_ticks(self) -> int:
        """Gets the number of ticks since the Unix epoch.

        Negative values represent instants before the Unix epoch. A tick is equal to 100 nanoseconds. There are 10,000
        ticks in a millisecond. If the number of nanoseconds in this instant is not an exact number of ticks, the value
        is truncated towards the start of time.
        """
        from . import PyodaConstants

        return _TickArithmetic.bounded_days_and_tick_of_day_to_ticks(
            self.__duration._floor_days,
            _towards_zero_division(self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_TICK),
        )

    @classmethod
    def from_unix_time_milliseconds(cls, milliseconds: int) -> Instant:
        """Initializes a new Instant struct based on a number of milliseconds since the Unix epoch of (ISO) January 1st
        1970, midnight, UTC."""
        _Preconditions._check_argument_range(
            "milliseconds", milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS
        )
        return Instant._from_trusted_duration(Duration.from_milliseconds(milliseconds))

    @classmethod
    def from_unix_time_seconds(cls, seconds: int) -> Instant:
        """Initializes a new Instant based on a number of seconds since the Unix epoch of (ISO) January 1st 1970,
        midnight, UTC."""
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        return cls._from_trusted_duration(Duration.from_seconds(seconds))

    def to_unix_time_seconds(self) -> int:
        """Gets the number of seconds since the Unix epoch.

        Negative values represent instants before the Unix epoch. If the number of nanoseconds in this instant is not an
        exact number of seconds, the value is truncated towards the start of time.
        """
        from . import PyodaConstants

        return self.__duration._floor_days * PyodaConstants.SECONDS_PER_DAY + _towards_zero_division(
            self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_SECOND
        )

    def to_unix_time_milliseconds(self) -> int:
        """Gets the number of milliseconds since the Unix epoch.

        Negative values represent instants before the Unix epoch. If the number of nanoseconds in this instant is not an
        exact number of milliseconds, the value is truncated towards the start of time.
        """
        from . import PyodaConstants

        return self.__duration._floor_days * PyodaConstants.MILLISECONDS_PER_DAY + _towards_zero_division(
            self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_MILLISECOND
        )

    @staticmethod
    def max(x: Instant, y: Instant) -> Instant:
        """Returns the later instant of the given two."""
        return max(x, y)

    @staticmethod
    def min(x: Instant, y: Instant) -> Instant:
        """Returns the earlier instant of the given two."""
        return min(x, y)

    # region IEquatable<Instant> Members

    def equals(self, other: Instant) -> bool:
        return self == other

    # endregion

    def to_julian_date(self) -> float:
        """Returns the Julian Date of this instance - the number of days since ``PyodaConstants.JULIAN_EPOCH``
        (noon on January 1st, 4713 BCE in the Julian calendar).

        :return: The number of days (including fractional days) since the Julian Epoch.
        """
        return (self - PyodaConstants.JULIAN_EPOCH).total_days

    @classmethod
    def from_julian_date(cls, julian_date: float) -> Instant:
        """Converts a Julian Date representing the given number of days since ``PyodaConstants.JULIAN_EPOCH`` (noon on
        January 1st, 4713 BCE in the Julian calendar) into an ``Instant``.

        :param julian_date: The number of days since the Julian Epoch to convert into an ``Instant``.
        :return: An ``Instant`` value which is ``julianDate`` days after the Julian Epoch.
        """
        return PyodaConstants.JULIAN_EPOCH + Duration.from_days(julian_date)

    @classmethod
    def from_datetime_utc(cls, datetime: datetime.datetime) -> Instant:
        """Converts a datetime.datetime into a new Instant representing the same instant in time.

        The datetime must have a truthy tzinfo, and must have a UTC offset of 0.
        """
        from . import PyodaConstants

        # TODO Precondition.CheckArgument
        # TODO Better exceptions?
        # Roughly equivalent to DateTimeKind.Local
        if (utc_offset := datetime.utcoffset()) is not None and utc_offset.total_seconds() != 0:
            raise ValueError()
        # Roughly equivalent to DateTimeKind.Unspecified
        if datetime.tzinfo is None:
            raise ValueError()
        return PyodaConstants.BCL_EPOCH.plus_ticks(_to_ticks(datetime))

    @classmethod
    def from_utc(
        cls,
        year: int,
        month_of_year: int,
        day_of_month: int,
        hour_of_day: int,
        minute_of_hour: int,
        second_of_minute: int = 0,
    ) -> Instant:
        """Returns a new Instant corresponding to the given UTC date and time in the ISO calendar.

        In most cases applications should use ZonedDateTime to represent a date and time, but this method is useful in
        some situations where an Instant is required, such as time zone testing.
        """

        days = LocalDate(year=year, month=month_of_year, day=day_of_month)._days_since_epoch
        nano_of_day = LocalTime(hour=hour_of_day, minute=minute_of_hour, second=second_of_minute).nanosecond_of_day
        return Instant._ctor(days=days, nano_of_day=nano_of_day)

    def __hash__(self) -> int:
        return hash(self.__duration)

    def plus_ticks(self, ticks: int) -> Instant:
        """Returns a new value of this instant with the given number of ticks added to it."""
        return self._from_untrusted_duration(self.__duration + Duration.from_ticks(ticks))

    def plus_nanoseconds(self, nanoseconds: int) -> Instant:
        return self._from_untrusted_duration(self.__duration + Duration.from_nanoseconds(nanoseconds))

    @property
    def _is_valid(self) -> bool:
        """Returns whether or not this is a valid instant.

        Returns true for all but before_min_value and after_max_value.
        """
        return self._MIN_DAYS <= self._days_since_epoch <= self._MAX_DAYS

    def _plus(self, offset: Offset) -> _LocalInstant:
        """Adds the given offset to this instant, to return a LocalInstant.

        A positive offset indicates that the local instant represents a "later local time" than the UTC representation
        of this instant.
        """
        from ._local_instant import _LocalInstant

        return _LocalInstant._ctor(nanoseconds=self.__duration._plus_small_nanoseconds(offset.nanoseconds))

    @staticmethod
    def add(left: Instant, right: Duration) -> Instant:
        """Adds a duration to an instant. Friendly alternative to ``+``.

        :param left: The left hand side of the operator.
        :param right: >The right hand side of the operator.
        :return: A new ``Instant`` representing the sum of the given values.
        """
        return left + right

    def plus(self, other: Duration) -> Instant:
        """Returns the result of adding a duration to this instant, for a fluent alternative to the + operator."""
        return self + other

    def _safe_plus(self, offset: Offset) -> _LocalInstant:
        """Adds the given offset to this instant, either returning a normal LocalInstant, or
        LocalInstant.before_min_value() or LocalInstant.after_max_value() if the value would overflow."""
        from ._local_instant import _LocalInstant

        days = self.__duration._floor_days
        if self._MIN_DAYS < days < self._MAX_DAYS:
            return self._plus(offset)
        if days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        as_duration = self.__duration._plus_small_nanoseconds(offset.nanoseconds)
        if as_duration._floor_days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if as_duration._floor_days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        return _LocalInstant._ctor(nanoseconds=as_duration)

    def in_zone(self, zone: DateTimeZone, calendar: CalendarSystem | None = None) -> ZonedDateTime:
        from . import ZonedDateTime

        _Preconditions._check_not_null(zone, "zone")
        if calendar is None:
            return ZonedDateTime(instant=self, zone=zone)
        return ZonedDateTime(instant=self, zone=zone, calendar=calendar)

    @property
    def _nanosecond_of_day(self) -> int:
        return self.__duration._nanosecond_of_floor_day

    # region IComparable<Instant> and IComparable Members

    def compare_to(self, other: Instant | None) -> int:
        """Compares the current object with another object of the same type. See the type documentation for a
        description of ordering semantics.

        :param other: An object to compare with this object.
        :return: An integer that indicates the relative order of the objects being compared.

        The return value has the following meanings:

        =====  ======
        Value  Meaning
        =====  ======
        < 0    This object is less than the ``other`` parameter.
        0      This object is equal to ``other``.
        > 0    This object is greater than ``other``.
        =====  ======
        """
        if other is None:
            return 1
        if not isinstance(other, Instant):
            raise TypeError(f"{self.__class__.__name__} cannot be compared to {other.__class__.__name__}")
        return self.__duration.compare_to(other.__duration)

    # endregion

    def in_utc(self) -> ZonedDateTime:
        from . import DateTimeZone, LocalDate, OffsetDateTime, OffsetTime, ZonedDateTime

        offset_date_time = OffsetDateTime._ctor(
            local_date=LocalDate._ctor(days_since_epoch=self.__duration._floor_days),
            offset_time=OffsetTime._ctor(nanosecond_of_day_zero_offset=self.__duration._nanosecond_of_floor_day),
        )
        return ZonedDateTime._ctor(offset_date_time=offset_date_time, zone=DateTimeZone.utc)

    def __repr__(self) -> str:
        from pyoda_time._compatibility._culture_info import CultureInfo
        from pyoda_time.text import InstantPattern

        return InstantPattern._bcl_support.format(self, None, CultureInfo.current_culture)

    def __format__(self, format_spec: str) -> str:
        from pyoda_time._compatibility._culture_info import CultureInfo
        from pyoda_time.text import InstantPattern

        return InstantPattern._bcl_support.format(self, format_spec, CultureInfo.current_culture)
