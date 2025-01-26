# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, final, overload

from ._calendar_system import CalendarSystem
from .utility._csharp_compatibility import _sealed, _to_ticks
from .utility._preconditions import _Preconditions
from .utility._tick_arithmetic import _TickArithmetic

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import Offset, OffsetDateTime, Period, ZonedDateTime
    from ._iso_day_of_week import IsoDayOfWeek
    from ._local_date import LocalDate
    from ._local_instant import _LocalInstant
    from ._local_time import LocalTime
    from .calendars import Era

__all__ = ["LocalDateTime"]


class _LocalDateTimeMeta(type):
    pass


@final
@_sealed
class LocalDateTime(metaclass=_LocalDateTimeMeta):
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

        self.__date = LocalDate(year=year, month=month, day=day, calendar=calendar)
        self.__time = LocalTime(hour=hour, minute=minute, second=second, millisecond=millisecond)

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
        return LocalDateTime._ctor(local_date=self.__date.plus_days(days), local_time=self.__time)

    def plus_weeks(self, weeks: int) -> LocalDateTime:
        return LocalDateTime._ctor(local_date=self.__date.plus_weeks(weeks), local_time=self.__time)

    def plus_hours(self, hours: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._hours._add_local_date_time(self, hours)

    def plus_minutes(self, minutes: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._minutes._add_local_date_time(self, minutes)

    def plus_seconds(self, seconds: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._seconds._add_local_date_time(self, seconds)

    def plus_milliseconds(self, milliseconds: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._milliseconds._add_local_date_time(self, milliseconds)

    def plus_ticks(self, ticks: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._ticks._add_local_date_time(self, ticks)

    def plus_nanoseconds(self, nanoseconds: int) -> LocalDateTime:
        from .fields._time_period_field import _TimePeriodField

        return _TimePeriodField._nanoseconds._add_local_date_time(self, nanoseconds)

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
        if not isinstance(other, LocalDateTime):
            return NotImplemented
        return self.__date == other.__date and self.__time == other.__time

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, LocalDateTime):
            return NotImplemented
        return not (self == other)

    def __lt__(self, other: LocalDateTime) -> bool:
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) < 0

    def __le__(self, other: LocalDateTime) -> bool:
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) <= 0

    def __gt__(self, other: LocalDateTime) -> bool:
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) > 0

    def __ge__(self, other: LocalDateTime) -> bool:
        if not isinstance(other, LocalDateTime):
            return NotImplemented  # type: ignore[unreachable]
        _Preconditions._check_argument(
            self.calendar == other.calendar, "other", "Only values in the same calendar can be compared"
        )
        return self.compare_to(other) >= 0

    def compare_to(self, other: LocalDateTime | None) -> int:
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
        from . import Period

        if isinstance(other, Period):
            return self.plus(other)
        return NotImplemented  # type: ignore[unreachable]

    def plus(self, period: Period) -> LocalDateTime:
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

    # endregion

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
