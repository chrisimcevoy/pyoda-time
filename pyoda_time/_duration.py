# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
import decimal
import typing

from ._pyoda_constants import PyodaConstants
from .utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from .utility._preconditions import _Preconditions
from .utility._tick_arithmetic import _TickArithmetic

__all__ = ["Duration"]


class _DurationMeta(type):
    # TODO: In Noda Time, these properties use the private ctor which bypasses validation

    @property
    def zero(cls) -> Duration:
        """Gets a zero Duration of 0 nanoseconds."""
        return Duration()

    @property
    def epsilon(cls) -> Duration:
        """Return a Duration representing 1 nanosecond.

        This is the smallest amount by which an instant can vary.
        """
        return Duration._ctor(days=0, nano_of_day=1)

    @property
    def max_value(self) -> Duration:
        """The maximum value supported by ``Duration``."""
        return Duration._ctor(days=Duration._MAX_DAYS, nano_of_day=PyodaConstants.NANOSECONDS_PER_DAY - 1)

    @property
    def min_value(self) -> Duration:
        """The minimum value supported by ``Duration``."""
        return Duration._ctor(days=Duration._MIN_DAYS, nano_of_day=0)

    @property
    def one_week(self) -> Duration:
        """Return a ``Duration`` equal to the number of nanoseconds in 1 standard week (7 days).

        equal to the number of nanoseconds in 1 standard week (7 days).
        """
        return Duration._ctor(days=7, nano_of_day=0)

    @property
    def one_day(self) -> Duration:
        """Represents the ``Duration`` value equal to the number of nanoseconds in 1 day.

        The value of this property is 86.4 trillion nanoseconds; that is, 86,400,000,000,000 nanoseconds.
        """
        return Duration._ctor(days=1, nano_of_day=0)


@typing.final
@_sealed
class Duration(metaclass=_DurationMeta):
    """Represents a fixed (and calendar-independent) length of time."""

    # TODO: Noda Time's Duration class defines MaxDays as `(1 << 24) - 1` and MinDays as
    #  `~MaxDays`. However, that range is not sufficiently large for timedelta conversion.
    #  The thinking here is to retain the flavour of the Noda Time implementation, while
    #  accommodating the range of the standard way of representing durations in Python.
    _MAX_DAYS: typing.Final[int] = (1 << 30) - 1
    _MIN_DAYS: typing.Final[int] = ~_MAX_DAYS

    _MIN_NANOSECONDS: typing.Final[int] = _MIN_DAYS * PyodaConstants.NANOSECONDS_PER_DAY
    _MAX_NANOSECONDS: typing.Final[int] = ((_MAX_DAYS + 1) * PyodaConstants.NANOSECONDS_PER_DAY) - 1

    _MIN_DECIMAL_NANOSECONDS: typing.Final[decimal.Decimal] = decimal.Decimal(_MIN_NANOSECONDS)
    _MAX_DECIMAL_NANOSECONDS: typing.Final[decimal.Decimal] = decimal.Decimal(_MAX_NANOSECONDS)

    def __init__(self) -> None:
        self.__days = 0
        self.__nano_of_day = 0

    @classmethod
    def _ctor(cls, *, days: int, nano_of_day: int = 0) -> Duration:
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            _Preconditions._check_argument_range("days", days, cls._MIN_DAYS, cls._MAX_DAYS)
        # TODO: _Precondition._debug_check_argument_range()
        self = super().__new__(cls)
        self.__days = days
        self.__nano_of_day = nano_of_day
        return self

    @classmethod
    @typing.overload
    def __ctor(
        cls,
        *,
        units: int,
        param_name: str,
        min_value: int,
        max_value: int,
        units_per_day: int,
        nanos_per_unit: int,
    ) -> Duration:
        """Constructs an instance from a given number of units.

        This was previously a method (FromUnits) but making it a constructor avoids calling the other constructor which
        validates its "days" parameter. Note that we could compute various parameters from nanosPerUnit, but we know
        them as compile-time constants, so there's no point in recomputing them on each call.
        """
        ...

    @classmethod
    @typing.overload
    def __ctor(cls, *, days: int, nano_of_day: int, no_validation: bool) -> Duration:
        """Trusted constructor with no validation.

        The value of the noValidation parameter is ignored completely; its name is just to be suggestive.
        """
        ...

    @classmethod
    def __ctor(
        cls,
        *,
        days: int | None = None,
        nano_of_day: int | None = None,
        no_validation: bool | None = None,
        units: int | None = None,
        param_name: str | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
        units_per_day: int | None = None,
        nanos_per_unit: int | None = None,
    ) -> Duration:
        """Internal constructor implementation."""
        self = super().__new__(cls)
        if days is not None and nano_of_day is not None and no_validation is not None:
            self.__days = days
            self.__nano_of_day = nano_of_day
        elif (
            units is not None
            and param_name is not None
            and min_value is not None
            and max_value is not None
            and units_per_day is not None
            and nanos_per_unit is not None
        ):
            _Preconditions._check_argument_range(param_name, units, min_value, max_value)
            self.__days = _towards_zero_division(units, units_per_day)
            unit_of_day = units - (units_per_day * self.__days)
            if unit_of_day < 0:
                self.__days -= 1
                unit_of_day += units_per_day
            self.__nano_of_day = unit_of_day * nanos_per_unit
        else:
            raise TypeError
        return self

    @property
    def _floor_days(self) -> int:
        """Days portion of this duration."""
        return self.__days

    @property
    def _nanosecond_of_floor_day(self) -> int:
        """Nanosecond within the "floor day".

        This is *always* non-negative, even for negative durations.
        """
        return self.__nano_of_day

    @property
    def days(self) -> int:
        """The whole number of standard (24 hour) days within the duration.

        This is truncated towards zero; For example, "-1.75 days" and "1.75 days" would have results of -1 and 1
        respectively.
        """
        return self.__days if self.__days >= 0 or self.__nano_of_day == 0 else self.__days + 1

    @property
    def nanosecond_of_day(self) -> int:
        """The number of nanoseconds within the day of this duration.

        For negative durations, this will be negative (or zero).
        """
        if self.__days >= 0:
            return self.__nano_of_day
        if self.__nano_of_day == 0:
            return 0
        return self.__nano_of_day - PyodaConstants.NANOSECONDS_PER_DAY

    @property
    def hours(self) -> int:
        """The hour component of this duration, in the range [-23, 23], truncated towards zero."""
        return _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_HOUR)

    @property
    def minutes(self) -> int:
        """The minute component of this duration, in the range [-59, 59], truncated towards zero."""
        return _csharp_modulo(
            _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_MINUTE),
            PyodaConstants.MINUTES_PER_HOUR,
        )

    @property
    def seconds(self) -> int:
        """The second component of this duration, in the range [-59, 59], truncated towards zero."""
        return _csharp_modulo(
            _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_SECOND),
            PyodaConstants.SECONDS_PER_MINUTE,
        )

    @property
    def milliseconds(self) -> int:
        """The subsecond component of this duration, expressed in milliseconds, in the range [-999, 999] and truncated
        towards zero."""
        return _csharp_modulo(
            _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_MILLISECOND),
            PyodaConstants.MILLISECONDS_PER_SECOND,
        )

    @property
    def microseconds(self) -> int:
        """The subsecond component of this duration, expressed in microseconds, in the range [-999999, 999999] and
        truncated towards zero."""
        return _csharp_modulo(
            _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_MICROSECOND),
            PyodaConstants.MICROSECONDS_PER_SECOND,
        )

    @property
    def subsecond_ticks(self) -> int:
        """The subsecond component of this duration, expressed in ticks, in the range [-9999999, 9999999] and truncated
        towards zero."""
        return _csharp_modulo(
            _towards_zero_division(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_TICK),
            PyodaConstants.TICKS_PER_SECOND,
        )

    @property
    def subsecond_nanoseconds(self) -> int:
        """The subsecond component of this duration, expressed in nanoseconds, in the range [-999999999, 999999999]."""
        return _csharp_modulo(self.nanosecond_of_day, PyodaConstants.NANOSECONDS_PER_SECOND)

    @property
    def bcl_compatible_ticks(self) -> int:
        """The total number of ticks in the duration, truncated towards zero where necessary.

        Within the constraints specified below, this property is intended to be equivalent to .NET's ``TimeSpan.Ticks``.

        If the number of nanoseconds in a duration is not a whole number of ticks, it is truncated towards zero.
        For example, durations in the range [-99ns, 99ns] would all count as 0 ticks.

        See also: total_ticks()
        """
        ticks = _TickArithmetic.days_and_tick_of_day_to_ticks(
            self.__days, _towards_zero_division(self.__nano_of_day, PyodaConstants.NANOSECONDS_PER_TICK)
        )
        if self.__days < 0 and self.__nano_of_day % PyodaConstants.NANOSECONDS_PER_TICK != 0:
            ticks += 1
        return ticks

    @property
    def total_days(self) -> float:
        """The total number of days in this duration, as a ``float``.

        This property is the ``Duration`` equivalent of ``TimeSpan.TotalDays``.
        It represents the complete duration in days, rather than only the whole number of
        days. For example, for a duration of 36 hours, this property would return 1.5.
        """
        return self.__days + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_DAY

    @property
    def total_hours(self) -> float:
        """The total number of hours in this duration, as a ``float``.

        This property is the ``Duration`` equivalent of ``TimeSpan.TotalHours``.
        Unlike ``hours``, it represents the complete duration in hours rather than the
        whole number of hours as part of the day. So for a duration
        of 1 day, 2 hours and 30 minutes, the ``hours`` property will return 2, but ``total_hours``
        will return 26.5.
        """
        return self.__days * 24.0 + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_HOUR

    @property
    def total_minutes(self) -> float:
        """The total number of minutes in this duration, as a ``float``.

        This property is the ``Duration`` equivalent of ``TimeSpan.TotalMinutes``.
        Unlike ``minutes``, it represents the complete duration in minutes rather than
        the whole number of minutes within the hour. So for a duration
        of 2 hours, 30 minutes and 45 seconds, the ``minutes`` property will return 30, but ``total_minutes``
        will return 150.75.
        """
        return self.__days * PyodaConstants.MINUTES_PER_DAY + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_MINUTE

    @property
    def total_seconds(self) -> float:
        """The total number of seconds in this duration, as a ``float``.

        This property is the <c>Duration</c> equivalent of <see cref="TimeSpan.TotalSeconds"/>.
        Unlike ``seconds``, it represents the complete duration in seconds rather than
        the whole number of seconds within the minute. So for a duration
        of 10 minutes, 20 seconds and 250 milliseconds, the ``seconds`` property will return 20, but ``total_seconds``
        will return 620.25.
        """
        return self.__days * PyodaConstants.SECONDS_PER_DAY + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_SECOND

    @property
    def total_milliseconds(self) -> float:
        """The total number of milliseconds in this duration, as a ``float``.

        This property is the ``Duration`` equivalent of ``TimeSpan.TotalMilliseconds``.
        Unlike ``milliseconds``, it represents the complete duration in milliseconds rather than
        the whole number of milliseconds within the second. So for a duration
        of 10 minutes, 20 seconds and 250 milliseconds, the ``milliseconds`` property will return
        250, but ``total_milliseconds`` will return 620250.
        """
        return (
            self.__days * PyodaConstants.MILLISECONDS_PER_DAY
            + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_MILLISECOND
        )

    @property
    def total_microseconds(self) -> float:
        # TODO: docstring
        return self.total_ticks / PyodaConstants.TICKS_PER_MICROSECOND

    @property
    def total_ticks(self) -> float:
        """The total number of ticks in this duration, as a ``float``.

        This property is the ``Duration`` equivalent of ``TimeSpan.Ticks``.
        """
        return self.__days * PyodaConstants.TICKS_PER_DAY + self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_TICK

    @property
    def total_nanoseconds(self) -> float:
        """The total number of nanoseconds in this duration, as a ``float``.

        The result is always an integer, but may not be precise due to the limitations
        of the ``float`` type. In other words, ``Duration.from_nanoseconds(duration.total_nanoseconds)``
        is not guaranteed to round-trip. To guarantee precision and round-tripping,
        use ``to_nanoseconds()`` and ``from_nanoseconds()``.
        """
        return self.__days * PyodaConstants.NANOSECONDS_PER_DAY + self.__nano_of_day

    def _plus_small_nanoseconds(self, small_nanos: int) -> Duration:
        """Adds a "small" number of nanoseconds to this duration.

        It is trusted to be less or equal to than 24 hours in magnitude.
        """
        _Preconditions._check_argument_range(
            "small_nanos", small_nanos, -PyodaConstants.NANOSECONDS_PER_DAY, PyodaConstants.NANOSECONDS_PER_DAY
        )
        new_days = self.__days
        new_nanos = self.__nano_of_day + small_nanos
        if new_nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
            new_days += 1
            new_nanos -= PyodaConstants.NANOSECONDS_PER_DAY
        elif new_nanos < 0:
            new_days -= 1
            new_nanos += PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=new_days, nano_of_day=new_nanos)

    def _minus_small_nanoseconds(self, small_nanos: int) -> Duration:
        """Subtracts a "small" number of nanoseconds from this duration.

        It is trusted to be less or equal to than 24 hours in magnitude.
        """
        # TODO: unchecked
        # TODO: Preconditions.DebugCheckArgumentRange
        new_days = self.__days
        new_nanos = self.__nano_of_day - small_nanos
        if new_nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
            new_days += 1
            new_nanos -= PyodaConstants.NANOSECONDS_PER_DAY
        elif new_nanos < 0:
            new_days -= 1
            new_nanos += PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=new_days, nano_of_day=new_nanos)

    # region Object overrides

    def __hash__(self) -> int:
        return self.__days ^ hash(self.__nano_of_day)

    # endregion Object overrides

    # region Formatting

    # TODO: Duration.ToString() [requires DurationPattern]

    # endregion Formatting

    # region Operators

    def __add__(self, other: Duration) -> Duration:
        if isinstance(other, Duration):
            # TODO: unchecked
            days = self.__days + other.__days
            nanos = self.__nano_of_day + other.__nano_of_day
            if nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nanos -= PyodaConstants.NANOSECONDS_PER_DAY
            # nanoOfDay is always non-negative (and much less than half of long.MaxValue), so adding two
            # of them together will never produce a negative result.
            return Duration._ctor(days=days, nano_of_day=nanos)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def add(left: Duration, right: Duration) -> Duration:
        """Adds one duration to another. Friendly alternative to ``__add__``.

        :param left: The left hand side of the operator.
        :param right: The right hand side of the operator.
        :return: A new ``Duration`` representing the sum of the given values.
        """
        return left + right

    def plus(self, other: Duration) -> Duration:
        """Returns the result of adding another duration to this one, for a fluent alternative to ``__add__``.

        :param other: The duration to add
        :return: A new ``Duration`` representing the result of the addition.
        """
        return self + other

    def __sub__(self, other: Duration) -> Duration:
        if isinstance(other, Duration):
            days = self.__days - other.__days
            nanos = self.__nano_of_day - other.__nano_of_day
            if nanos < 0:
                days -= 1
                nanos += PyodaConstants.NANOSECONDS_PER_DAY
            return Duration._ctor(days=days, nano_of_day=nanos)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def subtract(left: Duration, right: Duration) -> Duration:
        """Subtracts one duration from another. Friendly alternative to ``__add__``.

        :param left: The left hand side of the operator.
        :param right: The right hand side of the operator.
        :return: A new ``Duration`` representing the difference of the given values.
        """
        return left - right

    def minus(self, other: Duration) -> Duration:
        """Returns the result of subtracting another duration from this one, for a fluent alternative to ``__sub__``.

        :param other: The duration to subtract
        :return: A new ``Duration`` representing the result of the subtraction.
        """
        return self - other

    @typing.overload
    def __truediv__(self, other: int | float) -> Duration: ...

    @typing.overload
    def __truediv__(self, other: Duration) -> float: ...

    def __truediv__(self, other: int | float | Duration) -> Duration | float:
        # TODO: This is a dramatically simpler implementation for int/float than Noda Time.
        if isinstance(other, int | float):
            return self.from_nanoseconds(_towards_zero_division(self.total_nanoseconds, other))
        if isinstance(other, Duration):
            return self.total_nanoseconds / other.total_nanoseconds
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    @typing.overload
    def divide(left: Duration, right: int | float) -> Duration: ...

    @staticmethod
    @typing.overload
    def divide(left: Duration, right: Duration) -> float: ...

    @staticmethod
    def divide(left: Duration, right: int | float | Duration) -> Duration | float:
        # TODO: Duration.divide() docstring
        return left / right

    def __mul__(self, other: int | float) -> Duration:
        # TODO: This is much simpler than the Noda Time implementation
        if isinstance(other, int | float):
            return self.from_nanoseconds(self.to_nanoseconds() * other)
        return NotImplemented  # type: ignore[unreachable]

    def __rmul__(self, other: int | float) -> Duration:
        if isinstance(other, int | float):
            return self * other
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    @typing.overload
    def multiply(left: Duration, right: int | float) -> Duration: ...

    @staticmethod
    @typing.overload
    def multiply(left: int | float, right: Duration) -> Duration: ...

    @staticmethod
    def multiply(left: Duration | int | float, right: Duration | int | float) -> Duration:
        # TODO: Cursed isinstance checks are to pacify mypy - can we do better?
        if isinstance(left, Duration) and isinstance(right, int | float):
            return left * right
        if isinstance(left, int | float) and isinstance(right, Duration):
            return right * left
        raise TypeError("Duration.multiply() accepts one Duration argument and one int/float argument.")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Duration):
            return self.__days == other.__days and self.__nano_of_day == other.__nano_of_day
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    def __lt__(self, other: Duration | None) -> bool:
        if other is None:
            return False
        if isinstance(other, Duration):
            return self.__days < other.__days or (
                self.__days == other.__days and self.__nano_of_day < other.__nano_of_day
            )
        return NotImplemented  # type: ignore[unreachable]

    def __le__(self, other: Duration | None) -> bool:
        return self < other or self == other

    def __gt__(self, other: Duration | None) -> bool:
        if other is None:
            return True
        if isinstance(other, Duration):
            return (self.__days > other.__days) or (
                (self.__days == other.__days) and (self.__nano_of_day > other.__nano_of_day)
            )
        return NotImplemented  # type: ignore[unreachable]

    def __ge__(self, other: Duration | None) -> bool:
        return self > other or self == other

    def __neg__(self) -> Duration:
        old_days = self.__days
        old_nano_of_day = self.__nano_of_day
        if old_nano_of_day == 0:
            return Duration._ctor(days=-old_days, nano_of_day=0)
        new_nano_of_day = PyodaConstants.NANOSECONDS_PER_DAY - old_nano_of_day
        return Duration._ctor(days=-old_days - 1, nano_of_day=new_nano_of_day)

    @staticmethod
    def negate(duration: Duration) -> Duration:
        """Implements a friendly alternative to the unary negation operator.

        :param duration: Duration to negate
        :return: The negative value of this duration
        """
        return -duration

    # endregion Operators

    # region IComparable<Duration> Members

    def compare_to(self, other: Duration | None) -> int:
        """Compares the current object with another object of the same type. See the type documentation for a
        description of ordering semantics.

        :param other: An object to compare with this object.
        :return: An integer that indicates the relative order of the objects being compared.
        :exception TypeError: An object of an incompatible type was passed to this method.

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
        if isinstance(other, Duration):
            if not (day_comparison := self.__days - other.__days) == 0:
                return day_comparison
            return self.__nano_of_day - other.__nano_of_day
        raise TypeError

    # endregion IComparable<Duration> Members

    # region IEquatable<Duration> Members

    def equals(self, other: Duration) -> bool:
        """Indicates whether the current object is equal to another object of the same type. See the type documentation
        for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: true if the current object is equal to the ``other`` parameter; otherwise, false.
        """
        return self == other

    # endregion IEquatable<Duration> Members

    @classmethod
    def from_days(cls, days: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of days, assuming a 'standard' 24-hour day.

        :param days: The number of days.
        :return: A ``Duration`` representing the given number of days.
        """
        if isinstance(days, float):
            _Preconditions._check_argument_range(
                "days",
                days,
                cls._MIN_DAYS,
                cls._MAX_DAYS,
            )
            return cls.from_nanoseconds(days * PyodaConstants.NANOSECONDS_PER_DAY)
        return cls._ctor(days=days)

    @classmethod
    def from_hours(cls, hours: int | float) -> Duration:
        """Returns a Duration that represents the given number of hours.

        :param hours: The number of hours.
        :return: A ``Duration`` representing the number of hours.
        """
        if isinstance(hours, float):
            _Preconditions._check_argument_range(
                "hours",
                hours,
                cls._MIN_DAYS * PyodaConstants.HOURS_PER_DAY,
                (cls._MAX_DAYS + 1) * PyodaConstants.HOURS_PER_DAY - 1,
            )
            return cls.from_nanoseconds(hours * PyodaConstants.NANOSECONDS_PER_HOUR)
        return cls.__ctor(
            units=hours,
            param_name="hours",
            min_value=cls._MIN_DAYS * PyodaConstants.HOURS_PER_DAY,
            max_value=(cls._MAX_DAYS + 1) * PyodaConstants.HOURS_PER_DAY - 1,
            units_per_day=PyodaConstants.HOURS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_HOUR,
        )

    @classmethod
    def from_minutes(cls, minutes: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of minutes.

        :param minutes: The number of minutes.
        :return: A ``Duration`` representing the given number of minutes.
        """
        if isinstance(minutes, float):
            _Preconditions._check_argument_range(
                "minutes",
                minutes,
                cls._MIN_DAYS * PyodaConstants.MINUTES_PER_DAY,
                (cls._MAX_DAYS + 1) * PyodaConstants.MINUTES_PER_DAY - 1,
            )
            return cls.from_nanoseconds(minutes * PyodaConstants.NANOSECONDS_PER_MINUTE)
        return cls.__ctor(
            units=minutes,
            param_name="minutes",
            min_value=cls._MIN_DAYS * PyodaConstants.MINUTES_PER_DAY,
            max_value=(cls._MAX_DAYS + 1) * PyodaConstants.MINUTES_PER_DAY - 1,
            units_per_day=PyodaConstants.MINUTES_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_MINUTE,
        )

    @classmethod
    def from_seconds(cls, seconds: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of seconds.

        :param seconds: The number of seconds.
        :return: A ``Duration`` representing the given number of seconds.
        """
        if isinstance(seconds, float):
            _Preconditions._check_argument_range(
                "seconds",
                seconds,
                cls._MIN_DAYS * PyodaConstants.SECONDS_PER_DAY,
                (cls._MAX_DAYS + 1) * PyodaConstants.SECONDS_PER_DAY - 1,
            )
            return cls.from_nanoseconds(seconds * PyodaConstants.NANOSECONDS_PER_SECOND)
        return cls.__ctor(
            units=seconds,
            param_name="seconds",
            min_value=cls._MIN_DAYS * PyodaConstants.SECONDS_PER_DAY,
            max_value=(cls._MAX_DAYS + 1) * PyodaConstants.SECONDS_PER_DAY - 1,
            units_per_day=PyodaConstants.SECONDS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_SECOND,
        )

    @classmethod
    def from_milliseconds(cls, milliseconds: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of milliseconds.

        :param milliseconds: The number of milliseconds.
        :return: A ``Duration`` representing the given number of milliseconds.
        """
        if isinstance(milliseconds, float):
            _Preconditions._check_argument_range(
                "milliseconds",
                milliseconds,
                cls._MIN_DAYS * PyodaConstants.MILLISECONDS_PER_DAY,
                (cls._MAX_DAYS + 1) * PyodaConstants.MILLISECONDS_PER_DAY - 1,
            )
            return cls.from_nanoseconds(milliseconds * PyodaConstants.NANOSECONDS_PER_MILLISECOND)
        return cls.__ctor(
            units=milliseconds,
            param_name="milliseconds",
            min_value=cls._MIN_DAYS * PyodaConstants.MILLISECONDS_PER_DAY,
            max_value=((cls._MAX_DAYS + 1) * PyodaConstants.MILLISECONDS_PER_DAY) - 1,
            units_per_day=PyodaConstants.MILLISECONDS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_MILLISECOND,
        )

    @classmethod
    def from_ticks(cls, ticks: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of ticks.

        :param ticks: The number of ticks.
        :return: A ``Duration`` representing the given number of ticks.
        """
        if isinstance(ticks, float):
            _Preconditions._check_argument_range(
                "ticks",
                ticks,
                cls._MIN_DAYS * float(PyodaConstants.TICKS_PER_DAY),
                (cls._MAX_DAYS + 1) * PyodaConstants.TICKS_PER_DAY - 1,
            )
            return cls.from_nanoseconds(ticks * PyodaConstants.NANOSECONDS_PER_TICK)
        # TODO: FromTicks(long) never throws.
        #  Noda Time has the following comment:
        #  "No precondition here, as we cover a wider range than Int64 ticks can handle..."
        #  If this ever changes, the test_factory_methods_out_of_range test will need changed too.
        days, tick_of_day = _TickArithmetic.ticks_to_days_and_tick_of_day(ticks)
        return cls.__ctor(days=days, nano_of_day=tick_of_day * PyodaConstants.NANOSECONDS_PER_TICK, no_validation=True)

    @classmethod
    def from_microseconds(cls, microseconds: int | float) -> Duration:
        """Returns a ``Duration`` that represents the given number of microseconds.

        :param microseconds: The number of microseconds.
        :return: A ``Duration`` representing the given number of microseconds.
        """
        if isinstance(microseconds, float):
            _Preconditions._check_argument_range(
                "microseconds",
                microseconds,
                cls._MIN_DAYS * PyodaConstants.MICROSECONDS_PER_DAY,
                (cls._MAX_DAYS + 1) * PyodaConstants.MICROSECONDS_PER_DAY - 1,
            )
            return cls.from_nanoseconds(microseconds * PyodaConstants.NANOSECONDS_PER_MICROSECOND)
        return cls.__ctor(
            units=microseconds,
            param_name="microseconds",
            min_value=cls._MIN_DAYS * PyodaConstants.MICROSECONDS_PER_DAY,
            max_value=((cls._MAX_DAYS + 1) * PyodaConstants.MICROSECONDS_PER_DAY) - 1,
            units_per_day=PyodaConstants.MICROSECONDS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_MICROSECOND,
        )

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int | float) -> Duration:  # TODO from_nanoseconds overrides
        """Returns a ``Duration`` that represents the given number of nanoseconds.

        When nanoseconds is a ``float``, any fractional parts of the value are
        truncated towards zero.

        :param nanoseconds: The number of nanoseconds.
        :return: A ``Duration`` representing the given number of nanoseconds.
        """

        _Preconditions._check_argument_range("nanoseconds", nanoseconds, cls._MIN_NANOSECONDS, cls._MAX_NANOSECONDS)

        # In Noda Time, the ``double`` overload merely rounds ``nanoseconds`` towards zero
        # and passes it to either the ``long`` or ``BigInteger`` overload.
        # Here we just allow it to fall through to the next code block.
        if isinstance(nanoseconds, float):
            # TODO: Consider creating a function that rounds towards zero without any division.
            nanoseconds = _towards_zero_division(nanoseconds, 1)

        if nanoseconds >= 0:
            # TODO: Is divmod compatible with C# integer division?
            quotient, remainder = divmod(nanoseconds, PyodaConstants.NANOSECONDS_PER_DAY)
            return cls._ctor(days=quotient, nano_of_day=remainder)

        # Work out the "floor days"; division truncates towards zero and
        # nanoseconds is definitely negative by now, hence the addition and subtraction here.
        days = _towards_zero_division(nanoseconds + 1, PyodaConstants.NANOSECONDS_PER_DAY) - 1
        nano_of_day = nanoseconds - days * PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=days, nano_of_day=nano_of_day)

    @classmethod
    def _from_nanoseconds(cls, nanoseconds: decimal.Decimal) -> Duration:
        # TODO: For comparison between min/max decimal nanoseconds (and values near
        #  those limits) to work, we need to make sure that the precision is sufficient
        #  to avoid truncation. This is a bit of a "finger in the air" precision which
        #  may need revisited.
        with decimal.localcontext(prec=100):
            if nanoseconds < cls._MIN_DECIMAL_NANOSECONDS or nanoseconds > cls._MAX_DECIMAL_NANOSECONDS:
                # Note: use the BigInteger value rather than decimal to avoid decimal points in the message.
                # They're the same values.
                raise ValueError(f"Value should be in range [{cls._MIN_NANOSECONDS}-{cls._MAX_NANOSECONDS}]")

            days = (
                _towards_zero_division(nanoseconds, PyodaConstants.NANOSECONDS_PER_DAY)
                if nanoseconds >= 0
                else _towards_zero_division(nanoseconds + 1, PyodaConstants.NANOSECONDS_PER_DAY) - 1
            )
            nano_of_day = _towards_zero_division(
                nanoseconds - (decimal.Decimal(days) * PyodaConstants.NANOSECONDS_PER_DAY), 1
            )
            return cls._ctor(days=days, nano_of_day=nano_of_day)

    @classmethod
    def from_timedelta(cls, time_delta: datetime.timedelta) -> Duration:
        """Returns a ``Duration`` that represents the same number of microseconds as the given ``datetime.timedelta``.

        :param time_delta: The ``datetime.timedelta`` to convert.
        :return: A new Duration with the same number of microseconds as the given ``datetime.timedelta``.
        """
        # Note that we don't use `cls.from_seconds(timedelta.total_seconds())` here.
        # That is because `total_seconds()` loses microsecond accuracy for deltas > 270 years.
        # https://docs.python.org/3/library/datetime.html#datetime.timedelta.total_seconds
        return (
            Duration.from_days(time_delta.days)
            + Duration.from_seconds(time_delta.seconds)
            + Duration.from_microseconds(time_delta.microseconds)
        )

    def to_timedelta(self) -> datetime.timedelta:
        """Returns a ``datetime.timedelta`` that represents the same number of microseconds as this ``Duration``.

        If the number of nanoseconds in a duration is not a whole number of microseconds, it will be
        passed to ``datetime.timedelta()`` as a fractional argument, and will be subject to the internal
        summing/rounding behaviour documented at https://docs.python.org/3/library/datetime.html#datetime.timedelta.

        If the duration can be resolved to a whole number of microseconds, then the conversion should not lose
        information.

        :return: A new TimeSpan with the same number of ticks as this Duration.
        """

        return datetime.timedelta(
            days=self.__days, microseconds=self.__nano_of_day / PyodaConstants.NANOSECONDS_PER_MICROSECOND
        )

    def to_nanoseconds(self) -> int:
        # TODO: This covers implementations for:
        #  public long ToInt64Nanoseconds()
        #  private long ToInt64NanosecondsUnchecked()
        #  public BigInteger ToBigIntegerNanoseconds()
        return self.__days * PyodaConstants.NANOSECONDS_PER_DAY + self.__nano_of_day

    @staticmethod
    def max(x: Duration, y: Duration) -> Duration:
        """Returns the larger duration of the given two.

        A "larger" duration is one that advances time by more than a "smaller" one. This means
        that a positive duration is always larger than a negative one, for example. (This is the same
        comparison used by the binary comparison operators.)

        :param x: The first duration to compare.
        :param y: The second duration to compare.
        :return: The larger duration of ``x`` or ``y``.
        """
        return max(x, y)

    @staticmethod
    def min(x: Duration, y: Duration) -> Duration:
        """Returns the smaller duration of the given two.

        A "larger" duration is one that advances time by more than a "smaller" one. This means
        that a positive duration is always larger than a negative one, for example. (This is the same
        comparison used by the binary comparison operators.)

        :param x: The first duration to compare.
        :param y: The second duration to compare.
        :return: The smaller duration of ``x`` or ``y``.
        """
        return min(x, y)
