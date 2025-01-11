# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import threading
from typing import TYPE_CHECKING, Final, _ProtocolMeta, overload

from ._duration import Duration
from ._instant import Instant
from ._offset import Offset
from ._offset_date_time import OffsetDateTime
from ._pyoda_constants import PyodaConstants
from ._skipped_time_error import SkippedTimeError
from ._zoned_date_time import ZonedDateTime
from .time_zones import Resolvers, ZoneLocalMappingResolver
from .time_zones._i_zone_interval_map import _IZoneIntervalMap
from .time_zones._zone_local_mapping import ZoneLocalMapping
from .utility._csharp_compatibility import _csharp_modulo, _towards_zero_division
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Generator

    from ._interval import Interval
    from ._local_date import LocalDate
    from ._local_date_time import LocalDateTime
    from ._local_instant import _LocalInstant
    from .time_zones._zone_interval import ZoneInterval

__all__ = ["DateTimeZone"]


class _DateTimeZoneMeta(_ProtocolMeta, type):
    __lock: Final[threading.Lock] = threading.Lock()
    __utc: DateTimeZone | None = None

    @property
    def utc(cls) -> DateTimeZone:
        """Gets the UTC (Coordinated Universal Time) time zone.

        This is a single instance which is not provider-specific; it is guaranteed to have the ID "UTC", and to
        compare equal to an instance returned by calling ``for_offset`` with an offset of zero, but it may
        or may not compare equal to an instance returned by e.g. ``DateTimeZoneProviders.Tzdb["UTC"]``.

        :return: The UTC ``DateTimeZone``.
        """
        if not cls.__utc:
            with cls.__lock:
                if not cls.__utc:
                    from .time_zones._fixed_date_time_zone import _FixedDateTimeZone

                    cls.__utc = _FixedDateTimeZone(Offset.zero)
        return cls.__utc


class DateTimeZone(abc.ABC, _IZoneIntervalMap, metaclass=_DateTimeZoneMeta):
    """Represents a time zone - a mapping between UTC and local time.
    A time zone maps UTC instants to local times - or, equivalently, to the offset from UTC at any particular instant.
    """

    _UTC_ID: Final[str] = "UTC"
    __FIXED_ZONE_CACHE_GRANULARITY_SECONDS: Final[int] = PyodaConstants.SECONDS_PER_MINUTE * 30
    __FIXED_ZONE_CACHE_MINIMUM_SECONDS: Final[int] = -__FIXED_ZONE_CACHE_GRANULARITY_SECONDS * 12 * 2  # From UTC-12
    __FIXED_ZONE_CACHE_SIZE: Final[int] = (12 + 15) * 2 + 1  # To UTC+15 inclusive

    # Unlike in Noda Time, this cache is not built up-front, because doing so would require the ability to import
    # _FixedDateTimeZone inside this class body, which is impossible in Python. This cache is only used by the
    # `for_offset()` classmethod, so we just call `__build_fixed_zone_cache()` there instead.
    __fixed_zone_cache: list[DateTimeZone] | None = None

    @classmethod
    def for_offset(cls, offset: Offset) -> DateTimeZone:
        """Returns a fixed time zone with the given offset.

        The returned time zone will have an ID of "UTC" if the offset is zero, or "UTC+/-Offset"
        otherwise. In the former case, the returned instance will be equal to ``DateTimeZone.utc``.

        Note also that this method is not required to return the same ``DateTimeZone`` instance for
        successive requests for the same offset; however, all instances returned for a given offset will compare
        as equal.

        :param offset: The offset for the returned time zone
        :return: A fixed time zone with the given offset.
        """
        # Unlike in Noda Time, build the cache if it is empty.
        if not cls.__fixed_zone_cache:
            cls.__fixed_zone_cache = cls.__build_fixed_zone_cache()

        from .time_zones._fixed_date_time_zone import _FixedDateTimeZone

        seconds: int = offset.seconds
        if _csharp_modulo(seconds, cls.__FIXED_ZONE_CACHE_GRANULARITY_SECONDS) != 0:
            return _FixedDateTimeZone(offset=offset)
        index: int = _towards_zero_division(
            seconds - cls.__FIXED_ZONE_CACHE_MINIMUM_SECONDS, cls.__FIXED_ZONE_CACHE_GRANULARITY_SECONDS
        )
        if index < 0 or index >= cls.__FIXED_ZONE_CACHE_SIZE:
            return _FixedDateTimeZone(offset=offset)
        return cls.__fixed_zone_cache[index]

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

    def at_start_of_day(self, date: LocalDate) -> ZonedDateTime:
        """Returns the earliest valid `ZonedDateTime` with the given local date.

        If midnight exists unambiguously on the given date, it is returned.
        If the given date has an ambiguous start time (e.g. the clocks go back from 1am to midnight)
        then the earlier ZonedDateTime is returned. If the given date has no midnight (e.g. the clocks
        go forward from midnight to 1am) then the earliest valid value is returned; this will be the instant
        of the transition.

        :param date: The local date to map in this time zone.
        :raises SkippedTimeError: The entire day was skipped due to a very large time zone transition. (This is
            extremely rare.)
        :return: The `ZonedDateTime` representing the earliest time in the given date, in this time zone.
        """
        midnight: LocalDateTime = date.at_midnight()
        mapping = self.map_local(local_date_time=midnight)
        match mapping.count:
            # Midnight doesn't exist. Maybe we just skip to 1am (or whatever), or maybe the whole day is missed.
            case 0:
                interval = mapping.late_interval
                # Safe to use Start, as it can't extend to the start of time.
                offset_date_time = OffsetDateTime._ctor(
                    instant=interval.start, offset=interval.wall_offset, calendar=date.calendar
                )
                # It's possible that the entire day is skipped. For example, Samoa skipped December 30th 2011.
                # We know the two values are in the same calendar here, so we just need to check the YearMonthDay.
                if offset_date_time._year_month_day != date._year_month_day:
                    raise SkippedTimeError(local_date_time=midnight, zone=self)
                return ZonedDateTime._ctor(offset_date_time=offset_date_time, zone=self)
            # Unambiguous or occurs twice, we can just use the offset from the earlier interval.
            case 1 | 2:
                return ZonedDateTime._ctor(
                    offset_date_time=midnight.with_offset(mapping.early_interval.wall_offset), zone=self
                )
            case _:
                raise RuntimeError("This won't happen.")

    def resolve_local(self, local_date_time: LocalDateTime, resolver: ZoneLocalMappingResolver) -> ZonedDateTime:
        """Maps the given ``LocalDateTime`` to the corresponding ``ZonedDateTime``, following the given
        ``ZoneLocalMappingResolver`` to handle ambiguity and skipped times.

        This is a convenience method for calling ``map_local`` and passing the result to the resolver.
        Common options for resolvers are provided in the static ``Resolvers`` class.

        See ``at_strictly`` and ``at_leniently`` for alternative ways to map a local time to a specific instant.

        :param local_date_time: The local date and time to map in this time zone.
        :param resolver: The resolver to apply to the mapping.
        :return: The result of resolving the mapping.
        """
        _Preconditions._check_not_null(resolver, "resolver")
        return resolver(self.map_local(local_date_time=local_date_time))

    def at_strictly(self, local_date_time: LocalDateTime) -> ZonedDateTime:
        """Maps the given ``LocalDateTime`` to the corresponding ``ZonedDateTime``, if and only if that mapping is
        unambiguous in this time zone.  Otherwise, ``SkippedTimeError`` or ``AmbiguousTimeException`` is thrown,
        depending on whether the mapping is ambiguous or the local date/time is skipped entirely.

        See ``at_leniently`` and ``resolve_local(LocalDateTime, ZoneLocalMappingResolver)`` for alternative ways to map
        a local time to a specific instant.

        :param local_date_time: The local date and time to map into this time zone.
        :raises SkippedTimeError: The given local date/time is skipped in this time zone.
        :raises AmbiguousTimeError: The given local date/time is ambiguous in this time zone.
        :return: The unambiguous matching ``ZonedDateTime`` if it exists.
        """
        return self.resolve_local(
            local_date_time=local_date_time,
            resolver=Resolvers.strict_resolver,
        )

    def at_leniently(self, local_date_time: LocalDateTime) -> ZonedDateTime:
        """Maps the given ``LocalDateTime`` to the corresponding ``ZonedDateTime`` in a lenient manner.

        Ambiguous values map to the earlier of the alternatives, and "skipped" values are shifted forward by the
        duration of the "gap".

        See ``at_strictly`` and ``resolve_local(LocalDateTime, ZoneLocalMappingResolver) for alternative ways to map a
        local time to a specific instant.

        :param local_date_time: The local date/time to map.
        :return: The unambiguous mapping if there is one, the earlier result if the mapping is ambiguous, or the
        forward-shifted value if the given local date/time is skipped.
        """
        return self.resolve_local(local_date_time=local_date_time, resolver=Resolvers.lenient_resolver)

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
        if local_instant._minus(guess_interval.wall_offset) < guess_interval._raw_start:
            return self.get_zone_interval(guess_interval.start - Duration.epsilon)
        return guess_interval

    def __get_interval_after_gap(self, local_instant: _LocalInstant) -> ZoneInterval:
        guess: Instant = local_instant._minus_zero_offset()
        guess_interval = self.get_zone_interval(guess)
        # If the local interval occurs before the zone interval we're looking at starts,
        # it's the one we're looking for. Otherwise, we need to find the next interval.
        if local_instant._minus(guess_interval.wall_offset) < guess_interval._raw_start:
            return guess_interval
        else:
            # Will definitely be valid - there can't be a gap after an infinite interval.
            return self.get_zone_interval(guess_interval.end)

    # region Object overrides

    def __repr__(self) -> str:
        """Returns the ID of this time zone.

        :return: The ID of this time zone.
        """
        return self.id

    # endregion

    @classmethod
    def __build_fixed_zone_cache(cls) -> list[DateTimeZone]:
        """Creates a fixed time zone for offsets -12 to +15 at every half hour, fixing the 0 offset as
        DateTimeZone.utc."""
        from .time_zones._fixed_date_time_zone import _FixedDateTimeZone

        ret: list[DateTimeZone] = [
            _FixedDateTimeZone(
                offset=Offset.from_seconds(
                    i * cls.__FIXED_ZONE_CACHE_GRANULARITY_SECONDS + cls.__FIXED_ZONE_CACHE_MINIMUM_SECONDS
                )
            )
            for i in range(cls.__FIXED_ZONE_CACHE_SIZE)
        ]
        ret[
            _towards_zero_division(-cls.__FIXED_ZONE_CACHE_MINIMUM_SECONDS, cls.__FIXED_ZONE_CACHE_GRANULARITY_SECONDS)
        ] = cls.utc
        return ret

    @overload
    def get_zone_intervals(self, *, start: Instant, end: Instant) -> Generator[ZoneInterval]: ...

    @overload
    def get_zone_intervals(self, *, interval: Interval) -> Generator[ZoneInterval]: ...

    # TODO:
    #  @overload
    #  def get_zone_intervals(self, *, interval: Interval, options: ZoneEqualityComparer.Options) -> Generator[ZoneInterval]:  # noqa: E501
    #      ...

    def get_zone_intervals(
        self,
        *,
        interval: Interval | None = None,
        start: Instant | None = None,
        end: Instant | None = None,
    ) -> Generator[ZoneInterval]:
        if start is not None and end is not None and interval is None:
            from ._interval import Interval

            interval = Interval(start=start, end=end)
        if interval is not None:

            def gen() -> Generator[ZoneInterval]:
                current = interval.start if interval.has_start else Instant.min_value
                end = interval._raw_end
                while current < end:
                    zone_interval = self.get_zone_interval(current)
                    yield zone_interval
                    # If this is the end of time, this will just fail on the next comparison.
                    current = zone_interval._raw_end

            return gen()
        raise TypeError("Called with incorrect arguments")
