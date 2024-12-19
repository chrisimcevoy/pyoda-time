# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from collections.abc import Generator
from typing import Final, final

from pyoda_time._duration import Duration
from pyoda_time._instant import Instant
from pyoda_time._pyoda_constants import PyodaConstants
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class Interval:
    """An interval between two instants in time (start and end).

    Equality is defined in a component-wise fashion: two intervals are considered equal if their start instants are
    equal to each other and their end instants are equal to each other. Ordering between intervals is not defined.

    The interval includes the start instant and excludes the end instant. However, an interval
    may be missing its start or end, in which case the interval is deemed to be infinite in that
    direction.

    The end may equal the start (resulting in an empty interval), but will not be before the start.

    The default value of this type is an empty interval with a start and end of ``PyodaConstant.UNIX_EPOCH``.
    """

    __slots__ = ("__end", "__start")

    def __init__(
        self, start: Instant | None = PyodaConstants.UNIX_EPOCH, end: Instant | None = PyodaConstants.UNIX_EPOCH
    ) -> None:
        """Initializes a new instance of the ``Interval`` struct from two nullable ``Instant`` values.

        If the start is null, the interval is deemed to stretch to the start of time. If the end is null,
        the interval is deemed to stretch to the end of time.

        :param start: The start ``Instant`` or ``None``.
        :param end: The end ``Instant`` or ``None``.
        :raises ValueError: If ``end`` is earlier than ``start``.
        """

        if start is None:
            start = Instant._before_min_value()
        if end is None:
            end = Instant._after_max_value()

        if end < start:
            raise ValueError("The end parameter must be equal to or later than the start parameter")

        self.__start: Final[Instant] = start
        """The start of the interval."""
        self.__end: Final[Instant] = end
        """The end of the interval.

        This will never be earlier than the start.
        """

    @property
    def start(self) -> Instant:
        """Gets the start instant - the inclusive lower bound of the interval.

        This will never be later than ``end``, though it may be equal to it.

        :return: The start ``Instant``.
        :raises RuntimeError: The interval extends to the start of time.
        :seealso: :attr:`has_start`
        """
        _Preconditions._check_state(self.__start._is_valid, "Interval extends to start of time")
        return self.__start

    @property
    def has_start(self) -> bool:
        """Returns ``True`` if this interval has a fixed start point, or ``False`` if it extends to the start of time.

        :return: ``True`` if this interval has a fixed start point, ``False`` if it extends to the start of time.
        """
        return self.__start._is_valid

    @property
    def end(self) -> Instant:
        """Gets the end instant - the exclusive upper bound of the interval.

        :return: The end ``Instant``.
        :raises RuntimeError: The interval extends to the end of time.
        :seealso: :attr:`has_end`
        """
        _Preconditions._check_state(self.__end._is_valid, "Interval extends to end of time")
        return self.__end

    @property
    def _raw_end(self) -> Instant:
        """Returns the raw end value of the interval; a normal instant or ``Instant._after_max_value``.

        This value should never be exposed.
        """
        return self.__end

    @property
    def has_end(self) -> bool:
        """Returns ``True`` if this interval has a fixed end point, or ``False`` if it extends to the end of time.

        :return: ``True`` if this interval has a fixed end point, or ``False`` if it xtends to the end of time.
        """
        return self.__end._is_valid

    @property
    def duration(self) -> Duration:
        """Returns the duration of the interval.

        This will always be a non-negative duration, though it may be zero.

        :return: The duration of the interval.
        :raises RuntimeError: The interval extends to the start or end of time.
        """
        return self.end - self.start

    def __contains__(self, instant: Instant) -> bool:
        """Returns ``True`` if this interval contains the given ``Instant``; otherwise ``False``.

        :param instant: The ``Instant`` to test.
        :return: ``True`` if this interval contains the given ``Instant``; otherwise ``False``.
        """
        return self.__start <= instant < self.__end

    def contains(self, instant: Instant) -> bool:
        """Returns ``True`` if this interval contains the given ``Instant``; otherwise ``False``.

        Friendly alternative to ``__contains__``.

        :param instant: The ``Instant`` to test.
        :return: ``True`` if this interval contains the given ``Instant``; otherwise ``False``.
        """
        return instant in self

    def __iter__(self) -> Generator[Instant | None, None, None]:
        """Deconstruct this value into its components.

        :yields: The start and end ``Instant`` of the interval, or ``None`` if it extends to the start or end of time.
        """
        yield self.__start if self.__start._is_valid else None
        yield self.__end if self.__end._is_valid else None

    # region Implementation of IEquatable<Interval>

    def equals(self, other: Interval) -> bool:
        """Indicates whether the value of this interval is equal to the value of the specified interval.

        See the type documentation for a description of equality semantics.

        :param other: The value to compare with this instance.
        :return: ``True`` if the value of this interval is equal to the value of the ``other`` parameter;
            otherwise, false.
        """
        return self == other

    # endregion

    # region Object overrides

    def __hash__(self) -> int:
        """Returns the hash code for this instance.

        See the type documentation for a description of equality semantics.

        :return: An integer that is the hash code for this instance.
        """
        return _hash_code_helper(self.__start, self.__end)

    def __repr__(self) -> str:
        """Returns a string representation of this interval, in extended ISO-8601 format: the format is "start/end"
        where each instant uses a format of "uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF'Z'". If the start or end is
        infinite, the relevant part uses "StartOfTime" or "EndOfTime" to represent this.

        :return: A string representation of this interval.
        """
        from pyoda_time.text import InstantPattern

        pattern: InstantPattern = InstantPattern.extended_iso
        return f"{pattern.format(self.__start)}/{pattern.format(self.__end)}"

    # endregion

    # region Operator

    def __eq__(self, other: object) -> bool:
        """Implements the operator ==.

        See the type documentation for a description of equality semantics.

        :param other: The object to compare with this instance.
        :return: ``True`` if the value of this interval is equal to the value of the ``other`` parameter.
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return self.__start == other.__start and self.__end == other.__end

    def __ne__(self, other: object) -> bool:
        """Implements the operator !=.

        See the type documentation for a description of equality semantics.

        :param other: The object to compare with this instance.
        :return: ``True`` if the value of this interval is not equal to the value of the ``other`` parameter.
        """
        return not (self == other)

    # endregion
