# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time._date_time_zone import DateTimeZone
from pyoda_time._instant import Instant
from pyoda_time._offset import Offset
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.utility._csharp_compatibility import _sealed


@final
@_sealed
class SingleTransitionDateTimeZone(DateTimeZone):
    """Time zone with a single transition between two offsets.

    This provides a simple way to test behaviour across a transition.
    """

    @property
    def early_interval(self) -> ZoneInterval:
        """Gets the ``ZoneInterval`` for the period before the transition, starting at the beginning of time.

        :return: The zone interval for the period before the transition, starting at the beginning of time.
        """
        return self.__early_interval

    @property
    def late_interval(self) -> ZoneInterval:
        """Gets the ``ZoneInterval`` for the period after the transition, ending at the end of time.

        :return: The zone interval for the period after the transition, ending at the end of time.
        """
        return self.__late_interval

    @property
    def transition(self) -> Instant:
        """Gets the transition instant of the zone.

        :return: The transition instant of the zone.
        """
        return self.early_interval.end

    def __init__(
        self,
        transition_point: Instant,
        offset_before: Offset | int,
        offset_after: Offset | int,
        id_: str = "Single",
    ) -> None:
        """Creates a zone with a single transition between two offsets.

        :param transition_point: The transition point as an ``Instant``.
        :param offset_before: The offset of local time from UTC before the transition.
        :param offset_after: The offset of local time from UTC before the transition.
        :param id_:
        """
        if isinstance(offset_before, int):
            offset_before = Offset.from_hours(offset_before)
        if isinstance(offset_after, int):
            offset_after = Offset.from_hours(offset_after)
        super().__init__(id_, False, min(offset_before, offset_after), max(offset_before, offset_after))
        self.__early_interval = ZoneInterval(
            name=id_ + "-Early", start=None, end=transition_point, wall_offset=offset_before, savings=Offset.zero
        )
        self.__late_interval = ZoneInterval(
            name=id_ + "-Late", start=transition_point, end=None, wall_offset=offset_after, savings=Offset.zero
        )

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        return self.early_interval if instant in self.early_interval else self.late_interval
