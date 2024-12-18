# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pyoda_time._date_time_zone import DateTimeZone


class IDateTimeZoneProvider(Protocol):
    """Provides stable, performant time zone data.

    Consumers should be able to treat an ``IDateTimeZoneProvider`` like a cache:
    lookups should be quick (after at most one lookup of a given ID), and multiple calls for a given ID must
    always return references to equal instances, even if they are not references to a single instance.
    Consumers should not feel the need to cache data accessed through this interface.

    Implementations designed to work with any ``IDateTimeZoneSource`` implementation (such as
    ``DateTimeZoneCache``) should not attempt to handle exceptions thrown by the source. A source-specific
    provider may do so, as it has more detailed knowledge of what can go wrong and how it can best be handled.
    """

    @property
    @abstractmethod
    def version_id(self) -> str:
        """Gets the version ID of this provider.

        :return: The version ID of this provider.
        """
        ...

    @property
    @abstractmethod
    def ids(self) -> Iterable[str]:
        """Gets the list of valid time zone ids advertised by this provider.

        This list will be sorted in ordinal lexicographic order. It cannot be modified by callers, and
        must not be modified by the provider either: client code can safely treat it as thread-safe
        and deeply immutable.

        In addition to the list returned here, providers always support the fixed-offset timezones with IDs "UTC"
        and "UTC+/-Offset". These may or may not be included explicitly in this list.

        :return: The ``Iterable`` of string ids.
        """
        ...

    @abstractmethod
    def get_system_default(self) -> DateTimeZone:
        """Gets the time zone from this provider that matches the system default time zone, if a matching time zone is
        available.

        Callers should be aware that this method will throw ``DateTimeZoneNotFoundError`` if no matching
        time zone is found. For the built-in Pyoda Time providers, this is unlikely to occur in practice (assuming
        the system is using a standard Windows time zone), but can occur even then, if no mapping is found. The TZDB
        source contains mappings for almost all Windows system time zones, but a few (such as "Mid-Atlantic Standard
        Time") are unmappable.

        :return: The provider-specific representation of the system default time zone.
        :raises DateTimeZoneNotFoundError: The system default time zone is not mapped by this provider.
        """
        # TODO: In Pyoda Time, the docstring discusses `BclDateTimeZone.ForSystemDefault` usage.
        ...

    @abstractmethod
    def get_zone_or_none(self, zone_id: str) -> DateTimeZone | None:
        """Returns the time zone for the given ID, if it's available.

        Note that this may return a ``DateTimeZone`` that has a different ID to that requested, if the ID
        provided is an alias.

        Note also that this method is not required to return the same ``DateTimeZone`` instance for
        successive requests for the same ID; however, all instances returned for a given ID must compare
        as equal.

        The fixed-offset timezones with IDs "UTC" and "UTC+/-Offset" are always available.

        :param zone_id: The time zone ID to find.
        :return: The ``DateTimeZone`` for the given ID or null if the provider does not support the given ID.
        """
        ...

    @abstractmethod
    def __getitem__(self, zone_id: str) -> DateTimeZone:
        """Returns the time zone for the given ID.

        Unlike ``get_zone_or_none``, this will never return None. If the ID is not
        supported by this provider, it will raise ``DateTimeZoneNotFoundException``.

        Note that this may return a ``DateTimeZone`` that has a different ID to that requested, if the ID
        provided is an alias.

        Note also that this method is not required to return the same ``DateTimeZone`` instance for
        successive requests for the same ID; however, all instances returned for a given ID must compare
        as equal.

        The fixed-offset timezones with IDs "UTC" and "UTC+/-Offset" are always available.

        :param zone_id: The time zone id to find.
        :return: The ``DateTimeZone`` for the given ID.
        :raises DateTimeZoneNotFoundError: This provider does not support the given ID.
        """
