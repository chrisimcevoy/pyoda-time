# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time import Duration, Instant, LocalDateTime, Offset
from pyoda_time.time_zones import ZoneInterval
from tests import helpers


class TestZoneInterval:
    SAMPLE_START = Instant.from_utc(2011, 6, 3, 10, 15)
    SAMPLE_END = Instant.from_utc(2011, 8, 2, 13, 45)

    SAMPLE_INTERVAL = ZoneInterval(
        name="TestTime",
        start=SAMPLE_START,
        end=SAMPLE_END,
        wall_offset=Offset.from_hours(9),
        savings=Offset.from_hours(1),
    )

    def test_passthrough_properties(self) -> None:
        assert self.SAMPLE_INTERVAL.name == "TestTime"
        assert self.SAMPLE_INTERVAL.standard_offset == Offset.from_hours(8)
        assert self.SAMPLE_INTERVAL.savings == Offset.from_hours(1)
        assert self.SAMPLE_INTERVAL.wall_offset == Offset.from_hours(9)
        assert self.SAMPLE_INTERVAL.start == self.SAMPLE_START
        assert self.SAMPLE_INTERVAL.end == self.SAMPLE_END

    def test_computed_properties(self) -> None:
        start = LocalDateTime(2011, 6, 3, 19, 15)
        end = LocalDateTime(2011, 8, 2, 22, 45)
        assert self.SAMPLE_INTERVAL.iso_local_start == start
        assert self.SAMPLE_INTERVAL.iso_local_end == end
        assert self.SAMPLE_INTERVAL.duration == self.SAMPLE_END - self.SAMPLE_START

    def test_contains_instant_normal(self) -> None:
        assert self.SAMPLE_START in self.SAMPLE_INTERVAL
        assert self.SAMPLE_END not in self.SAMPLE_INTERVAL
        assert Instant.min_value not in self.SAMPLE_INTERVAL
        assert Instant.max_value not in self.SAMPLE_INTERVAL

    def test_contains_instant_whole_of_time_via_nullity(self) -> None:
        interval = ZoneInterval(
            name="All Time",
            start=None,
            end=None,
            wall_offset=Offset.from_hours(9),
            savings=Offset.from_hours(1),
        )
        assert self.SAMPLE_START in interval
        assert Instant.min_value in interval
        assert Instant.max_value in interval

    def test_contains_instant_whole_of_time_via_special_instants(self) -> None:
        interval = ZoneInterval(
            name="All Time",
            start=Instant._before_min_value(),
            end=Instant._after_max_value(),
            wall_offset=Offset.from_hours(9),
            savings=Offset.from_hours(1),
        )
        assert self.SAMPLE_START in interval
        assert Instant.min_value in interval
        assert Instant.max_value in interval

    def test_contains_local_instant_whole_of_time(self) -> None:
        interval = ZoneInterval(
            name="All Time",
            start=Instant._before_min_value(),
            end=Instant._after_max_value(),
            wall_offset=Offset.from_hours(9),
            savings=Offset.from_hours(1),
        )
        assert interval._contains(self.SAMPLE_START._plus(Offset.zero))
        assert interval._contains(Instant.min_value._plus(Offset.zero))
        assert interval._contains(Instant.max_value._plus(Offset.zero))

    def test_contains_outside_local_instant_range(self) -> None:
        very_early = ZoneInterval(
            name="Very early",
            start=Instant._before_min_value(),
            end=Instant.min_value + Duration.from_hours(8),
            wall_offset=Offset.from_hours(-9),
            savings=Offset.zero,
        )
        very_late = ZoneInterval(
            name="Very late",
            start=Instant.max_value - Duration.from_hours(8),
            end=Instant._after_max_value(),
            wall_offset=Offset.from_hours(9),
            savings=Offset.zero,
        )
        # The instants are contained...
        assert (Instant.min_value + Duration.from_hours(4)) in very_early
        assert (Instant.max_value - Duration.from_hours(4)) in very_late
        # But there are no valid local instants
        assert not very_early._contains(Instant.min_value._plus(Offset.zero))
        assert not very_early._contains(Instant.max_value._plus(Offset.zero))

    def test_iso_local_start_and_end_infinite(self) -> None:
        interval = ZoneInterval(
            name="All time",
            start=None,
            end=None,
            wall_offset=Offset.zero,
            savings=Offset.zero,
        )
        with pytest.raises(RuntimeError):
            str(interval.iso_local_start)
        with pytest.raises(RuntimeError):
            str(interval.iso_local_end)

    def test_iso_local_start_and_end_out_of_range(self) -> None:
        interval = ZoneInterval(
            name="All time",
            start=Instant.min_value,
            end=None,
            wall_offset=Offset.from_hours(-1),
            savings=Offset.zero,
        )
        with pytest.raises(OverflowError):
            str(interval.iso_local_start)
        interval = ZoneInterval(
            name="All time",
            start=None,
            end=Instant.max_value,
            wall_offset=Offset.from_hours(11),
            savings=Offset.zero,
        )
        with pytest.raises(OverflowError):
            str(interval.iso_local_end)

    def test_equality(self) -> None:
        helpers.test_equals_class(
            # Equal values
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(2),
            ),
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(2),
            ),
            # Unequal values
            ZoneInterval(
                name="name2",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(2),
            ),
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START.plus_nanoseconds(1),
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(2),
            ),
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END.plus_nanoseconds(1),
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(2),
            ),
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(2),
                savings=Offset.from_hours(2),
            ),
            ZoneInterval(
                name="name",
                start=self.SAMPLE_START,
                end=self.SAMPLE_END,
                wall_offset=Offset.from_hours(1),
                savings=Offset.from_hours(3),
            ),
        )

    def test_equality_operators(self) -> None:
        val1 = ZoneInterval(
            name="name",
            start=self.SAMPLE_START,
            end=self.SAMPLE_END,
            wall_offset=Offset.from_hours(1),
            savings=Offset.from_hours(2),
        )
        val2 = ZoneInterval(
            name="name",
            start=self.SAMPLE_START,
            end=self.SAMPLE_END,
            wall_offset=Offset.from_hours(1),
            savings=Offset.from_hours(2),
        )
        val3 = ZoneInterval(
            name="name2",
            start=self.SAMPLE_START,
            end=self.SAMPLE_END,
            wall_offset=Offset.from_hours(1),
            savings=Offset.from_hours(2),
        )
        val4 = None

        assert val1 == val2
        assert not val1 == val3
        assert not val1 == val4
        assert not val4 == val1
        assert not val4 != None  # noqa
        assert None == val4  # noqa

        assert not val1 != val2
        assert val1 != val3
        assert val1 != val4
        assert val4 != val1
        assert not val4 != None  # noqa
        assert not None != val4  # noqa

    def test_zone_interval_to_string(self) -> None:
        # TODO: Only the simplest case in the default culture is covered (kind of)
        assert self.SAMPLE_INTERVAL.__str__() == "TestTime: [2011-06-03T10:15:00Z, 2011-08-02T13:45:00Z) +09 (+01)"
