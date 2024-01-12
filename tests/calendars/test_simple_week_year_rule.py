# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time import CalendarSystem, IsoDayOfWeek, LocalDate
from pyoda_time.calendars import CalendarWeekRule, WeekYearRules

ISO_DAYS_OF_WEEK = list(IsoDayOfWeek)
CALENDAR_WEEK_RULES = list(CalendarWeekRule)


class TestSimpleWeekYearRule:
    def test_round_trip_first_day_iso_7(self) -> None:
        # In the Gregorian calendar with a minimum of 7 days in the first
        # week, Tuesday January 1st -9998 is in week year -9999. We should be able to
        # round-trip.
        rule = WeekYearRules.for_min_days_in_first_week(7)
        date = LocalDate(year=-9998, month=1, day=1)
        assert rule.get_local_date(rule.get_week_year(date), rule.get_week_of_week_year(date), date.day_of_week) == date

    def test_round_trip_first_day_iso_1(self) -> None:
        # In the Gregorian calendar with a minimum of 1 day in the first
        # week, Friday December 31st 9999 is in week year 10000. We should be able to
        # round-trip.
        rule = WeekYearRules.for_min_days_in_first_week(1)
        date = LocalDate(year=9999, month=12, day=31)
        assert (
            rule.get_local_date(
                rule.get_week_year(date),
                rule.get_week_of_week_year(date),
                date.day_of_week,
            )
            == date
        )

    def test_out_of_range_valid_week_year_and_week_too_early(self) -> None:
        # Gregorian 4: Week year 1 starts on Monday December 31st -9999,
        # and is therefore out of range, even though the week-year
        # and week-of-week-year are valid.
        with pytest.raises(ValueError):
            WeekYearRules.iso.get_local_date(-9998, 1, IsoDayOfWeek.MONDAY)

        # Sanity check: no exception for January 1st
        WeekYearRules.iso.get_local_date(-9998, 1, IsoDayOfWeek.TUESDAY)

    def test_out_of_range_valid_week_year_and_week_too_late(self) -> None:
        # Gregorian 4: December 31st 9999 is a Friday, so the Saturday of the
        # same week is therefore out of range, even though the week-year
        # and week-of-week-year are valid.
        with pytest.raises(ValueError):
            WeekYearRules.iso.get_local_date(9999, 52, IsoDayOfWeek.SATURDAY)

        # Sanity check: no exception for December 31st
        WeekYearRules.iso.get_local_date(9999, 52, IsoDayOfWeek.FRIDAY)

    # Tests ported from IsoCalendarSystemTest and LocalDateTest.Construction
    @pytest.mark.parametrize(
        "year,month,day,week_year,week_of_week_year,day_of_week",
        [
            (2011, 1, 1, 2010, 52, IsoDayOfWeek.SATURDAY),
            (2012, 12, 31, 2013, 1, IsoDayOfWeek.MONDAY),
            (1960, 1, 19, 1960, 3, IsoDayOfWeek.TUESDAY),
            (2012, 10, 19, 2012, 42, IsoDayOfWeek.FRIDAY),
            (2005, 1, 2, 2004, 53, IsoDayOfWeek.SUNDAY),
        ],
    )
    def test_week_year_different_to_year(
        self, year: int, month: int, day: int, week_year: int, week_of_week_year: int, day_of_week: IsoDayOfWeek
    ) -> None:
        date = LocalDate(year=year, month=month, day=day)
        assert WeekYearRules.iso.get_week_year(date) == week_year
        assert WeekYearRules.iso.get_week_of_week_year(date) == week_of_week_year
        assert date.day_of_week == day_of_week
        assert WeekYearRules.iso.get_local_date(week_year, week_of_week_year, day_of_week) == date

    # Ported from CalendarSystemTest.Validation
    @pytest.mark.parametrize(
        "week_year,expected_result",
        [
            (2009, 53),
            (2010, 52),
            (2011, 52),
            (2012, 52),
            (2013, 52),
            (2014, 52),
            (2015, 53),
            (2016, 52),
            (2017, 52),
            (2018, 52),
            (2019, 52),
        ],
    )
    def test_get_weeks_in_year(self, week_year: int, expected_result: int) -> None:
        assert WeekYearRules.iso.get_weeks_in_week_year(week_year) == expected_result

    # Ported from LocalDateTest.BasicProperties
    # See https://stackoverflow.com/questions/8010125
    @pytest.mark.parametrize(
        "year,month,day,week_of_week_year",
        [
            (2007, 12, 31, 1),
            (2008, 1, 6, 1),
            (2008, 1, 7, 2),
            (2008, 12, 28, 52),
            (2008, 12, 29, 1),
            (2009, 1, 4, 1),
            (2009, 1, 5, 2),
            (2009, 12, 27, 52),
            (2009, 12, 28, 53),
            (2010, 1, 3, 53),
            (2010, 1, 4, 1),
        ],
    )
    def test_week_of_week_year_comparison_with_oracle(
        self, year: int, month: int, day: int, week_of_week_year: int
    ) -> None:
        date = LocalDate(year=year, month=month, day=day)
        assert WeekYearRules.iso.get_week_of_week_year(date) == week_of_week_year

    @pytest.mark.parametrize(
        "year,first_day_of_year,max_min_days_in_first_week_for_same_week_year",
        [
            (2000, IsoDayOfWeek.SATURDAY, 2),
            (2001, IsoDayOfWeek.MONDAY, 7),
            (2002, IsoDayOfWeek.TUESDAY, 6),
            (2003, IsoDayOfWeek.WEDNESDAY, 5),
            (2004, IsoDayOfWeek.THURSDAY, 4),
            (2005, IsoDayOfWeek.SATURDAY, 2),
            (2006, IsoDayOfWeek.SUNDAY, 1),
        ],
    )
    def test_gregorian(
        self, year: int, first_day_of_year: IsoDayOfWeek, max_min_days_in_first_week_for_same_week_year: int
    ) -> None:
        start_of_calendar_year = LocalDate(year=year, month=1, day=1)
        assert start_of_calendar_year.day_of_week == first_day_of_year

        # Rules which put the first day of the calendar year into the same week year
        for i in range(1, max_min_days_in_first_week_for_same_week_year + 1):
            rule = WeekYearRules.for_min_days_in_first_week(i)
            assert rule.get_week_year(start_of_calendar_year) == year
            assert rule.get_week_of_week_year(start_of_calendar_year) == 1
        # Rules which put the first day of the calendar year into the previous week year
        for i in range(max_min_days_in_first_week_for_same_week_year + 1, 8):
            rule = WeekYearRules.for_min_days_in_first_week(i)
            assert rule.get_week_year(start_of_calendar_year) == year - 1
            assert rule.get_week_of_week_year(start_of_calendar_year) == rule.get_weeks_in_week_year(year - 1)

    # Test cases from https://blogs.msdn.microsoft.com/shawnste/2006/01/24/iso-8601-week-of-year-format-in-microsoft-net/
    # which distinguish our ISO option from the BCL. When we implement the BCL equivalents, we should have similar
    # tests there...
    @pytest.mark.parametrize(
        "year,month,day,week_year,week_of_week_year,day_of_week",
        [
            (2000, 12, 31, 2000, 52, IsoDayOfWeek.SUNDAY),
            (2001, 1, 1, 2001, 1, IsoDayOfWeek.MONDAY),
            (2005, 1, 1, 2004, 53, IsoDayOfWeek.SATURDAY),
            (2007, 12, 31, 2008, 1, IsoDayOfWeek.MONDAY),
        ],
    )
    def test_iso(
        self, year: int, month: int, day: int, week_year: int, week_of_week_year: int, day_of_week: IsoDayOfWeek
    ) -> None:
        via_calendar = LocalDate(year=year, month=month, day=day)
        rule = WeekYearRules.iso
        assert rule.get_week_year(via_calendar) == week_year
        assert rule.get_week_of_week_year(via_calendar) == week_of_week_year
        assert via_calendar.day_of_week == day_of_week
        via_rule = rule.get_local_date(week_year, week_of_week_year, day_of_week)
        assert via_rule == via_calendar

    @pytest.mark.parametrize(
        "year,expected_first_day,iso_year,iso_month,iso_day,expected_weeks,expected_week_year_of_first_day,expected_week_of_week_year_of_first_day",
        [
            (5400, IsoDayOfWeek.THURSDAY, 1639, 9, 29, 51, 5400, 1),
            (5401, IsoDayOfWeek.MONDAY, 1640, 9, 17, 50, 5401, 1),
            (5402, IsoDayOfWeek.THURSDAY, 1641, 9, 5, 55, 5402, 1),
            (5403, IsoDayOfWeek.THURSDAY, 1642, 9, 25, 51, 5403, 1),
            (5404, IsoDayOfWeek.MONDAY, 1643, 9, 14, 55, 5404, 1),
            (5405, IsoDayOfWeek.SATURDAY, 1644, 10, 1, 50, 5404, 55),
            (5406, IsoDayOfWeek.THURSDAY, 1645, 9, 21, 51, 5406, 1),
            (5407, IsoDayOfWeek.MONDAY, 1646, 9, 10, 55, 5407, 1),
            (5408, IsoDayOfWeek.MONDAY, 1647, 9, 30, 50, 5408, 1),
            (5409, IsoDayOfWeek.THURSDAY, 1648, 9, 17, 51, 5409, 1),
            (5410, IsoDayOfWeek.TUESDAY, 1649, 9, 7, 55, 5410, 1),
        ],
    )
    def test_hebrew_calendar(
        self,
        year: int,
        expected_first_day: IsoDayOfWeek,
        iso_year: int,
        iso_month: int,
        iso_day: int,
        expected_weeks: int,
        expected_week_year_of_first_day: int,
        expected_week_of_week_year_of_first_day: int,
    ) -> None:
        """Just a sample test of not using the Gregorian/ISO calendar system."""
        civil_date = LocalDate(year=year, month=1, day=1, calendar=CalendarSystem.hebrew_civil)
        rule = WeekYearRules.iso
        assert civil_date.day_of_week == expected_first_day
        assert LocalDate(year=iso_year, month=iso_month, day=iso_day) == civil_date.with_calendar(CalendarSystem.iso)
        assert rule.get_weeks_in_week_year(year, CalendarSystem.hebrew_civil) == expected_weeks
        assert rule.get_week_year(civil_date) == expected_week_year_of_first_day
        assert (
            rule.get_local_date(
                expected_week_year_of_first_day,
                expected_week_of_week_year_of_first_day,
                expected_first_day,
                CalendarSystem.hebrew_civil,
            )
            == civil_date
        )

        # The scriptural month numbering system should have the same week-year and week-of-week-year.
        scriptural_date = civil_date.with_calendar(CalendarSystem.hebrew_scriptural)
        assert rule.get_weeks_in_week_year(year, CalendarSystem.hebrew_scriptural) == expected_weeks
        assert rule.get_week_year(scriptural_date) == expected_week_year_of_first_day
        assert (
            rule.get_local_date(
                expected_week_year_of_first_day,
                expected_week_of_week_year_of_first_day,
                expected_first_day,
                CalendarSystem.hebrew_scriptural,
            )
            == scriptural_date
        )

    # Jan 1st 2015 = Thursday
    # Jan 1st 2016 = Friday
    # Jan 1st 2017 = Sunday
    @pytest.mark.parametrize(
        "min_days_in_first_week,first_day_of_week,week_year,week,day_of_week,expected_year,expected_month,expected_day",
        [
            (1, IsoDayOfWeek.WEDNESDAY, 2015, 2, IsoDayOfWeek.FRIDAY, 2015, 1, 9),
            (7, IsoDayOfWeek.WEDNESDAY, 2015, 2, IsoDayOfWeek.FRIDAY, 2015, 1, 16),
            (1, IsoDayOfWeek.WEDNESDAY, 2015, 1, IsoDayOfWeek.WEDNESDAY, 2014, 12, 31),
            (3, IsoDayOfWeek.FRIDAY, 2016, 1, IsoDayOfWeek.FRIDAY, 2016, 1, 1),
            (3, IsoDayOfWeek.FRIDAY, 2017, 1, IsoDayOfWeek.FRIDAY, 2016, 12, 30),
        ],
    )
    def test_non_monday_first_day_of_week(
        self,
        min_days_in_first_week: int,
        first_day_of_week: IsoDayOfWeek,
        week_year: int,
        week: int,
        day_of_week: IsoDayOfWeek,
        expected_year: int,
        expected_month: int,
        expected_day: int,
    ) -> None:
        rule = WeekYearRules.for_min_days_in_first_week(min_days_in_first_week, first_day_of_week)
        actual = rule.get_local_date(week_year, week, day_of_week)
        expected = LocalDate(year=expected_year, month=expected_month, day=expected_day)
        assert actual == expected
        assert rule.get_week_year(actual) == week_year
        assert rule.get_week_of_week_year(actual) == week

    # TODO def test_bcl_equivalence(self): [requires bcl]

    # TODO def test_get_weeks_in_week_year [requires bcl]

    @pytest.mark.parametrize(
        "bcl_rule,first_day_of_week,week_year,week,day_of_week",
        [
            (CalendarWeekRule.FIRST_DAY, IsoDayOfWeek.MONDAY, 2015, 53, IsoDayOfWeek.SATURDAY),
            (CalendarWeekRule.FIRST_DAY, IsoDayOfWeek.MONDAY, 2016, 1, IsoDayOfWeek.THURSDAY),
        ],
    )
    def test_get_local_date_invalid(
        self,
        bcl_rule: CalendarWeekRule,
        first_day_of_week: IsoDayOfWeek,
        week_year: int,
        week: int,
        day_of_week: IsoDayOfWeek,
    ) -> None:
        pyoda_rule = WeekYearRules.from_calendar_week_rule(bcl_rule, first_day_of_week)
        with pytest.raises(ValueError):
            pyoda_rule.get_local_date(week_year, week, day_of_week)

    @pytest.mark.parametrize("bcl_rule", CALENDAR_WEEK_RULES)
    @pytest.mark.parametrize("first_day_of_week", ISO_DAYS_OF_WEEK)
    def test_round_trip_first_day_bcl(self, bcl_rule: CalendarWeekRule, first_day_of_week: IsoDayOfWeek) -> None:
        # TODO: Unlike Noda Time which uses `System.DayOfWeek`, we have to account for IsoDayOfWeek.None
        if first_day_of_week == IsoDayOfWeek.NONE:
            with pytest.raises(ValueError):
                WeekYearRules.from_calendar_week_rule(bcl_rule, first_day_of_week)
            return
        rule = WeekYearRules.from_calendar_week_rule(bcl_rule, first_day_of_week)
        date = LocalDate(year=-9998, month=1, day=1)
        assert (
            rule.get_local_date(
                rule.get_week_year(date),
                rule.get_week_of_week_year(date),
                date.day_of_week,
            )
            == date
        )

    @pytest.mark.parametrize("bcl_rule", CALENDAR_WEEK_RULES)
    @pytest.mark.parametrize("first_day_of_week", ISO_DAYS_OF_WEEK)
    def test_round_trip_last_day_bcl(self, bcl_rule: CalendarWeekRule, first_day_of_week: IsoDayOfWeek) -> None:
        # TODO: Unlike Noda Time which uses `System.DayOfWeek`, we have to account for IsoDayOfWeek.None
        if first_day_of_week == IsoDayOfWeek.NONE:
            with pytest.raises(ValueError):
                WeekYearRules.from_calendar_week_rule(bcl_rule, first_day_of_week)
            return
        rule = WeekYearRules.from_calendar_week_rule(bcl_rule, first_day_of_week)
        date = LocalDate(year=9999, month=12, day=31)
        assert (
            rule.get_local_date(
                rule.get_week_year(date),
                rule.get_week_of_week_year(date),
                date.day_of_week,
            )
            == date
        )
