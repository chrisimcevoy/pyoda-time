# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

from ._calendar_system import CalendarSystem
from ._date_time_zone import DateTimeZone
from ._date_time_zone_providers import DateTimeZoneProviders

if TYPE_CHECKING:
    from ._instant import Instant
    from ._zoned_clock import ZonedClock


class IClock(Protocol):
    """Represents a clock which can return the current time as an ``Instant``.

    ``IClock`` is intended for use anywhere you need to have access to the current time.

    Although it's not strictly incorrect to call ``SystemClock.instance.get_current_instant()`` directly,
    in the same way as you might call ``datetime.now(tz=UTC)``, it's strongly discouraged
    as a matter of style for production code. We recommend providing an instance of ``IClock``
    to anything that needs it, which allows you to write tests using the fake clock in the pyoda_time.testing
    package (or your own implementation).
    """

    @abstractmethod
    def get_current_instant(self) -> Instant:
        """Gets the current ``Instant`` on the timeline according to this clock.

        :return: The current instant on the timeline according to this clock.
        """
        ...

    # region ClockExtensions methods

    def in_zone(self, zone: DateTimeZone, calendar: CalendarSystem = CalendarSystem.iso) -> ZonedClock:
        """Constructs a ``ZonedClock`` from this clock, a time zone, and a calendar system.

        :param zone: Time zone to use in the returned object.
        :param calendar: Calendar to use in the returned object.
        :return: A ``ZonedClock`` with the given clock, time zone and calendar system.
        """
        from ._zoned_clock import ZonedClock

        return ZonedClock(self, zone, calendar)

    def in_utc(self) -> ZonedClock:
        """Constructs a ``ZonedClock`` from this clock, using the UTC time zone and ISO calendar system.

        :return: A ``ZonedClock`` with the given clock, in the UTC time zone and ISO calendar system.
        """
        return self.in_zone(DateTimeZone.utc)

    def in_tzdb_system_default_zone(self) -> ZonedClock:
        """Constructs a ``ZonedClock`` from this clock, in the TZDB mapping for the system default time zone and the ISO
        calendar system.

        :return:
        """
        zone = DateTimeZoneProviders.tzdb.get_system_default()
        return self.in_zone(zone)

    # TODO: def in_bcl_system_default_zone(self) -> ZonedClock:

    # endregion
