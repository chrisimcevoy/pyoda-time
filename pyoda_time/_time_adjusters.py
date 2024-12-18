# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from collections.abc import Callable
from typing import final

from pyoda_time._local_time import LocalTime
from pyoda_time.utility._csharp_compatibility import _private, _sealed


class __TimeAdjustersMeta(type):
    @property
    def truncate_to_second(self) -> Callable[[LocalTime], LocalTime]:
        """Gets a time adjuster to truncate the time to the second, discarding fractional seconds.

        :return: A time adjuster to truncate the time to the second, discarding fractional seconds.
        """
        return lambda time: LocalTime(time.hour, time.minute, time.second)

    @property
    def truncate_to_minute(self) -> Callable[[LocalTime], LocalTime]:
        """Gets a time adjuster to truncate the time to the minute, discarding fractional minutes.

        :return: A time adjuster to truncate the time to the minute, discarding fractional minutes.
        """
        return lambda time: LocalTime(time.hour, time.minute)

    @property
    def truncate_to_hour(self) -> Callable[[LocalTime], LocalTime]:
        """Get a time adjuster to truncate the time to the hour, discarding fractional hours.

        :return: A time adjuster to truncate the time to the hour, discarding fractional hours.
        """
        return lambda time: LocalTime(time.hour)


@final
@_sealed
@_private
class TimeAdjusters(metaclass=__TimeAdjustersMeta):
    """Factory class for time adjusters: functions from ``LocalTime`` to ``LocalTime``,
    which can be applied to ``LocalTime``, ``LocalDateTime``, and ``OffsetDateTime``.
    """
