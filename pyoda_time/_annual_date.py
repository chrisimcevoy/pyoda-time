# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from ._calendar_ordinal import _CalendarOrdinal
from ._calendar_system import CalendarSystem
from ._local_date import LocalDate
from ._year_month_day import _YearMonthDay
from .calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions


@final
@_sealed
class AnnualDate:
    """Represents an annual date (month and day) in the ISO calendar but without a specific year, typically for
    recurrent events such as birthdays, anniversaries, and deadlines.

    Equality and comparison order are defined in the natural way. Two values are equal if they represent the same month
    and the same day-of-month. One value is earlier than another if it has a smaller month, or the same month but an
    earlier day-of-month.

    In the future, this class may be expanded to support other calendar systems, but this does not generalize terribly
    cleanly, particularly to the Hebrew calendar system with its leap month.

    The default value of this type is January 1st.
    """

    __slots__ = ("__value",)

    def __init__(self, month: int = 1, day: int = 1) -> None:
        """Constructs an instance for the given month and day in the ISO calendar.

        :param month: The month of year.
        :param day: The day of month.
        :raises ValueError: The parameters do not form a valid date. (February 29th is considered valid.)
        """
        # The year 2000 is a leap year, so this is fine for all valid dates.
        _GregorianYearMonthDayCalculator._validate_gregorian_year_month_day(2000, month, day)
        # See comment above for why this is using year 1, and why that's okay even for February 29th.
        self.__value: _YearMonthDay = _YearMonthDay._ctor(year=1, month=month, day=day)
        """The underlying value.

        We only care about the month and day, but for the sake of compatibility with the default value, this ends up
        being in year 1. This would be an invalid date, but we only actually use it as an argument to SetYear, which we
        know ignores the year in the ISO calendar. If we ever allow other calendar systems, we can have a
        YearMonthDayCalendar which would still be in year 1 for the ISO calendar, but would probably be in a more
        suitable year for other calendars.
        """

    @property
    def month(self) -> int:
        """Gets the month of year.

        :return: The month of year.
        """
        return self.__value._month

    @property
    def day(self) -> int:
        """Gets the day of month.

        :return: The day of month.
        """
        return self.__value._day

    def in_year(self, year: int) -> LocalDate:
        """Returns this annual date in a particular year, as a ``LocalDate``.

        If this value represents February 29th, and the specified year is not a leap year, the returned value will be
        February 28th of that year. To see whether the original month and day is valid without truncation in a
        particular year, use ``is_valid_year``.

        :param year: The year component of the required date.
        :return: A date in the given year, suitable for this annual date.
        """
        _Preconditions._check_argument_range(
            "year",
            year,
            _GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR,
            _GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR,
        )
        ymd: _YearMonthDay = CalendarSystem.iso._year_month_day_calculator._set_year(self.__value, year)
        return LocalDate._ctor(year_month_day_calendar=ymd._with_calendar_ordinal(_CalendarOrdinal.ISO))

    def is_valid_year(self, year: int) -> bool:
        """Checks whether the specified year forms a valid date with the month/day in this value, without any
        truncation.

        This will always return ``True`` except for values representing February 29th, where the specified year is a non
        leap year.

        :param year: The year to test for validity
        :return: ``True`` if the current value occurs within the given year; ``False`` otherwise.
        """
        return self.month != 2 or self.day != 29 or CalendarSystem.iso.is_leap_year(year)

    def __hash__(self) -> int:
        """Returns a hash code for this annual date.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this annual date.
        """
        return hash(self.__value)

    def __repr__(self) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import AnnualDatePattern

        return AnnualDatePattern._bcl_support.format(self, None, CultureInfo.current_culture)

    def __format__(self, format_spec: str) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import AnnualDatePattern

        return AnnualDatePattern._bcl_support.format(self, format_spec, CultureInfo.current_culture)

    def equals(self, other: AnnualDate) -> bool:
        """Compares this annual date with the specified one for equality.

        See the type documentation for a description of equality semantics.

        :param other: The other annual date to compare this one with
        :return: True if the specified annual date is equal to this one; false otherwise
        """
        return self == other

    def compare_to(self, other: AnnualDate | None) -> int:
        """Indicates whether this annual date is earlier, later or the same as another one.

        See the type documentation for a description of ordering semantics.

        :param other: The other annual date to compare this one with
        :return: A value less than zero if this annual date is earlier than ``other``;
            zero if this time is the same as ``other``; a value greater than zero if this annual date is
            later than ``other``.
        """
        if other is None:
            return 1
        if not isinstance(other, AnnualDate):
            raise TypeError(f"{self.__class__.__name__} cannot be compared to {other.__class__.__name__}")
        return self.__value.compare_to(other.__value)

    def __eq__(self, other: object) -> bool:
        """Compares two ``AnnualDate`` values for equality.

        See the type documentation for a description of equality semantics.

        :param other: The other annual date to compare this one with
        :return: True if the two dates are the same; false otherwise
        """
        if not isinstance(other, AnnualDate):
            return NotImplemented
        return self.__value == other.__value

    def __ne__(self, other: object) -> bool:
        """Compares two ``AnnualDate`` values for inequality.

        See the type documentation for a description of equality semantics.

        :param other: The other annual date to compare this one with
        :return: False if the two dates are the same; true otherwise
        """
        return not (self == other)

    def __lt__(self, other: AnnualDate) -> bool:
        """Compares two annual dates to see if this one is strictly earlier than the other one.

        See the type documentation for a description of ordering semantics.

        :param other: The other annual date to compare this one with
        :return: true if this is strictly earlier than ``other``, false otherwise.
        """
        if not isinstance(other, AnnualDate):
            return NotImplemented  # type: ignore[unreachable]
        return self.compare_to(other) < 0

    def __le__(self, other: AnnualDate) -> bool:
        """Compares two annual dates to see if this one is earlier than or equal to the other one.

        See the type documentation for a description of ordering semantics.

        :param other: The other annual date to compare this one with
        :return: true if this is strictly earlier than or equal to ``other``, false otherwise.
        """
        if not isinstance(other, AnnualDate):
            return NotImplemented  # type: ignore[unreachable]
        return self.compare_to(other) <= 0

    def __gt__(self, other: AnnualDate) -> bool:
        """Compares two annual dates to see if this one is strictly later than the other one.

        See the type documentation for a description of ordering semantics.

        :param other: The other annual date to compare this one with
        :return: true if this is strictly later than ``other``, false otherwise.
        """
        if not isinstance(other, AnnualDate):
            return NotImplemented  # type: ignore[unreachable]
        return self.compare_to(other) > 0

    def __ge__(self, other: AnnualDate) -> bool:
        """Compares two annual dates to see if this one is later than or equal to the other one.

        See the type documentation for a description of ordering semantics.

        :param other: The other annual date to compare this one with
        :return: true if this is strictly later than or equal to ``other``, false otherwise.
        """
        if not isinstance(other, AnnualDate):
            return NotImplemented  # type: ignore[unreachable]
        return self.compare_to(other) >= 0
