# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ._calendar_system import CalendarSystem
from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

if typing.TYPE_CHECKING:
    from ._calendar_ordinal import _CalendarOrdinal
    from ._date_interval import DateInterval
    from ._local_date import LocalDate
    from ._year_month_day import _YearMonthDay
    from ._year_month_day_calendar import _YearMonthDayCalendar
    from .calendars import Era


__all__ = ["YearMonth"]


@_sealed
@typing.final
class YearMonth:
    """A year and month in a particular calendar.

    This is effectively ``LocalDate`` without the day-of-month component.
    """

    # The start of the month. This is used as our base representation as we already have
    # plenty of other code that integrates it, and it implements a compact representation
    # without us having to duplicate any of the logic.
    __start_of_month: typing.Final[_YearMonthDayCalendar]

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system associated with this year/month."""
        return CalendarSystem._for_ordinal(self.__calendar_ordinal)

    @property
    def __calendar_ordinal(self) -> _CalendarOrdinal:
        return self.__start_of_month._calendar_ordinal

    @property
    def year(self) -> int:
        """The year of this year/month.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.
        """
        return self.__start_of_month._year

    @property
    def month(self) -> int:
        """The month of this year/month within the year."""
        return self.__start_of_month._month

    @property
    def year_of_era(self) -> int:
        """The year of this value within the era."""
        return self.calendar._get_year_of_era(self.__start_of_month._year)

    @property
    def era(self) -> Era:
        """The era of this year/month."""
        return self.calendar._get_era(self.__start_of_month._year)

    @property
    def _start_date(self) -> LocalDate:
        """The date of the start of this year/month."""
        from ._local_date import LocalDate

        return LocalDate._ctor(year_month_day_calendar=self.__start_of_month)

    @property
    def _end_date(self) -> LocalDate:
        """The date of the end of this year/month."""
        from ._local_date import LocalDate

        return LocalDate(
            year=self.year,
            month=self.month,
            day=self.calendar.get_days_in_month(self.year, self.month),
            calendar=self.calendar,
        )

    @property
    def __year_month_day(self) -> _YearMonthDay:
        return self.__start_of_month._to_year_month_day()

    @typing.overload
    def __init__(self, *, year: int, month: int, calendar: CalendarSystem = CalendarSystem.iso) -> None: ...

    @typing.overload
    def __init__(
        self, *, era: Era, year_of_era: int, month: int, calendar: CalendarSystem = CalendarSystem.iso
    ) -> None: ...

    def __init__(
        self,
        *,
        year: int | None = None,
        month: int | None = None,
        era: Era | None = None,
        year_of_era: int | None = None,
        calendar: CalendarSystem = CalendarSystem.iso,
    ) -> None:
        from ._year_month_day_calendar import _YearMonthDayCalendar

        _Preconditions._check_not_null(calendar, "calendar")
        if era is not None and year_of_era is not None:
            year = calendar.get_absolute_year(year_of_era, era)
        if year is not None and month is not None:
            calendar._validate_year_month_day(year, month, 1)
            self.__start_of_month = _YearMonthDayCalendar._ctor(
                year=year,
                month=month,
                day=1,
                calendar_ordinal=calendar._ordinal,
            )
        else:
            raise ValueError  # TODO: Better error for incorrect arguments

    def to_date_interval(self) -> DateInterval:
        """Return a ``DateInterval`` covering the month represented by this value."""
        from ._date_interval import DateInterval

        return DateInterval(self._start_date, self._end_date)

    def plus_months(self, months: int) -> YearMonth:
        """Returns a ``YearMonth`` object which is the result of adding the specified number of months to this object.

        :param months: The number of months to add to this object.
        :return: The resulting ``YearMonth`` after adding the specified number of months.
        """
        return self.on_day_of_month(1).plus_months(months).to_year_month()

    def on_day_of_month(self, day: int) -> LocalDate:
        """Returns a ``LocalDate`` with the year/month of this value, and the given day of month.

        :param day: The day within the month.
        :return: The result of combining this year and month with ``day``.
        """
        from ._local_date import LocalDate

        _Preconditions._check_argument_range("day", day, 1, self.calendar.get_days_in_month(self.year, self.month))
        return LocalDate(
            year=self.year,
            month=self.month,
            day=day,
            calendar=self.calendar,
        )

    def compare_to(self, other: YearMonth) -> int:
        """Indicates whether this year/month is earlier, later or the same as another one. See the type documentation
        for a description of ordering semantics.

        :param other: The other year/month to compare this one with.
        :return: A value less than zero if this year/month is earlier than ``other``;
            zero if this year/month is the same as ``other``;
            a value greater than zero if this date is later than ``other``.
        """
        _Preconditions._check_argument(isinstance(other, YearMonth), "other", "Object must be of type YearMonth.")
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values with the same calendar system can be compared",
        )
        return self.__trusted_compare_to(other)

    def __trusted_compare_to(self, other: YearMonth) -> int:
        """Performs a comparison with another YearMonth, trusting that the calendar of the other date is already
        correct.

        This avoids duplicate calendar checks.
        """
        return self.calendar._compare(self.__year_month_day, other.__year_month_day)

    def __lt__(self, other: YearMonth | None) -> bool:
        if other is None:
            return False
        if isinstance(other, YearMonth):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) < 0
        return NotImplemented  # type: ignore[unreachable]

    def __le__(self, other: YearMonth | None) -> bool:
        if other is None:
            return False
        if isinstance(other, YearMonth):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) <= 0
        return NotImplemented  # type: ignore[unreachable]

    def __gt__(self, other: YearMonth | None) -> bool:
        if other is None:
            return True
        if isinstance(other, YearMonth):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) > 0
        return NotImplemented  # type: ignore[unreachable]

    def __ge__(self, other: YearMonth | None) -> bool:
        if other is None:
            return True
        if isinstance(other, YearMonth):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) >= 0
        return NotImplemented  # type: ignore[unreachable]

    def __hash__(self) -> int:
        return hash(self.__start_of_month)

    def equals(self, other: YearMonth) -> bool:
        """Compares two ``YearMonth`` values for equality."""
        return self == other

    def __eq__(self, other: object) -> bool:
        if isinstance(other, YearMonth):
            return self.__start_of_month == other.__start_of_month
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        """Compares two ``YearMonth`` values for equality."""
        return not self == other

    # TODO: ToString()
