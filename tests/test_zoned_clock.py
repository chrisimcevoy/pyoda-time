# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

from pyoda_time import (
    CalendarSystem,
    DateTimeZone,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    PyodaConstants,
    ZonedDateTime,
)
from pyoda_time.testing import FakeClock
from pyoda_time.testing.time_zones import SingleTransitionDateTimeZone

SAMPLE_ZONE: Final[DateTimeZone] = SingleTransitionDateTimeZone(PyodaConstants.UNIX_EPOCH, 1, 2)


class TestZonedClock:
    def test_get_current(self) -> None:
        julian = CalendarSystem.julian
        underlying_clock = FakeClock(PyodaConstants.UNIX_EPOCH)
        zoned_clock = underlying_clock.in_zone(SAMPLE_ZONE, julian)
        assert zoned_clock.get_current_instant() == PyodaConstants.UNIX_EPOCH
        assert zoned_clock.get_current_zoned_date_time() == ZonedDateTime(
            instant=underlying_clock.get_current_instant(), zone=SAMPLE_ZONE, calendar=julian
        )
        assert zoned_clock.get_current_local_date_time() == LocalDateTime(1969, 12, 19, 2, 0, calendar=julian)
        assert zoned_clock.get_current_offset_date_time() == LocalDateTime(
            1969, 12, 19, 2, 0, calendar=julian
        ).with_offset(Offset.from_hours(2))
        assert zoned_clock.get_current_date() == LocalDate(1969, 12, 19, julian)
        assert zoned_clock.get_curent_time_of_day() == LocalTime(2, 0, 0)

    def test_properties(self) -> None:
        calendar = CalendarSystem.julian
        clock = FakeClock(PyodaConstants.UNIX_EPOCH)
        zoned_clock = clock.in_zone(SAMPLE_ZONE, calendar)
        assert zoned_clock.clock is clock
        assert zoned_clock.calendar is calendar
        assert zoned_clock.zone is SAMPLE_ZONE
