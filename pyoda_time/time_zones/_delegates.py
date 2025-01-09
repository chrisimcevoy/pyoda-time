# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pyoda_time import DateTimeZone, LocalDateTime, ZonedDateTime
    from pyoda_time.time_zones import ZoneInterval, ZoneLocalMapping


class AmbiguousTimeResolver(Protocol):
    """Chooses between two ``ZonedDateTime`` values that resolve to the same ``LocalDateTime``.

    This delegate is used by ``Resolvers.create_mapping_resolver`` when handling an ambiguous local time,
    due to clocks moving backward in a time zone transition (usually due to an autumnal daylight saving transition).

    The returned value should be one of the two parameter values, based on the policy of the specific
    implementation. Alternatively, it can raise an ``AmbiguousTimeError`` to implement a policy of
    "reject ambiguous times."

    See the ``Resolvers`` class for predefined implementations.

    Implementations of this delegate can reasonably assume that the target local date and time really is ambiguous;
    the behaviour when the local date and time can be unambiguously mapped into the target time zone (or when it's
    skipped) is undefined.
    """

    def __call__(self, earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
        """Chooses between two ``ZonedDateTime`` values that resolve to the same ``LocalDateTime``.

        :param earlier: The earlier of the ambiguous matches for the original local date and time.
        :param later: The later of the ambiguous matches for the original local date and time.
        :raises AmbiguousTimeError: The implementation rejects requests to map ambiguous times.
        :return: A ``ZonedDateTime`` in the target time zone; typically, one of the two input parameters.
        """


class SkippedTimeResolver(Protocol):
    """Resolves a ``LocalDateTime`` to a ``ZonedDateTime`` in the situation where the requested local time does not
    exist in the target time zone.

    This delegate is used by ``Resolvers.create_mapping_resolver`` when handling the situation where the
    requested local time does not exist, due to clocks moving forward in a time zone transition (usually due to a
    spring daylight saving transition).

    The returned value will necessarily represent a different local date and time to the target one, but
    the exact form of mapping is up to the delegate implementation. For example, it could return a value
    as close to the target local date and time as possible, or the time immediately after the transition.
    Alternatively, it can throw a ``SkippedTimeError`` to implement a policy of "reject
    skipped times."

    See the ``Resolvers`` class for predefined implementations.

    Implementations of this delegate can reasonably
    assume that the target local date and time really is skipped; the behaviour when the local date and time
    can be directly mapped into the target time zone is undefined.
    """

    def __call__(
        self,
        local_date_time: LocalDateTime,
        zone: DateTimeZone,
        interval_before: ZoneInterval,
        interval_after: ZoneInterval,
    ) -> ZonedDateTime:
        """

        :param local_date_time: The local date and time to map to the given time zone.
        :param zone: The target time zone.
        :param interval_before: The zone interval directly before the target local date and time would have occurred.
        :param interval_after: The zone interval directly after the target local date and time would have occurred.
        :raises SkippedTimeError: The implementation rejects requests to map skipped times.
        :return: A ``ZonedDateTime`` in the target time zone.
        """


class ZoneLocalMappingResolver(Protocol):
    """Resolves the result of attempting to map a local date and time to a target time zone.

    This delegate is consumed by ``LocalDateTime.in_zone`` and
    ``DateTimeZone.resolve_local(LocalDateTime, ZoneLocalMappingResolver)``,
    among others. It provides the strategy for converting a ``ZoneLocalMapping`` (the result of attempting
    to map a local date and time to a target time zone) to a ``ZonedDateTime``.

    See the ``Resolvers`` class for predefined implementations and a way of combining
    separate ``SkippedTimeResolver`` and ``AmbiguousTimeResolver`` values.
    """

    def __call__(self, mapping: ZoneLocalMapping) -> ZonedDateTime:
        """Resolves the result of attempting to map a local date and time to a target time zone.

        :param mapping: The intermediate result of mapping a local time to a target time zone.
        :raises AmbiguousTimeError: The implementation rejects requests to map ambiguous times.
        :raises SkippedTimeError: The implementation rejects requests to map skipped times.
        :return: A ``ZonedDateTime`` in the target time zone.
        """


__all__ = [
    "AmbiguousTimeResolver",
    "SkippedTimeResolver",
    "ZoneLocalMappingResolver",
]
