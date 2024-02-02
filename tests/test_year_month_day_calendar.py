# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time._calendar_ordinal import _CalendarOrdinal
from pyoda_time._year_month_day_calendar import _YearMonthDayCalendar


class TestYearMonthDayCalendar:
    def test_all_years(self) -> None:
        for year in range(-9_999, 10_000):
            ymdc = _YearMonthDayCalendar._ctor(year=year, month=5, day=20, calendar_ordinal=_CalendarOrdinal(0))
            assert ymdc._year == year
            assert ymdc._month == 5
            assert ymdc._day == 20
            assert _CalendarOrdinal.ISO == ymdc._calendar_ordinal

    def test_all_months(self) -> None:
        for month in range(1, 33):
            ymdc = _YearMonthDayCalendar._ctor(
                year=-123, month=month, day=20, calendar_ordinal=_CalendarOrdinal.HEBREW_CIVIL
            )
            assert ymdc._year == -123
            assert ymdc._month == month
            assert ymdc._day == 20
            assert _CalendarOrdinal.HEBREW_CIVIL == ymdc._calendar_ordinal

    def test_all_days(self) -> None:
        for day in range(1, 65):
            ymdc = _YearMonthDayCalendar._ctor(
                year=-123, month=12, day=day, calendar_ordinal=_CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15
            )
            assert ymdc._year == -123
            assert ymdc._month == 12
            assert ymdc._day == day
            assert ymdc._calendar_ordinal == _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15

    def test_all_calendars(self) -> None:
        # TODO: In C# this test casts integers to CalendarOrdinal which are outisde the range of the enum - why??
        for calendar in _CalendarOrdinal:
            ymdc = _YearMonthDayCalendar._ctor(year=-123, month=30, day=64, calendar_ordinal=calendar)
            assert ymdc._year == -123
            assert ymdc._month == 30
            assert ymdc._day == 64
            assert ymdc._calendar_ordinal == calendar

    # TODO: def test_equality():

    @pytest.mark.parametrize(
        "text,year,month,day,calendar",
        [
            ("2017-08-21-JULIAN", 2017, 8, 21, _CalendarOrdinal.JULIAN),
            ("-0005-08-21-ISO", -5, 8, 21, _CalendarOrdinal.ISO),
        ],
    )
    def test_parse(self, text: str, year: int, month: int, day: int, calendar: _CalendarOrdinal) -> None:
        value: _YearMonthDayCalendar = _YearMonthDayCalendar._parse(text)
        assert value._year == year
        assert value._month == month
        assert value._day == day
        assert value._calendar_ordinal == calendar
