# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

import pytest

from pyoda_time import DateTimeZone, Duration, Instant, LocalDateTime, LocalTime, Offset
from pyoda_time.testing.time_zones import SingleTransitionDateTimeZone
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.time_zones._fixed_date_time_zone import _FixedDateTimeZone
from pyoda_time.time_zones._precalculated_date_time_zone import _PrecalculatedDateTimeZone
from pyoda_time.time_zones._standard_daylight_alternating_map import _StandardDaylightAlternatingMap
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

FIRST_INTERVAL = ZoneInterval(
    name="First",
    start=Instant._before_min_value(),
    end=Instant.from_utc(2000, 3, 10, 10, 0),
    wall_offset=Offset.from_hours(3),
    savings=Offset.zero,
)

# Note that this is effectively UTC +3 + 1 hour DST.
SECOND_INTERVAL = ZoneInterval(
    name="Second",
    start=FIRST_INTERVAL.end,
    end=Instant.from_utc(2000, 9, 15, 5, 0),
    wall_offset=Offset.from_hours(4),
    savings=Offset.from_hours(1),
)

THIRD_INTERVAL = ZoneInterval(
    name="Third",
    start=SECOND_INTERVAL.end,
    end=Instant.from_utc(2005, 1, 20, 8, 0),
    wall_offset=Offset.from_hours(-5),
    savings=Offset.zero,
)

WINTER = _ZoneRecurrence(
    "Winter",
    Offset.zero,
    _ZoneYearOffset._ctor(_TransitionMode.WALL, 10, 5, 0, False, LocalTime(2, 0)),
    1960,
    _CsharpConstants.INT_MAX_VALUE,
)
SUMMER = _ZoneRecurrence(
    "Summer",
    Offset.from_hours(1),
    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, False, LocalTime(1, 0)),
    1960,
    _CsharpConstants.INT_MAX_VALUE,
)

TAIL_ZONE = _StandardDaylightAlternatingMap._ctor(Offset.from_hours(-6), WINTER, SUMMER)

# We don't actually want an interval from the beginning of time when we ask our composite time zone for an interval
# - because that could give the wrong idea. So we clamp it at the end of the precalculated interval.
CLAMPED_TAIL_ZONE_INTERVAL = TAIL_ZONE.get_zone_interval(THIRD_INTERVAL.end)._with_start(THIRD_INTERVAL.end)

TEST_ZONE = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], TAIL_ZONE)


class TestPrecalculatedDateTimeZone:
    def test_min_max_offsets(self) -> None:
        assert TEST_ZONE.min_offset == Offset.from_hours(-6)
        assert TEST_ZONE.max_offset == Offset.from_hours(4)

    def test_min_max_offsets_with_other_tail_zone(self) -> None:
        tail_zone = _FixedDateTimeZone(id_="TestFixed", offset=Offset.from_hours(8))
        test_zone = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], tail_zone)
        assert test_zone.min_offset == Offset.from_hours(-5)
        assert test_zone.max_offset == Offset.from_hours(8)

    def test_min_max_offsets_with_null_tail_zone(self) -> None:
        test_zone = _PrecalculatedDateTimeZone(
            "Test",
            [
                FIRST_INTERVAL,
                SECOND_INTERVAL,
                THIRD_INTERVAL,
                ZoneInterval(
                    name="Last",
                    start=THIRD_INTERVAL.end,
                    end=Instant._after_max_value(),
                    wall_offset=Offset.zero,
                    savings=Offset.zero,
                ),
            ],
            None,
        )
        assert test_zone.min_offset == Offset.from_hours(-5)
        assert test_zone.max_offset == Offset.from_hours(4)

    def test_get_zone_interval_instant_end(self) -> None:
        assert TEST_ZONE.get_zone_interval(SECOND_INTERVAL.end - Duration.epsilon) == SECOND_INTERVAL

    def test_get_zone_interval_instant_start(self) -> None:
        assert TEST_ZONE.get_zone_interval(SECOND_INTERVAL.start) == SECOND_INTERVAL

    def test_get_zone_interval_instant_final_interval_end(self) -> None:
        assert TEST_ZONE.get_zone_interval(THIRD_INTERVAL.end - Duration.epsilon) == THIRD_INTERVAL

    def test_get_zone_interval_instant_final_interval_start(self) -> None:
        assert TEST_ZONE.get_zone_interval(THIRD_INTERVAL.start) == THIRD_INTERVAL

    def test_get_zone_interval_instant_tail_zone(self) -> None:
        assert TEST_ZONE.get_zone_interval(THIRD_INTERVAL.end) == CLAMPED_TAIL_ZONE_INTERVAL

    def test_map_local_unambiguous_in_precalculated(self) -> None:
        self.__check_mapping(LocalDateTime(2000, 6, 1), SECOND_INTERVAL, SECOND_INTERVAL, 1)

    def test_map_local_unambiguous_in_tail_zone(self) -> None:
        self.__check_mapping(LocalDateTime(2005, 2, 1), CLAMPED_TAIL_ZONE_INTERVAL, CLAMPED_TAIL_ZONE_INTERVAL, 1)

    def test_map_local_ambiguous_within_precalculated(self) -> None:
        # Transition from +4 to -5 has a 9 hour ambiguity
        self.__check_mapping(THIRD_INTERVAL.iso_local_start, SECOND_INTERVAL, THIRD_INTERVAL, 2)

    def test_map_local_ambiguous_around_tail_zone_transition(self) -> None:
        # Transition from -5 to -6 has a 1 hour ambiguity
        self.__check_mapping(
            THIRD_INTERVAL.iso_local_end.plus_nanoseconds(-1), THIRD_INTERVAL, CLAMPED_TAIL_ZONE_INTERVAL, 2
        )

    def test_map_local_ambiguous_but_too_early_in_tail_zone_transition(self) -> None:
        # Tail zone is +10 / +8, with the transition occurring just after
        # the transition *to* the tail zone from the precalculated zone.
        # A local instant of one hour before after the transition from the precalculated zone (which is -5)
        # will therefore be ambiguous, but the resulting instants from the ambiguity occur
        # before our transition into the tail zone, so are ignored.
        tail_zone = SingleTransitionDateTimeZone(THIRD_INTERVAL.end + Duration.from_hours(1), 10, 0)
        gap_zone = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], tail_zone)
        mapping = gap_zone.map_local(THIRD_INTERVAL.iso_local_end.plus_hours(-1))
        assert mapping.early_interval == THIRD_INTERVAL
        assert mapping.late_interval == THIRD_INTERVAL
        assert mapping.count == 1

    def test_map_local_gap_within_precalculated(self) -> None:
        # Transition from +3 to +4 has a 1 hour gap
        assert FIRST_INTERVAL.iso_local_end < SECOND_INTERVAL.iso_local_start
        self.__check_mapping(FIRST_INTERVAL.iso_local_end, FIRST_INTERVAL, SECOND_INTERVAL, 0)

    def test_map_local_single_interval_around_tail_zone_transition(self) -> None:
        # Tail zone is fixed at +5. A local instant of one hour before the transition
        # from the precalculated zone (which is -5) will therefore give an instant from
        # the tail zone which occurs before the precalculated-to-tail transition,
        # and can therefore be ignored, resulting in an overall unambiguous time.
        tail_zone = _FixedDateTimeZone(Offset.from_hours(5))
        gap_zone = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], tail_zone)
        mapping = gap_zone.map_local(THIRD_INTERVAL.iso_local_end.plus_hours(-1))
        assert mapping.early_interval == THIRD_INTERVAL
        assert mapping.late_interval == THIRD_INTERVAL
        assert mapping.count == 1

    def test_map_local_gap_around_tail_zone_transition(self) -> None:
        # Tail zone is fixed at +5. A local time at the transition
        # from the precalculated zone (which is -5) will therefore give an instant from
        # the tail zone which occurs before the precalculated-to-tail transition,
        # and can therefore be ignored, resulting in an overall gap.
        tail_zone = _FixedDateTimeZone(Offset.from_hours(5))
        gap_zone = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], tail_zone)
        mapping = gap_zone.map_local(THIRD_INTERVAL.iso_local_end)
        assert mapping.early_interval == THIRD_INTERVAL
        assert mapping.late_interval == ZoneInterval(
            name="UTC+05",
            start=THIRD_INTERVAL.end,
            end=Instant._after_max_value(),
            wall_offset=Offset.from_hours(5),
            savings=Offset.zero,
        )
        assert mapping.count == 0

    def test_map_local_gap_around_and_in_tail_zone_transition(self) -> None:
        # Tail zone is -10 / +5, with the transition occurring just after
        # the transition *to* the tail zone from the precalculated zone.
        # A local time of one hour after the transition from the precalculated zone (which is -5)
        # will therefore be in the gap.
        tail_zone = SingleTransitionDateTimeZone(THIRD_INTERVAL.end + Duration.from_hours(1), -10, +5)
        gap_zone = _PrecalculatedDateTimeZone("Test", [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL], tail_zone)
        mapping = gap_zone.map_local(THIRD_INTERVAL.iso_local_end.plus_hours(1))
        assert mapping.early_interval == THIRD_INTERVAL
        assert mapping.late_interval == ZoneInterval(
            name="Single-Early",
            start=THIRD_INTERVAL.end,
            end=tail_zone.transition,
            wall_offset=Offset.from_hours(-10),
            savings=Offset.zero,
        )
        assert mapping.count == 0

    def test_get_zone_intervals_null_tail_zone_eot(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant._before_min_value(),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(20),
                end=Instant._after_max_value(),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        zone = _PrecalculatedDateTimeZone("Test", intervals, None)
        assert zone.get_zone_interval(Instant.max_value) == intervals[1]

    @staticmethod
    def __check_mapping(
        local_date_time: LocalDateTime, early_interval: ZoneInterval, late_interval: ZoneInterval, count: int
    ) -> None:
        mapping = TEST_ZONE.map_local(local_date_time)
        assert mapping.early_interval == early_interval
        assert mapping.late_interval == late_interval
        assert mapping.count == count

    def test_validation_empty_period_array(self) -> None:
        with pytest.raises(ValueError):
            _PrecalculatedDateTimeZone._validate_periods([], DateTimeZone.utc)

    def test_validation_bad_first_starting_point(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(10),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(20),
                end=Instant.from_unix_time_ticks(30),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        with pytest.raises(ValueError):
            _PrecalculatedDateTimeZone._validate_periods(intervals, DateTimeZone.utc)

    def test_validation_non_adjoining_intervals(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant._before_min_value(),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(25),
                end=Instant.from_unix_time_ticks(30),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        with pytest.raises(ValueError):
            _PrecalculatedDateTimeZone._validate_periods(intervals, DateTimeZone.utc)

    def test_validation_success(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant._before_min_value(),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(20),
                end=Instant.from_unix_time_ticks(30),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(30),
                end=Instant.from_unix_time_ticks(100),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(100),
                end=Instant.from_unix_time_ticks(200),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        _PrecalculatedDateTimeZone._validate_periods(intervals, DateTimeZone.utc)

    def test_validation_null_tail_zone_with_middle_of_time_final_period(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant._before_min_value(),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(20),
                end=Instant.from_unix_time_ticks(30),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        with pytest.raises(ValueError):
            _PrecalculatedDateTimeZone._validate_periods(intervals, None)

    def test_validation_null_tail_zone_with_eot_period_end(self) -> None:
        intervals = [
            ZoneInterval(
                name="foo",
                start=Instant._before_min_value(),
                end=Instant.from_unix_time_ticks(20),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
            ZoneInterval(
                name="foo",
                start=Instant.from_unix_time_ticks(20),
                end=Instant._after_max_value(),
                wall_offset=Offset.zero,
                savings=Offset.zero,
            ),
        ]
        _PrecalculatedDateTimeZone._validate_periods(intervals, None)

    def test_serialization(self) -> None:
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        TEST_ZONE._write(writer)
        stream.seek(0)
        reloaded = _PrecalculatedDateTimeZone._read(_DateTimeZoneReader._ctor(stream, None), TEST_ZONE.id)

        # TODO: [requires ZoneEqualityComparer] Check equivalence by finding zone intervals
        #  This will have to do for now...
        assert reloaded.id == TEST_ZONE.id
        assert reloaded.min_offset == TEST_ZONE.min_offset
        assert reloaded.max_offset == TEST_ZONE.max_offset
        for interval in [FIRST_INTERVAL, SECOND_INTERVAL, THIRD_INTERVAL]:
            if interval.has_start:
                assert reloaded.get_zone_interval(interval.start) == TEST_ZONE.get_zone_interval(interval.start)
            if interval.has_end:
                assert reloaded.get_zone_interval(interval.end) == TEST_ZONE.get_zone_interval(interval.end)
