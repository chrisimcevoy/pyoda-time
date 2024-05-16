# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import abstractmethod
from typing import Protocol

from pyoda_time._instant import Instant
from pyoda_time._offset import Offset
from pyoda_time.time_zones._zone_interval import ZoneInterval


class _IZoneIntervalMap(Protocol):
    """The core part of a DateTimeZone: mapping an Instant to an Interval.

    Separating this out into an interface allows for flexible caching.
    """

    def get_zone_interval(self, instant: Instant) -> ZoneInterval: ...

    @property
    @abstractmethod
    def min_offset(self) -> Offset: ...

    @property
    @abstractmethod
    def max_offset(self) -> Offset: ...
