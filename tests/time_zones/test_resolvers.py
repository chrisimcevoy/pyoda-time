# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

import pytest

from pyoda_time import (
    AmbiguousTimeError,
    DateTimeZone,
    Duration,
    Instant,
    LocalDateTime,
    SkippedTimeError,
    ZonedDateTime,
)
from pyoda_time.testing.time_zones import SingleTransitionDateTimeZone
from pyoda_time.time_zones import Resolvers, ZoneInterval

AMBIGUOUS_ZONE: Final[SingleTransitionDateTimeZone] = SingleTransitionDateTimeZone(
    Instant.from_utc(2000, 1, 1, 0, 0), 1, 0
)
"""Zone where the clocks go back at 1am at the start of the year 2000, back to midnight."""

GAP_ZONE: Final[SingleTransitionDateTimeZone] = SingleTransitionDateTimeZone(Instant.from_utc(2000, 1, 1, 0, 0), 0, 1)
"""Zone where the clocks go forward at midnight at the start of the year 2000, to 1am."""

TIME_IN_TRANSITION: Final[LocalDateTime] = LocalDateTime(2000, 1, 1, 0, 20)
"""Local time which is either skipped or ambiguous, depending on the zones above."""


class TestResolvers:
    def test_return_earlier(self) -> None:
        mapping = AMBIGUOUS_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 2
        resolved = Resolvers.return_earlier(mapping.first(), mapping.last())
        assert resolved == mapping.first()

    def test_return_later(self) -> None:
        mapping = AMBIGUOUS_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 2
        resolved = Resolvers.return_later(mapping.first(), mapping.last())
        assert resolved == mapping.last()

    def throw_when_ambiguous(self) -> None:
        mapping = AMBIGUOUS_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 2
        with pytest.raises(AmbiguousTimeError):
            Resolvers.throw_when_ambiguous(mapping.first(), mapping.last())

    def test_return_end_of_interval_before(self) -> None:
        mapping = GAP_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 0
        resolved = Resolvers.return_end_of_interval_before(
            TIME_IN_TRANSITION, GAP_ZONE, mapping.early_interval, mapping.late_interval
        )
        assert resolved.to_instant() == GAP_ZONE.early_interval.end - Duration.epsilon
        assert resolved.zone == GAP_ZONE

    def test_start_of_interval_after(self) -> None:
        mapping = GAP_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 0
        resolved = Resolvers.return_start_of_interval_after(
            TIME_IN_TRANSITION, GAP_ZONE, mapping.early_interval, mapping.late_interval
        )
        assert resolved.to_instant() == GAP_ZONE.late_interval.start
        assert resolved.zone == GAP_ZONE

    def test_return_forward_shifted(self) -> None:
        mapping = GAP_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 0
        resolved = Resolvers.return_forward_shifted(
            TIME_IN_TRANSITION, GAP_ZONE, mapping.early_interval, mapping.late_interval
        )

        gap = mapping.late_interval.wall_offset.ticks - mapping.early_interval.wall_offset.ticks
        expected = TIME_IN_TRANSITION._to_local_instant().minus(mapping.late_interval.wall_offset).plus_ticks(gap)
        assert resolved.to_instant() == expected
        assert resolved.offset == mapping.late_interval.wall_offset
        assert resolved.zone == GAP_ZONE

    def test_throw_when_skipped(self) -> None:
        mapping = GAP_ZONE.map_local(TIME_IN_TRANSITION)
        assert mapping.count == 0
        with pytest.raises(SkippedTimeError):
            Resolvers.throw_when_skipped(TIME_IN_TRANSITION, GAP_ZONE, mapping.early_interval, mapping.late_interval)

    def test_create_resolver_unambiguous(self) -> None:
        def ambiguity_resolver(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
            pytest.fail("Shouldn't be called")

        def skipped_time_resolver(
            local_date_time: LocalDateTime,
            zone: DateTimeZone,
            interval_before: ZoneInterval,
            interval_after: ZoneInterval,
        ) -> ZonedDateTime:
            pytest.fail("Shouldn't be called")

        resolver = Resolvers.create_mapping_resolver(ambiguity_resolver, skipped_time_resolver)

        local_time = LocalDateTime(1900, 1, 1, 0, 0)
        resolved = resolver(GAP_ZONE.map_local(local_time))
        assert resolved == ZonedDateTime._ctor(local_time.with_offset(GAP_ZONE.early_interval.wall_offset), GAP_ZONE)

    def test_create_resolver_ambiguous(self) -> None:
        zoned = ZonedDateTime._ctor(
            TIME_IN_TRANSITION.plus_days(1).with_offset(GAP_ZONE.early_interval.wall_offset), GAP_ZONE
        )

        def ambiguity_resolver(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
            return zoned

        def skipped_time_resolver(
            local_date_time: LocalDateTime,
            zone: DateTimeZone,
            interval_before: ZoneInterval,
            interval_after: ZoneInterval,
        ) -> ZonedDateTime:
            pytest.fail("Shouldn't be called")

        resolver = Resolvers.create_mapping_resolver(ambiguity_resolver, skipped_time_resolver)

        resolved = resolver(AMBIGUOUS_ZONE.map_local(TIME_IN_TRANSITION))
        assert resolved == zoned

    def test_create_resolver_skipped(self) -> None:
        zoned = ZonedDateTime._ctor(
            TIME_IN_TRANSITION.plus_days(1).with_offset(GAP_ZONE.early_interval.wall_offset), GAP_ZONE
        )

        def ambiguity_resolver(earlier: ZonedDateTime, later: ZonedDateTime) -> ZonedDateTime:
            pytest.fail("Shouldn't be called")

        def skipped_time_resolver(
            local_date_time: LocalDateTime,
            zone: DateTimeZone,
            interval_before: ZoneInterval,
            interval_after: ZoneInterval,
        ) -> ZonedDateTime:
            return zoned

        resolver = Resolvers.create_mapping_resolver(ambiguity_resolver, skipped_time_resolver)

        resolved = resolver(GAP_ZONE.map_local(TIME_IN_TRANSITION))
        assert resolved == zoned
