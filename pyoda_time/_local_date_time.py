# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, final, overload

from ._calendar_system import CalendarSystem
from .utility._csharp_compatibility import _sealed, _to_ticks
from .utility._hash_code_helper import _hash_code_helper
from .utility._preconditions import _Preconditions
from .utility._tick_arithmetic import _TickArithmetic

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import DateTimeZone, Offset, OffsetDateTime, Period, ZonedDateTime
    from ._iso_day_of_week import IsoDayOfWeek
    from ._local_date import LocalDate
    from ._local_instant import _LocalInstant
    from ._local_time import LocalTime
    from .calendars import Era
    from .time_zones import ZoneLocalMappingResolver

__all__ = ["LocalDateTime"]


class _LocalDateTimeMeta(type):
    @property
    def max_iso_value(self) -> LocalDateTime:
        """The maximum (latest) date and time representable in the ISO calendar system.

        This is a nanosecond before midnight at the end of ``LocalDate.max_iso_value``.
        """
        from pyoda_time import LocalDate, LocalTime

        return LocalDate.max_iso_value + LocalTime.max_value

    @property
    def min_iso_value(self) -> LocalDateTime:
        """The minimum (earliest) date and time representable in the ISO calendar system.

        This is midnight at the start of ``LocalDate.min_iso_value``.
        """
        from pyoda_time import LocalDate, LocalTime

        return LocalDate.min_iso_value + LocalTime.min_value


@final
@_sealed
class LocalDateTime(metaclass=_LocalDateTimeMeta):
    """A date and time in a particular calendar system.

    A LocalDateTime value does not represent an instant on the global time line, because it has no associated time zone:
    "November 12th 2009 7pm, ISO calendar" occurred at different instants for different people around the world.

    This type defaults to using the ISO calendar system unless a different calendar system is specified.

    Values can freely be compared for equality: a value in a different calendar system is not equal to
    a value in a different calendar system. However, ordering comparisons fail with ``ValueError``;
    attempting to compare values in different calendars almost always indicates a bug in the calling code.

    The default value of this type is 0001-01-01T00:00:00 (midnight on January 1st, 1 C.E.) in the ISO calendar.
    """

    def __init__(
        self,
        year: int = 1,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        calendar: CalendarSystem = CalendarSystem.iso,
    ) -> None:
        """Initializes a new instance of the ``LocalDateTime`` class.

        :param year: The year. This is the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for
            example.
        :param month: The month of year.
        :param day: The day of month.
        :param hour: The hour.
        :param minute: The minute.
        :param second: The second.
        :param millisecond: The millisecond.
        :param calendar: The calendar.
        :raises ValueError: The parameters do not form a valid date and time.
        """
        from ._local_date import LocalDate
        from ._local_time import LocalTime

        self.__date: LocalDate = LocalDate(year=year, month=month, day=day, calendar=calendar)
        self.__time: LocalTime = LocalTime(hour=hour, minute=minute, second=second, millisecond=millisecond)

    @classmethod
    @overload
    def _ctor(cls, *, local_instant: _LocalInstant) -> LocalDateTime: ...

    @classmethod
    @overload
    def _ctor(cls, *, local_date: LocalDate, local_time: LocalTime) -> LocalDateTime: ...

    @classmethod
    def _ctor(
        cls,
        *,
        local_instant: _LocalInstant | None = None,
        local_date: LocalDate | None = None,
        local_time: LocalTime | None = None,
    ) -> LocalDateTime:
        from ._local_date import LocalDate
        from ._local_time import LocalTime

        self = super().__new__(cls)
        if local_instant is not None and local_time is None and local_date is None:
            self.__date = LocalDate._ctor(days_since_epoch=local_instant._days_since_epoch)
            self.__time = LocalTime._ctor(nanoseconds=local_instant._nanosecond_of_day)
        elif local_instant is None and local_date is not None and local_time is not None:
            self.__date = local_date
            self.__time = local_time
        else:
            raise TypeError
        return self

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system associated with this local date and time."""
        return self.__date.calendar

    @property
    def year(self) -> int:
        """The year of this local date and time.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.
        """
        return self.__date.year

    @property
    def year_of_era(self) -> int:
        """The year of this local date and time within its era."""
        return self.__date.year_of_era

    @property
    def era(self) -> Era:
        """The era of this local date and time."""
        return self.__date.era

    @property
    def month(self) -> int:
        """The month of this local date and time within the year."""
        return self.__date.month

    @property
    def day_of_year(self) -> int:
        """The day of this local date and time within the year."""
        return self.__date.day_of_year

    @property
    def day(self) -> int:
        """The day of this local date and time within the month."""
        return self.__date.day

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """The week day of this local date and time expressed as an ``IsoDayOfWeek``."""
        return self.__date.day_of_week

    @property
    def hour(self) -> int:
        """The hour of day of this local date and time, in the range 0 to 23 inclusive."""
        return self.__time.hour

    @property
    def clock_hour_of_half_day(self) -> int:
        """The hour of the half-day of this local date and time, in the range 1 to 12 inclusive."""
        return self.__time.clock_hour_of_half_day

    @property
    def minute(self) -> int:
        """The minute of this local date and time, in the range 0 to 59 inclusive."""
        return self.__time.minute

    @property
    def second(self) -> int:
        """The second of this local date and time within the minute, in the range 0 to 59 inclusive."""
        return self.__time.second

    @property
    def millisecond(self) -> int:
        """The millisecond of this local date and time within the second, in the range 0 to 999 inclusive."""
        return self.__time.millisecond

    @property
    def microsecond(self) -> int:
        """The microsecond of this local date and time within the second, in the range 0 to 999,999 inclusive."""
        return self.__time.microsecond

    @property
    def tick_of_second(self) -> int:
        """The tick of this local time within the second, in the range 0 to 9,999,999 inclusive."""
        return self.__time.tick_of_second

    @property
    def tick_of_day(self) -> int:
        """The tick of this local date and time within the day, in the range 0 to 863,999,999,999 inclusive."""
        return self.__time.tick_of_day

    @property
    def nanosecond_of_second(self) -> int:
        """The nanosecond of this local time within the second, in the range 0 to 999,999,999 inclusive."""
        return self.__time.nanosecond_of_second

    @property
    def nanosecond_of_day(self) -> int:
        """The nanosecond of this local date and time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__time.nanosecond_of_day

    @property
    def time_of_day(self) -> LocalTime:
        """The time portion of this local date and time as a ``LocalTime``."""
        return self.__time

    @property
    def date(self) -> LocalDate:
        """The date portion of this local date and time as a ``LocalDate``."""
        return self.__date

    def to_naive_datetime(self) -> datetime.datetime:
        """Constructs a naive ``datetime.datetime`` from this value.

        If the date and time is not on a microsecond boundary (the unit of granularity of ``datetime.datetime``) the
        value will be truncated towards the start of time.

        ``datetime.datetime`` uses the Gregorian calendar by definition, so the value is implicitly converted
        to the Gregorian calendar first. The result will be on the same physical day,
        but the values returned by the Year/Month/Day properties of the ``datetime.datetime`` may not
        match the Year/Month/Day properties of this value.

        :return: A ``datetime.datetime`` for the same date and time as this value.
        """
        # Implementation note:
        # This function is intended to be roughly equivalent to ``LocalDateTime.ToDateTimeUnspecified()`` in Noda Time.
        # But the way in which they are implemented is quite different.

        gregorian = self.with_calendar(CalendarSystem.gregorian)

        # In Noda Time, they measure the ticks since the BCL epoch here and throw if < 0.
        # This is a bit simpler...
        if gregorian.year <= datetime.datetime.min.year:
            raise RuntimeError("LocalDateTime out of range of datetime")

        return datetime.datetime(
            year=gregorian.year,
            month=gregorian.month,
            day=gregorian.day,
            hour=gregorian.hour,
            minute=gregorian.minute,
            second=gregorian.second,
            microsecond=gregorian.microsecond,
        )

    def _to_local_instant(self) -> _LocalInstant:
        from ._local_instant import _LocalInstant

        return _LocalInstant._ctor(days=self.date._days_since_epoch, nano_of_day=self.__time.nanosecond_of_day)

    @classmethod
    def from_naive_datetime(cls, dt: datetime.datetime, calendar: CalendarSystem = CalendarSystem.iso) -> LocalDateTime:
        """Converts a timezone-naive ``datetime.datetime`` to a ``LocalDateTime``, optionally in a specified calendar.

        :param dt: Timezone-naive datetime to convert into a Pyoda Time local date and time.
        :param calendar: The calendar system to convert into.
        :return: A new ``LocalDateTime`` with the same values as the specified ``datetime.datetime``.
        :raises ValueError: If ``dt`` is a timezone-aware ``datetime.datetime``.
        """
        # Unlike Noda Time, we need to verify the tzinfo of the datetime.
        # In C#, DateTime doesn't have this...
        # They have DateTimeKind, but that is irrelevant.
        # What is important is that it is a DateTime, not a DateTimeOffset.

        _Preconditions._check_argument(
            expession=dt.tzinfo is None,
            parameter="datetime",
            message="Invalid datetime.tzinfo for LocalDateTime.from_datetime_utc",
        )
        from pyoda_time._local_date import LocalDate
        from pyoda_time._local_time import LocalTime
        from pyoda_time._pyoda_constants import PyodaConstants

        days, tick_of_day = _TickArithmetic.ticks_to_days_and_tick_of_day(_to_ticks(dt))
        days -= PyodaConstants._BCL_DAYS_AT_UNIX_EPOCH
        return cls._ctor(
            local_date=LocalDate._ctor(days_since_epoch=days, calendar=calendar),
            local_time=LocalTime._ctor(nanoseconds=tick_of_day * PyodaConstants.NANOSECONDS_PER_TICK),
        )

    # region Implementation of IEquatable<LocalDateTime>

    def equals(self, other: LocalDateTime) -> bool:
        """Indicates whether the current object is equal to another object of the same type. See the type documentation
        for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: True if the current object is equal to the ``other`` parameter; otherwise, False.
        """
        return self == other

    # endregion

    # region Operators

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality).

        See the type documentation for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is equal to the ``other`` parameter; otherwise, ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented
        return self.__date == other.__date and self.__time == other.__time

    def __ne__(self, other: object) -> bool:
        """Implements the operator != (inequality).

        See the type documentation for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is not equal to the ``other`` parameter; otherwise, ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented
        return not (self == other)

    def __lt__(self, other: LocalDateTime) -> bool:
        """Compares two LocalDateTime values to see if the left one is strictly earlier than the right one.

        See the type documentation for a description of ordering semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is equal to the ``other`` parameter; otherwise, ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) < 0

    def __le__(self, other: LocalDateTime) -> bool:
        """Compares two LocalDateTime values to see if the left one is earlier than or equal to the right one.

        See the type documentation for a description of ordering semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is earlier than or equal to the ``other`` parameter; otherwise,
            ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) <= 0

    def __gt__(self, other: LocalDateTime) -> bool:
        """Compares two LocalDateTime values to see if the left one is later than the right one.

        See the type documentation for a description of ordering semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is strictly later than the ``other`` parameter; otherwise, ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) > 0

    def __ge__(self, other: LocalDateTime) -> bool:
        """Compares two LocalDateTime values to see if the left one is later than or equal to the right one.

        See the type documentation for a description of ordering semantics.

        :param other: An object to compare with this object.
        :return: ``True`` if the current object is later than or equal to the ``other`` parameter; otherwise, ``False``.
        """
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) >= 0

    def compare_to(self, other: LocalDateTime | None) -> int:
        """Indicates whether this date/time is earlier, later or the same as another one.

        See the type documentation for a description of ordering semantics.

        :param other: The other local date/time to compare with this value.
        :raises ValueError: The calendar system of ``other`` is not the same as the calendar system of this value.
        :return: A value less than zero if this date/time is earlier than ``other``; zero if this date/time is the same
            as ``other``; a value greater than zero if this value is later than ``other``.
        """
        if other is None:
            return 1
        if not isinstance(other, LocalDateTime):
            raise TypeError(f"{self.__class__.__name__} cannot be compared to {other.__class__.__name__}")
        # This will check calendars...
        date_comparison = self.__date.compare_to(other.__date)
        if date_comparison != 0:
            return date_comparison
        return self.__time.compare_to(other.__time)

    def __add__(self, other: Period) -> LocalDateTime:
        """Adds a period to a local date/time.

        Fields are added in descending order of significance (years first, then months, and so on).

        This is a convenience operator over the ``plus`` method.

        :param other: Period to add
        :return: The resulting local date and time
        """
        from . import Period

        if isinstance(other, Period):
            return self.plus(other)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    def add(local_date_time: LocalDateTime, period: Period) -> LocalDateTime:
        """Add the specified period to the date and time.

        Fields are added in descending order of significance (years first, then months, and so on).

        Friendly alternative to ``+``.

        :param local_date_time: Initial local date and time
        :param period: Period to add
        :return: The resulting local date and time
        """
        return local_date_time.plus(period)

    def plus(self, period: Period) -> LocalDateTime:
        """Adds a period to this local date/time.

        Fields are added in descending order of significance (years first, then months, and so on).

        :param period: Period to add
        :return: The resulting local date and time
        """
        _Preconditions._check_not_null(period, "period")
        extra_days = 0
        time = self.time_of_day
        from .fields._time_period_field import _TimePeriodField

        time, plus_extra_days = _TimePeriodField._hours._add_local_time_with_extra_days(time, period.hours)
        extra_days += plus_extra_days
        time, plus_extra_days = _TimePeriodField._minutes._add_local_time_with_extra_days(time, period.minutes)
        extra_days += plus_extra_days
        time, plus_extra_days = _TimePeriodField._seconds._add_local_time_with_extra_days(time, period.seconds)
        extra_days += plus_extra_days
        time, plus_extra_days = _TimePeriodField._milliseconds._add_local_time_with_extra_days(
            time, period.milliseconds
        )
        extra_days += plus_extra_days
        time, plus_extra_days = _TimePeriodField._ticks._add_local_time_with_extra_days(time, period.ticks)
        extra_days += plus_extra_days
        time, plus_extra_days = _TimePeriodField._nanoseconds._add_local_time_with_extra_days(time, period.nanoseconds)
        extra_days += plus_extra_days
        date = (
            self.date.plus_years(period.years)
            .plus_months(period.months)
            .plus_weeks(period.weeks)
            .plus_days(period.days + extra_days)
        )
        return LocalDateTime._ctor(local_date=date, local_time=time)

    @overload
    def __sub__(self, other: Period) -> LocalDateTime:
        """Subtracts a period from a local date/time.

        Fields are subtracted in descending order of significance (years first, then months, and so on).

        This is a convenience operator over the ``minus(Period)`` method.

        :param other: Period to subtract
        :return: The resulting local date and time
        """

    @overload
    def __sub__(self, other: LocalDateTime) -> Period:
        """Subtracts one date/time from another, returning the result as a ``Period``.

        This is simply a convenience operator for calling ``Period.between(LocalDateTime, LocalDateTime)``.

        The calendar systems of the two date/times must be the same.

        :param other: The date/time to subtract
        :return: The result of subtracting one date/time from another.
        """

    def __sub__(self, other: Period | LocalDateTime) -> LocalDateTime | Period:
        from . import Period

        if isinstance(other, Period):
            return self.minus(other)
        if isinstance(other, LocalDateTime):
            return Period.between(other, self)
        return NotImplemented  # type: ignore[unreachable]

    @staticmethod
    @overload
    def subtract(local_date_time: LocalDateTime, period: Period, /) -> LocalDateTime:
        """Subtracts a period from a local date/time.

        Friendly alternative to ``-``.

        :param local_date_time: Initial local date and time
        :param period: Period to subtract
        :return: The resulting local date and time
        """

    @staticmethod
    @overload
    def subtract(lhs: LocalDateTime, rhs: LocalDateTime, /) -> Period:
        """Subtracts one date/time from another, returning the result as a ``Period``.

        This is simply a convenience method for calling ``Period.between(LocalDateTime, LocalDateTime)``.

        The calendar systems of the two date/times must be the same.

        :param lhs: The date/time to subtract from
        :param rhs: The date/time to subtract
        :return: The result of subtracting one date/time from another.
        """

    @staticmethod
    def subtract(local_date_time: LocalDateTime, other: Period | LocalDateTime, /) -> LocalDateTime | Period:
        return local_date_time.minus(other)

    @overload
    def minus(self, period: Period, /) -> LocalDateTime:
        """Subtracts a period from a local date/time.

        Fields are subtracted in descending order of significance (years first, then months, and so on.)

        :param period: Period to subtract
        :return: The resulting local date and time
        """

    @overload
    def minus(self, local_date_time: LocalDateTime, /) -> Period:
        """Subtracts the specified date/time from this date/time, returning the result as a ``Period``.

        Fluent alternative to ``-``.

        The specified date/time must be in the same calendar system as this.

        :param local_date_time: The date/time to subtract from this
        :return: The difference between the specified date/time and this one
        """

    def minus(self, other: Period | LocalDateTime, /) -> LocalDateTime | Period:
        from pyoda_time import Period

        if isinstance(other, Period):
            _Preconditions._check_not_null(other, "period")
            from .fields._time_period_field import _TimePeriodField

            extra_days = 0
            time = self.time_of_day
            time, plus_extra_days = _TimePeriodField._hours._add_local_time_with_extra_days(time, -other.hours)
            extra_days += plus_extra_days
            time, plus_extra_days = _TimePeriodField._minutes._add_local_time_with_extra_days(time, -other.minutes)
            extra_days += plus_extra_days
            time, plus_extra_days = _TimePeriodField._seconds._add_local_time_with_extra_days(time, -other.seconds)
            extra_days += plus_extra_days
            time, plus_extra_days = _TimePeriodField._milliseconds._add_local_time_with_extra_days(
                time, -other.milliseconds
            )
            extra_days += plus_extra_days
            time, plus_extra_days = _TimePeriodField._ticks._add_local_time_with_extra_days(time, -other.ticks)
            extra_days += plus_extra_days
            time, plus_extra_days = _TimePeriodField._nanoseconds._add_local_time_with_extra_days(
                time, -other.nanoseconds
            )
            extra_days += plus_extra_days
            date = (
                self.date.plus_years(-other.years)
                .plus_months(-other.months)
                .plus_weeks(-other.weeks)
                .plus_days(extra_days - other.days)
            )
            return LocalDateTime._ctor(local_date=date, local_time=time)
        return self - other

    # endregion

    # region object overrides

    # TODO: Equals(object? obj)

    def __hash__(self) -> int:
        """Returns a hash code for this instance.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this instance, suitable for use in hashing algorithms and data structures like a hash
            table.
        """
        return _hash_code_helper(self.__date, self.__time, self.calendar)

    # endregion

    def with_date_adjuster(self, adjuster: Callable[[LocalDate], LocalDate]) -> LocalDateTime:
        """Returns this date/time, with the given date adjuster applied to it, maintaining the existing time of day.

        If the adjuster attempts to construct an invalid date (such as by trying to set a day-of-month of 30 in
        February), any exception thrown by that construction attempt will be propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted date/time.
        """
        return self.__date.with_date_adjuster(adjuster=adjuster) + self.__time

    def with_time_adjuster(self, adjuster: Callable[[LocalTime], LocalTime]) -> LocalDateTime:
        """Returns this date/time, with the given time adjuster applied to it, maintaining the existing date.

        If the adjuster attempts to construct an invalid time, any exception thrown by that construction attempt will be
        propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted date/time.
        """
        return self.__date + self.__time.with_time_adjuster(adjuster=adjuster)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDateTime:
        """Creates a new LocalDateTime representing the same physical date and time, but in a different calendar. The
        returned LocalDateTime is likely to have different date field values to this one. For example, January 1st 1970
        in the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this local date to.
        :return: The converted LocalDateTime.
        """
        _Preconditions._check_not_null(calendar, "calendar")
        return LocalDateTime._ctor(local_date=self.date.with_calendar(calendar), local_time=self.__time)

    def plus_years(self, years: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of years added.

        If the resulting date is invalid, lower fields (typically the day of month) are reduced to find a valid value.
        For example, adding one year to February 29th 2012 will return February 28th 2013; subtracting one year from
        February 29th 2012 will return February 28th 2011.

        :param years: The number of years to add
        :return: The current value plus the given number of years.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_years(years), local_time=self.__time)

    def plus_months(self, months: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of months added.

        This method does not try to maintain the year of the current value, so adding four months to a value in October
        will result in a value in the following February.

        If the resulting date is invalid, the day of month is reduced to find a valid value. For example, adding one
        month to January 30th 2011 will return February 28th 2011; subtracting one month from March 30th 2011 will
        return February 28th 2011.

        :param months: The number of months to add
        :return: The current value plus the given number of months.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_months(months), local_time=self.__time)

    def plus_days(self, days: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of days added.

        This method does not try to maintain the month or year of the current value, so adding 3 days to a value on
        January 30th will result in a value on February 2nd.

        :param days: The number of days to add
        :return: The current value plus the given number of days.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_days(days), local_time=self.__time)

    def plus_weeks(self, weeks: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of weeks added.

        :param weeks: The number of weeks to add
        :return: The current value plus the given number of weeks.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_weeks(weeks), local_time=self.__time)

    def plus_hours(self, hours: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of hours added.

        :param hours: The number of hours to add
        :return: The current value plus the given number of hours.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._hours._add_local_date_time(self, hours)

    def plus_minutes(self, minutes: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of minutes added.

        :param minutes: The number of minutes to add
        :return: The current value plus the given number of minutes.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._minutes._add_local_date_time(self, minutes)

    def plus_seconds(self, seconds: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of seconds added.

        :param seconds: The number of seconds to add
        :return: The current value plus the given number of seconds.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._seconds._add_local_date_time(self, seconds)

    def plus_milliseconds(self, milliseconds: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of milliseconds added.

        :param milliseconds: The number of milliseconds to add
        :return: The current value plus the given number of milliseconds.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._milliseconds._add_local_date_time(self, milliseconds)

    def plus_ticks(self, ticks: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of ticks added.

        :param ticks: The number of ticks to add
        :return: The current value plus the given number of ticks.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._ticks._add_local_date_time(self, ticks)

    def plus_nanoseconds(self, nanoseconds: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of nanoseconds added.

        :param nanoseconds: The number of nanoseconds to add
        :return: The current value plus the given number of nanoseconds.
        """
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._nanoseconds._add_local_date_time(self, nanoseconds)

    def next(self, target_day_of_week: IsoDayOfWeek) -> LocalDateTime:
        """Returns the next ``LocalDateTime`` falling on the specified ``IsoDayOfWeek``, at the same time of day as this
        value.

        This is a strict "next" - if this value on already falls on the target day of the week, the returned value will
        be a week later.

        :param target_day_of_week: The ISO day of the week to return the next date of.
        :return: The next ``LocalDateTime`` falling on the specified day of the week.
        :raises RuntimeError: The underlying calendar doesn't use ISO days of the week.
        :raises ValueError: ``target_day_of_week`` is not a valid day of the week (Monday to Sunday).
        """
        return LocalDateTime._ctor(
            local_date=self.__date.next(target_day_of_week=target_day_of_week), local_time=self.__time
        )

    def previous(self, target_day_of_week: IsoDayOfWeek) -> LocalDateTime:
        """Returns the previous ``LocalDateTime`` falling on the specified ``IsoDayOfWeek``, at the same time of day as
        this value.

        This is a strict "previous" - if this value on already falls on the target day of the week, the returned value
        will be a week earlier.

        :param target_day_of_week: The ISO day of the week to return the previous date of.
        :return: The previous ``LocalDateTime`` falling on the specified day of the week.
        :raises RuntimeError: The underlying calendar doesn't use ISO days of the week.
        :raises ValueError: ``target_day_of_week`` is not a valid day of the week (Monday to Sunday).
        """
        return LocalDateTime._ctor(
            local_date=self.date.previous(target_day_of_week=target_day_of_week), local_time=self.__time
        )

    def with_offset(self, offset: Offset) -> OffsetDateTime:
        """Returns an ``OffsetDateTime`` for this local date/time with the given offset.

        This method is purely a convenient alternative to calling the ``OffsetDateTime`` constructor directly.

        :param offset: The offset to apply.
        :return: The result of this local date/time offset by the given amount.
        """
        from ._offset_date_time import OffsetDateTime
        from ._offset_time import OffsetTime

        return OffsetDateTime._ctor(local_date=self.__date, offset_time=OffsetTime(self.__time, offset))

    def in_utc(self) -> ZonedDateTime:
        """Returns the mapping of this local date/time within ``DateTimeZone.Utc``.

        As UTC is a fixed time zone, there is no chance that this local date/time is ambiguous or skipped.

        :return: The result of mapping this local date/time in UTC.
        """
        # TODO: Check if the use of local imports are really necessary...
        from pyoda_time._offset_time import OffsetTime

        from ._date_time_zone import DateTimeZone
        from ._offset_date_time import OffsetDateTime
        from ._zoned_date_time import ZonedDateTime

        # Use the internal constructors to avoid validation. We know it will be fine.
        return ZonedDateTime._ctor(
            offset_date_time=OffsetDateTime._ctor(
                local_date=self.date,
                offset_time=OffsetTime._ctor(nanosecond_of_day_zero_offset=self.__time.nanosecond_of_day),
            ),
            zone=DateTimeZone.utc,
        )

    def in_zone_strictly(self, zone: DateTimeZone) -> ZonedDateTime:
        """Returns the mapping of this local date/time within the given ``DateTimeZone``, with "strict" rules applied
        such that an exception is thrown if either the mapping is ambiguous or the time is skipped.

        See ``in_zone_leniently`` and ``in_zone`` for alternative ways to map a local time to a specific instant.
        This is solely a convenience method for calling ``DateTimeZone.at_strictly``.

        :param zone: The time zone in which to map this local date/time.
        :exception SkippedTimeError: This local date/time is skipped in the given time zone.
        :exception AmbiguousTimeError: This local date/time is ambiguous in the given time zone.
        :return: The result of mapping this local date/time in the given time zone.
        """
        _Preconditions._check_not_null(zone, "zone")
        return zone.at_strictly(self)

    def in_zone_leniently(self, zone: DateTimeZone) -> ZonedDateTime:
        """Returns the mapping of this local date/time within the given ``DateTimeZone``, with "lenient" rules applied
        such that ambiguous values map to the earlier of the alternatives, and "skipped" values are shifted forward by
        the duration of the "gap".

        See ``in_zone_strictly`` and ``in_zone`` for alternative ways to map a local time to a specific instant.
        This is solely a convenience method for calling ``DateTimeZone.at_leniently``.

        :param zone: The time zone in which to map this local date/time.
        :return: The result of mapping this local date/time in the given time zone.
        """
        _Preconditions._check_not_null(zone, "zone")
        return zone.at_leniently(self)

    def in_zone(self, zone: DateTimeZone, resolver: ZoneLocalMappingResolver) -> ZonedDateTime:
        """Resolves this local date and time into a ``ZonedDateTime`` in the given time zone, following the given
        ``ZoneLocalMappingResolver`` to handle ambiguity and skipped times.

        See ``in_zone_strictly`` and ``in_zone_leniently`` for alternative ways to map a local time to a specific
        instant.

        This is a convenience method for calling
        ``DateTimeZone.resolve_local(LocalDateTime, ZoneLocalMappingResolver)``.

        :param zone: The time zone in which to map this local date and time into.
        :param resolver: The resolver to apply to the mapping.
        :return: The result of resolving the mapping.
        """
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(resolver, "resolver")
        return zone.resolve_local(self, resolver)

    # TODO: Deconstruct

    @staticmethod
    def max(x: LocalDateTime, y: LocalDateTime) -> LocalDateTime:
        """Returns the later date/time of the given two.

        :param x: The first date/time to compare.
        :param y: The second date/time to compare.
        :exception ValueError: The two date/times have different calendar systems.
        :return: The later date/time of ``x`` or ``y``.
        """
        return max(x, y)

    # TODO: Deconstruct

    @staticmethod
    def min(x: LocalDateTime, y: LocalDateTime) -> LocalDateTime:
        """Returns the earlier date/time of the given two.

        :param x: The first date/time to compare.
        :param y: The second date/time to compare.
        :exception ValueError: The two date/times have different calendar systems.
        :return: The earlier date/time of ``x`` or ``y``.
        """
        return min(x, y)

    # region Formatting

    def __repr__(self) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import LocalDateTimePattern

        return LocalDateTimePattern._bcl_support.format(self, None, CultureInfo.current_culture)

    def __format__(self, format_spec: str) -> str:
        from ._compatibility._culture_info import CultureInfo
        from .text import LocalDateTimePattern

        return LocalDateTimePattern._bcl_support.format(self, format_spec, CultureInfo.current_culture)

    # endregion
