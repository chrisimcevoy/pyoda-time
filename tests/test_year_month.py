# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import cast

import pytest

from pyoda_time import CalendarSystem, DateInterval, Instant, LocalDate, YearMonth
from pyoda_time._calendar_ordinal import _CalendarOrdinal
from pyoda_time.calendars import Era, IslamicEpoch, IslamicLeapYearPattern
from tests import helpers


class TestYearMonthTestBasicProperties:
    def test_properties(self) -> None:
        year_month = YearMonth(year=2000, month=1)
        assert year_month.year == 2000
        assert year_month.month == 1
        assert year_month.calendar == CalendarSystem.iso
        assert year_month.year_of_era == 2000
        assert year_month.era == Era.common

        assert year_month._start_date == LocalDate(year=2000, month=1, day=1)
        assert year_month._end_date == LocalDate(year=2000, month=1, day=31)

    def test_to_date_interval(self) -> None:
        year_month = YearMonth(year=2000, month=1)

        interval = DateInterval(LocalDate(year=2000, month=1, day=1), LocalDate(year=2000, month=1, day=31))
        assert year_month.to_date_interval() == interval


class TestYearMonthComparison:
    def test_equals_equal_values(self) -> None:
        calendar = CalendarSystem.julian
        year_month_1 = YearMonth(year=2011, month=1, calendar=calendar)
        year_month_2 = YearMonth(year=2011, month=1, calendar=calendar)
        assert year_month_1.equals(year_month_2)
        assert hash(year_month_1) == hash(year_month_2)
        assert year_month_1 == year_month_2
        assert not year_month_1 != year_month_2
        # In Noda Time, there is an extra assert on the IEquatable implementation

    def test_equals_different_months(self) -> None:
        calendar = CalendarSystem.julian
        year_month_1 = YearMonth(year=2011, month=1, calendar=calendar)
        year_month_2 = YearMonth(year=2011, month=2, calendar=calendar)
        assert not year_month_1.equals(year_month_2)
        assert not hash(year_month_1) == hash(year_month_2)
        assert not year_month_1 == year_month_2
        assert year_month_1 != year_month_2

    def test_equals_different_calendars(self) -> None:
        calendar = CalendarSystem.julian
        year_month_1 = YearMonth(year=2011, month=1, calendar=calendar)
        year_month_2 = YearMonth(year=2011, month=1, calendar=CalendarSystem.iso)
        assert not year_month_1.equals(year_month_2)
        assert not hash(year_month_1) == hash(year_month_2)
        assert not year_month_1 == year_month_2
        # In Noda Time, there is an extra assert on the IEquatable implementation

    def test_equals_different_to_null(self) -> None:
        date = YearMonth(year=2011, month=1)
        assert not date.equals(cast(YearMonth, None))

    def test_equals_different_to_other_type(self) -> None:
        date = YearMonth(year=2011, month=1)
        assert not date == Instant.from_unix_time_ticks(0)

    def test_compare_to_same_calendar(self) -> None:
        year_month_1 = YearMonth(year=2011, month=1)
        year_month_2 = YearMonth(year=2011, month=1)
        year_month_3 = YearMonth(year=2011, month=2)

        helpers.test_operator_comparison_equality(year_month_1, year_month_2, year_month_3)

    def test_compare_to_different_calendars_throws(self) -> None:
        islamic: CalendarSystem = CalendarSystem.get_islamic_calendar(
            IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL
        )
        year_month_1 = YearMonth(year=2011, month=1)
        year_month_2 = YearMonth(year=1500, month=1, calendar=islamic)

        with pytest.raises(ValueError):  # TODO: ArgumentException
            year_month_1.compare_to(year_month_2)
        # IComparable implementation omitted
        with pytest.raises(ValueError):  # TODO: ArgumentException
            str(year_month_1 > year_month_2)

    # TODO:
    #  public void IComparableCompareTo_SameCalendar()
    #  public void IComparableCompareTo_Null_Positive()
    #  public void IComparableCompareTo_WrongType_ArgumentException()


class TestYearMonthConstruction:
    @pytest.mark.parametrize(
        "year,month",
        [
            (2000, 1),
            (2000, 12),
            (-9998, 1),
            (9999, 12),
        ],
    )
    def test_valid_construction(self, year: int, month: int) -> None:
        year_month = YearMonth(year=year, month=month)
        assert year_month.year == year
        assert year_month.month == month
        assert year_month.calendar == CalendarSystem.iso

    @pytest.mark.parametrize(
        "year,month",
        [
            (-9999, 1),
            (10000, 1),
            (2000, 0),
            (2000, 13),
        ],
    )
    def test_invalid_construction(self, year: int, month: int) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            YearMonth(year=year, month=month)

    @pytest.mark.parametrize(
        "year,month,ordinal",
        [
            (2000, 1, _CalendarOrdinal.ISO),
            (2000, 12, _CalendarOrdinal.ISO),
            (-9998, 1, _CalendarOrdinal.ISO),
            (9999, 12, _CalendarOrdinal.ISO),
            (2000, 1, _CalendarOrdinal.JULIAN),
            (-9997, 1, _CalendarOrdinal.JULIAN),
            (9998, 12, _CalendarOrdinal.JULIAN),
            (5403, 1, _CalendarOrdinal.HEBREW_CIVIL),
            (5403, 12, _CalendarOrdinal.HEBREW_CIVIL),
            (5404, 1, _CalendarOrdinal.HEBREW_CIVIL),
            (5404, 13, _CalendarOrdinal.HEBREW_CIVIL),
        ],
    )
    def test_valid_construction_with_calendar(self, year: int, month: int, ordinal: _CalendarOrdinal) -> None:
        calendar = CalendarSystem._for_ordinal(ordinal)
        year_month = YearMonth(year=year, month=month, calendar=calendar)
        assert year_month.year == year
        assert year_month.month == month
        assert year_month.calendar == calendar

    @pytest.mark.parametrize(
        "year,month,ordinal",
        [
            (-9999, 1, _CalendarOrdinal.ISO),
            (10000, 1, _CalendarOrdinal.ISO),
            (2000, 0, _CalendarOrdinal.ISO),
            (2000, 13, _CalendarOrdinal.ISO),
            (5403, 13, _CalendarOrdinal.HEBREW_CIVIL),
            (5404, 14, _CalendarOrdinal.HEBREW_CIVIL),
            (-9998, 12, _CalendarOrdinal.JULIAN),
            (9999, 11, _CalendarOrdinal.JULIAN),
        ],
    )
    def test_invalid_construction_with_calendar(self, year: int, month: int, ordinal: _CalendarOrdinal) -> None:
        calendar = CalendarSystem._for_ordinal(ordinal)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            YearMonth(year=year, month=month, calendar=calendar)

    @pytest.mark.parametrize(
        "year_of_era,month,era",
        [
            (100, 1, Era.before_common),
            (2000, 1, Era.common),
        ],
    )
    def test_valid_construction_with_iso_era(self, year_of_era: int, month: int, era: Era) -> None:
        year_month = YearMonth(era=era, year_of_era=year_of_era, month=month)
        assert year_month.era == era
        assert year_month.year_of_era == year_of_era
        assert year_month.month == month
        assert year_month.calendar == CalendarSystem.iso

    @pytest.mark.parametrize(
        "year_of_era,month,era",
        [
            (0, 1, Era.before_common),
            (10000, 1, Era.before_common),
            (10000, 1, Era.common),
            (100, 13, Era.common),
            (100, 1, Era.anno_mundi),
        ],
    )
    def test_invalid_construction_with_iso_era(self, year_of_era: int, month: int, era: Era) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentException
            YearMonth(era=era, year_of_era=year_of_era, month=month)

    @pytest.mark.parametrize(
        "year_of_era,month,era,calendar_ordinal",
        [
            (100, 1, Era.before_common, _CalendarOrdinal.ISO),
            (2000, 1, Era.common, _CalendarOrdinal.ISO),
            (100, 1, Era.before_common, _CalendarOrdinal.JULIAN),
            (2000, 1, Era.common, _CalendarOrdinal.JULIAN),
            (5403, 1, Era.anno_mundi, _CalendarOrdinal.HEBREW_CIVIL),
        ],
    )
    def test_valid_construction_with_era_and_calendar(
        self, year_of_era: int, month: int, era: Era, calendar_ordinal: _CalendarOrdinal
    ) -> None:
        calendar = CalendarSystem._for_ordinal(calendar_ordinal)
        year_month = YearMonth(era=era, year_of_era=year_of_era, month=month, calendar=calendar)
        assert year_month.era == era
        assert year_month.year_of_era == year_of_era
        assert year_month.month == month
        assert year_month.calendar == calendar

    @pytest.mark.parametrize(
        "year_of_era,month,era,calendar_ordinal",
        [
            (0, 1, Era.before_common, _CalendarOrdinal.ISO),
            (10000, 1, Era.before_common, _CalendarOrdinal.ISO),
            (10000, 1, Era.common, _CalendarOrdinal.ISO),
            (100, 13, Era.common, _CalendarOrdinal.ISO),
            (100, 1, Era.anno_mundi, _CalendarOrdinal.ISO),
            (100, 1, Era.common, _CalendarOrdinal.HEBREW_SCRIPTURAL),
        ],
    )
    def test_invalid_construction_with_era_and_calendar(
        self, year_of_era: int, month: int, era: Era, calendar_ordinal: _CalendarOrdinal
    ) -> None:
        calendar = CalendarSystem._for_ordinal(calendar_ordinal)
        with pytest.raises(ValueError):  # TODO: ArgumentException
            YearMonth(era=era, year_of_era=year_of_era, month=month, calendar=calendar)


class TestYearMonthMisc:
    """Tests for YearMonth which don't naturally fall into other categories."""

    @pytest.mark.parametrize(
        "calendar_ordinal,year,month,day",
        [
            (_CalendarOrdinal.ISO, 1904, 2, 29),
            (_CalendarOrdinal.JULIAN, 1900, 2, 29),
            (_CalendarOrdinal.HEBREW_CIVIL, 5402, 2, 30),
            (_CalendarOrdinal.HEBREW_CIVIL, 5402, 3, 30),
            (_CalendarOrdinal.HEBREW_SCRIPTURAL, 5402, 8, 30),
            (_CalendarOrdinal.HEBREW_SCRIPTURAL, 5402, 9, 30),
        ],
    )
    def test_on_day_of_month_valid(self, calendar_ordinal: _CalendarOrdinal, year: int, month: int, day: int) -> None:
        calendar = CalendarSystem._for_ordinal(calendar_ordinal)
        year_month = YearMonth(year=year, month=month, calendar=calendar)
        actual_date = year_month.on_day_of_month(day)
        expected_date = LocalDate(year=year, month=month, day=day, calendar=calendar)
        assert actual_date == expected_date

    @pytest.mark.parametrize(
        "calendar_ordinal,year,month,day",
        [
            (_CalendarOrdinal.ISO, 1900, 2, 29),
            (_CalendarOrdinal.JULIAN, 1900, 2, 30),
            (_CalendarOrdinal.HEBREW_CIVIL, 5401, 2, 30),
            (_CalendarOrdinal.HEBREW_CIVIL, 5401, 3, 30),
            (_CalendarOrdinal.HEBREW_SCRIPTURAL, 5401, 8, 30),
            (_CalendarOrdinal.HEBREW_SCRIPTURAL, 5401, 9, 30),
        ],
    )
    def test_on_day_of_month_invalid(self, calendar_ordinal: _CalendarOrdinal, year: int, month: int, day: int) -> None:
        calendar = CalendarSystem._for_ordinal(calendar_ordinal)
        year_month = YearMonth(year=year, month=month, calendar=calendar)
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            year_month.on_day_of_month(day)

    @pytest.mark.parametrize(
        "year,month,months_to_add,expected_year,expected_month",
        [
            (2014, 8, 4, 2014, 12),
            (2014, 8, 5, 2015, 1),
            (2014, 8, 0, 2014, 8),
            (2014, 8, -1, 2014, 7),
            (2014, 8, -8, 2013, 12),
        ],
    )
    def test_plus_months(
        self, year: int, month: int, months_to_add: int, expected_year: int, expected_month: int
    ) -> None:
        year_month = YearMonth(year=year, month=month)
        expected = YearMonth(year=expected_year, month=expected_month)
        assert year_month.plus_months(months_to_add) == expected

    # TODO: def test_to_string_test_iso(self) [requires CultureInfo]
    # TODO: def test_to_string_bcl_equality(self) [requires CultureInfo]


# TODO: class TestXmlSerialization:
