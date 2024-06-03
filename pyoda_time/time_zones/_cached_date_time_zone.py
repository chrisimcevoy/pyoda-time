# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time._date_time_zone import DateTimeZone
from pyoda_time._instant import Instant
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.time_zones._caching_zone_interval_map import _CachingZoneIntervalMap
from pyoda_time.time_zones._i_zone_interval_map import _IZoneIntervalMap
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class _CachedDateTimeZone(DateTimeZone):
    """Provides a ``DateTimeZone`` wrapper class that implements a simple cache to speed up the lookup of
    transitions."""

    __map: _IZoneIntervalMap
    __time_zone: DateTimeZone

    @property
    def _time_zone(self) -> DateTimeZone:
        """Gets the cached time zone.

        :return: The time zone.
        """
        return self.__time_zone

    @classmethod
    def __ctor(cls, time_zone: DateTimeZone, map: _IZoneIntervalMap) -> _CachedDateTimeZone:
        """Initializes a new instance of the ``_CachedDateTimeZone`` class.

        :param time_zone: The time zone to cache.
        :param map: The caching map
        :return: The new instance of the ``_CachedDateTimeZone`` class.
        """
        self = super().__new__(cls)
        super(_CachedDateTimeZone, self).__init__(time_zone.id, False, time_zone.min_offset, time_zone.max_offset)
        self.__time_zone = time_zone
        self.__map = map
        return self

    @classmethod
    def _for_zone(cls, time_zone: DateTimeZone) -> DateTimeZone:
        _Preconditions._check_not_null(time_zone, "time_zone")
        if isinstance(time_zone, _CachedDateTimeZone) or time_zone._is_fixed:
            return time_zone
        return cls.__ctor(time_zone, _CachingZoneIntervalMap._cache_map(time_zone))

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        """Delegates fetching a zone interval to the caching map."""
        return self.__map.get_zone_interval(instant)
