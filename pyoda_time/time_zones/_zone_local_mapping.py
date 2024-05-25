# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final

from pyoda_time._ambiguous_time_error import AmbiguousTimeError
from pyoda_time._local_date_time import LocalDateTime
from pyoda_time._skipped_time_error import SkippedTimeError
from pyoda_time._zoned_date_time import ZonedDateTime
from pyoda_time.utility._csharp_compatibility import _private, _sealed

if TYPE_CHECKING:
    from pyoda_time._date_time_zone import DateTimeZone
    from pyoda_time.time_zones import ZoneInterval


@final
@_sealed
@_private
class ZoneLocalMapping:
    """The result of mapping a ``LocalDateTime`` within a time zone, i.e. finding out at what "global" time the "local"
    time occurred.

    This class is used as the return type of DateTimeZone.map_local. It allows for
    finely-grained handling of the three possible results:

    Unambiguous Mapping
        The local time occurs exactly once in the target time zone.
    Ambiguous Mapping
        The local time occurs twice in the target time zone, due to the offset from UTC
        changing. This usually occurs for an autumnal daylight saving transition, where the clocks
        are put back by an hour. If the clocks change from 2am to 1am for example, then 1:30am occurs
        twice - once before the transition and once afterwards.
    Impossible mapping
        The local time does not occur at all in the target time zone, due to the offset from UTC
        changing. This usually occurs for a vernal (spring-time) daylight saving transition, where the clocks
        are put forward by an hour. If the clocks change from 1am to 2am for example, then 1:30am is
        skipped entirely.
    """

    __zone: DateTimeZone
    __early_interval: ZoneInterval
    __late_interval: ZoneInterval
    __local_date_time: LocalDateTime
    __count: int

    @property
    def zone(self) -> DateTimeZone:
        """Gets the ``DateTimeZone`` in which this mapping was performed.

        :return: The time zone in which this mapping was performed.
        """
        return self.__zone

    @property
    def local_date_time(self) -> LocalDateTime:
        """Gets the ``LocalDateTime`` which was mapped within the time zone.

        :return: The local date and time which was mapped within the time zone.
        """
        return self.__local_date_time

    @property
    def early_interval(self) -> ZoneInterval:
        """Gets the earlier ``ZoneInterval`` within this mapping.

        For unambiguous mappings, this is the same as ``late_interval``; for ambiguous mappings,
        this is the interval during which the mapped local time first occurs; for impossible
        mappings, this is the interval before which the mapped local time occurs.

        :return: The earlier zone interval within this mapping.
        """
        return self.__early_interval

    @property
    def late_interval(self) -> ZoneInterval:
        """Gets the later ``ZoneInterval`` within this mapping.

        For unambiguous
        mappings, this is the same as ``early_interval``; for ambiguous mappings,
        this is the interval during which the mapped local time last occurs; for impossible
        mappings, this is the interval after which the mapped local time occurs.

        :return: The earlier zone interval within this mapping.
        """
        return self.__late_interval

    @property
    def count(self) -> int:
        """Gets the number of results within this mapping: the number of distinct ``ZonedDateTime`` values which map to
        the original ``LocalDateTime``.

        :return: The number of results within this mapping: the number of distinct values which map to the original
            local date and time.
        """
        return self.__count

    @classmethod
    def _ctor(
        cls,
        zone: DateTimeZone,
        local_date_time: LocalDateTime,
        early_interval: ZoneInterval,
        late_interval: ZoneInterval,
        count: int,
    ) -> ZoneLocalMapping:
        # TODO:
        #  Preconditions.DebugCheckNotNull(zone, nameof(zone));
        #  Preconditions.DebugCheckNotNull(earlyInterval, nameof(earlyInterval));
        #  Preconditions.DebugCheckNotNull(lateInterval, nameof(lateInterval));
        #  Preconditions.DebugCheckArgumentRange(nameof(count), count, 0, 2);
        self = super().__new__(cls)
        self.__zone = zone
        self.__early_interval = early_interval
        self.__late_interval = late_interval
        self.__local_date_time = local_date_time
        self.__count = count
        return self

    def single(self) -> ZonedDateTime:
        """Returns the single ``ZonedDateTime`` which maps to the original ``LocalDateTime`` in the mapped
        ``DateTimeZone``.

        :raises SkippedTimeError: The local date/time was skipped in the time zone.
        :raises AmbiguousTimeError: The local date/time was ambiguous in the time zone.
        :return: The unambiguous result of mapping the local date/time in the time zone.
        """
        match self.count:
            case 0:
                raise SkippedTimeError(self.local_date_time, self.zone)
            case 1:
                return self.__build_zoned_date_time(self.early_interval)
            case 2:
                raise AmbiguousTimeError(
                    self.__build_zoned_date_time(self.early_interval),
                    self.__build_zoned_date_time(self.late_interval),
                )
            case _:
                raise RuntimeError("Can't happen")

    def first(self) -> ZonedDateTime:
        """Returns a ``ZonedDateTime`` which maps to the original ``LocalDateTime`` in the mapped ``DateTimeZone``:
        either the single result if the mapping is unambiguous, or the earlier result if the local date/time occurs
        twice in the time zone due to a time zone offset change such as an autumnal daylight saving transition.

        :raises SkippedTimeError: The local date/time was skipped in the time zone.
        :return: The unambiguous result of mapping a local date/time in a time zone.
        """
        match self.count:
            case 0:
                raise SkippedTimeError(self.local_date_time, self.zone)
            case 1 | 2:
                return self.__build_zoned_date_time(self.early_interval)
            case _:
                raise RuntimeError("Can't happen")

    def __build_zoned_date_time(self, interval: ZoneInterval) -> ZonedDateTime:
        return ZonedDateTime._ctor(
            offset_date_time=self.local_date_time.with_offset(interval.wall_offset), zone=self.zone
        )
