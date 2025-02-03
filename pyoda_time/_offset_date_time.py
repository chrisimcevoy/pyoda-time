# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, overload

from ._calendar_system import CalendarSystem
from ._duration import Duration
from ._local_date_time import LocalDateTime
from ._offset import Offset
from ._pyoda_constants import PyodaConstants
from ._zoned_date_time import ZonedDateTime
from .utility._hash_code_helper import _hash_code_helper
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable

    from . import DateTimeZone, IsoDayOfWeek, LocalDate, LocalTime, OffsetDate, OffsetTime
    from ._instant import Instant
    from ._year_month_day import _YearMonthDay
    from .calendars import Era


__all__ = ["OffsetDateTime"]


class OffsetDateTime:
    """A local date and time in a particular calendar system, combined with an offset from UTC.

    This is broadly similar to an aware ``datetime`` with a fixed-offset ``timezone``.

    Equality is defined in a component-wise fashion: two values are the same if they represent equal date/time values
    (including being in the same calendar) and equal offsets from UTC.

    Ordering between offset date/time values has no natural definition; see ``comparer`` for built-in comparers.

    A value of this type unambiguously represents both a local time and an instant on the timeline,
    but does not have a well-defined time zone. This means you cannot reliably know what the local
    time would be five minutes later, for example. While this doesn't sound terribly useful, it's very common
    in text representations.

    The default value of this type is 0001-01-01T00:00:00Z (midnight on January 1st, 1 C.E. with a UTC offset of 0) in
    the ISO calendar.
    """

    def __init__(self, local_date_time: LocalDateTime = LocalDateTime(), offset: Offset = Offset()) -> None:
        from . import OffsetTime

        self.__local_date = local_date_time.date
        self.__offset_time = OffsetTime._ctor(
            nanosecond_of_day=local_date_time.nanosecond_of_day, offset_seconds=offset.seconds
        )

    @classmethod
    @overload
    def _ctor(cls, *, local_date: LocalDate, offset_time: OffsetTime) -> OffsetDateTime: ...

    @classmethod
    @overload
    def _ctor(cls, *, instant: Instant, offset: Offset) -> OffsetDateTime: ...

    @classmethod
    @overload
    def _ctor(cls, *, instant: Instant, offset: Offset, calendar: CalendarSystem) -> OffsetDateTime: ...

    @classmethod
    def _ctor(
        cls,
        *,
        local_date: LocalDate | None = None,
        offset_time: OffsetTime | None = None,
        instant: Instant | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> OffsetDateTime:
        from . import LocalDate, OffsetTime

        if instant is not None and offset is not None:
            days = instant._days_since_epoch
            nano_of_day = instant._nanosecond_of_day + offset.nanoseconds
            if nano_of_day >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nano_of_day -= PyodaConstants.NANOSECONDS_PER_DAY
            elif nano_of_day < 0:
                days -= 1
                nano_of_day += PyodaConstants.NANOSECONDS_PER_DAY
            local_date = (
                LocalDate._ctor(days_since_epoch=days)
                if calendar is None
                else LocalDate._ctor(days_since_epoch=days, calendar=calendar)
            )
            offset_time = OffsetTime._ctor(nanosecond_of_day=nano_of_day, offset_seconds=offset.seconds)
        if local_date is not None and offset_time is not None:
            self = super().__new__(cls)
            self.__local_date = local_date
            self.__offset_time = offset_time
            return self
        raise TypeError

    @property
    def calendar(self) -> CalendarSystem:
        """Gets the calendar system associated with this offset date and time.

        :return: The calendar system associated with this offset date and time.
        """
        return self.__local_date.calendar

    @property
    def year(self) -> int:
        """Gets the year of this offset date and time.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.

        :return: The year of this offset date and time.
        """
        return self.__local_date.year

    @property
    def month(self) -> int:
        """Gets the month of this offset date and time within the year.

        :return: The month of this offset date and time within the year.
        """
        return self.__local_date.month

    @property
    def day(self) -> int:
        """Gets the day of this offset date and time within the month.

        :return: The day of this offset date and time within the month.
        """
        return self.__local_date.day

    @property
    def _year_month_day(self) -> _YearMonthDay:
        return self.__local_date._year_month_day

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """Gets the week day of this offset date and time expressed as an ``IsoDayOfWeek``.

        :return: The week day of this offset date and time expressed as an ``IsoDayOfWeek``.
        """
        return self.__local_date.day_of_week

    @property
    def year_of_era(self) -> int:
        """Gets the year of this offset date and time within the era.

        :return: The year of this offset date and time within the era.
        """
        return self.__local_date.year_of_era

    @property
    def era(self) -> Era:
        """Gets the era of this offset date and time.

        :return: The era of this offset date and time.
        """
        return self.__local_date.era

    @property
    def day_of_year(self) -> int:
        """Gets the day of this offset date and time within the year.

        :return: The day of this offset date and time within the year.
        """
        return self.__local_date.day_of_year

    @property
    def hour(self) -> int:
        """Gets the hour of day of this offset date and time, in the range 0 to 23 inclusive.

        :return: The hour of day of this offset date and time, in the range 0 to 23 inclusive.
        """
        return self.__offset_time.hour

    @property
    def clock_hour_of_half_day(self) -> int:
        """Gets the hour of the half-day of this offset date and time, in the range 1 to 12 inclusive.

        :return: The hour of the half-day of this offset date and time, in the range 1 to 12 inclusive.
        """
        return self.__offset_time.clock_hour_of_half_day

    @property
    def minute(self) -> int:
        """Gets the minute of this offset date and time, in the range 0 to 59 inclusive.

        :return: The minute of this offset date and time, in the range 0 to 59 inclusive.
        """
        return self.__offset_time.minute

    @property
    def second(self) -> int:
        """Gets the second of this offset date and time within the minute, in the range 0 to 59 inclusive.

        :return: The second of this offset date and time within the minute, in the range 0 to 59 inclusive.
        """
        return self.__offset_time.second

    @property
    def millisecond(self) -> int:
        """Gets the millisecond of this offset date and time within the second, in the range 0 to 999 inclusive.

        :return: The millisecond of this offset date and time within the second, in the range 0 to 999 inclusive.
        """
        return self.__offset_time.millisecond

    @property
    def tick_of_second(self) -> int:
        """Gets the tick of this offset date and time within the second, in the range 0 to 9,999,999 inclusive.

        :return: The tick of this offset date and time within the second, in the range 0 to 9,999,999 inclusive.
        """
        return self.__offset_time.tick_of_second

    @property
    def tick_of_day(self) -> int:
        """Gets the tick of this offset date and time within the day, in the range 0 to 863,999,999,999 inclusive.

        :return: The tick of this offset date and time within the day, in the range 0 to 863,999,999,999 inclusive.
        """
        return self.__offset_time.tick_of_day

    @property
    def nanosecond_of_second(self) -> int:
        """Gets the nanosecond of this offset date and time within the second, in the range 0 to 999,999,999 inclusive.

        :return: The nanosecond of this offset date and time within the second, in the range 0 to 999,999,999 inclusive.
        """
        return self.__offset_time.nanosecond_of_second

    @property
    def nanosecond_of_day(self) -> int:
        """Gets the nanosecond of this offset date and time within the day, in the range 0 to 86,399,999,999,999
        inclusive.

        :return: The nanosecond of this offset date and time within the day, in the range 0 to 86,399,999,999,999
            inclusive.
        """
        return self.__offset_time.nanosecond_of_day

    @property
    def local_date_time(self) -> LocalDateTime:
        """Returns the local date and time represented within this offset date and time.

        :return: The local date and time represented within this offset date and time.
        """
        from . import LocalDateTime

        return LocalDateTime._ctor(local_date=self.date, local_time=self.time_of_day)

    @property
    def date(self) -> LocalDate:
        """Gets the local date represented by this offset date and time.

        The returned `LocalDate` will have the same calendar system and return the same values for each of the
        date-based calendar properties (Year, MonthOfYear and so on), but will not have any offset information.

        :return: The local date represented by this offset date and time.
        """
        return self.__local_date

    @property
    def time_of_day(self) -> LocalTime:
        """Gets the time portion of this offset date and time.

        The returned `LocalTime` will return the same values for each of the time-based properties (Hour, Minute and
        so on), but will not have any offset information.

        :return: The time portion of this offset date and time.
        """
        from . import LocalTime

        return LocalTime._ctor(nanoseconds=self.nanosecond_of_day)

    @property
    def offset(self) -> Offset:
        """Gets the offset from UTC.

        :return: The offset from UTC.
        """
        return self.__offset_time.offset

    def to_instant(self) -> Instant:
        """Converts this offset date and time to an instant in time by subtracting the offset from the local date and
        time.

        :return: The instant represented by this offset date and time
        """
        from ._instant import Instant

        return Instant._from_untrusted_duration(self.__to_elapsed_time_since_epoch())

    def __to_elapsed_time_since_epoch(self) -> Duration:
        # Equivalent to LocalDateTime.ToLocalInstant().Minus(offset)
        days: int = self.__local_date._days_since_epoch
        elapsed_time: Duration = Duration._ctor(days=days, nano_of_day=self.nanosecond_of_day)._minus_small_nanoseconds(
            self.__offset_time._offset_nanoseconds
        )
        return elapsed_time

    def in_fixed_zone(self) -> ZonedDateTime:
        """Returns this value as a ``ZonedDateTime``.

        This method returns a ``ZonedDateTime`` with the same local date and time as this value, using a
        fixed time zone with the same offset as the offset for this value.

        Note that because the resulting ``ZonedDateTime`` has a fixed time zone, it is generally not useful to
        use this result for arithmetic operations, as the zone will not adjust to account for daylight savings.

        :return: A zoned date/time with the same local time and a fixed time zone using the offset from this value.
        """
        from pyoda_time import DateTimeZone

        return ZonedDateTime._ctor(offset_date_time=self, zone=DateTimeZone.for_offset(offset=self.offset))

    def in_zone(self, zone: DateTimeZone) -> ZonedDateTime:
        """Returns this value in ths specified time zone.

        This method does not expect the offset in the zone to be the same as for the current value; it simply converts
        this value into an ``Instant`` and finds the ``ZonedDateTime`` for that instant in the specified zone.

        :param zone: The time zone of the new value.
        :return: The instant represented by this value, in the specified time zone.
        """
        _Preconditions._check_not_null(zone, "zone")
        return self.to_instant().in_zone(zone=zone)

    def to_aware_datetime(self) -> datetime:
        """Returns an aware ``datetime.datetime`` correspdonding to this offset date and time.

        Note that although the returned ``datetime.datetime`` is "aware", the ``tzinfo`` will be an instance of
        ``datetime.timezone`` with a fixed utcoffset. It will not be associated with a real-word time zone.

        If the date and time is not on a microsecond boundary (the unit of granularity of ``datetime``) the value will
        be truncated towards the start of time.

        ``datetime`` uses the Gregorian calendar by definition, so the value is implicitly converted to the Gregorian
        calendar first. The result will be the same instant in time (potentially truncated as described above), but the
        values returned by the Year/Month/Day properties of the ``datetime`` may not match the Year/Month/Day properties
        of this value.

        :return: A ``datetime.datetime`` with the same local date/time and offset as this.
        """
        # Different to Noda Time:
        # In .NET, DateTimeOffset has an offset granularity of minutes, which is coarser than that of Noda Time.
        # In Python, offsets use datetime.timedelta and therefore could have microsecond granularity.
        # If there's a reason for doing so, I'm not sure what it is.
        # The point is that we do not need to truncate the offset granularity like Noda Time's `ToDateTimeOffset`.

        gregorian = self.with_calendar(CalendarSystem.gregorian)

        # TODO: Noda Time throws InvalidOperationException if outside the range of DateTimeOffset)
        #  That's because in dotnet, DateTimeOffset has a min/max offset range of -14 to 14 hours.
        #  This is less than the range of Noda Time's Offset which is -18 to 18 hours.
        #  At time of writing, Pyoda Time's Offset shares the same range.
        #  But python's datetime/date/time may have an offset (timedelta) range of "strictly between" -24 to 24 hours.

        dt_timezone = timezone(offset=timedelta(seconds=self.offset.seconds))

        return gregorian.local_date_time.to_naive_datetime().replace(tzinfo=dt_timezone)

    @classmethod
    def from_aware_datetime(cls, aware_datetime: datetime) -> OffsetDateTime:
        """Builds an ``OffsetDateTime`` from an aware ``datetime.datetime``.

        Note that even if the ``tzinfo`` represents a real-world time zone, the ``offset`` will remain fixed.

        :param aware_datetime: The aware ``datetime.datetime`` to convert.
        :return: The converted offset date and time.
        """
        # Different from Noda Time:
        if (tzinfo := aware_datetime.tzinfo) is None:
            raise ValueError("aware_datetime must be timezone-aware")

        if not isinstance(delta := tzinfo.utcoffset(aware_datetime), timedelta):
            raise ValueError(  # pragma: no cover
                f"aware_datetime.tzinfo.utcoffset() must be an instance of timedelta; got {delta.__class__.__name__}"
            )

        return OffsetDateTime(
            local_date_time=LocalDateTime.from_naive_datetime(aware_datetime.replace(tzinfo=None)),
            offset=Offset.from_timedelta(timedelta=delta),
        )

    def with_calendar(self, calendar: CalendarSystem) -> OffsetDateTime:
        """Creates a new OffsetDateTime representing the same physical date, time and offset, but in a different
        calendar.

        The returned OffsetDateTime is likely to have different date field values to this one.

        For example, January 1st 1970 in the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this offset date and time to.
        :return: The converted OffsetDateTime.
        """
        new_date = self.date.with_calendar(calendar=calendar)
        return OffsetDateTime._ctor(local_date=new_date, offset_time=self.__offset_time)

    def with_date_adjuster(self, adjuster: Callable[[LocalDate], LocalDate]) -> OffsetDateTime:
        """Returns this offset date/time, with the given date adjuster applied to it, maintaining the existing time of
        day and offset.

        If the adjuster attempts to construct an invalid date (such as by trying to set a day-of-month of 30 in
        February), any exception thrown by that construction attempt will be propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted offset date/time.
        """
        return OffsetDateTime._ctor(
            local_date=self.__local_date.with_date_adjuster(adjuster=adjuster),
            offset_time=self.__offset_time,
        )

    def with_time_adjuster(self, adjuster: Callable[[LocalTime], LocalTime]) -> OffsetDateTime:
        """Returns this offset date/time, with the given time adjuster applied to it, maintaining the existing date and
        offset.

        If the adjuster attempts to construct an invalid time, any exception thrown by that construction attempt will be
        propagated through this method.

        :param adjuster: The adjuster to apply.
        :return: The adjusted offset date/time.
        """
        from ._offset_time import OffsetTime

        new_time = self.time_of_day.with_time_adjuster(adjuster=adjuster)
        return OffsetDateTime._ctor(
            local_date=self.__local_date,
            offset_time=OffsetTime._ctor(
                nanosecond_of_day=new_time.nanosecond_of_day, offset_seconds=self.__offset_time._offset_seconds
            ),
        )

    def with_offset(self, offset: Offset) -> OffsetDateTime:
        """Creates a new OffsetDateTime representing the instant in time in the same calendar, but with a different
        offset. The local date and time is adjusted accordingly.

        :param offset: The new offset to use.
        :return: The converted OffsetDateTime.
        """
        from ._offset_time import OffsetTime

        # TODO: unchecked
        # Slight change to the normal operation, as it's *just* about plausible that we change day
        # twice in one direction or the other.
        days = 0
        nanos = self.__offset_time.nanosecond_of_day + offset.nanoseconds - self.__offset_time._offset_nanoseconds
        if nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
            days += 1
            nanos -= PyodaConstants.NANOSECONDS_PER_DAY
            if nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nanos -= PyodaConstants.NANOSECONDS_PER_DAY
        elif nanos < 0:
            days -= 1
            nanos += PyodaConstants.NANOSECONDS_PER_DAY
            if nanos < 0:
                days -= 1
                nanos += PyodaConstants.NANOSECONDS_PER_DAY
        return OffsetDateTime._ctor(
            local_date=self.__local_date if days == 0 else self.__local_date.plus_days(days),
            offset_time=OffsetTime._ctor(
                nanosecond_of_day=nanos,
                offset_seconds=offset.seconds,
            ),
        )

    def to_offset_date(self) -> OffsetDate:
        """Constructs a new ``OffsetDate`` from the date and offset of this value, but omitting the time-of-day.

        :return: A value representing the date and offset aspects of this value.
        """
        from . import OffsetDate

        return OffsetDate(date=self.date, offset=self.offset)

    def to_offset_time(self) -> OffsetTime:
        """Constructs a new ``OffsetTime`` from the time and offset of this value, but omitting the date.

        :return: A value representing the time and offset aspects of this value.
        """
        return self.__offset_time

    def __hash__(self) -> int:
        """Returns a hash code for this offset date and time.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this offset date and time.
        """
        return _hash_code_helper(self.__local_date, self.__offset_time)

    def equals(self, other: OffsetDateTime) -> bool:
        """Compares two ``OffsetDateTime`` values for equality.

        See the type documentation for a description of equality semantics.

        :param other: The object to compare this date with.
        :return: True if the given value is another offset date/time equal to this one; False otherwise.
        """
        return isinstance(other, OffsetDateTime) and self == other

    # TODO: Deconstruct [see issue 248]

    # region Formatting

    # TODO: def __repr__(self) -> str: [requires OffsetDateTimePattern]
    # TODO: def __format__(self) -> str: [requires OffsetDateTimePattern]

    # endregion

    # region Operators

    @staticmethod
    def add(offset_date_time: OffsetDateTime, duration: Duration) -> OffsetDateTime:
        """Adds a duration to an offset date and time.

        This is an alternative way of calling ``OffsetDateTime + Duration``.

        :param offset_date_time: The value to add the duration to.
        :param duration: The duration to add
        :return: A new value with the time advanced by the given duration, in the same calendar system and with the
            same offset.
        """
        return offset_date_time + duration

    def plus(self, duration: Duration) -> OffsetDateTime:
        """Returns the result of adding a duration to this offset date and time.

        This is an alternative way of calling ``OffsetDateTime + Duration``.

        :param duration: The duration to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + duration

    def plus_hours(self, hours: int) -> OffsetDateTime:
        """Returns the result of adding a increment of hours to this offset date and time.

        :param hours: The number of hours to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_hours(hours)

    def plus_minutes(self, minutes: int) -> OffsetDateTime:
        """Returns the result of adding an increment of minutes to this offset date and time.

        :param minutes: The number of minutes to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_minutes(minutes)

    def plus_seconds(self, seconds: int) -> OffsetDateTime:
        """Returns the result of adding an increment of seconds to this offset date and time.

        :param seconds: The number of seconds to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_seconds(seconds)

    def plus_milliseconds(self, milliseconds: int) -> OffsetDateTime:
        """Returns the result of adding an increment of milliseconds to this offset date and time.

        :param milliseconds: The number of milliseconds to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_milliseconds(milliseconds)

    def plus_ticks(self, ticks: int) -> OffsetDateTime:
        """Returns the result of adding an increment of ticks to this offset date and time.

        :param ticks: The number of ticks to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_ticks(ticks)

    def plus_nanoseconds(self, nanoseconds: int) -> OffsetDateTime:
        """Returns the result of adding an increment of nanoseconds to this offset date and time.

        :param nanoseconds: The number of nanoseconds to add
        :return: A new ``OffsetDateTime`` representing the result of the addition.
        """
        return self + Duration.from_nanoseconds(nanoseconds)

    def __add__(self, duration: Duration) -> OffsetDateTime:
        """Returns a new ``OffsetDateTime`` with the time advanced by the given duration.

        The returned value retains the calendar system and offset of the ``OffsetDateTime``.

        :param duration: The duration to add.
        :return: A new value with the time advanced by the given duration, in the same calendar system and with the
            same offset.
        """
        return OffsetDateTime._ctor(
            instant=self.to_instant() + duration,
            offset=self.offset,
        )

    @staticmethod
    @overload
    def subtract(offset_date_time: OffsetDateTime, duration: Duration, /) -> OffsetDateTime:
        """Subtracts a duration from an offset date and time.

        This is an alternative way of calling ``OffsetDateTime - Duration``.

        :param offset_date_time: The value to subtract the duration from.
        :param duration: The duration to subtract.
        :return: A new value with the time "rewound" by the given duration, in the same calendar system and with the
            same offset.
        """

    @staticmethod
    @overload
    def subtract(end: OffsetDateTime, start: OffsetDateTime, /) -> Duration:
        """Subtracts one offset date and time from another, returning an elapsed duration.

        This is an alternative way of calling ``OffsetDateTime - OffsetDateTime``.

        :param end: The offset date and time value to subtract from; if this is later than ``start`` then the result
            will be positive.
        :param start: The offset date and time to subtract from ``end``.
        :return: The elapsed duration from ``start`` to ``end``.
        """

    @staticmethod
    def subtract(
        offset_date_time: OffsetDateTime, duration_or_offset: Duration | OffsetDateTime, /
    ) -> OffsetDateTime | Duration:
        return offset_date_time - duration_or_offset

    @overload
    def minus(self, duration: Duration, /) -> OffsetDateTime:
        """Returns the result of subtracting a duration from this offset date and time, for a fluent alternative to
        ``OffsetDateTime - Duration``.

        :param duration: The duration to subtract
        :return: A new ``OffsetDateTime`` representing the result of the subtraction.
        """

    @overload
    def minus(self, other: OffsetDateTime, /) -> Duration:
        """Returns the result of subtracting another offset date and time from this one, resulting in the elapsed
        duration between the two instants represented in the values.

        This is an alternative way of calling ``OffsetDateTime - OffsetDateTime``.

        :param other: The offset date and time to subtract from this one.
        :return: The elapsed duration from ``other`` to this value.
        """

    def minus(self, other: Duration | OffsetDateTime, /) -> OffsetDateTime | Duration:
        return self - other

    @overload
    def __sub__(self, other: Duration) -> OffsetDateTime:
        """Returns a new ``OffsetDateTime`` with the duration subtracted.

        The returned value retains the calendar system and offset of the ``OffsetDateTime``.

        :param other: The duration to subtract.
        :return: A new value with the time "rewound" by the given duration, in the same calendar system and with the
            same offset.
        """

    @overload
    def __sub__(self, other: OffsetDateTime) -> Duration:
        """Subtracts one ``OffsetDateTime`` from another, resulting in the elapsed time between the two values.

        This is equivalent to ``self.to_instant() - other.to_instant()``; in particular:

        * The two values can use different calendar systems
        * The two values can have different UTC offsets
        * If the left instance is later than the right instance, the result will be positive.

        :param other: The offset date and time to subtract from this one.
        :return: The elapsed duration from ``self`` to ``other``.
        """

    def __sub__(self, other: Duration | OffsetDateTime) -> OffsetDateTime | Duration:
        if isinstance(other, Duration):
            return OffsetDateTime._ctor(
                instant=self.to_instant() - other,
                offset=self.offset,
            )
        if isinstance(other, OffsetDateTime):
            return self.to_instant() - other.to_instant()
        return NotImplemented  # type: ignore[unreachable]  # pragma: no cover

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date/time with.
        :return: True if the given value is another offset date/time equal to this one; false otherwise..
        """
        if not isinstance(other, OffsetDateTime):
            return NotImplemented
        return self.__local_date == other.__local_date and self.__offset_time == other.__offset_time

    def __ne__(self, other: object) -> bool:
        """Implements the operator != (inequality).

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date/time with.
        :return: True if values are not equal to each other, otherwise False.
        """
        if isinstance(other, OffsetDateTime):
            return not (self == other)
        return NotImplemented

    # endregion

    # region Comparers

    # TODO: Comparers

    # endregion

    # region XML serialization

    # TODO: XML Serialization

    # endregion
