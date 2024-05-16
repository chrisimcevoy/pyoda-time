# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import functools
from typing import TYPE_CHECKING, Final, _ProtocolMeta

from .time_zones._i_zone_interval_map import _IZoneIntervalMap
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from . import Instant, Offset


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
        from . import Offset
        from .time_zones._fixed_date_time_zone import _FixedDateTimeZone

        return _FixedDateTimeZone(Offset.zero)


class DateTimeZone(abc.ABC, _IZoneIntervalMap, metaclass=_DateTimeZoneMeta):
    """Represents a time zone - a mapping between UTC and local time.
    A time zone maps UTC instants to local times - or, equivalently, to the offset from UTC at any particular instant.
    """

    _UTC_ID: Final[str] = "UTC"

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
        return self.get_zone_interval(instant).wall_offset

    # endregion
