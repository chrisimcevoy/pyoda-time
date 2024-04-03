# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
import typing

from ._compatibility._culture_info import CultureInfo
from ._pyoda_constants import PyodaConstants
from .utility._csharp_compatibility import _sealed, _towards_zero_division
from .utility._preconditions import _Preconditions


class _OffsetMeta(type):
    @property
    def zero(self) -> Offset:
        """An offset of zero seconds - effectively the permanent offset for UTC."""
        return Offset.from_seconds(0)

    @property
    def min_value(self) -> Offset:
        """The minimum permitted offset; 18 hours before UTC."""
        return Offset.from_hours(-18)

    @property
    def max_value(self) -> Offset:
        """The maximum permitted offset; 18 hours after UTC."""
        return Offset.from_hours(18)


@typing.final
@_sealed
class Offset(metaclass=_OffsetMeta):
    """An offset from UTC in seconds."""

    __MIN_HOURS: typing.Final[int] = -18
    __MAX_HOURS: typing.Final[int] = 18
    __MIN_SECONDS: typing.Final[int] = -18 * PyodaConstants.SECONDS_PER_HOUR
    __MAX_SECONDS: typing.Final[int] = 18 * PyodaConstants.SECONDS_PER_HOUR
    __MIN_MILLISECONDS: typing.Final[int] = -18 * PyodaConstants.MILLISECONDS_PER_HOUR
    __MAX_MILLISECONDS: typing.Final[int] = 18 * PyodaConstants.MILLISECONDS_PER_HOUR
    __MIN_TICKS: typing.Final[int] = -18 * PyodaConstants.TICKS_PER_HOUR
    __MAX_TICKS: typing.Final[int] = 18 * PyodaConstants.TICKS_PER_HOUR
    __MIN_NANOSECONDS: typing.Final[int] = -18 * PyodaConstants.NANOSECONDS_PER_HOUR
    __MAX_NANOSECONDS: typing.Final[int] = 18 * PyodaConstants.NANOSECONDS_PER_HOUR

    def __init__(self) -> None:
        self.__seconds = 0

    @classmethod
    def _ctor(cls, *, seconds: int) -> Offset:
        """Internal constructor."""
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        self = super().__new__(cls)
        self.__seconds = seconds
        return self

    @property
    def seconds(self) -> int:
        """Gets the number of seconds represented by this offset, which may be negative."""
        return self.__seconds

    @property
    def milliseconds(self) -> int:
        """Gets the number of milliseconds represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 1,000 to give the
        number of milliseconds.
        """

        return self.__seconds * PyodaConstants.MILLISECONDS_PER_SECOND

    @property
    def ticks(self) -> int:
        """Gets the number of ticks represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 10,000,000 to give
        the number of ticks.
        """

        return self.__seconds * PyodaConstants.TICKS_PER_SECOND

    @property
    def nanoseconds(self) -> int:
        """Gets the number of nanoseconds represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 1,000,000,000 to
        give the number of nanoseconds.
        """

        return self.__seconds * PyodaConstants.NANOSECONDS_PER_SECOND

    @staticmethod
    def max(x: Offset, y: Offset) -> Offset:
        """Returns the greater offset of the given two, i.e. the one which will give a later local time when added to an
        instant.

        :param x: The first offset
        :param y: The second offset
        :return: The greater offset of x and y.
        """
        return x if x > y else y

    @staticmethod
    def min(x: Offset, y: Offset) -> Offset:
        """Returns the lower offset of the given two, i.e. the one which will give an earlier local time when added to
        an instant.

        :param x: The first offset
        :param y: The second offset
        :return: The lower offset of x and y.
        """
        return x if x < y else y

    # region Operators

    def __neg__(self) -> Offset:
        """Implements the unary operator - (negation).

        :return: A new ``Offset`` instance with a negated value.
        """
        # Guaranteed to still be in range.
        return Offset._ctor(seconds=-self.seconds)

    @staticmethod
    def negate(offset: Offset) -> Offset:
        """Returns the negation of the specified offset. This is the method form of the unary minus operator.

        :param offset: The offset to negate.
        :return: The negation of the specified offset.
        """
        return -offset

    def __pos__(self) -> Offset:
        """Implements the unary operator + .

        :return: The same ``Offset`` instance

        There is no method form of this operator; the ``plus`` method is an instance
        method for addition, and is more useful than a method form of this would be.
        """
        return self

    def __add__(self, other: Offset) -> Offset:
        """Implements the operator + (addition).

        :param other: The offset to add.
        :return: A new ``Offset`` representing the sum of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        if isinstance(other, Offset):
            return self.from_seconds(self.seconds + other.seconds)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def add(left: Offset, right: Offset) -> Offset:
        """Adds one Offset to another. Friendly alternative to ``+``.

        :param left: The left hand side of the operator.
        :param right: The right hand side of the operator.
        :return: A new ``Offset`` representing the sum of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return left + right

    def plus(self, other: Offset) -> Offset:
        """Returns the result of adding another Offset to this one, for a fluent alternative to ``+``.

        :param other: The offset to add
        :return: THe result of adding the other offset to this one.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return self + other

    def __sub__(self, other: Offset) -> Offset:
        """Implements the operator - (subtraction).

        :param other: The offset to subtract.
        :return: A new ``Offset`` representing the difference of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        if isinstance(other, Offset):
            return self.from_seconds(self.seconds - other.seconds)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def subtract(minuend: Offset, subtrahend: Offset) -> Offset:
        """Subtracts one Offset from another. Friendly alternative to ``-``.

        :param minuend: The left hand side of the operator.
        :param subtrahend: The right hand side of the operator.
        :return: A new ``Offset`` representing the difference of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return minuend - subtrahend

    def minus(self, other: Offset) -> Offset:
        """Returns the result of subtracting another Offset from this one, for a fluent alternative to ``-``.

        :param other: The offset to subtract
        :return: The result of subtracting the other offset from this one.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return self - other

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality). See the type documentation for a description of equality semantics.

        :param other: The object to compare this one to for equality.
        :return: ``True`` if values are equal to each other, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.equals(other)

    def __ne__(self, other: object) -> bool:
        """Implements the operator != (inequality). See the type documentation for a description of equality semantics.

        :param other: The object to compare with this one.
        :return: ``True`` if values are not equal to each other, otherwise ``False``.
        """
        return not (self == other)

    def __lt__(self, other: Offset | None) -> bool:
        """Implements the operator ``<`` (less than). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is less than ``other``, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.compare_to(other) < 0

    def __le__(self, other: Offset) -> bool:
        """Implements the operator ``<=`` (less than or equal). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is less than or equal to ``other``, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.compare_to(other) <= 0

    def __gt__(self, other: Offset | None) -> bool:
        """Implements the operator ``>`` (greater than). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is greater than ``other``, otherwise ``False``.
        """
        return other is None or (isinstance(other, Offset) and self.compare_to(other) > 0)

    def __ge__(self, other: Offset) -> bool:
        """Implements the operator ``>=`` (greater than or equal). See the type documentation for a description of
        ordering semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is greater than or equal to ``other``, otherwise ``False``.
        """
        return other is None or (isinstance(other, Offset) and self.compare_to(other) >= 0)

    # endregion

    # region IComparable<Offset> Members

    def compare_to(self, other: Offset) -> int:
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
        if not isinstance(other, Offset):
            raise TypeError(f"Offset can only be compared_to another Offset, not {other.__class__.__name__}")
        return self.seconds - other.seconds

    # endregion

    # region IEquatable<Offset> Members

    def equals(self, other: Offset) -> bool:
        """Indicates whether the current object is equal to another object of the same type. See the type documentation
        for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: true if the current object is equal to the ``other`` parameter; otherwise, false.
        """
        return self.seconds == other.seconds

    # endregion

    # region object overrides

    def __hash__(self) -> int:
        return hash(self.seconds)

    # endregion

    # region Construction

    @classmethod
    def from_seconds(cls, seconds: int) -> Offset:
        """Returns an offset for the given seconds value, which may be negative.

        :param seconds: The int seconds value.
        :return: An offset representing the given number of seconds.
        :raises ValueError: The specified number of seconds is outside the range of [-18, +18] hours.
        """
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        return cls._ctor(seconds=seconds)

    @classmethod
    def from_milliseconds(cls, milliseconds: int) -> Offset:
        """Returns an offset for the given milliseconds value, which may be negative.

        :param milliseconds: The int milliseconds value.
        :return: An offset representing the given number of milliseconds, to the (truncated) second.
        :raises ValueError: The specified number of milliseconds is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of milliseconds is simply divided by 1,000 to
        give the number of seconds - any remainder is truncated.
        """

        _Preconditions._check_argument_range(
            "milliseconds", milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS
        )
        return cls._ctor(seconds=_towards_zero_division(milliseconds, PyodaConstants.MILLISECONDS_PER_SECOND))

    @classmethod
    def from_ticks(cls, ticks: int) -> Offset:
        """Returns an offset for the given number of ticks, which may be negative.

        :param ticks: The number of ticks specifying the length of the new offset.
        :return: An offset representing the given number of ticks, to the (truncated) second.
        :raises ValueError: The specified number of ticks is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of ticks is simply divided
        by 10,000,000 to give the number of seconds - any remainder is truncated.
        """

        _Preconditions._check_argument_range("ticks", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return cls._ctor(seconds=_towards_zero_division(ticks, PyodaConstants.TICKS_PER_SECOND))

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int) -> Offset:
        """Returns an offset for the given number of nanoseconds, which may be negative.

        :param nanoseconds: The number of nanoseconds specifying the length of the new offset.
        :return: An offset representing the given number of nanoseconds, to the (truncated) second.
        :raises ValueError: The specified number of nanoseconds is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of nanoseconds is simply divided by
        1,000,000,000 to give the number of seconds - any remainder is truncated towards zero.
        """

        _Preconditions._check_argument_range("nanoseconds", nanoseconds, cls.__MIN_NANOSECONDS, cls.__MAX_NANOSECONDS)
        return cls._ctor(seconds=_towards_zero_division(nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND))

    @classmethod
    def from_hours(cls, hours: int) -> Offset:
        """Returns an offset for the specified number of hours, which may be negative.

        :param hours: The number of hours to represent in the new offset.
        :return: An offset representing the given value.
        :raises ValueError: The specified number of hours is outside the range of [-18, +18].
        """

        _Preconditions._check_argument_range("hours", hours, cls.__MIN_HOURS, cls.__MAX_HOURS)
        return cls._ctor(seconds=hours * PyodaConstants.SECONDS_PER_HOUR)

    @classmethod
    def from_hours_and_minutes(cls, hours: int, minutes: int) -> Offset:
        """Returns an offset for the specified number of hours and minutes.

        :param hours: The number of hours to represent in the new offset.
        :param minutes: The number of minutes to represent in the new offset.
        :return: An offset representing the given value.
        :raises ValueError: The result of the operation is outside the range of Offset.

        The result simply takes the hours and minutes and converts each component into milliseconds
        separately. As a result, a negative offset should usually be obtained by making both arguments
        negative. For example, to obtain "three hours and ten minutes behind UTC" you might call
        ``Offset.from_hours_and_minutes(-3, -10)``.
        """

        return cls.from_seconds(hours * PyodaConstants.SECONDS_PER_HOUR + minutes * PyodaConstants.SECONDS_PER_MINUTE)

    # endregion

    # region Conversion

    def to_timedelta(self) -> datetime.timedelta:
        """Converts this offset to a stdlib ``datetime.timedelta`` value.

        :return: An equivalent ``datetime.timedelta`` to this value.
        """
        return datetime.timedelta(seconds=self.seconds)

    @classmethod
    def from_timedelta(cls, timedelta: datetime.timedelta) -> Offset:
        """Converts the given ``timedelta`` to an offset, with fractional seconds truncated.

        :param timedelta: The timedelta to convert
        :returns: An offset for the same time as the given timedelta. :exception ValueError: The given timedelta falls
            outside the range of +/- 18 hours.
        """
        # TODO: Consider introducing a "from_microseconds" constructor?

        # Convert to ticks first, then divide that float by 1 using our special
        # function to convert to a rounded-towards-zero int.
        ticks = _towards_zero_division(timedelta.total_seconds() * PyodaConstants.TICKS_PER_SECOND, 1)
        _Preconditions._check_argument_range("timedelta", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Offset.from_ticks(ticks)

    # endregion

    # region XML serialization

    # TODO: XML serialization???

    # endregion

    def __str__(self) -> str:
        from .text import OffsetPattern

        return OffsetPattern._bcl_support.format(self, None, CultureInfo.current_culture)
