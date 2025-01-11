# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING

from .._ambiguous_time_error import AmbiguousTimeError
from .._duration import Duration
from .._offset_date_time import OffsetDateTime
from .._skipped_time_error import SkippedTimeError
from .._zoned_date_time import ZonedDateTime
from ..utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from .._date_time_zone import DateTimeZone
    from .._local_date_time import LocalDateTime
    from . import ZoneInterval, ZoneLocalMapping
    from ._delegates import AmbiguousTimeResolver, SkippedTimeResolver, ZoneLocalMappingResolver


class __ResolversMeta(type):
    __strict_resolver: ZoneLocalMappingResolver | None = None
    __lenient_resolver: ZoneLocalMappingResolver | None = None

    @staticmethod
    def return_earlier(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
        """An ``AmbiguousTimeResolver`` which returns the earlier of the two matching times."""
        return earlier

    @staticmethod
    def return_later(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
        """An ``AmbiguousTimeResolver`` which returns the later of the two matching times."""
        return later

    @staticmethod
    def throw_when_ambiguous(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
        """An ``AmbiguousTimeResolver`` which simply raises an ``AmbiguousTimeError``."""
        raise AmbiguousTimeError(earlier, later)

    @staticmethod
    def return_end_of_interval_before(
        local_date_time: LocalDateTime,
        zone: DateTimeZone,
        interval_before: ZoneInterval,
        interval_after: ZoneInterval,
    ) -> ZonedDateTime:
        """A ``SkippedTimeResolver`` which returns the final tick of the time zone interval before the "gap"."""
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(interval_before, "interval_before")
        _Preconditions._check_not_null(interval_after, "interval_after")
        # Given that there's a zone after before, it can't extend to the end of time.
        return ZonedDateTime(
            instant=interval_before.end - Duration.epsilon, zone=zone, calendar=local_date_time.calendar
        )

    @staticmethod
    def return_start_of_interval_after(
        local_date_time: LocalDateTime,
        zone: DateTimeZone,
        interval_before: ZoneInterval,
        interval_after: ZoneInterval,
    ) -> ZonedDateTime:
        """A ``SkippedTimeResolver`` which returns the first tick of the time zone interval after the "gap"."""
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(interval_before, "interval_before")
        _Preconditions._check_not_null(interval_after, "interval_after")
        return ZonedDateTime(instant=interval_after.start, zone=zone, calendar=local_date_time.calendar)

    @staticmethod
    def return_forward_shifted(
        local_date_time: LocalDateTime,
        zone: DateTimeZone,
        interval_before: ZoneInterval,
        interval_after: ZoneInterval,
    ) -> ZonedDateTime:
        """A ``SkippedTimeResolver`` which shifts values in the "gap" forward by the duration of the gap (which is
        usually 1 hour).

        This corresponds to the instant that would have occured, had there not been a transition.
        """
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(interval_before, "interval_before")
        _Preconditions._check_not_null(interval_after, "interval_after")
        return ZonedDateTime._ctor(
            offset_date_time=OffsetDateTime(
                local_date_time=local_date_time,
                offset=interval_before.wall_offset,
            ).with_offset(interval_after.wall_offset),
            zone=zone,
        )

    @staticmethod
    def throw_when_skipped(
        local_date_time: LocalDateTime,
        zone: DateTimeZone,
        interval_before: ZoneInterval,
        interval_after: ZoneInterval,
    ) -> ZonedDateTime:
        """A ``SkippedTimeResolver`` which simply throws a ``SkippedTimeError``."""
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(interval_before, "interval_before")
        _Preconditions._check_not_null(interval_after, "interval_after")
        raise SkippedTimeError(local_date_time, zone)

    @property
    def strict_resolver(self) -> ZoneLocalMappingResolver:
        """A ``ZoneLocalMappingResolver`` which only ever succeeds in the (usual) case where the result of the mapping
        is unambiguous.

        If the mapping is ambiguous or skipped, this raises ``SkippedTimeError`` or ``AmbiguousTimeError`` as
        appropriate.

        This resolver combines ``throw_when_ambiguous`` and ``throw_when_skipped``.

        :return: A ``ZoneLocalMappingResolver`` which only ever succeeds in the (usual) case where the result of the
            mapping is unambiguous.
        """
        if (strict_resolver := self.__strict_resolver) is None:
            strict_resolver = self.__strict_resolver = self.create_mapping_resolver(
                ambiguous_time_resolver=self.throw_when_ambiguous, skipped_time_resolver=self.throw_when_skipped
            )
        return strict_resolver

    @property
    def lenient_resolver(self) -> ZoneLocalMappingResolver:
        """A ``ZoneLocalMappingResolver`` which never raises an exception due to ambiguity or skipped time.

        Ambiguity is handled by returning the earlier occurrence, and skipped times are shifted forward by the duration
        of the gap. This resolver combines ``return_earlier`` and ``return_forward_shifted``.

        :return: A ``ZoneLocalMappingResolver`` which never throws an exception due to ambiguity or skipped time.
        """
        if (lenient_resolver := self.__lenient_resolver) is None:
            lenient_resolver = self.__lenient_resolver = self.create_mapping_resolver(
                ambiguous_time_resolver=self.return_earlier,
                skipped_time_resolver=self.return_forward_shifted,
            )
        return lenient_resolver

    @staticmethod
    def create_mapping_resolver(
        ambiguous_time_resolver: AmbiguousTimeResolver, skipped_time_resolver: SkippedTimeResolver
    ) -> ZoneLocalMappingResolver:
        """Combines an ``AmbiguousTimeResolver`` and a ``SkippedTimeResolver`` to create a ``ZoneLocalMappingResolver``.

        The ``ZoneLocalMappingResolver`` created by this method operates in the obvious way: unambiguous mappings
        are returned directly, ambiguous mappings are delegated to the given ``AmbiguousTimeResolver``, and
        "skipped" mappings are delegated to the given ``SkippedTimeResolver``.

        :param ambiguous_time_resolver: Resolver to use for ambiguous mappings.
        :param skipped_time_resolver: Resolver to use for "skipped" mappings.
        :return: The logical combination of the two resolvers.
        """
        _Preconditions._check_not_null(ambiguous_time_resolver, "ambiguous_time_resolver")
        _Preconditions._check_not_null(skipped_time_resolver, "skipped_time_resolver")

        def func(mapping: ZoneLocalMapping) -> ZonedDateTime:
            match _Preconditions._check_not_null(mapping, "mapping").count:
                case 0:
                    return skipped_time_resolver(
                        mapping.local_date_time, mapping.zone, mapping.early_interval, mapping.late_interval
                    )
                case 1:
                    return mapping.first()
                case 2:
                    return ambiguous_time_resolver(mapping.first(), mapping.last())
                case _:
                    raise ValueError("Mapping has count outside range 0-2; should not happen.")

        return func


class Resolvers(metaclass=__ResolversMeta):
    """Commonly-used implementations of the delegates used in resolving a ``LocalDateTime`` to a ``ZonedDateTime``, and
    a method to combine two "partial" resolvers into a full one.

    This class contains predefined implementations of ``ZoneLocalMappingResolver``, ``AmbiguousTimeResolver``, and
    ``SkippedTimeResolver``, along with ``CreateMappingResolver``, which produces a ``ZoneLocalMappingResolver``
    from instances of the other two.
    """
