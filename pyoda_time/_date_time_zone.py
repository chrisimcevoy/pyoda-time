# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import functools
from typing import Final, _ProtocolMeta

from ._duration import Duration
from ._instant import Instant
from ._local_date_time import LocalDateTime
from ._local_instant import _LocalInstant
from ._offset import Offset
from .time_zones._i_zone_interval_map import _IZoneIntervalMap
from .time_zones._zone_interval import ZoneInterval
from .time_zones._zone_local_mapping import ZoneLocalMapping
from .utility._preconditions import _Preconditions

__all__ = ["DateTimeZone"]


class _DateTimeZoneMeta(_ProtocolMeta, type):
    @property
    @functools.cache
    def utc(cls) -> DateTimeZone:
        """Gets the UTC (Coordinated Universal Time) time zone.

        This is a single instance which is not provider-specific; it is guaranteed to have the ID "UTC", and to
        compare equal to an instance returned by calling ``for_offset`` with an offset of zero, but it may
        or may not compare equal to an instance returned by e.g. ``DateTimeZoneProviders.Tzdb["UTC"]``.

        :return: The UTC ``DateTimeZone``.
        """
        from .time_zones._fixed_date_time_zone import _FixedDateTimeZone

        return _FixedDateTimeZone(Offset.zero)


class DateTimeZone(abc.ABC, _IZoneIntervalMap, metaclass=_DateTimeZoneMeta):
    """Represents a time zone - a mapping between UTC and local time.
    A time zone maps UTC instants to local times - or, equivalently, to the offset from UTC at any particular instant.
    """

    _UTC_ID: Final[str] = "UTC"

    @classmethod
    def for_offset(cls, offset: Offset) -> DateTimeZone:
        raise NotImplementedError

    def __init__(self, id_: str, is_fixed: bool, min_offset: Offset, max_offset: Offset) -> None:
        """Initializes a new instance of the DateTimeZone class.

        :param id_: The unique id of this time zone.
        :param is_fixed: Set to True is this time zone has no transitions.
        :param min_offset: Minimum offset applied with this zone
        :param max_offset: Maximum offset applied with this zone
        """
        self.__id: str = _Preconditions._check_not_null(id_, "id_")
        self.__is_fixed: bool = is_fixed
        self.__min_offset: Offset = min_offset
        self.__max_offset: Offset = max_offset

    @property
    def id(self) -> str:
        """The provider's ID for the time zone.

        This identifies the time zone within the current time zone provider; a different provider may provide a
        different time zone with the same ID, or may not provide a time zone with that ID at all.
        """
        return self.__id

    @property
    def _is_fixed(self) -> bool:
        """Indicates whether the time zone is fixed, i.e. contains no transitions.

        This is used as an optimization. If the time zone has no transitions but returns False for this then the
        behavior will be correct but the system will have to do extra work. However if the time zone has transitions and
        this returns <c>true</c> then the transitions will never be examined.
        """
        return self.__is_fixed

    @property
    def min_offset(self) -> Offset:
        """The least (most negative) offset within this time zone, over all time."""
        return self.__min_offset

    @property
    def max_offset(self) -> Offset:
        """The greatest (most positive) offset within this time zone, over all time."""
        return self.__max_offset

    # region Core abstract/virtual methods

    def get_utc_offset(self, instant: Instant) -> Offset:
        """Returns the offset from UTC, where a positive duration indicates that local time is later than UTC. In other
        words, local time = UTC + offset.

        This is mostly a convenience method for calling <c>GetZoneInterval(instant).WallOffset</c>, although it can also
        be overridden for more efficiency.

        :param instant: The instant for which to calculate the offset.
        :return: The offset from UTC at the specified instant.
        """
        return self.get_zone_interval(instant).wall_offset

    @abc.abstractmethod
    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        raise NotImplementedError

    def map_local(self, local_date_time: LocalDateTime) -> ZoneLocalMapping:
        """Returns complete information about how the given ``LocalDateTime`` is mapped in this time zone.

        Mapping a local date/time to a time zone can give an unambiguous, ambiguous or impossible result, depending on
        time zone transitions. Use the return value of this method to handle these cases in an appropriate way for
        your use case.

        As an alternative, consider ``resolve_local``, which uses a caller-provided strategy to
        convert the ``ZoneLocalMapping`` returned here to a ``ZonedDateTime``.

        :param local_date_time: The local date and time to map in this time zone.
        :return: A mapping of the given local date and time to zero, one or two zoned date/time values.
        """
        local_instant: _LocalInstant = local_date_time._to_local_instant()
        first_guess: Instant = local_instant._minus_zero_offset()
        interval: ZoneInterval = self.get_zone_interval(first_guess)

        # Most of the time we'll go into here... the local instant and the instant
        # are close enough that we've found the right instant.
        if interval._contains(local_instant):
            if earlier := self.__get_earlier_matching_interval(interval, local_instant):
                return ZoneLocalMapping._ctor(self, local_date_time, earlier, interval, 2)
            if later := self.__get_later_matching_interval(interval, local_instant):
                return ZoneLocalMapping._ctor(self, local_date_time, interval, later, 2)
            return ZoneLocalMapping._ctor(self, local_date_time, interval, interval, 1)
        else:
            # Our first guess was wrong. Either we need to change interval by one (either direction)
            # or we're in a gap.
            if earlier := self.__get_earlier_matching_interval(interval, local_instant):
                return ZoneLocalMapping._ctor(self, local_date_time, earlier, earlier, 1)
            if later := self.__get_later_matching_interval(interval, local_instant):
                return ZoneLocalMapping._ctor(self, local_date_time, later, later, 1)
            return ZoneLocalMapping._ctor(
                self,
                local_date_time,
                self.__get_interval_before_gap(local_instant),
                self.__get_interval_after_gap(local_instant),
                0,
            )

    # endregion

    # region Conversion between local dates/times and ZonedDateTime

    # endregion

    def __get_earlier_matching_interval(
        self, interval: ZoneInterval, local_instant: _LocalInstant
    ) -> ZoneInterval | None:
        """Returns the interval before this one, if it contains the given local instant, or null otherwise."""
        # Micro-optimization to avoid fetching interval.Start multiple times. Seems
        # to give a performance improvement on x86 at least...
        # If the zone interval extends to the start of time, the next check will definitely evaluate to false.
        interval_start = interval._raw_start
        # This allows for a maxOffset of up to +1 day, and the "truncate towards beginning of time"
        # nature of the Days property.
        if local_instant._days_since_epoch <= interval_start._days_since_epoch + 1:
            # We *could* do a more accurate check here based on the actual maxOffset, but it's probably
            # not worth it.
            candidate: ZoneInterval = self.get_zone_interval(interval_start - Duration.epsilon)
            if candidate._contains(local_instant):
                return candidate
        return None

    def __get_later_matching_interval(
        self, interval: ZoneInterval, local_instant: _LocalInstant
    ) -> ZoneInterval | None:
        """Returns the next interval after this one, if it contains the given local instant, or null otherwise."""
        # Micro-optimization to avoid fetching interval.End multiple times. Seems
        # to give a performance improvement on x86 at least...
        # If the zone interval extends to the end of time, the next check will
        # definitely evaluate to false.
        interval_end = interval._raw_end
        # Crude but cheap first check to see whether there *might* be a later interval.
        # This allows for a minOffset of up to -1 day, and the "truncate towards beginning of time"
        # nature of the Days property.
        if local_instant._days_since_epoch >= interval_end._days_since_epoch - 1:
            # We *could* do a more accurate check here based on the actual maxOffset, but it's probably
            # not worth it.
            candidate = self.get_zone_interval(interval_end)
            if candidate._contains(local_instant):
                return candidate
        return None

    def __get_interval_before_gap(self, local_instant: _LocalInstant) -> ZoneInterval:
        guess: Instant = local_instant._minus_zero_offset()
        guess_interval = self.get_zone_interval(guess)
        # If the local interval occurs before the zone interval we're looking at starts,
        # we need to find the earlier one; otherwise this interval must come after the gap, and
        # it's therefore the one we want.
        if local_instant.minus(guess_interval.wall_offset) < guess_interval._raw_start:
            return self.get_zone_interval(guess_interval.start - Duration.epsilon)
        return guess_interval

    def __get_interval_after_gap(self, local_instant: _LocalInstant) -> ZoneInterval:
        guess: Instant = local_instant._minus_zero_offset()
        guess_interval = self.get_zone_interval(guess)
        # If the local interval occurs before the zone interval we're looking at starts,
        # it's the one we're looking for. Otherwise, we need to find the next interval.
        if local_instant.minus(guess_interval.wall_offset) < guess_interval._raw_start:
            return guess_interval
        else:
            # Will definitely be valid - there can't be a gap after an infinite interval.
            return self.get_zone_interval(guess_interval.end)
