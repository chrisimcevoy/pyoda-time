# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final, overload

from ._local_date import LocalDate
from ._period import Period
from .text import LocalDatePattern

if TYPE_CHECKING:
    from collections.abc import Iterator

    from . import CalendarSystem

from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

__all__ = ["DateInterval"]


@_sealed
@final
class DateInterval:
    """An interval between two dates.

    Equality is defined in a component-wise fashion: two date intervals are considered equal if their start dates are
    equal to each other and their end dates are equal to each other. Ordering between date intervals is not defined.

    The two dates must be in the same calendar, and the end date must not be earlier than the start date.

    The end date is deemed to be part of the range, as this matches many real life uses of
    date ranges. For example, if someone says "I'm going to be on holiday from Monday to Friday," they
    usually mean that Friday is part of their holiday.
    """

    @property
    def start(self) -> LocalDate:
        """The start date of the interval."""
        return self.__start

    @property
    def end(self) -> LocalDate:
        """The end date of the interval."""
        return self.__end

    def __init__(self, start: LocalDate, end: LocalDate) -> None:
        """Constructs a date interval from a start date and an end date, both of which are included in the interval.

        :param start: Start date of the interval
        :param end: End date of the interval
        """
        _Preconditions._check_argument(
            start.calendar == end.calendar, "end", "Calendars of start and end dates must be the same."
        )
        _Preconditions._check_argument(not end < start, "end", "End date must not be earlier than the start date")
        self.__start: LocalDate = start
        self.__end: LocalDate = end

    def __hash__(self) -> int:
        """Returns the hash code for this interval, consistent with ``__eq__()``.

        See the type documentation for a description of equality semantics.

        :return: The hash code for this interval.
        """
        from pyoda_time.utility._hash_code_helper import _hash_code_helper

        return _hash_code_helper(self.start, self.end)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, DateInterval):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __ne__(self, other: object) -> bool:
        if isinstance(other, DateInterval):
            return not self == other
        return NotImplemented

    def equals(self, other: DateInterval) -> bool:
        return self == other

    def __contains__(self, item: LocalDate | DateInterval) -> bool:
        if isinstance(item, LocalDate):
            _Preconditions._check_argument(
                item.calendar == self.__start.calendar,
                "item",
                "The date to check must be in the same calendar as the start and end dates",
            )
            return self.__start <= item <= self.__end
        elif isinstance(item, DateInterval):
            self.__validate_interval(item)
            return self.__start <= item.__start and item.__end <= self.__end
        raise TypeError(f"item must be one of LocalDate or DateInterval; got {item.__class__.__name__}")

    @overload
    def contains(self, date: LocalDate, /) -> bool:
        """Checks whether the given date is within this date interval.

        This requires that the date is not earlier than the start date, and not later than the end date.

        Friendly alternative to ``__contains__()``.

        :param date: The date to check for containment within this interval.
        :return: ``True`` if ``date`` is within this interval; ``False`` otherwise.
        """

    @overload
    def contains(self, interval: DateInterval, /) -> bool:
        """Checks whether the given interval is within this interval.

        This requires that the start date of the specified interval is not earlier than the start date of this interval,
        and the end date of the specified interval is not later than the end date of this interval.

        Friendly alternative to ``__contains__()``.

        :param interval: The interval to check for containment within this interval.
        :return: ``True`` if ``interval`` is within this interval; ``False`` otherwise.
        """

    @overload
    def contains(self, date: LocalDate | DateInterval, /) -> bool: ...

    def contains(self, date_or_interval: LocalDate | DateInterval, /) -> bool:
        return date_or_interval in self

    def __len__(self) -> int:
        """Return the length of the interval in days."""
        # Period.InternalDaysBetween will give us the exclusive result, so we need to add 1
        # to include the end date.

        return Period._internal_days_between(self.__start, self.__end) + 1

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system of the dates in this interval."""
        return self.__start.calendar

    def __repr__(self) -> str:
        pattern = LocalDatePattern.iso
        # TODO: Invariant
        return f"[{pattern.format(self.__start)}, {pattern.format(self.__end)}]"

    # def __iter__(self) -> Iterator[LocalDate]:
    #     """Deconstruct this date interval into its components."""
    #     yield self.__start
    #     yield self.__end

    # Different to Noda Time: In Python I think users will reasonably expect & to work.
    def __and__(self, interval: DateInterval) -> DateInterval | None:
        """Return the intersection between the given interval and this interval.

        :param interval: The specified interval to intersect with this one.
        :return: A ``DateInterval`` corresponding to the intersection between the given interval and the current
            instance. If there is no intersection, ``None`` is returned.
        :raises ValueError: ``interval`` uses a different calendar to this date interval.
        """
        if interval in self:
            return interval
        if self in interval:
            return self
        if self.__start in interval:
            return DateInterval(self.__start, interval.__end)
        if self.__end in interval:
            return DateInterval(interval.__start, self.__end)
        return None

    def intersection(self, interval: DateInterval) -> DateInterval | None:
        """Return the intersection between the given interval and this interval.

        Friendly alternative to ``__and__()``.

        :param interval: The specified interval to intersect with this one.
        :return: A ``DateInterval`` corresponding to the intersection between the given interval and the current
            instance. If there is no intersection, ``None`` is returned.
        :raises ValueError: ``interval`` uses a different calendar to this date interval.
        """
        return self & interval

    # Different to Noda Time: In Python I think users will reasonably expect | to work.
    def __or__(self, interval: DateInterval) -> DateInterval | None:
        """Return the union between the given interval and this interval, as long as they're overlapping or contiguous.

        :param interval: The specified interval from which to generate the union interval.
        :return: A ``DateInterval`` corresponding to the union between the given interval and the current instance, in
            the case the intervals overlap or are contiguous; None otherwise.
        :raises ValueError: ``interval`` uses a different calendar to this date interval.
        """
        self.__validate_interval(interval)

        start = LocalDate.min(self.__start, interval.__start)
        end = LocalDate.max(self.__end, interval.__end)

        # Check whether the length of the interval we *would* construct is greater
        # than the sum of the lengths - if it is, there's a day in that candidate union
        # that isn't in either interval. Note the absence of "+ 1" and the use of >=
        # - it's equivalent to Period.InternalDaysBetween(...) + 1 > Length + interval.Length,
        # but with fewer operations.
        if Period.days_between(start, end) >= len(self) + len(interval):
            return None
        return DateInterval(start, end)

    def union(self, interval: DateInterval) -> DateInterval | None:
        """Return the union between the given interval and this interval, as long as they're overlapping or contiguous.

        Friendly alternative to ``__or__()``.

        :param interval: The specified interval from which to generate the union interval.
        :return: A ``DateInterval`` corresponding to the union between the given interval and the current instance, in
            the case the intervals overlap or are contiguous; None otherwise.
        :raises ValueError: ``interval`` uses a different calendar to this date interval.
        """
        return self | interval

    def __validate_interval(self, interval: DateInterval) -> None:
        _Preconditions._check_not_null(interval, "interval")
        _Preconditions._check_argument(
            interval.calendar == self.__start.calendar,
            "interval",
            "The specified interval uses a different calendar system to this one",
        )

    def __iter__(self) -> Iterator[LocalDate]:
        """Returns an iterator for the dates in the interval, including both ``start`` and ``end``.

        :return: An iterator for the interval.
        """
        # Stop when we know we've reach End, and then yield that.
        # We can't use a <= condition, as otherwise we'd try to create a date past End, which may be invalid.
        # We could use < but that's significantly less efficient than !=
        # We know that adding a day at a time we'll eventually reach End (because they're validated to be in the same
        # calendar system, with Start <= End), so that's the simplest way to go.
        days_to_add = 0
        while (date := self.__start.plus_days(days_to_add)) != self.__end:
            yield date
            days_to_add += 1
        yield self.__end
