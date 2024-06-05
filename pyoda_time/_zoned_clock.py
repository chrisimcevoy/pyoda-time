# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time import Instant
from pyoda_time._calendar_system import CalendarSystem
from pyoda_time._date_time_zone import DateTimeZone
from pyoda_time._i_clock import IClock
from pyoda_time._local_date import LocalDate
from pyoda_time._local_date_time import LocalDateTime
from pyoda_time._local_time import LocalTime
from pyoda_time._offset_date_time import OffsetDateTime
from pyoda_time._zoned_date_time import ZonedDateTime
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class ZonedClock(IClock):
    """A clock with an associated time zone and calendar.

    This is effectively a convenience class decorating an ``IClock``.
    """

    @property
    def clock(self) -> IClock:
        """Gets the clock used to provide the current instant.

        :return: The clock associated with this zoned clock.
        """
        return self.__clock

    @property
    def zone(self) -> DateTimeZone:
        """Gets the time zone used when converting the current instant into a zone-sensitive value.

        :return: The time zone associated with this zoned clock.
        """
        return self.__zone

    @property
    def calendar(self) -> CalendarSystem:
        """Gets the calendar system used when converting the current instant into a calendar-sensitive value.

        :return: The calendar system associated with this zoned clock.
        """
        return self.__calendar

    def __init__(self, clock: IClock, zone: DateTimeZone, calendar: CalendarSystem) -> None:
        """Creates a new ``ZonedClock`` with the given clock, time zone and calendar system.

        :param clock: Clock to use to obtain instants.
        :param zone: Time zone to adjust instants into.
        :param calendar: Calendar system to use.
        """
        self.__clock = _Preconditions._check_not_null(clock, "clock")
        self.__zone = _Preconditions._check_not_null(zone, "zone")
        self.__calendar = _Preconditions._check_not_null(calendar, "calendar")

    def get_current_instant(self) -> Instant:
        """Returns the current instant provided by the underlying clock.

        :return: The current instant provided by the underlying clock.
        """
        return self.__clock.get_current_instant()

    def get_current_zoned_date_time(self) -> ZonedDateTime:
        """Returns the current instant provided by the underlying clock, adjusted to the time zone of this object.

        :return: The current instant provided by the underlying clock, adjusted to the time zone of this object.
        """
        return self.get_current_instant().in_zone(self.zone, self.calendar)

    def get_current_local_date_time(self) -> LocalDateTime:
        """Returns the local date/time of the current instant provided by the underlying clock, adjusted to the time
        zone of this object.

        :return: The local date/time of the current instant provided by the underlying clock, adjusted to the time zone
            of this object.
        """
        return self.get_current_zoned_date_time().local_date_time

    def get_current_offset_date_time(self) -> OffsetDateTime:
        """Returns the offset date/time of the current instant provided by the underlying clock, adjusted to the time
        zone of this object.

        :return: The offset date/time of the current instant provided by the underlying clock, adjusted to the time zone
            of this object.
        """
        return self.get_current_zoned_date_time().to_offset_date_time()

    def get_current_date(self) -> LocalDate:
        """Returns the local date of the current instant provided by the underlying clock, adjusted to the time zone of
        this object.

        :return: The local date of the current instant provided by the underlying clock, adjusted to the time zone of
            this object.
        """
        return self.get_current_zoned_date_time().date

    def get_curent_time_of_day(self) -> LocalTime:
        """Returns the local time of the current instant provided by the underlying clock, adjusted to the time zone of
        this object.

        :return: The local time of the current instant provided by the underlying clock, adjusted to the time zone of
            this object.
        """
        return self.get_current_zoned_date_time().time_of_day
