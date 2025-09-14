# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, final, overload

from ._calendar_ordinal import _CalendarOrdinal
from ._calendar_system import CalendarSystem
from ._iso_day_of_week import IsoDayOfWeek
from ._period import Period
from .calendars import Era, WeekYearRules
from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from . import DateTimeZone, LocalDateTime, LocalTime, Offset, OffsetDate, YearMonth, ZonedDateTime
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


@final
@_sealed
class LocalDate(metaclass=_LocalDateMeta):
    """LocalDate is an immutable object representing a date within the calendar, with no reference to a particular time
    zone or time of day.

    Values can freely be compared for equality: a value in a different calendar system is not equal to a value in a
    different calendar system. However, ordering comparisons fail with ``ValueError``; attempting to compare values in
    different calendars almost always indicates a bug in the calling code.

    The default value of this type is 0001-01-01 (January 1st, 1 C.E.) in the ISO calendar.
    """

    def __init__(
        self,
        year: int = 1,
        month: int = 1,
        day: int = 1,
        calendar: CalendarSystem = CalendarSystem.iso,
        era: Era | None = None,
    ) -> None:
        """Initialises a new instance of ``LocalDate`` for the given ``year``, ``month`` and ``day`` in a given
        ``calendar``.

        If ``era`` is not None, ``year`` is interpreted as the "year of era" rather than the absolute year, and is
        passed to ``CalendarSystem.get_absolute_year`` to determine the absolute year.

        :param year: The year. If ``era`` is None, this is the "absolute year", so, for the ISO calendar, a value of 0
            means 1 BC, for example. If ``era`` is provided, this is interpreted as the "year of era".
        :param month: The month of year.
        :param day: The day of month.
        :param calendar: Calendar system in which to create the date.
        :param era: The era within which to create a date. Must be a valid era within the specified calendar.
        """
        _Preconditions._check_not_null(calendar, "calendar")

        if era is not None:
            year = calendar.get_absolute_year(year, era)

        calendar._validate_year_month_day(year, month, day)

        from ._year_month_day_calendar import _YearMonthDayCalendar

        self.__year_month_day_calendar = _YearMonthDayCalendar._ctor(
            year=year, month=month, day=day, calendar_ordinal=calendar._ordinal
        )

    @classmethod
    @overload
    def _ctor(cls, *, year_month_day_calendar: _YearMonthDayCalendar) -> LocalDate:
        """Constructs an instance from values which are assumed to already have been validated."""

    @classmethod
    @overload
    def _ctor(cls, *, days_since_epoch: int) -> LocalDate:
        """Constructs an instance from the number of days since the unix epoch, in the ISO calendar system."""

    @classmethod
    @overload
    def _ctor(cls, *, days_since_epoch: int, calendar: CalendarSystem) -> LocalDate:
        """Constructs an instance from the number of days since the unix epoch, and a calendar system.

        The calendar system is assumed to be non-null, but the days since the epoch are validated.
        """

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
        """The day of this local date within the month."""
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

    def at_midnight(self) -> LocalDateTime:
        """Gets a ``LocalDateTime`` at midnight on the date represented by this local date.

        :return: The ``LocalDateTime`` representing midnight on this local date, in the same calendar system.
        """
        from ._local_date_time import LocalDateTime
        from ._local_time import LocalTime

        return LocalDateTime._ctor(local_date=self, local_time=LocalTime.midnight)

    @classmethod
    def from_week_year_week_and_day(
        cls, week_year: int, week_of_week_year: int, day_of_week: IsoDayOfWeek
    ) -> LocalDate:
        """Returns the local date corresponding to the given "week year", "week of week year", and "day of week" in the
        ISO calendar system, using the ISO week-year rules.

        :param week_year: ISO-8601 week year of value to return
        :param week_of_week_year: ISO-8601 week of week year of value to return
        :param day_of_week: ISO-8601 day of week to return
        :return: The date corresponding to the given week year / week of week year / day of week.
        """
        return WeekYearRules.iso.get_local_date(week_year, week_of_week_year, day_of_week, CalendarSystem.iso)

    @classmethod
    def from_year_month_week_and_day(
        cls, year: int, month: int, occurrence: int, day_of_week: IsoDayOfWeek
    ) -> LocalDate:
        """Returns the local date corresponding to a particular occurrence of a day-of-week within a year and month. For
        example, this method can be used to ask for "the third Monday in April 2012".

        The returned date is always in the ISO calendar. This method is unrelated to week-years and any rules for
        "business weeks" and the like - if a month begins on a Friday, then asking for the first Friday will give
        that day, for example.

        :param year: The year of the value to return.
        :param month: The month of the value to return.
        :param occurrence: The occurrence of the value to return, which must be in the range [1, 5]. The value 5 can be
            used to always return the last occurrence of the specified day-of-week, even if there are only 4
            occurrences of that day-of-week in the month.
        :param day_of_week: The day-of-week of the value to return.
        :return: The date corresponding to the given year and month, on the given occurrence of the given day of week.
        """
        # This validates year and month as well as getting us a useful date.
        start_of_month = LocalDate(year, month, 1)
        _Preconditions._check_argument_range("occurrence", occurrence, 1, 5)
        _Preconditions._check_argument_range("day_of_week", day_of_week, 1, 7)

        # Correct day of week, 1st week of month.
        week_1_day: int = start_of_month.day_of_week + 1
        if week_1_day <= 0:
            week_1_day += 7
        target_day: int = week_1_day + (occurrence - 1) * 7
        if target_day > CalendarSystem.iso.get_days_in_month(year, month):
            target_day -= 7
        return LocalDate(year, month, target_day)

    def to_year_month(self) -> YearMonth:
        """Creates a ``YearMonth`` value for the month containing this date.

        :return: A year/month value containing this date.
        """
        from . import YearMonth

        return YearMonth(year=self.year, month=self.month, calendar=self.calendar)

    @overload
    def __add__(self, other: Period) -> LocalDate:
        """Adds the specified period to the date.

        Fields are added in descending order of significance (years first, then months, and so on).

        :param other: The period to add. Must not contain any (non-zero) time units.
        :return: The sum of the given date and period
        """

    @overload
    def __add__(self, other: LocalTime) -> LocalDateTime:
        """Combines the given ``LocalDate`` and ``LocalTime`` components into a single ``LocalDateTime``.

        :param other: The time to add to the date
        :return: The sum of the given date and time
        """

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

    @staticmethod
    def add(date: LocalDate, period: Period) -> LocalDate:
        """Adds the specified period to the date. Fields are added in descending order of significance (years first,
        then months, and so on). Friendly alternative to ``+``.

        :param date: The date to add the period to.
        :param period: The period to add. Must not contain any (non-zero) time units.
        :return: The sum of the given date and period.
        """
        return date + period

    def plus(self, period: Period) -> LocalDate:
        """Adds the specified period to this date. Fields are added in descending order of significance (years first,
        then months, and so on). Fluent alternative to ``+``.

        :param period: The period to add. Must not contain any (non-zero) time units.
        :return: The sum of this date and the given period.
        """
        return self + period

    @overload
    def __sub__(self, other: LocalDate) -> Period:
        """Subtracts one date from another, returning the result as a ``Period`` with units of years, months and days.

        This is simply a convenience operator for calling ``Period.between(LocalDate, LocalDate)``.
        The calendar systems of the two dates must be the same; an exception will be thrown otherwise.

        :param other: The date to subtract.
        :return: The result of subtracting one date from another.
        :exception ValueError: The two dates are not in the same calendar system.
        """

    @overload
    def __sub__(self, other: Period) -> LocalDate:
        """Subtracts the specified period from the date. Fields are subtracted in descending order of significance
        (years first, then months, and so on). This is a convenience operator over the ``minus(Period)`` method.

        :param other: The period to subtract. Must not contain any (non-zero) time units.
        :return: The result of subtracting the given period from the date.
        """

    def __sub__(self, other: LocalDate | Period) -> LocalDate | Period:
        if isinstance(other, LocalDate):
            return Period.between(other, self)
        elif isinstance(other, Period):
            _Preconditions._check_argument(
                not other.has_time_component, "period", "Cannot subtract a period with a time component from a date"
            )
            return (
                self.plus_years(-other.years).plus_months(-other.months).plus_weeks(-other.weeks).plus_days(-other.days)
            )
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    @overload
    def subtract(date: LocalDate, period: Period, /) -> LocalDate:
        """Subtracts the specified period from the date. Fields are subtracted in descending order of significance
        (years first, then months, and so on). Friendly alternative to ``-``.

        :param date: The date to subtract the period from.
        :param period: The period to subtract. Must not contain any (non-zero) time units.
        :return: The result of subtracting the given period from the date.
        """

    @staticmethod
    @overload
    def subtract(lhs: LocalDate, rhs: LocalDate, /) -> Period:
        """Subtracts one date from another, returning the result as a ``Period`` with units of years, months and days.

        This is simply a convenience method for calling ``Period.between(LocalDate, LocalDate)``.
        The calendar systems of the two dates must be the same.

        :param lhs: The date to subtract from.
        :param rhs: The date to subtract.
        :return: The result of subtracting one date from another.
        """

    @staticmethod
    def subtract(date: LocalDate, other: LocalDate | Period, /) -> LocalDate | Period:
        return date - other

    @overload
    def minus(self, period: Period, /) -> LocalDate:
        """Subtracts the specified period from this date. Fields are subtracted in descending order of significance
        (years first, then months, and so on). Fluent alternative to ``-``.

        :param period: The period to subtract. Must not contain any (non-zero) time units.
        :return: The result of subtracting the given period from this date.
        """

    @overload
    def minus(self, date: LocalDate, /) -> Period:
        """Subtracts the specified date from this date, returning the result as a ``Period`` with units of years, months
        and days. Fluent alternative to ``-``.

        The specified date must be in the same calendar system as this.

        :param date: The date to subtract from this.
        :return: The difference between the specified date and this one.
        """

    def minus(self, period: LocalDate | Period, /) -> LocalDate | Period:
        return self - period

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented
        return self.__year_month_day_calendar == other.__year_month_day_calendar

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented
        return not self == other

    def __lt__(self, other: LocalDate) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values in the same calendar can be compared",
        )
        return self.__trusted_compare_to(other) < 0

    def __le__(self, other: LocalDate) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values in the same calendar can be compared",
        )
        return self.__trusted_compare_to(other) <= 0

    def __gt__(self, other: LocalDate) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values in the same calendar can be compared",
        )
        return self.__trusted_compare_to(other) > 0

    def __ge__(self, other: LocalDate) -> bool:
        if not isinstance(other, LocalDate):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.__calendar_ordinal == other.__calendar_ordinal,
            "other",
            "Only values in the same calendar can be compared",
        )
        return self.__trusted_compare_to(other) >= 0

    def compare_to(self, other: LocalDate | None) -> int:
        if other is None:
            return 1
        if not isinstance(other, LocalDate):
            raise TypeError(f"{self.__class__.__name__} cannot be compared to {other.__class__.__name__}")
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

    @classmethod
    def max(cls, x: LocalDate, y: LocalDate) -> LocalDate:
        """Returns the later date of the given two.

        :param x: The first date to compare.
        :param y: The second date to compare.
        :raises ValueError: The two dates have different calendar systems.
        :return: The later date of x or y.
        """
        _Preconditions._check_argument(
            x.calendar == y.calendar, "y", "Only values with the same calendar system can be compared"
        )
        return max(x, y)

    @classmethod
    def min(cls, x: LocalDate, y: LocalDate) -> LocalDate:
        """Returns the earlier date of the given two.

        :param x: The first date to compare.
        :param y: The second date to compare.
        :raises ValueError: The two dates have different calendar systems.
        :return: The earlier date of x or y.
        """
        _Preconditions._check_argument(
            x.calendar == y.calendar, "y", "Only values with the same calendar system can be compared"
        )
        return min(x, y)

    def __hash__(self) -> int:
        """Returns a hash code for this local date.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this local date.
        """
        return hash(self.__year_month_day_calendar)

    def at_start_of_day_in_zone(self, zone: DateTimeZone) -> ZonedDateTime:
        """Resolves this local date into a ``ZonedDateTime`` in the given time zone representing the start of this date
        in the given zone.

        This is a convenience method for calling ``DateTimeZone.at_start_of_day(LocalDate)``.

        :param zone: The time zone to map this local date into
        :raises SkippedTimeError: The entire day was skipped due to a very large time zone transition. (This is
            extremely rare.)
        :return: The ``ZonedDateTime`` representing the earliest time on this date, in the given time zone.
        """
        _Preconditions._check_not_null(zone, "zone")
        return zone.at_start_of_day(self)

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
        """Returns a new LocalDate representing the current value with the given number of days added.

        This method does not try to maintain the month or year of the current value, so adding 3 days to a value of
        January 30th will result in a value of February 2nd.

        :param days: The number of days to add.
        :return: The current value plus the given number of days.
        """
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._days_field.add(self, days)

    def plus_weeks(self, weeks: int) -> LocalDate:
        """Returns a new LocalDate representing the current value with the given number of weeks added.

        :param weeks: The number of weeks to add.
        :return: The current value plus the given number of weeks.
        """
        from .fields._date_period_fields import _DatePeriodFields

        return _DatePeriodFields._weeks_field.add(self, weeks)

    def next(self, target_day_of_week: IsoDayOfWeek) -> LocalDate:
        """Returns the next ``LocalDate`` falling on the specified ``IsoDayOfWeek``.

        This is a strict "next" - if this date on already falls on the target day of the week, the returned value will
        be a week later.

        :param target_day_of_week: The ISO day of the week to return the next date of.
        :return: The next ``LocalDate`` falling on the specified day of the week.
        :raises RuntimeError: The underlying calendar doesn't use ISO days of the week.
        :raises ValueError: ``target_day_of_week`` is not a valid day of the week (Monday to Sunday).
        """
        if target_day_of_week < IsoDayOfWeek.MONDAY or target_day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(  # pragma: no cover
                f"target_day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]"
            )
        # This will throw the desired exception for calendars with different week systems.
        this_day = self.day_of_week
        difference = target_day_of_week - this_day
        if difference <= 0:
            difference += 7
        return self.plus_days(difference)

    def previous(self, target_day_of_week: IsoDayOfWeek) -> LocalDate:
        """Returns the previous ``LocalDate`` falling on the specified ``IsoDayOfWeek``.

        This is a strict "previous" - if this date on already falls on the target day of the week, the returned value
        will be a week earlier.

        :param target_day_of_week: The ISO day of the week to return the previous date of.
        :return: The previous ``LocalDate`` falling on the specified day of the week.
        :raises RuntimeError: The underlying calendar doesn't use ISO days of the week.
        :raises ValueError: ``target_day_of_week`` is not a valid day of the week (Monday to Sunday).
        """
        if target_day_of_week < IsoDayOfWeek.MONDAY or target_day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(  # pragma: no cover
                f"target_day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]"
            )
        # This will throw the desired exception for calendars with different week systems.
        this_day = self.day_of_week
        difference = target_day_of_week - this_day
        if difference >= 0:
            difference -= 7
        return self.plus_days(difference)

    def with_offset(self, offset: Offset) -> OffsetDate:
        """Returns an ``OffsetDate`` for this local date with the given offset.

        This method is purely a convenient alternative to calling the ``OffsetDate`` constructor directly.

        :param offset: The offset to apply.
        :return: The result of this date offset by the given amount.
        """
        from . import OffsetDate

        return OffsetDate(self, offset)

    def at(self, time: LocalTime) -> LocalDateTime:
        """Combines this ``LocalDate`` with the given ``LocalTime`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param time: The time to combine with this date.
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return self + time

    def with_date_adjuster(self, adjuster: Callable[[LocalDate], LocalDate]) -> LocalDate:
        """Returns this date, with the given adjuster applied to it.

        If the adjuster attempts to construct an invalid date (such as by trying to set a day-of-month of 30 in
        February), any exception thrown by that construction attempt will be propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted date.
        """
        return _Preconditions._check_not_null(adjuster, "adjuster")(self)

    def __iter__(self) -> Iterator[int]:
        """Deconstructs the current instance into its components.

        This enables instances of ``LocalDate`` to be unpacked into year, month
        and day, similar to the equivalent ``LocalDate.Deconstruct`` in Noda Time.

        :return: An iterator of integers representing the "year", "month" and "day" components of this date.
        """
        yield self.year
        yield self.month
        yield self.day

    # region Formatting

    def __repr__(self) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import LocalDatePattern

        return LocalDatePattern._bcl_support.format(self, None, CultureInfo.current_culture)

    def __format__(self, format_spec: str) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import LocalDatePattern

        return LocalDatePattern._bcl_support.format(self, format_spec, CultureInfo.current_culture)

    # endregion

    # region date conversions

    def to_date(self) -> datetime.date:
        """Converts this object to a ``datetime.date``.

        ``datetime.date`` uses the Gregorian calendar by definition, so the value is implicitly converted to the
        Gregorian calendar first. The result will be on the same physical day, but the values returned by the
        Year/Month/Day properties of the ``datetime.date`` may not match the Year/Month/Day properties of this value.

        :return: A ``datetime.date`` value equivalent to this one.
        """
        return datetime.date(1970, 1, 1) + datetime.timedelta(days=self._days_since_epoch)

    @classmethod
    def from_date(cls, date: datetime.date) -> LocalDate:
        """Constructs a ``LocalDate`` from a ``datetime.date``.

        :param date: The date to convert.
        :return: The ``LocalDate`` equivalent, which is always in the ISO calendar system.
        """
        days_since_epoch: int = (date - datetime.date(1970, 1, 1)).days
        return cls._ctor(days_since_epoch=days_since_epoch)

    # endregion
