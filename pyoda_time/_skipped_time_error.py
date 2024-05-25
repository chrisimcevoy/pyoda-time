# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import final

from pyoda_time import DateTimeZone, LocalDateTime
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class SkippedTimeError(ValueError):
    """Exception thrown to indicate that the specified local time doesn't exist in a particular time zone due to
    daylight saving time changes.

    This normally occurs for spring transitions, where the clock goes forward (usually by an hour). For example,
    suppose the time zone goes forward at 2am, so the second after 01:59:59 becomes 03:00:00. In that case, local times
    such as 02:30:00 never occur.

    This exception is used to indicate such problems, as they're usually not the same as other ``ValueError`` causes,
    such as entering "15" for a month number.

    Note that it is possible (though extremely rare) for a whole day to be skipped due to a time zone transition, so
    this exception may also be thrown in cases where no local time is valid for a particular local date. (For example,
    Samoa skipped December 30th 2011 entirely, transitioning from UTC-10 to UTC+14 at midnight.)
    """

    @property
    def local_date_time(self) -> LocalDateTime:
        """Gets the local date/time which is invalid in the time zone, prompting this exception.

        :return: The local date/time which is invalid in the time zone.
        """
        return self.__local_date_time

    @property
    def zone(self) -> DateTimeZone:
        """Gets the time zone in which the local date/time is invalid.

        :return: The time zone in which the local date/time is invalid
        """
        return self.__zone

    def __init__(self, local_date_time: LocalDateTime, zone: DateTimeZone) -> None:
        """Creates a new instance for the given local date/time and time zone.

        User code is unlikely to need to deliberately call this constructor except possibly for testing.

        :param local_date_time: The local date/time which is skipped in the specified time zone.
        :param zone: The time zone in which the local date/time does not exist.
        """
        super().__init__(
            f"Local time {local_date_time} is invalid in time zone {_Preconditions._check_not_null(zone, "zone").id}"
        )
        self.__local_date_time = local_date_time
        self.__zone = zone
