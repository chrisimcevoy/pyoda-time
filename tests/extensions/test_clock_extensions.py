# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

from pyoda_time import CalendarSystem, DateTimeZone, DateTimeZoneProviders, PyodaConstants
from pyoda_time.testing import FakeClock

NEW_YORK: Final[DateTimeZone] = DateTimeZoneProviders.tzdb["America/New_York"]


class TestClockExtensions:
    def test_in_zone_no_calendar(self) -> None:
        clock = FakeClock(PyodaConstants.UNIX_EPOCH)
        zoned = clock.in_zone(NEW_YORK)
        zone_epoch = PyodaConstants.UNIX_EPOCH.in_zone(NEW_YORK)
        assert zoned.get_current_zoned_date_time() == zone_epoch

    def test_in_zone_with_calendar(self) -> None:
        clock = FakeClock(PyodaConstants.UNIX_EPOCH)
        zoned = clock.in_zone(NEW_YORK, CalendarSystem.julian)
        zone_epoch = PyodaConstants.UNIX_EPOCH.in_zone(NEW_YORK, CalendarSystem.julian)
        assert zoned.get_current_zoned_date_time() == zone_epoch

    def test_in_utc(self) -> None:
        clock = FakeClock(PyodaConstants.UNIX_EPOCH)
        zoned = clock.in_utc()
        zone_epoch = PyodaConstants.UNIX_EPOCH.in_utc()
        assert zoned.get_current_zoned_date_time() == zone_epoch

    # TODO:
    #  def test_in_tzdb_system_default_zone(self) -> None:
    #  def test_in_bcl_system_default_zone(self) -> None:
