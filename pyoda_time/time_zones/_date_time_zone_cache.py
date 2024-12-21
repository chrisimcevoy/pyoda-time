# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from .._i_date_time_zone_provider import IDateTimeZoneProvider
from ..utility._csharp_compatibility import _sealed
from ..utility._preconditions import _Preconditions
from ._date_time_zone_not_found_error import DateTimeZoneNotFoundError
from ._invalid_date_time_zone_source_error import InvalidDateTimeZoneSourceError

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .._date_time_zone import DateTimeZone
    from ._i_date_time_zone_source import IDateTimeZoneSource


@final
@_sealed
class DateTimeZoneCache(IDateTimeZoneProvider):
    """Provides an implementation of ``IDateTimeZoneProvider`` that caches results from an ``IDateTimeZoneSource``.

    The process of loading or creating time zones may be an expensive operation. This class implements an
    unlimited-size non-expiring cache over a time zone source, and adapts an implementation of the
    ``IDateTimeZoneSource`` interface to an ``IDateTimeZoneProvider``.
    """

    @property
    def version_id(self) -> str:
        """Gets the version ID of this provider. This is simply the ``IDateTimeZoneSource.version_id`` returned by the
        underlying source.

        :return: The version ID of this provider.
        """
        return self.__version_id

    @property
    def ids(self) -> Iterable[str]:
        # TODO: inheritdoc?
        return self.__ids

    def __init__(self, source: IDateTimeZoneSource) -> None:
        """Creates a provider backed by the given ``IDateTimeZoneSource``.

        Note that the source will never be consulted for requests for the fixed-offset timezones "UTC" and
        "UTC+/-Offset" (a standard implementation will be returned instead). This is true even if these IDs are
        advertised by the source.

        :param source: The ``IDateTimeZoneSource`` for this provider.
        :raises InvalidTimeZoneSourceError: ``source`` violates its contract.
        """
        self.__source: Final[IDateTimeZoneSource] = _Preconditions._check_not_null(source, "source")

        self.__version_id: Final[str] = source.version_id
        if self.__version_id is None:
            raise InvalidDateTimeZoneSourceError("Source-returned version ID was None")

        if (provider_ids := source.get_ids()) is None:
            raise InvalidDateTimeZoneSourceError("Source-returned ID sequence was None")
        if None in provider_ids:  # type: ignore[operator]
            raise InvalidDateTimeZoneSourceError("Source-returned ID sequence contained a null reference")
        self.__ids: Iterable[str] = sorted(provider_ids)

        # Populate the dictionary with null values meaning "the ID is valid, we haven't fetched the zone yet".
        self.__time_zone_map: Final[dict[str, DateTimeZone | None]] = {}
        for id_ in self.__ids:
            self.__time_zone_map[id_] = None

    def get_system_default(self) -> DateTimeZone:
        # TODO: inheritdoc?
        if (id_ := self.__source.get_system_default_id()) is None:
            raise DateTimeZoneNotFoundError(f"System default time zone is unknown to source {self.version_id}")
        return self[id_]

    def get_zone_or_none(self, zone_id: str) -> DateTimeZone | None:
        # TODO: inheritdoc?
        _Preconditions._check_not_null(zone_id, "zone_id")
        from pyoda_time.time_zones._fixed_date_time_zone import _FixedDateTimeZone

        return self.__get_zone_from_source_or_none(zone_id) or _FixedDateTimeZone._get_fixed_zone_or_null(zone_id)

    def __get_zone_from_source_or_none(self, zone_id: str) -> DateTimeZone | None:
        if zone_id not in self.__time_zone_map:
            return None

        if (zone := self.__time_zone_map.get(zone_id)) is None:
            if (zone := self.__source.for_id(zone_id)) is None:
                raise InvalidDateTimeZoneSourceError(
                    f"Time zone {zone_id} is supported by source {self.version_id} but not returned"
                )
            self.__time_zone_map[zone_id] = zone

        return zone

    def __getitem__(self, zone_id: str) -> DateTimeZone:
        if (zone := self.get_zone_or_none(zone_id)) is None:
            from pyoda_time.time_zones._fixed_date_time_zone import _FixedDateTimeZone

            if (zone := _FixedDateTimeZone._get_fixed_zone_or_null(zone_id)) is None:
                raise DateTimeZoneNotFoundError(f"Time zone {zone_id} is unknown to source {self.version_id}")
        return zone
