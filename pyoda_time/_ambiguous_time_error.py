# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING

from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from pyoda_time._date_time_zone import DateTimeZone
    from pyoda_time._local_date_time import LocalDateTime
    from pyoda_time._zoned_date_time import ZonedDateTime


class AmbiguousTimeError(ValueError):
    """Exception thrown to indicate that the specified local date/time occurs twice in a particular time zone due to
    daylight saving time changes.

    This occurs for transitions where the clock goes backward (usually by an hour). For example, suppose the time zone
    goes backward at 2am, so the second after 01:59:59 becomes 01:00:00. In that case, times such as 01:30:00 occur
    twice.

    This exception is used to indicate such problems, as they're usually not the same as other <see
    cref="ArgumentOutOfRangeException" /> causes, such as entering "15" for a month number.

    In theory this isn't calendar-specific; the local value will be ambiguous in this time zone regardless of the
    calendar used. However, this exception is always created in conjunction with a specific calendar, which leads to a
    more natural way of examining its information and constructing an error message.
    """

    @property
    def local_date_time(self) -> LocalDateTime:
        """Get the local date and time which is ambiguous in the time zone.

        :return: The local date and time which is ambiguous in the time zone.
        """
        return self.earlier_mapping.local_date_time

    @property
    def zone(self) -> DateTimeZone:
        """The time zone in which the local date and time is ambiguous.

        :return: The time zone in which the local date and time is ambiguous.
        """
        return self.earlier_mapping.zone

    @property
    def earlier_mapping(self) -> ZonedDateTime:
        """Gets the earlier of the two occurrences of the local date and time within the time zone.

        :return: The earlier of the two occurrences of the local date and time within the time zone.
        """
        return self.__earlier_mapping

    @property
    def later_mapping(self) -> ZonedDateTime:
        """Gets the later of the two occurrences of the local date and time within the time zone.

        :return: The later of the two occurrences of the local date and time within the time zone.
        """
        return self.__later_mapping

    def __init__(self, earlier_mapping: ZonedDateTime, later_mapping: ZonedDateTime) -> None:
        """Constructs an instance from the given information.

        User code is unlikely to need to deliberately call this constructor except possibly for testing.

        The two mappings must have the same local time and time zone.

        :param earlier_mapping: The earlier possible mapping
        :param later_mapping: The later possible mapping
        """
        super().__init__(
            f"Local time {earlier_mapping.local_date_time} is ambiguous in time zone {earlier_mapping.zone.id}"
        )
        self.__earlier_mapping = earlier_mapping
        self.__later_mapping = later_mapping
        _Preconditions._check_argument(
            earlier_mapping.zone == later_mapping.zone,
            "later_mapping",
            "Ambiguous possible values must use the same time zone",
        )
        _Preconditions._check_argument(
            earlier_mapping.local_date_time == later_mapping.local_date_time,
            "later_mapping",
            "Ambiguous possible values must have the same local date/time",
        )
