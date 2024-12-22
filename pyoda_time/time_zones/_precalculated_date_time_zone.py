# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, cast, final

from pyoda_time._date_time_zone import DateTimeZone
from pyoda_time._instant import Instant
from pyoda_time._offset import Offset
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.time_zones._standard_daylight_alternating_map import _StandardDaylightAlternatingMap
from pyoda_time.utility._csharp_compatibility import _sealed, _towards_zero_division
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyoda_time.time_zones._i_zone_interval_map import _IZoneIntervalMap
    from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
    from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter


@final
@_sealed
class _PrecalculatedDateTimeZone(DateTimeZone):
    """Most time zones have a relatively small set of transitions at their start until they finally settle down to
    either a fixed time zone or a daylight savings time zone.

    This provides the container for the initial zone intervals and a pointer to the time zone that handles all of the
    rest until the end of time.
    """

    __periods: list[ZoneInterval]
    __tail_zone: _IZoneIntervalMap | None
    __tail_zone_start: Instant
    """The first instant covered by the tail zone, or Instant.AfterMaxValue if there's no tail zone."""
    __first_tail_zone_interval: ZoneInterval | None

    def __init__(self, id_: str, intervals: list[ZoneInterval], tail_zone: _IZoneIntervalMap | None) -> None:
        """Initializes a new instance of the ``_PrecalculatedDateTimeZone`` class.

        :param id_: The id.
        :param intervals: The intervals before the tail zone.
        :param tail_zone: The tail zone - which can be any IZoneIntervalMap for normal operation,
            but must be a StandardDaylightAlternatingMap if the result is to be serialized.
        """
        super().__init__(
            id_,
            False,
            self.__compute_offset(intervals, tail_zone, Offset.min),
            self.__compute_offset(intervals, tail_zone, Offset.max),
        )
        self.__periods = intervals
        self.__tail_zone = tail_zone
        self.__tail_zone_start = intervals[-1]._raw_end  # We want this to be AfterMaxValue for tail-less zones.
        if tail_zone is not None:
            self.__first_tail_zone_interval = tail_zone.get_zone_interval(self.__tail_zone_start)._with_start(
                self.__tail_zone_start
            )
        else:
            self.__first_tail_zone_interval = None
        self._validate_periods(intervals, tail_zone)

    @staticmethod
    def _validate_periods(periods: list[ZoneInterval], tail_zone: _IZoneIntervalMap | None) -> None:
        """Validates that all the periods before the tail zone make sense. We have to start at the beginning of time,
        and then have adjoining periods. This is only called in the constructors.

        This is only called from the constructors, but is internal to make it easier to test.

        :raises ValueError: The periods specified are invalid.
        """
        _Preconditions._check_argument(len(periods) > 0, "periods", "No periods specified in precalculated time zone")
        _Preconditions._check_argument(
            not periods[0].has_start,
            "periods",
            "Periods in precalculated time zone must start with the beginning of time",
        )
        for i in range(len(periods) - 1):
            # Safe to use End here: there can't be a period *after* an endless one.
            # Likewise it's safe to use Start on the next period, as there can't be
            # a period *before* one which goes back to the start of time.
            _Preconditions._check_argument(
                periods[i].end == periods[i + 1].start,
                "periods",
                "Non-adjoining ZoneIntervals for precalculated time zone",
            )
        _Preconditions._check_argument(
            tail_zone is not None or periods[-1]._raw_end == Instant._after_max_value(),
            "tail_zone",
            "Null tail zone given but periods don't cover all of time",
        )

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        """Gets the zone offset period for the given instant.

        :param instant: The Instant to find.
        :return: The ZoneInterval including the current instant.
        """
        if self.__tail_zone is not None and instant >= self.__tail_zone_start:
            # Clamp the tail zone interval to start at the end of our final period, if necessary, so that the
            # join is seamless.
            interval_from_tail_zone: ZoneInterval = self.__tail_zone.get_zone_interval(instant)
            return (
                cast(ZoneInterval, self.__first_tail_zone_interval)
                if interval_from_tail_zone._raw_start < self.__tail_zone_start
                else interval_from_tail_zone
            )

        lower = 0  # Inclusive
        upper = len(self.__periods)  # Exclusive

        while lower < upper:
            current = _towards_zero_division(lower + upper, 2)
            candidate = self.__periods[current]
            if candidate._raw_start > instant:
                upper = current
            # Safe to use RawEnd, as it's just for the comparison.
            elif candidate._raw_end <= instant:
                lower = current + 1
            else:
                return candidate
        # Note: this would indicate a bug. The time zone is meant to cover the whole of time.
        raise RuntimeError(f"Instant {instant} did not exist in time zone {self.id}")

    # region I/O

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        """Writes the time zone to the specified writer.

        :param writer: The writer to write to.
        """
        _Preconditions._check_not_null(writer, "writer")

        # We used to create a pool of strings just for this zone. This was more efficient
        # for some zones, as it meant that each string would be written out with just a single
        # byte after the pooling. Optimizing the string pool globally instead allows for
        # roughly the same efficiency, and simpler code here.
        writer.write_count(len(self.__periods))
        previous: Instant | None = None
        for period in self.__periods:
            writer.write_zone_interval_transition(previous, previous := period._raw_start)
            writer.write_string(period.name)
            writer.write_offset(period.wall_offset)
            writer.write_offset(period.savings)

        writer.write_zone_interval_transition(previous, self.__tail_zone_start)
        # We could just check whether we've got to the end of the stream, but this
        # feels slightly safer.
        writer.write_byte(0 if self.__tail_zone is None else 1)
        if self.__tail_zone is not None:
            # TODO: In Noda Time, this is done with a cast...
            # This is the only kind of zone we support in the new format. Enforce that...
            if not isinstance(self.__tail_zone, _StandardDaylightAlternatingMap):
                raise RuntimeError(f"Only {_StandardDaylightAlternatingMap.__name__} is supported")
            self.__tail_zone._write(writer)

    @classmethod
    def _read(cls, reader: _IDateTimeZoneReader, id_: str) -> DateTimeZone:
        """Reads a time zone from the specified reader.

        :param reader: The reader.
        :param id_: The id.
        :return: The time zone.
        """
        # TODO:
        #  Preconditions.DebugCheckNotNull(reader, nameof(reader));
        #  Preconditions.DebugCheckNotNull(id, nameof(id));
        size = reader.read_count()
        periods: list[ZoneInterval] = []
        # It's not entirely clear why we don't just assume that the first zone interval always starts at
        # Instant.BeforeMinValue (given that we check that later) but we don't... and changing that now could cause
        # compatibility issues.
        start = reader.read_zone_interval_transition(None)
        for i in range(size):
            name = reader.read_string()
            offset = reader.read_offset()
            savings = reader.read_offset()
            next_start = reader.read_zone_interval_transition(start)
            periods.append(ZoneInterval(name=name, start=start, end=next_start, wall_offset=offset, savings=savings))
            start = next_start
        tail_zone = _StandardDaylightAlternatingMap._read(reader) if reader.read_byte() == 1 else None
        return _PrecalculatedDateTimeZone(id_=id_, intervals=periods, tail_zone=tail_zone)

    # endregion

    # region Offset computation for constructors

    @staticmethod
    def __compute_offset(
        intervals: list[ZoneInterval],
        tail_zone: _IZoneIntervalMap | None,
        aggregator: Callable[[Offset, Offset], Offset],
    ) -> Offset:
        """Reasonably simple way of computing the maximum/minimum offset from either periods or transitions, with or
        without a tail zone."""
        _Preconditions._check_not_null(intervals, "intervals")
        _Preconditions._check_argument(len(intervals) > 0, "intervals", "No intervals specified")
        ret: Offset = intervals[0].wall_offset
        for i in range(len(intervals)):
            ret = aggregator(ret, intervals[i].wall_offset)
        if tail_zone is not None:
            # Effectively a shortcut for picking either tailZone.MinOffset or
            # tailZone.MaxOffset
            best_from_zone: Offset = aggregator(tail_zone.min_offset, tail_zone.max_offset)
            ret = aggregator(ret, best_from_zone)
        return ret

    # endregion
