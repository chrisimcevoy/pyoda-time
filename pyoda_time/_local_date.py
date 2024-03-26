# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ._calendar_ordinal import _CalendarOrdinal
from ._calendar_system import CalendarSystem
from ._iso_day_of_week import IsoDayOfWeek
from .calendars import Era
from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

if typing.TYPE_CHECKING:
    from . import LocalDateTime, LocalTime, Period, YearMonth
    from ._year_month_day import _YearMonthDay
    from ._year_month_day_calendar import _YearMonthDayCalendar


__all__ = ["LocalDate"]


class _LocalDateMeta(type):
    @property
    def max_iso_value(self) -> LocalDate:
        """The maximum (latest) date representable in the ISO calendar system."""
        from ._year_month_day_calendar import _YearMonthDayCalendar
        from .calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator

        return LocalDate._ctor(
            year_month_day_calendar=_YearMonthDayCalendar._ctor(
                year=_GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR,
                month=12,
                day=31,
                calendar_ordinal=_CalendarOrdinal.ISO,
            )
        )

    @property
    def min_iso_value(self) -> LocalDate:
        """The minimum (earliest) date representable in the ISO calendar system."""
        from ._year_month_day_calendar import _YearMonthDayCalendar
        from .calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator

        return LocalDate._ctor(
            year_month_day_calendar=_YearMonthDayCalendar._ctor(
                year=_GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR,
                month=1,
                day=1,
                calendar_ordinal=_CalendarOrdinal.ISO,
            )
        )


@typing.final
@_sealed
class LocalDate(metaclass=_LocalDateMeta):
    """LocalDate is an immutable struct representing a date within the calendar, with no reference to a particular time
    zone or time of day."""

    @typing.overload
    def __init__(self) -> None: ...

    @typing.overload
    def __init__(self, *, year: int, month: int, day: int): ...

    @typing.overload
    def __init__(self, *, year: int, month: int, day: int, calendar: CalendarSystem): ...

    @typing.overload
    def __init__(self, *, era: Era, year_of_era: int, month: int, day: int): ...

    @typing.overload
    def __init__(self, *, era: Era, year_of_era: int, month: int, day: int, calendar: CalendarSystem): ...

    def __init__(
        self,
        year: int = 1,
        month: int = 1,
        day: int = 1,
        calendar: CalendarSystem | None = None,
        era: Era | None = None,
        year_of_era: int | None = None,
    ):
        from ._year_month_day_calendar import _YearMonthDayCalendar

        calendar = calendar or CalendarSystem.iso

        if era is not None and year_of_era is not None and month is not None and day is not None:
            year = calendar.get_absolute_year(year_of_era, era)

        if year is not None and month is not None and day is not None:
            calendar._validate_year_month_day(year, month, day)
            self.__year_month_day_calendar = _YearMonthDayCalendar._ctor(
                year=year, month=month, day=day, calendar_ordinal=calendar._ordinal
            )
        else:
            raise TypeError

    @classmethod
    @typing.overload
    def _ctor(cls, *, year_month_day_calendar: _YearMonthDayCalendar) -> LocalDate: ...

    @classmethod
    @typing.overload
    def _ctor(cls, *, days_since_epoch: int) -> LocalDate: ...

    @classmethod
    @typing.overload
    def _ctor(cls, *, days_since_epoch: int, calendar: CalendarSystem) -> LocalDate: ...

    @classmethod
    def _ctor(
        cls,
        *,
        year_month_day_calendar: _YearMonthDayCalendar | None = None,
        days_since_epoch: int | None = None,
        calendar: CalendarSystem | None = None,
    ) -> LocalDate:
        from .calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator

        self = super().__new__(cls)
        if year_month_day_calendar is not None:
            self.__year_month_day_calendar = year_month_day_calendar
        elif days_since_epoch is not None:
            if calendar is None:
                self.__year_month_day_calendar = (
                    _GregorianYearMonthDayCalculator._get_gregorian_year_month_day_calendar_from_days_since_epoch(
                        days_since_epoch
                    )
                )
            else:
                self.__year_month_day_calendar = calendar._get_year_month_day_calendar_from_days_since_epoch(
                    days_since_epoch
                )
        else:
            raise TypeError
        return self

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system associated with this local date."""
        return CalendarSystem._for_ordinal(self.__calendar_ordinal)

    @property
    def __calendar_ordinal(self) -> _CalendarOrdinal:
        return self.__year_month_day_calendar._calendar_ordinal

    @property
    def year(self) -> int:
        """The year of this local date.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.
        """
        return self.__year_month_day_calendar._year

    @property
    def month(self) -> int:
        """The month of this local date within the year."""
        return self.__year_month_day_calendar._month

    @property
    def day(self) -> int:
        return self.__year_month_day_calendar._day

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.calendar._get_days_since_epoch(self.__year_month_day_calendar._to_year_month_day())

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """The week day of this local date expressed as an ``IsoDayOfWeek``."""
        return self.calendar._get_day_of_week(self._year_month_day)

    @property
    def year_of_era(self) -> int:
        """The year of this local date within the era."""
        return self.calendar._get_year_of_era(self.__year_month_day_calendar._year)

    @property
    def era(self) -> Era:
        """The era of this local date."""
        return self.calendar._get_era(self.__year_month_day_calendar._year)

    @property
    def day_of_year(self) -> int:
        """The day of this local date within the year."""
        return self.calendar._get_day_of_year(self._year_month_day)

    @property
    def _year_month_day(self) -> _YearMonthDay:
        return self.__year_month_day_calendar._to_year_month_day()

    def to_year_month(self) -> YearMonth:
        from . import YearMonth

        return YearMonth(year=self.year, month=self.month, calendar=self.calendar)

    @typing.overload
    def __add__(self, other: Period) -> LocalDate:
        """Adds the specified period to the date.

        Fields are added in descending order of significance (years first, then months, and so on).

        :param other: The period to add. Must not contain any (non-zero) time units.
        :return: The sum of the given date and period
        """

    @typing.overload
    def __add__(self, other: LocalTime) -> LocalDateTime:
        """Combines the given ``LocalDate`` and ``LocalTime`` components into a single ``LocalDateTime``.

        :param other: The time to add to the date
        :return: The sum of the given date and time
        """
        ...

    def __add__(self, other: LocalTime | Period) -> LocalDateTime | LocalDate:
        from . import LocalDateTime, LocalTime, Period

        if isinstance(other, Period):
            _Preconditions._check_not_null(other, "period")
            _Preconditions._check_argument(
                not other.has_time_component, "period", "Cannot add a period with a time component to a date"
            )
            return self.plus_years(other.years).plus_months(other.months).plus_weeks(other.weeks).plus_days(other.days)
        if isinstance(other, LocalTime):
            return LocalDateTime._ctor(local_date=self, local_time=other)
        return NotImplemented  # type: ignore[unreachable]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LocalDate):
            return self.__year_month_day_calendar == other.__year_month_day_calendar
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, LocalDate):
            return not self == other
        return NotImplemented

    def __lt__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) < 0
        return NotImplemented  # type: ignore[unreachable]

    def __le__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) <= 0

    def __gt__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) > 0
        return NotImplemented  # type: ignore[unreachable]

    def __ge__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) >= 0

    def compare_to(self, other: LocalDate) -> int:
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values in the same calendar can be compared",
        )
        return self.__trusted_compare_to(other)

    def __trusted_compare_to(self, other: LocalDate) -> int:
        """Performs a comparison with another date, trusting that the calendar of the other date is already correct.

        This avoids duplicate calendar checks.
        """
        return self.calendar._compare(self._year_month_day, other._year_month_day)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDate:
        """Creates a new LocalDate representing the same physical date, but in a different calendar.

        The returned LocalDate is likely to have different field values to this one. For example, January 1st 1970 in
        the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this local date to.
        :return: The converted LocalDate
        """
        _Preconditions._check_not_null(calendar, "calendar")
        return LocalDate._ctor(days_since_epoch=self._days_since_epoch, calendar=calendar)

    def plus_years(self, years: int) -> LocalDate:
        """Returns a new LocalDate representing the current value with the given number of years added.

        If the resulting date is invalid, lower fields (typically the day of month) are reduced to find a valid value.
        For example, adding one year to February 29th 2012 will return February 28th 2013; subtracting one year from
        February 29th 2012 will return February 28th 2011.

        :param years: The number of years to add.
        :return: The current value plus the given number of years.
        """
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._years_field.add(self, years)

    def plus_months(self, months: int) -> LocalDate:
        """Returns a new LocalDate representing the current value with the given number of months added.

        This method does not try to maintain the year of the current value, so adding four months to a value in October
        will result in a value in the following February.

        If the resulting date is invalid, the day of month is reduced to find a valid value. For example, adding one
        month to January 30th 2011 will return February 28th 2011; subtracting one month from March 30th 2011 will
        return February 28th 2011.

        :param months: The number of months to add
        :return: The current date plus the given number of months
        """
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._months_field.add(self, months)

    def plus_days(self, days: int) -> LocalDate:
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._days_field.add(self, days)

    def plus_weeks(self, weeks: int) -> LocalDate:
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._weeks_field.add(self, weeks)

    def at(self, time: LocalTime) -> LocalDateTime:
        """Combines this ``LocalDate`` with the given ``LocalTime`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param time: The time to combine with this date.
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return self + time

    # region Formatting

    # TODO: def __str__(self): [requires LocalDatePattern.BclSupport]

    # endregion
