# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, overload

from pyoda_time._duration import Duration
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from . import (
        CalendarSystem,
        DateTimeZone,
        Instant,
        IsoDayOfWeek,
        LocalDate,
        LocalDateTime,
        LocalTime,
        Offset,
        OffsetDateTime,
    )

__all__ = ["ZonedDateTime"]


class ZonedDateTime:
    @classmethod
    def _ctor(cls, offset_date_time: OffsetDateTime, zone: DateTimeZone) -> ZonedDateTime:
        self = super().__new__(cls)
        self.__offset_date_time = offset_date_time
        self.__zone = zone
        return self

    @overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone) -> None: ...

    @overload
    def __init__(self, *, local_date_time: LocalDateTime, zone: DateTimeZone, offset: Offset) -> None: ...

    @overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone, calendar: CalendarSystem) -> None: ...

    def __init__(
        self,
        *,
        zone: DateTimeZone,
        instant: Instant | None = None,
        local_date_time: LocalDateTime | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> None:
        from . import OffsetDateTime

        if offset is not None and calendar is not None:
            raise ValueError("offset and calendar are mutually exclusive")

        offset_date_time: OffsetDateTime
        if local_date_time is not None and offset is not None:
            candidate_instant = local_date_time._to_local_instant()._minus(offset)
            correct_offset: Offset = zone.get_utc_offset(candidate_instant)
            if correct_offset != offset:
                raise ValueError(
                    f"Offset {offset} is invalid for local date and time {local_date_time} in time zone {zone.id}"
                )
            offset_date_time = OffsetDateTime(local_date_time=local_date_time, offset=offset)
        elif calendar is not None and instant is not None:
            offset_date_time = OffsetDateTime._ctor(
                instant=instant, offset=zone.get_utc_offset(instant), calendar=calendar
            )
        elif instant is not None:
            offset_date_time = OffsetDateTime._ctor(instant=instant, offset=zone.get_utc_offset(instant))
        else:
            raise ValueError

        self.__offset_date_time: OffsetDateTime = offset_date_time
        self.__zone: DateTimeZone = _Preconditions._check_not_null(zone, "zone")

    @property
    def offset(self) -> Offset:
        """The offset of the local representation of this value from UTC."""
        return self.__offset_date_time.offset

    @property
    def zone(self) -> DateTimeZone:
        """Gets the time zone associated with this value.

        :return: The time zone associated with this value.
        """
        from ._date_time_zone import DateTimeZone

        return self.__zone or DateTimeZone.utc

    @property
    def local_date_time(self) -> LocalDateTime:
        """Gets the local date and time represented by this zoned date and time.

        The returned ``LocalDateTime`` will have the same calendar system and return the same values for each of the
        calendar properties (Year, MonthOfYear and so on), but will not be associated with any particular time zone.

        :return: The local date and time represented by this zoned date and time.
        """
        return self.__offset_date_time.local_date_time

    @property
    def calendar(self) -> CalendarSystem:
        """Gets the calendar system associated with this zoned date and time.

        :return: The calendar system associated with this zoned date and time.
        """
        return self.__offset_date_time.calendar

    @property
    def date(self) -> LocalDate:
        """Gets the local date represented by this zoned date and time.

        The returned ``LocalDate`` will have the same calendar system and return the same values for each of the
        date-based calendar properties (Year, MonthOfYear and so on), but will not be associated with any particular
        time zone.

        :return: The local date represented by this zoned date and time.
        """
        return self.__offset_date_time.date

    @property
    def time_of_day(self) -> LocalTime:
        """Gets the time portion of this zoned date and time.

        The returned ``LocalTime`` will return the same values for each of the time-based properties (Hour, Minute and
        so on), but will not be associated with any particular time zone.

        :return: The time portion of this zoned date and time.
        """
        return self.__offset_date_time.time_of_day

    @property
    def year(self) -> int:
        """Gets the year of this zoned date and time.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.

        :return: The year of this zoned date and time.
        """
        return self.__offset_date_time.year

    @property
    def month(self) -> int:
        """Gets the month of this zoned date and time within the year.

        :return: The month of this zoned date and time within the year.
        """
        return self.__offset_date_time.month

    @property
    def day_of_year(self) -> int:
        """Gets the day of this zoned date and time within the year.

        :return: The day of this zoned date and time within the year.
        """
        return self.__offset_date_time.day_of_year

    @property
    def day(self) -> int:
        """Gets the day of this zoned date and time within the month.

        :return: The day of this zoned date and time within the month.
        """
        return self.__offset_date_time.day

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """Gets the week day of this zoned date and time expressed as an ``IsoDayOfWeek`` value.

        :return: The week day of this zoned date and time expressed as an ``IsoDayOfWeek`` value.
        """
        return self.__offset_date_time.day_of_week

    @property
    def hour(self) -> int:
        """Gets the hour of day of this zoned date and time, in the range 0 to 23 inclusive.

        :return: The hour of day of this zoned date and time, in the range 0 to 23 inclusive.
        """
        return self.__offset_date_time.hour

    @property
    def minute(self) -> int:
        """Gets the minute of this zoned date and time, in the range 0 to 59 inclusive.

        :return: The minute of this zoned date and time, in the range 0 to 59 inclusive.
        """
        return self.__offset_date_time.minute

    @property
    def second(self) -> int:
        """Gets the second of this zoned date and time within the minute, in the range 0 to 59 inclusive.

        :return: The second of this zoned date and time within the minute, in the range 0 to 59 inclusive.
        """
        return self.__offset_date_time.second

    def to_instant(self) -> Instant:
        """Converts this value to the instant it represents on the timeline.

        This is always an unambiguous conversion. Any difficulties due to daylight saving
        transitions or other changes in time zone are handled when converting from a
        ``LocalDateTime`` to a ``ZonedDateTime``; the ``ZonedDateTime`` remembers
        the actual offset from UTC to local time, so it always knows the exact instant represented.

        :return: The instant corresponding to this value.
        """
        return self.__offset_date_time.to_instant()

    # region Operators

    def __eq__(self, other: object) -> bool:
        """Implements the operator ==.

        See the type documentation for a description of equality semantics.

        :param other: The object to compare to this one.
        :return: True if the specified value is a ``ZonedDateTime`` representing the same instant in the same time zone;
            false otherwise.
        """
        if not isinstance(other, ZonedDateTime):
            return NotImplemented
        return self.__offset_date_time == other.__offset_date_time and self.__zone == other.__zone

    def __add__(self, other: Duration) -> ZonedDateTime:
        """Returns a new ``ZonedDateTime`` with the time advanced by the given duration.

        Note that due to daylight saving time changes this may not advance the local time by the same amount.

        The returned value retains the calendar system and time zone of ``self``.

        :param other: The duration to add.
        :return: A new value with the time advanced by the given duration, in the same calendar system and time zone.
        """
        if not isinstance(other, Duration):
            return NotImplemented  # type: ignore[unreachable]
        return ZonedDateTime(instant=self.to_instant() + other, zone=self.zone, calendar=self.calendar)

    # endregion

    def to_offset_date_time(self) -> OffsetDateTime:
        """Constructs an ``OffsetDateTime`` with the same local date and time, and the same offset as this zoned date
        and time, effectively just "removing" the time zone itself.

        :return: An OffsetDateTime with the same local date/time and offset as this value.
        """
        return self.__offset_date_time
