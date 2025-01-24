# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from pyoda_time._local_date import LocalDate
from pyoda_time._offset import Offset
from pyoda_time._offset_date_time import OffsetDateTime
from pyoda_time.utility._hash_code_helper import _hash_code_helper

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyoda_time import CalendarSystem, IsoDayOfWeek, LocalTime
    from pyoda_time.calendars import Era


@final
class OffsetDate:
    """A combination of a ``LocalDate`` and an ``Offset``, to represent a date at a specific offset from UTC but without
    any time-of-day information.

    Equality is defined in a component-wise fashion: two values are the same if they represent equal dates
    (including being in the same calendar) and equal offsets from UTC.

    The default value of this type is 0001-01-01 (January 1st, 1 C.E.) in the ISO calendar with a UTC offset of zero.
    """

    def __init__(self, date: LocalDate = LocalDate(), offset: Offset = Offset()) -> None:
        """Constructs an instance of the specified date and offset.

        :param date: The date part of the value.
        :param offset: The offset part of the value.
        """
        self.__date: Final[LocalDate] = date
        self.__offset: Final[Offset] = offset

    @property
    def date(self) -> LocalDate:
        """Gets the local date represented by this value.

        :return: The local date represented by this value.
        """
        return self.__date

    @property
    def offset(self) -> Offset:
        """Gets the offset from UTC of this value.

        :return: The offset from UTC of this value.
        """
        return self.__offset

    @property
    def calendar(self) -> CalendarSystem:
        """Gets the calendar system associated with this offset date.

        :return: The calendar system associated with this offset date.
        """
        return self.date.calendar

    @property
    def year(self) -> int:
        """Gets the year of this offset date.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.

        :return: The year of this offset date.
        """
        return self.__date.year

    @property
    def month(self) -> int:
        """Gets the month of this offset date within the year.

        :return: The month of this offset date within the year.
        """
        return self.__date.month

    @property
    def day(self) -> int:
        """Gets the day of this offset date within the month.

        :return: The day of this offset date within the month.
        """
        return self.__date.day

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """Gets the week day of this offset date expressed as an ``IsoDayOfWeek`` value.

        :return: The week day of this offset date expressed as an ``IsoDayOfWeek`` value.
        """
        return self.__date.day_of_week

    @property
    def year_of_era(self) -> int:
        """Gets the year of this offset date within the era.

        :return: The year of this offset date within the era.
        """
        return self.__date.year_of_era

    @property
    def era(self) -> Era:
        """Gets the era of this offset date.

        :return: The era of this offset date.
        """
        return self.__date.era

    @property
    def day_of_year(self) -> int:
        """Gets the day of this offset date within the year.

        :return: The day of this offset date within the year.
        """
        return self.__date.day_of_year

    def with_offset(self, offset: Offset) -> OffsetDate:
        """Creates a new ``OffsetDate`` for the same date, but with the specified UTC offset.

        :param offset: The new UTC offset.
        :return: A new ``OffsetDate`` for the same date, but with the specified UTC offset.
        """
        return OffsetDate(self.__date, offset)

    def with_(self, adjuster: Callable[[LocalDate], LocalDate]) -> OffsetDate:
        """Returns this offset date, with the given date adjuster applied to it, maintaining the existing offset.

        If the adjuster attempts to construct an invalid date (such as by trying to set a day-of-month of 30 in
        February), any exception thrown by that construction attempt will be propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted offset date.
        """
        return OffsetDate(date=self.__date.with_(adjuster), offset=self.__offset)

    def with_calendar(self, calendar: CalendarSystem) -> OffsetDate:
        """Creates a new ``OffsetDate`` representing the same physical date and offset, but in a different calendar.

        The returned value is likely to have different date field values to this one.
        For example, January 1st 1970 in the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this offset date to.
        :return: The converted ``OffsetDate``.
        """
        return OffsetDate(date=self.__date.with_calendar(calendar), offset=self.__offset)

    def at(self, time: LocalTime) -> OffsetDateTime:
        """Combines this ``OffsetDate`` with the given ``LocalTime`` into an ``OffsetDateTime``.

        :param time: The time to combine with this date.
        :return: The ``OffsetDateTime`` representation of the given time on this date.
        """
        return OffsetDateTime(local_date_time=self.__date.at(time=time), offset=self.__offset)

    def __hash__(self) -> int:
        """Returns a hash code for this offset date.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this offset date.
        """
        return _hash_code_helper(self.__date, self.__offset)

    def equals(self, other: OffsetDate) -> bool:
        """Compares two ``OffsetDate`` values for equality.

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date with.
        :return: True if the given value is another offset date equal to this one; false otherwise.
        """
        return self == other

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date with.
        :return: ``True`` if values are equal to each other, otherwise ``False``.
        """
        if not isinstance(other, OffsetDate):
            return NotImplemented
        return self.__date == other.__date and self.__offset == other.__offset

    def __ne__(self, other: object) -> bool:
        """Implements the operator != (inequality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date with.
        :return: ``True`` if values are not equal to each other, otherwise ``False``.
        """
        if not isinstance(other, OffsetDate):
            return NotImplemented
        return not (self == other)

    # TODO: def __repr__(self) -> str: [requires OffsetDatePattern]
    # TODO: deconstruct?
    # TODO: XML Serialization...?


__all__ = ["OffsetDate"]
