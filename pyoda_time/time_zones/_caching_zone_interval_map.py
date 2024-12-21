# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, Self, final

from pyoda_time._duration import Duration
from pyoda_time._instant import Instant
from pyoda_time.time_zones._i_zone_interval_map import _IZoneIntervalMap
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from pyoda_time._offset import Offset
    from pyoda_time.time_zones import ZoneInterval

_PERIOD_SHIFT: int = 5
"""Defines the number of bits to shift an instant's "days since epoch" to get the period.

This converts an instant into a number of 32 day periods.
"""


@final
@_sealed
@_private
class _CachingZoneIntervalMap:
    """Helper methods for creating IZoneIntervalMaps which cache results."""

    @classmethod
    def _cache_map(cls, map_: _IZoneIntervalMap) -> _IZoneIntervalMap:
        """Returns a caching map for the given input map."""
        return cls.__HashArrayCache._ctor(map_)

    # region Nested type: HashArrayCache

    @final
    @_sealed
    @_private
    class __HashArrayCache(_IZoneIntervalMap):
        """This provides a simple cache based on two hash tables (one for local instants, another for instants).

        Each hash table entry is either entry or contains a node with enough
        information for a particular "period" of 32 days - so multiple calls for time
        zone information within the same few years are likely to hit the cache. Note that
        a single "period" may include a daylight saving change (or conceivably more than one);
        a node therefore has to contain enough intervals to completely represent that period.

        If another call is made which maps to the same cache entry number but is for a different
        period, the existing hash entry is simply overridden.
        """

        # region Nested type: _HashCacheNode

        @final
        @_sealed
        @_private
        class _HashCacheNode:
            __interval: ZoneInterval
            __period: int
            __previous: Self | None

            @property
            def _interval(self) -> ZoneInterval:
                return self.__interval

            @property
            def _period(self) -> int:
                return self.__period

            @property
            def _previous(self) -> Self | None:
                return self.__previous

            @classmethod
            def _create_node(cls, period: int, map_: _IZoneIntervalMap) -> Self:
                days = period << _PERIOD_SHIFT
                period_start = Instant._from_untrusted_duration(
                    Duration._ctor(days=max(days, Instant._MIN_DAYS), nano_of_day=0)
                )
                next_period_start_days = days + (1 << _PERIOD_SHIFT)

                interval = map_.get_zone_interval(period_start)
                node = cls.__ctor(interval, period, None)

                # Keep going while the current interval ends before the period.
                # (We only need to check the days, as every period lands on a
                # day boundary.)
                # If the raw end is the end of time, the condition will definitely
                # evaluate to false.
                while interval._raw_end._days_since_epoch < next_period_start_days:
                    interval = map_.get_zone_interval(interval.end)
                    node = cls.__ctor(interval, period, node)
                return node

            @classmethod
            def __ctor(cls, interval: ZoneInterval, period: int, previous: Self | None) -> Self:
                """Initializes a new instance of the ``_HashCacheNode`` class.

                :param interval: The zone interval.
                :param period:
                :param previous: The previous ``_HashCacheNode`` node.
                :return: The new instance of the ``_HashCacheNode`` class.
                """
                self = super().__new__(cls)
                self.__period = period
                self.__interval = interval
                self.__previous = previous
                return self

        # endregion

        __CACHE_SIZE: int = 512
        """Currently we have no need or way to create hash cache zones with different cache sizes.

        But the cache size should always be a power of 2 to get the "period to cache entry" conversion simply as a
        bitmask operation.
        """

        __CACHE_PERIOD_MASK: int = __CACHE_SIZE - 1
        """Mask to AND the period number with in order to get the cache entry index.

        The result will always be in the range [0, CacheSize).
        """

        @property
        def min_offset(self) -> Offset:
            return self.__map.min_offset

        @property
        def max_offset(self) -> Offset:
            return self.__map.max_offset

        __instant_cache: list[_HashCacheNode | None]
        __map: _IZoneIntervalMap

        @classmethod
        def _ctor(cls, map_: _IZoneIntervalMap) -> Self:
            self = super().__new__(cls)
            self.__map = _Preconditions._check_not_null(map_, "map_")
            self.__instant_cache = [None] * cls.__CACHE_SIZE
            return self

        def get_zone_interval(self, instant: Instant) -> ZoneInterval:
            """Gets the zone offset period for the given instant. Null is returned if no period is defined by the time
            zone for the given instant.

            :param instant: The Instant to test.
            :return: The defined ZoneOffsetPeriod or null.
            """
            period = instant._days_since_epoch >> _PERIOD_SHIFT
            index = period & self.__CACHE_PERIOD_MASK
            node = self.__instant_cache[index]
            if (node is None) or (node._period != period):
                node = self._HashCacheNode._create_node(period, self.__map)
                self.__instant_cache[index] = node

            # Note: moving this code into an instance method in HashCacheNode makes a surprisingly
            # large performance difference.
            while node._previous is not None and node._interval._raw_start > instant:
                node = node._previous
            return node._interval

    # endregion
