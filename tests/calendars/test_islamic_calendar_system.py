# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time import CalendarSystem, IsoDayOfWeek, LocalDate, LocalDateTime
from pyoda_time.calendars import Era, IslamicEpoch, IslamicLeapYearPattern, _IslamicYearMonthDayCalculator


class TestIslamicCalendarSystem:
    SAMPLE_CALENDAR = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE16, IslamicEpoch.CIVIL)

    def test_sample_date_1(self) -> None:
        ldt = LocalDateTime(1945, 11, 12, 0, 0, 0, 0, CalendarSystem.iso)
        ldt = ldt.with_calendar(self.SAMPLE_CALENDAR)
        assert ldt.year_of_era == 1364

        assert ldt.year == 1364
        assert ldt.month == 12
        assert ldt.day == 6
        assert ldt.day_of_week == IsoDayOfWeek.MONDAY
        assert ldt.day_of_year == 6 * 30 + 5 * 29 + 6

        assert ldt.hour == 0
        assert ldt.minute == 0
        assert ldt.second == 0
        assert ldt.tick_of_second == 0

    def test_sample_date_2(self) -> None:
        ldt = LocalDateTime(2005, 11, 26, 0, 0, 0, 0, CalendarSystem.iso)
        ldt = ldt.with_calendar(self.SAMPLE_CALENDAR)
        assert ldt.era == Era.anno_hegirae
        assert ldt.year_of_era == 1426

        assert ldt.year == 1426
        assert ldt.month == 10
        assert ldt.day == 24
        assert ldt.day_of_week == IsoDayOfWeek.SATURDAY
        assert ldt.day_of_year == 5 * 30 + 4 * 29 + 24
        assert ldt.hour == 0
        assert ldt.minute == 0
        assert ldt.second == 0
        assert ldt.tick_of_second == 0

    def test_sample_date_3(self) -> None:
        ldt = LocalDateTime(1426, 12, 24, 0, 0, 0, 0, calendar=self.SAMPLE_CALENDAR)
        assert ldt.era == Era.anno_hegirae

        assert ldt.year == 1426
        assert ldt.month == 12
        assert ldt.day == 24
        assert ldt.day_of_week == IsoDayOfWeek.TUESDAY
        assert ldt.day_of_year == 6 * 30 + 5 * 29 + 24
        assert ldt.hour == 0
        assert ldt.minute == 0
        assert ldt.second == 0
        assert ldt.tick_of_second == 0

    def test_internal_consistency(self) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
        # Check construction and then deconstruction for every day of every year in one 30-year cycle.
        for year in range(1, 31):
            for month in range(1, 13):
                month_length = calendar.get_days_in_month(year, month)
                for day in range(1, month_length + 1):
                    date = LocalDate(year=year, month=month, day=day, calendar=calendar)
                    assert date.year == year, f"Year of {year}-{month}-{day}"
                    assert date.month == month, f"Month of {year}-{month}-{day}"
                    assert date.day == day, f"Day of {year}-{month}-{day}"

    @pytest.mark.parametrize(
        "year,expected",
        [
            (1, False),
            (2, True),
            (3, False),
            (4, False),
            (5, True),
            (6, False),
            (7, True),
            (8, False),
            (9, False),
            (10, True),
            (11, False),
            (12, False),
            (13, True),
            (14, False),
            (15, True),
            (16, False),
            (17, False),
            (18, True),
            (19, False),
            (20, False),
            (21, True),
            (22, False),
            (23, False),
            (24, True),
            (25, False),
            (26, True),
            (27, False),
            (28, False),
            (29, True),
            (30, False),
        ],
    )
    def test_base15_leap_year(self, year: int, expected: bool) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(year) is expected

    @pytest.mark.parametrize(
        "year,expected",
        [
            (1, False),
            (2, True),
            (3, False),
            (4, False),
            (5, True),
            (6, False),
            (7, True),
            (8, False),
            (9, False),
            (10, True),
            (11, False),
            (12, False),
            (13, True),
            (14, False),
            (15, False),
            (16, True),
            (17, False),
            (18, True),
            (19, False),
            (20, False),
            (21, True),
            (22, False),
            (23, False),
            (24, True),
            (25, False),
            (26, True),
            (27, False),
            (28, False),
            (29, True),
            (30, False),
        ],
    )
    def test_base16_leap_year(self, year: int, expected: bool) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE16, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(year) is expected

    @pytest.mark.parametrize(
        "year,expected",
        [
            (1, False),
            (2, True),
            (3, False),
            (4, False),
            (5, True),
            (6, False),
            (7, False),
            (8, True),
            (9, False),
            (10, True),
            (11, False),
            (12, False),
            (13, True),
            (14, False),
            (15, False),
            (16, True),
            (17, False),
            (18, False),
            (19, True),
            (20, False),
            (21, True),
            (22, False),
            (23, False),
            (24, True),
            (25, False),
            (26, False),
            (27, True),
            (28, False),
            (29, True),
            (30, False),
        ],
    )
    def test_indian_based_leap_year(self, year: int, expected: bool) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.INDIAN, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(year) is expected

    @pytest.mark.parametrize(
        "year,expected",
        [
            (1, False),
            (2, True),
            (3, False),
            (4, False),
            (5, True),
            (6, False),
            (7, False),
            (8, True),
            (9, False),
            (10, False),
            (11, True),
            (12, False),
            (13, True),
            (14, False),
            (15, False),
            (16, True),
            (17, False),
            (18, False),
            (19, True),
            (20, False),
            (21, True),
            (22, False),
            (23, False),
            (24, True),
            (25, False),
            (26, False),
            (27, True),
            (28, False),
            (29, False),
            (30, True),
        ],
    )
    def test_habash_al_hasib_based_leap_year(self, year: int, expected: bool) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(year) is expected

    def test_thursday_epoch(self) -> None:
        thursday_epoch_calendar = CalendarSystem.islamic_bcl
        julian_calendar = CalendarSystem.julian

        thursday_epoch = LocalDate(year=1, month=1, day=1, calendar=thursday_epoch_calendar)
        thursday_epoch_julian = LocalDate(year=622, month=7, day=15, calendar=julian_calendar)
        assert thursday_epoch.with_calendar(julian_calendar) == thursday_epoch_julian

    def test_friday_epoch(self) -> None:
        friday_epoch_calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE16, IslamicEpoch.CIVIL)
        julian_calendar = CalendarSystem.julian

        friday_epoch = LocalDate(year=1, month=1, day=1, calendar=friday_epoch_calendar)
        friday_epoch_julian = LocalDate(year=622, month=7, day=16, calendar=julian_calendar)
        assert friday_epoch.with_calendar(julian_calendar) == friday_epoch_julian

    # TODO: def test_bcl_uses_astronomical_epoch(self) -> None: [requires System.Globalization.HijriCalendar]
    # TODO: def test_sample_date_bcl_compatibility(self) -> None: [requires System.Globalization.HijriCalendar]
    # TODO: def test_bcl_through_history(self) -> None: [requires System.Globalization.HijriCalendar]

    @pytest.mark.parametrize(
        "year,month,expected",
        [
            (7, 1, 30),
            (7, 2, 29),
            (7, 3, 30),
            (7, 4, 29),
            (7, 5, 30),
            (7, 6, 29),
            (7, 7, 30),
            (7, 8, 29),
            (7, 9, 30),
            (7, 10, 29),
            (7, 11, 30),
            # As noted before, 7 isn't a leap year in this calendar
            (7, 12, 29),
            # As noted before, 8 is a leap year in this calendar
            (8, 12, 30),
        ],
    )
    def test_get_days_in_month(self, year: int, month: int, expected: int) -> None:
        # Just check that we've got the long/short the right way round...
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.CIVIL)
        assert calendar.get_days_in_month(year, month) == expected

    def test_get_instance_caching(self) -> None:
        from collections import deque

        queue: deque = deque()
        set_: set[CalendarSystem] = set()
        ids: set[str] = set()
        for leap_year_pattern in IslamicLeapYearPattern:
            for epoch in IslamicEpoch:
                calendar: CalendarSystem = CalendarSystem.get_islamic_calendar(leap_year_pattern, epoch)
                queue.append(calendar)
                assert calendar not in set_  # Check we haven't already seen it...
                set_.add(calendar)
                assert calendar.id not in ids
                ids.add(calendar.id)
        # Now check we get the same references again...
        for leap_year_pattern in IslamicLeapYearPattern:
            for epoch in IslamicEpoch:
                old_calendar: CalendarSystem = queue.popleft()
                new_calendar: CalendarSystem = CalendarSystem.get_islamic_calendar(leap_year_pattern, epoch)
                assert new_calendar.id == old_calendar.id
                assert new_calendar is old_calendar

    def test_get_instance_argument_validation(self) -> None:
        # This first invocation is just to ensure that passing ints doesn't cause an exception.
        # That way, we can be assured that any exception raised below is coming from our validation.
        CalendarSystem.get_islamic_calendar(min(IslamicLeapYearPattern) + 0, min(IslamicEpoch) - 0)  # type: ignore
        # TODO: In Noda Time, this is ArgumentOutOfRangeException
        with pytest.raises(ValueError):
            CalendarSystem.get_islamic_calendar(min(IslamicLeapYearPattern) - 1, min(IslamicEpoch))  # type: ignore
        with pytest.raises(ValueError):
            CalendarSystem.get_islamic_calendar(min(IslamicLeapYearPattern), min(IslamicEpoch) - 1)  # type: ignore
        with pytest.raises(ValueError):
            CalendarSystem.get_islamic_calendar(max(IslamicLeapYearPattern) + 1, max(IslamicEpoch))  # type: ignore
        with pytest.raises(ValueError):
            CalendarSystem.get_islamic_calendar(max(IslamicLeapYearPattern), max(IslamicEpoch) + 1)  # type: ignore

    def test_plus_years_simple(self) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)

        start = LocalDateTime(5, 8, 20, 2, 0, calendar=calendar)
        expected_end = LocalDateTime(10, 8, 20, 2, 0, calendar=calendar)
        assert start.plus_years(5) == expected_end

    def test_plus_years_truncates_at_leap_year(self) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(2)
        assert not calendar.is_leap_year(3)

        start = LocalDateTime(2, 12, 30, 2, 0, calendar=calendar)
        expected_end = LocalDateTime(3, 12, 29, 2, 0, calendar=calendar)
        assert start.plus_years(1) == expected_end

    def test_plus_years_does_not_truncate_from_one_leap_year_to_another(self) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(2)
        assert calendar.is_leap_year(5)

        start: LocalDateTime = LocalDateTime(2, 12, 30, 2, 0, calendar=calendar)
        expected_end: LocalDateTime = LocalDateTime(5, 12, 30, 2, 0, calendar=calendar)
        assert start.plus_years(3) == expected_end

    def test_plus_months_simple(self) -> None:
        calendar = CalendarSystem.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
        assert calendar.is_leap_year(2)

        start = LocalDateTime(2, 12, 30, 2, 0, calendar=calendar)
        expected_end = LocalDateTime(3, 11, 30, 2, 0, calendar=calendar)
        assert expected_end.month == 11
        assert expected_end.day == 30
        assert start.plus_months(11) == expected_end

    def test_constructor_invalid_enums_for_coverage(self) -> None:
        with pytest.raises(ValueError):
            _IslamicYearMonthDayCalculator(IslamicLeapYearPattern.BASE15 + 100, IslamicEpoch.ASTRONOMICAL)  # type: ignore
        with pytest.raises(ValueError):
            _IslamicYearMonthDayCalculator(IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL + 100)  # type: ignore
