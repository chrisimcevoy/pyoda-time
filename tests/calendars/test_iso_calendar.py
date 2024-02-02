# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from datetime import datetime, timedelta, timezone

import pytest

from pyoda_time import (
    CalendarSystem,
    Instant,
    IsoDayOfWeek,
    LocalDate,
    LocalDateTime,
    PyodaConstants,
)
from pyoda_time._local_instant import _LocalInstant
from pyoda_time.calendars import Era, WeekYearRules
from pyoda_time.utility import _towards_zero_division

ISO: CalendarSystem = CalendarSystem.iso


class TestIsoCalendarSystem:
    UNIX_EPOCH_DATE_TIME = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    TIME_OF_GREAT_ACHIEVEMENT = datetime(2009, 11, 27, 18, 38, 25, 345 * 1000, tzinfo=timezone.utc) + timedelta(
        microseconds=8765 * 0.1
    )

    time_of_great_achievement_ticks = 633949439053458765
    unix_epoch_ticks = 621355968000000000

    def test_fields_of_unix_epoch(self) -> None:
        # It's easiest to test this using a LocalDateTime in the ISO calendar system.
        # LocalDateTime just passes everything through anyway.
        epoch: LocalDateTime = PyodaConstants.UNIX_EPOCH.in_utc().local_date_time

        assert epoch.year == 1970
        assert epoch.year_of_era == 1970
        assert WeekYearRules.iso.get_week_year(epoch.date) == 1970
        assert WeekYearRules.iso.get_week_of_week_year(epoch.date) == 1
        assert epoch.month == 1
        assert epoch.day == 1
        assert epoch.day_of_year == 1
        assert epoch.day_of_week == IsoDayOfWeek.THURSDAY
        assert epoch.era == Era.common
        assert epoch.hour == 0
        assert epoch.minute == 0
        assert epoch.second == 0
        assert epoch.millisecond == 0
        assert epoch.tick_of_day == 0
        assert epoch.tick_of_second == 0

    def test_fields_of_great_achievement(self) -> None:
        # TODO: In Noda Time, `now` is assigned to:
        #  `Instant.FromUnixTimeTicks((TimeOfGreatAchievement - UnixEpochDateTime).Ticks).InUtc().LocalDateTime;`
        #  A naive python implementation would use:
        #  ```
        #  from pyoda_time.utility import _to_ticks
        #  Instant.from_unix_time_ticks(
        #       _to_ticks(self.TIME_OF_GREAT_ACHIEVEMENT) - _to_ticks(self.UNIX_EPOCH_DATE_TIME)
        #  )
        #  ```
        #  But because python's datetime resolution is not as granular as C#'s DateTime,
        #  this leads to test failures when asserting on anything tick-related.
        #  So we are using hard-coded, manually-gathered ticks here instead.

        now: LocalDateTime = (
            Instant.from_unix_time_ticks(self.time_of_great_achievement_ticks - self.unix_epoch_ticks)
            .in_utc()
            .local_date_time
        )

        assert now.year == 2009
        assert now.year_of_era == 2009
        assert WeekYearRules.iso.get_week_year(now.date) == 2009
        assert WeekYearRules.iso.get_week_of_week_year(now.date) == 48
        assert now.month == 11
        assert now.day == 27
        assert now.day_of_year == self.TIME_OF_GREAT_ACHIEVEMENT.timetuple().tm_yday
        assert now.day_of_week == IsoDayOfWeek.FRIDAY
        assert now.era == Era.common
        assert now.hour == 18
        assert now.minute == 38
        assert now.second == 25
        assert now.millisecond == 345
        assert now.tick_of_second == 3458765
        assert now.tick_of_day == (
            18 * PyodaConstants.TICKS_PER_HOUR
            + 38 * PyodaConstants.TICKS_PER_MINUTE
            + 25 * PyodaConstants.TICKS_PER_SECOND
            + 3458765
        )

    def test_construct_local_instant(self) -> None:
        local_achievement: _LocalInstant = (
            LocalDateTime(2009, 11, 27, 18, 38, 25, 345).plus_ticks(8765)._to_local_instant()
        )
        bcl_ticks = self.time_of_great_achievement_ticks - self.unix_epoch_ticks
        bcl_days = _towards_zero_division(bcl_ticks, PyodaConstants.TICKS_PER_DAY)
        bcl_tick_of_day = bcl_ticks % PyodaConstants.TICKS_PER_DAY
        assert local_achievement._days_since_epoch == bcl_days
        assert local_achievement._nanosecond_of_day / PyodaConstants.NANOSECONDS_PER_TICK == bcl_tick_of_day

    def test_is_leap_year(self) -> None:
        assert CalendarSystem.iso.is_leap_year(2012)
        assert not CalendarSystem.iso.is_leap_year(2011)
        assert not CalendarSystem.iso.is_leap_year(2100)
        assert CalendarSystem.iso.is_leap_year(2000)

    def test_get_days_in_month(self) -> None:
        assert CalendarSystem.iso.get_days_in_month(2010, 9) == 30
        assert CalendarSystem.iso.get_days_in_month(2010, 1) == 31
        assert CalendarSystem.iso.get_days_in_month(2010, 2) == 28
        assert CalendarSystem.iso.get_days_in_month(2012, 2) == 29

    def test_before_common_era(self) -> None:
        # Year -1 in absolute terms is 2BCE
        local_date = LocalDate(year=-1, month=1, day=1)
        assert local_date.era == Era.before_common
        assert local_date.year == -1
        assert local_date.year_of_era == 2

    def test_before_common_era_by_specifying_era(self) -> None:
        # Year -1 in absolute terms is 2BCE
        local_date = LocalDate(era=Era.before_common, year_of_era=2, month=1, day=1)
        assert local_date.era == Era.before_common
        assert local_date.year == -1
        assert local_date.year_of_era == 2


class TestIsoCalendarEra:
    def test_get_max_year_of_era(self) -> None:
        date = LocalDate(year=ISO.max_year, month=1, day=1)
        assert ISO.get_max_year_of_era(Era.common) == date.year_of_era
        assert date.era == Era.common
        date = LocalDate(year=ISO.min_year, month=1, day=1)
        assert date.year == ISO.min_year
        assert ISO.get_max_year_of_era(Era.before_common) == date.year_of_era
        assert date.era == Era.before_common

    def test_get_min_year_of_era(self) -> None:
        date = LocalDate(year=1, month=1, day=1)
        assert ISO.get_min_year_of_era(Era.common) == date.year_of_era
        assert date.era == Era.common
        date = LocalDate(year=0, month=1, day=1)
        assert ISO.get_min_year_of_era(Era.before_common) == date.year_of_era
        assert date.era == Era.before_common

    def test_get_absolute_year(self) -> None:
        assert ISO.get_absolute_year(1, Era.common) == 1
        assert ISO.get_absolute_year(1, Era.before_common) == 0
        assert ISO.get_absolute_year(2, Era.before_common) == -1
        assert ISO.get_absolute_year(ISO.get_max_year_of_era(Era.common), Era.common) == ISO.max_year
        assert ISO.get_absolute_year(ISO.get_max_year_of_era(Era.before_common), Era.before_common) == ISO.min_year


class TestIsoCalendarSystemFields:
    # These tests assume that if the method doesn't throw, it's doing the right thing - this
    # is all tested elsewhere.

    def test_validate_year_month_day_all_values_valid_values_doesnt_throw(self) -> None:
        ISO._validate_year_month_day(20, 2, 20)

    def test_validate_year_month_day_invalid_year_throws(self) -> None:
        # TODO: ArgumentOutOfRangeException
        with pytest.raises(ValueError):
            ISO._validate_year_month_day(50000, 2, 20)

    def test_get_local_instant_invalid_month_throws(self) -> None:
        # TODO: ArgumentOutOfRangeException
        with pytest.raises(ValueError):
            ISO._validate_year_month_day(2010, 13, 20)

    def test_get_local_instant_29th_of_february_in_non_leap_year_throws(self) -> None:
        # TODO: ArgumentOutOfRangeException
        with pytest.raises(ValueError):
            ISO._validate_year_month_day(2010, 2, 29)

    def test_get_local_instant_29th_of_february_in_leap_year_doesnt_throw(self) -> None:
        ISO._validate_year_month_day(2012, 2, 29)
