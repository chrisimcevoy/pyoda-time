# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

import pytest

from pyoda_time import Instant, LocalDateTime, LocalTime, Offset
from pyoda_time.time_zones import ZoneInterval, ZoneLocalMapping
from pyoda_time.time_zones._precalculated_date_time_zone import _PrecalculatedDateTimeZone
from pyoda_time.time_zones._standard_daylight_alternating_map import _StandardDaylightAlternatingMap
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

from .. import helpers

WINTER = _ZoneRecurrence(
    name="Winter",
    savings=Offset.zero,
    year_offset=_ZoneYearOffset._ctor(
        mode=_TransitionMode.WALL,
        month_of_year=10,
        day_of_month=5,
        day_of_week=0,
        advance=False,
        time_of_day=LocalTime(2, 0),
    ),
    from_year=2000,
    to_year=_CsharpConstants.INT_MAX_VALUE,
)

SUMMER = _ZoneRecurrence(
    name="Summer",
    savings=Offset.from_hours(1),
    year_offset=_ZoneYearOffset._ctor(
        mode=_TransitionMode.WALL,
        month_of_year=3,
        day_of_month=10,
        day_of_week=0,
        advance=False,
        time_of_day=LocalTime(1, 0),
    ),
    from_year=2000,
    to_year=_CsharpConstants.INT_MAX_VALUE,
)

TEST_MAP = _StandardDaylightAlternatingMap._ctor(
    standard_offset=Offset.from_hours(5),
    start_recurrence=WINTER,
    end_recurrence=SUMMER,
)
"""Time zone with the following characteristics:

* Only valid from March 10th 2000
* Standard offset of +5 (so 4am UTC = 9am local)
* Summer time (DST = 1 hour) always starts at 1am local time on March 10th (skips to 2am)
* Winter time (DST = 0) always starts at 2am local time on October 5th (skips to 1am)
"""

TEST_ZONE = _PrecalculatedDateTimeZone(
    id_="zone",
    intervals=[
        ZoneInterval(
            name="Before",
            start=Instant._before_min_value(),
            end=Instant.from_utc(1999, 12, 1, 0, 0),
            wall_offset=Offset.from_hours(5),
            savings=SUMMER.savings,
        )
    ],
    tail_zone=_StandardDaylightAlternatingMap._ctor(
        standard_offset=Offset.from_hours(5),
        start_recurrence=WINTER,
        end_recurrence=SUMMER,
    ),
)


class TestStandardDaylightAlternatingMap:
    def test_min_max_offsets(self) -> None:
        assert TEST_MAP.max_offset == Offset.from_hours(6)
        assert TEST_MAP.min_offset == Offset.from_hours(5)

    def test_get_zone_interval_instant_summer(self) -> None:
        interval = TEST_MAP.get_zone_interval(Instant.from_utc(2010, 6, 1, 0, 0))
        assert interval.name == "Summer"
        assert interval.wall_offset == Offset.from_hours(6)
        assert interval.standard_offset == Offset.from_hours(5)
        assert interval.savings == Offset.from_hours(1)
        assert interval.iso_local_start == LocalDateTime(2010, 3, 10, 2, 0)
        assert interval.iso_local_end == LocalDateTime(2010, 10, 5, 2, 0)

    def test_get_zone_interval_instant_winter(self) -> None:
        interval = TEST_MAP.get_zone_interval(Instant.from_utc(2010, 11, 1, 0, 0))
        assert interval.name == "Winter"
        assert interval.wall_offset == Offset.from_hours(5)
        assert interval.standard_offset == Offset.from_hours(5)
        assert interval.savings == Offset.from_hours(0)
        assert interval.iso_local_start == LocalDateTime(2010, 10, 5, 1, 0)
        assert interval.iso_local_end == LocalDateTime(2011, 3, 10, 1, 0)

    def test_get_zone_interval_instant_start_of_first_summer(self) -> None:
        # This is only just about valid
        first_summer = Instant.from_utc(2000, 3, 9, 20, 0)
        interval = TEST_MAP.get_zone_interval(first_summer)
        assert interval.name == "Summer"

    def test_map_local_within_first_summer(self) -> None:
        early = LocalDateTime(2000, 6, 1, 0, 0)
        self.__check_mapping(TEST_ZONE.map_local(early), "Summer", "Summer", 1)

    def test_map_local_within_first_winter(self) -> None:
        winter = LocalDateTime(2000, 12, 1, 0, 0)
        self.__check_mapping(TEST_ZONE.map_local(winter), "Winter", "Winter", 1)

    def test_map_local_at_first_gap_start(self) -> None:
        start_of_first_gap = LocalDateTime(2000, 3, 10, 1, 0)
        self.__check_mapping(TEST_ZONE.map_local(start_of_first_gap), "Winter", "Summer", 0)

    def test_map_local_within_first_gap(self) -> None:
        middle_of_first_gap = LocalDateTime(2000, 3, 10, 1, 30)
        self.__check_mapping(TEST_ZONE.map_local(middle_of_first_gap), "Winter", "Summer", 0)

    def test_map_local_end_of_first_gap(self) -> None:
        end_of_first_gap = LocalDateTime(2000, 3, 10, 2, 0)
        self.__check_mapping(TEST_ZONE.map_local(end_of_first_gap), "Summer", "Summer", 1)

    def test_map_local_start_of_first_ambiguity(self) -> None:
        first_ambiguity = LocalDateTime(2000, 10, 5, 1, 0)
        self.__check_mapping(TEST_ZONE.map_local(first_ambiguity), "Summer", "Winter", 2)

    def test_map_local_middle_of_first_ambiguity(self) -> None:
        first_ambiguity = LocalDateTime(2000, 10, 5, 1, 30)
        self.__check_mapping(TEST_ZONE.map_local(first_ambiguity), "Summer", "Winter", 2)

    def test_map_local_after_first_ambiguity(self) -> None:
        unambiguous_winter = LocalDateTime(2000, 10, 5, 2, 0)
        self.__check_mapping(TEST_ZONE.map_local(unambiguous_winter), "Winter", "Winter", 1)

    def test_map_local_within_arbitrary_summer(self) -> None:
        summer = LocalDateTime(2010, 6, 1, 0, 0)
        self.__check_mapping(TEST_ZONE.map_local(summer), "Summer", "Summer", 1)

    def test_map_local_within_arbitrary_winter(self) -> None:
        winter = LocalDateTime(2010, 12, 1, 0, 0)
        self.__check_mapping(TEST_ZONE.map_local(winter), "Winter", "Winter", 1)

    def test_map_local_at_arbitrary_gap_start(self) -> None:
        start_of_gap = LocalDateTime(2010, 3, 10, 1, 0)
        self.__check_mapping(TEST_ZONE.map_local(start_of_gap), "Winter", "Summer", 0)

    def test_map_local_within_arbitrary_gap(self) -> None:
        middle_of_gap = LocalDateTime(2010, 3, 10, 1, 30)
        self.__check_mapping(TEST_ZONE.map_local(middle_of_gap), "Winter", "Summer", 0)

    def test_map_local_end_of_arbitrary_gap(self) -> None:
        end_of_gap = LocalDateTime(2010, 3, 10, 2, 0)
        self.__check_mapping(TEST_ZONE.map_local(end_of_gap), "Summer", "Summer", 1)

    def test_map_local_start_of_arbitrary_ambiguity(self) -> None:
        ambiguity = LocalDateTime(2010, 10, 5, 1, 0)
        self.__check_mapping(TEST_ZONE.map_local(ambiguity), "Summer", "Winter", 2)

    def test_map_local_middle_of_arbitrary_ambiguity(self) -> None:
        ambiguity = LocalDateTime(2010, 10, 5, 1, 30)
        self.__check_mapping(TEST_ZONE.map_local(ambiguity), "Summer", "Winter", 2)

    def test_map_local_after_arbitrary_ambiguity(self) -> None:
        ambiguity = LocalDateTime(2010, 10, 5, 2, 0)
        self.__check_mapping(TEST_ZONE.map_local(ambiguity), "Winter", "Winter", 1)

    def test_equality(self) -> None:
        # Order of recurrences doesn't matter
        map_1 = _StandardDaylightAlternatingMap._ctor(Offset.from_hours(1), SUMMER, WINTER)
        map_2 = _StandardDaylightAlternatingMap._ctor(Offset.from_hours(1), WINTER, SUMMER)
        map_3 = _StandardDaylightAlternatingMap._ctor(
            standard_offset=Offset.from_hours(1),
            start_recurrence=WINTER,
            # Summer, but starting from 1900
            end_recurrence=_ZoneRecurrence(
                name="Summer",
                savings=Offset.from_hours(1),
                year_offset=_ZoneYearOffset._ctor(
                    mode=_TransitionMode.WALL,
                    month_of_year=3,
                    day_of_month=10,
                    day_of_week=0,
                    advance=False,
                    time_of_day=LocalTime(1, 0),
                ),
                from_year=1900,
                to_year=_CsharpConstants.INT_MAX_VALUE,
            ),
        )
        # Standard offset does matter
        map_4 = _StandardDaylightAlternatingMap._ctor(Offset.from_hours(0), SUMMER, WINTER)

        helpers.test_equals_class(map_1, map_2, map_4)
        helpers.test_equals_class(map_1, map_3, map_4)

        # Recurrences like Summer, but different in one aspect each, *except*
        unequal_maps = [
            _StandardDaylightAlternatingMap._ctor(Offset.from_hours(1), WINTER, recurrence)
            for recurrence in (
                _ZoneRecurrence(
                    "Different name",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(2),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.STANDARD, 3, 10, 0, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 4, 10, 0, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 9, 0, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 1, False, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                # Advance with day-of-week 0 doesn't make any real difference, but they compare non-equal...
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, True, LocalTime(1, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
                _ZoneRecurrence(
                    "Summer",
                    Offset.from_hours(1),
                    _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, False, LocalTime(2, 0)),
                    2000,
                    _CsharpConstants.INT_MAX_VALUE,
                ),
            )
        ]

        helpers.test_equals_class(map_1, map_2, *unequal_maps)

    def test_read_write(self) -> None:
        map_1 = _StandardDaylightAlternatingMap._ctor(Offset.from_hours(1), SUMMER, WINTER)
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        map_1._write(writer)
        stream.seek(0)

        reader = _DateTimeZoneReader._ctor(stream, None)
        map_2 = _StandardDaylightAlternatingMap._read(reader)
        assert map_2 == map_1

    def test_extremes(self) -> None:
        winter = _ZoneRecurrence(
            "Winter",
            Offset.zero,
            _ZoneYearOffset._ctor(_TransitionMode.WALL, 10, 5, 0, False, LocalTime(2, 0)),
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        )

        summer = _ZoneRecurrence(
            "Summer",
            Offset.from_hours(1),
            _ZoneYearOffset._ctor(_TransitionMode.WALL, 3, 10, 0, False, LocalTime(1, 0)),
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        )

        zone = _StandardDaylightAlternatingMap._ctor(Offset.zero, winter, summer)

        first_spring = Instant.from_utc(-9998, 3, 10, 1, 0)
        first_autumn = Instant.from_utc(-9998, 10, 5, 1, 0)  # 1am UTC = 2am wall

        last_spring = Instant.from_utc(9999, 3, 10, 1, 0)
        last_autumn = Instant.from_utc(9999, 10, 5, 1, 0)  # 1am UTC = 2am wall

        dst_offset = Offset.from_hours(1)

        # Check both year -9998 and 9999, both the infinite interval and the next one in

        first_winter = ZoneInterval(
            name="Winter",
            start=Instant._before_min_value(),
            end=first_spring,
            wall_offset=Offset.zero,
            savings=Offset.zero,
        )
        first_summer = ZoneInterval(
            name="Summer", start=first_spring, end=first_autumn, wall_offset=dst_offset, savings=dst_offset
        )
        last_summer = ZoneInterval(
            name="Summer", start=last_spring, end=last_autumn, wall_offset=dst_offset, savings=dst_offset
        )
        last_winter = ZoneInterval(
            name="Winter",
            start=last_autumn,
            end=Instant._after_max_value(),
            wall_offset=Offset.zero,
            savings=Offset.zero,
        )

        assert zone.get_zone_interval(Instant.min_value) == first_winter
        assert zone.get_zone_interval(Instant.from_utc(-9998, 2, 1, 0, 0)) == first_winter
        assert zone.get_zone_interval(first_spring) == first_summer
        assert zone.get_zone_interval(Instant.from_utc(-9998, 5, 1, 0, 0)) == first_summer

        assert zone.get_zone_interval(last_spring) == last_summer
        assert zone.get_zone_interval(Instant.from_utc(9999, 5, 1, 0, 0)) == last_summer
        assert zone.get_zone_interval(last_autumn) == last_winter
        assert zone.get_zone_interval(Instant.from_utc(9999, 11, 1, 0, 0)) == last_winter
        assert zone.get_zone_interval(Instant.max_value) == last_winter

    def test_invalid_map_simultaneous_transition(self) -> None:
        # Two recurrences with different savings, but which occur at the same instant in time every year.
        r1 = _ZoneRecurrence(
            "Recurrence1",
            Offset.zero,
            _ZoneYearOffset._ctor(_TransitionMode.UTC, 10, 5, 0, False, LocalTime(2, 0)),
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        )
        r2 = _ZoneRecurrence(
            "Recurrence2",
            Offset.from_hours(1),
            _ZoneYearOffset._ctor(_TransitionMode.UTC, 10, 5, 0, False, LocalTime(2, 0)),
            _CsharpConstants.INT_MIN_VALUE,
            _CsharpConstants.INT_MAX_VALUE,
        )

        invalid_map = _StandardDaylightAlternatingMap._ctor(Offset.zero, r1, r2)

        with pytest.raises(RuntimeError):
            invalid_map.get_zone_interval(Instant.from_utc(2017, 8, 25, 0, 0, 0))

    def __check_mapping(
        self, mapping: ZoneLocalMapping, early_interval_name: str, late_interval_name: str, count: int
    ) -> None:
        assert mapping.early_interval.name == early_interval_name
        assert mapping.late_interval.name == late_interval_name
        assert mapping.count == count
