# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, overload

from ._duration import Duration
from ._pyoda_constants import PyodaConstants

if TYPE_CHECKING:
    from . import IsoDayOfWeek, LocalDate, LocalDateTime, LocalTime, OffsetTime
    from ._calendar_system import CalendarSystem
    from ._instant import Instant
    from ._offset import Offset
    from ._year_month_day import _YearMonthDay


__all__ = ["OffsetDateTime"]


class OffsetDateTime:
    def __init__(self, local_date_time: LocalDateTime, offset: Offset) -> None:
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

    def __to_elapsed_time_since_epoch(self) -> Duration:
        # Equivalent to LocalDateTime.ToLocalInstant().Minus(offset)
        days: int = self.__local_date._days_since_epoch
        elapsed_time: Duration = Duration._ctor(days=days, nano_of_day=self.nanosecond_of_day)._minus_small_nanoseconds(
            self.__offset_time._offset_nanoseconds
        )
        return elapsed_time

    # region Operators

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality). See the type documentation for a description of equality semantics.

        :param other: The value to compare this offset date/time with.
        :return: True if the given value is another offset date/time equal to this one; false otherwise..
        """
        if not isinstance(other, OffsetDateTime):
            return NotImplemented
        return self.__local_date == other.__local_date and self.__offset_time == other.__offset_time

    # endregion
