# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time import Instant, Offset
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.time_zones._transition import _Transition
from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _CsharpConstants, _private, _sealed
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class _StandardDaylightAlternatingMap:
    """Provides a zone interval map representing an infinite sequence of standard/daylight transitions from a pair of
    rules.

    IMPORTANT: This class *accepts* recurrences which start from a particular year
    rather than being infinite back to the start of time, but *treats* them as if
    they were infinite. This makes various calculations easier, but this map should
    only be used as part of a zone which will only ask it for values within the right
    portion of the timeline.
    """

    __standard_offset: Offset
    __standard_recurrence: _ZoneRecurrence
    __dst_recurrence: _ZoneRecurrence

    @property
    def min_offset(self) -> Offset:
        return Offset.min(self.__standard_offset, self.__standard_offset + self.__dst_recurrence.savings)

    @property
    def max_offset(self) -> Offset:
        return Offset.max(self.__standard_offset, self.__standard_offset + self.__dst_recurrence.savings)

    @classmethod
    def _ctor(
        cls, standard_offset: Offset, start_recurrence: _ZoneRecurrence, end_recurrence: _ZoneRecurrence
    ) -> _StandardDaylightAlternatingMap:
        """Initializes a new instance of the ``_StandardDaylightAlternatingMap`` class.

        At least one of the recurrences (it doesn't matter which) must be a "standard", i.e. not have any savings
        applied. The other may still not have any savings (e.g. for America/Resolute) or (for BCL compatibility) may
        even have negative daylight savings.

        :param standard_offset: The standard offset.
        :param start_recurrence: The start recurrence.
        :param end_recurrence: The end recurrence.
        :return: The initialized ``_StandardDaylightAlternatingMap`` instance.
        """
        self = super().__new__(cls)
        self.__standard_offset = standard_offset
        # Treat the recurrences as if they extended to the start of time.
        start_recurrence = start_recurrence._to_start_of_time()
        end_recurrence = end_recurrence._to_start_of_time()
        _Preconditions._check_argument(
            start_recurrence.is_infinite, "start_recurrence", "Start recurrence must extend to the end of time"
        )
        _Preconditions._check_argument(
            end_recurrence.is_infinite, "end_recurrence", "End recurrence must extend to the end of time"
        )
        dst = start_recurrence
        standard = end_recurrence
        if start_recurrence.savings == Offset.zero:
            dst = end_recurrence
            standard = start_recurrence
        _Preconditions._check_argument(
            standard.savings == Offset.zero, "start_recurrence", "At least one recurrence must not have savings applied"
        )
        self.__dst_recurrence = dst
        self.__standard_recurrence = standard
        return self

    def equals(self, other: _StandardDaylightAlternatingMap) -> bool:
        return self == other

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _StandardDaylightAlternatingMap):
            return NotImplemented
        return (
            self.__standard_offset == other.__standard_offset
            and self.__dst_recurrence == other.__dst_recurrence
            and self.__standard_recurrence == other.__standard_recurrence
            and self.__standard_recurrence == other.__standard_recurrence
        )

    def __hash__(self) -> int:
        return _hash_code_helper(
            self.__standard_offset,
            self.__dst_recurrence,
            self.__standard_recurrence,
        )

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        """Gets the zone interval for the given instant.

        :param instant: The Instant to test.
        :return: The ZoneInterval in effect at the given instant.
        """
        next_, recurrence = self.__next_transition(instant)
        # Now we know the recurrence we're in, we can work out when we went into it. (We'll never have
        # two transitions into the same recurrence in a row.)
        previous_savings: Offset = (
            self.__dst_recurrence.savings if recurrence is self.__standard_recurrence else Offset.zero
        )
        previous = recurrence._previous_or_same_or_fail(instant, self.__standard_offset, previous_savings)
        return ZoneInterval(
            name=recurrence.name,
            start=previous._instant,
            end=next_._instant,
            wall_offset=self.__standard_offset + recurrence.savings,
            savings=recurrence.savings,
        )

    def __next_transition(self, instant: Instant) -> tuple[_Transition, _ZoneRecurrence]:
        """Returns the transition occurring strictly after the specified instant.

        The ``recurrence`` parameter will be populated with the recurrence the transition goes *from*.

        :param instant: The instant after which to consider transitions.
        :return: Receives the savings offset for the transition.
        """
        # Both recurrences are infinite, so they'll both have next transitions (possibly at infinity).
        dst_transition: _Transition = self.__dst_recurrence._next_or_fail(instant, self.__standard_offset, Offset.zero)
        standard_transition: _Transition = self.__standard_recurrence._next_or_fail(
            instant, self.__standard_offset, self.__dst_recurrence.savings
        )

        standard_transition_instant = standard_transition._instant
        dst_transition_instant = dst_transition._instant

        if standard_transition_instant < dst_transition_instant:
            # Next transition is from DST to standard.
            return standard_transition, self.__dst_recurrence

        if standard_transition_instant > dst_transition_instant:
            # Next transition is from standard to DST.
            return dst_transition, self.__standard_recurrence

        # Okay, the transitions happen at the same time. If they're not at infinity, we're stumped.
        if standard_transition_instant._is_valid:
            raise RuntimeError(
                f"Zone recurrence rules have identical transitions. "
                f"This time zone is broken. Transition time: {standard_transition_instant}"
            )

        # Okay, the two transitions must be to the end of time.
        # Find which recurrence has the later *previous* transition...
        previous_dst_transition = self.__dst_recurrence._previous_or_same_or_fail(
            instant, self.__standard_offset, Offset.zero
        )
        previous_standard_transition = self.__standard_recurrence._previous_or_same_or_fail(
            instant, self.__standard_offset, self.__dst_recurrence.savings
        )

        # No point in checking for equality here... they can't go back from the end of time to the start...
        if previous_dst_transition._instant > previous_standard_transition._instant:
            # The previous transition is from standard to DST. Therefore the next one is from DST to standard.
            return standard_transition, self.__dst_recurrence

        # The previous transition is from DST to standard. Therefore the next one is from standard to DST.
        return dst_transition, self.__standard_recurrence

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        """Writes the time zone to the specified writer.

        :param writer: The writer to write to.
        """
        # We don't need everything a recurrence can supply: we know that both recurrences should be
        # infinite, and that only the DST recurrence should have savings.
        _Preconditions._check_not_null(writer, "writer")
        writer.write_offset(self.__standard_offset)
        writer.write_string(self.__standard_recurrence.name)
        self.__standard_recurrence.year_offset._write(writer)
        writer.write_string(self.__dst_recurrence.name)
        self.__dst_recurrence.year_offset._write(writer)
        writer.write_offset(self.__dst_recurrence.savings)

    @classmethod
    def _read(cls, reader: _IDateTimeZoneReader) -> _StandardDaylightAlternatingMap:
        _Preconditions._check_not_null(reader, "reader")
        standard_offset = reader.read_offset()
        standard_name = reader.read_string()
        standard_year_offset = _ZoneYearOffset.read(reader)
        daylight_name = reader.read_string()
        daylight_year_offset = _ZoneYearOffset.read(reader)
        savings = reader.read_offset()
        standard_recurrence = _ZoneRecurrence(
            standard_name,
            Offset.zero,
            standard_year_offset,
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        )
        dst_recurrence = _ZoneRecurrence(
            daylight_name, savings, daylight_year_offset, _CsharpConstants.INT_MIN_VALUE, _CsharpConstants.INT_MAX_VALUE
        )
        return _StandardDaylightAlternatingMap._ctor(standard_offset, standard_recurrence, dst_recurrence)
