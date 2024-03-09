# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Final

import pytest

from pyoda_time import (
    CalendarSystem,
    DateAdjusters,
    DateTimeZone,
    IsoDayOfWeek,
    LocalDate,
    Period,
    PeriodUnits,
    PyodaConstants,
)
from pyoda_time.calendars import Era, _BadiYearMonthDayCalculator
from pyoda_time.utility import _Preconditions


class TestBadiCalendarSystem:
    """Tests for the Badíʿ calendar system."""

    # For use with CreateBadíʿDate, this is a notional "month"
    # containing Ayyam-i-Ha. The days here are represented in month
    # 18 in LocalDate etc.
    __AYYAMI_HA_MONTH: Final[int] = 0

    # TODO: def test_badi_epoch(self) -> None: [requires LocalDatePattern.bclsupport]

    def test_unix_epoch(self) -> None:
        badi: CalendarSystem = CalendarSystem.badi
        unix_epoch_in_badi_calendar: LocalDate = PyodaConstants.UNIX_EPOCH.in_zone(
            DateTimeZone.utc, badi
        ).local_date_time.date
        expected: LocalDate = self.__create_badi_date(126, 16, 2)
        assert unix_epoch_in_badi_calendar == expected

    def test_sample_date(self) -> None:
        badi_calendar: CalendarSystem = CalendarSystem.badi
        iso: LocalDate = LocalDate(year=2017, month=3, day=4)
        badi: LocalDate = iso.with_calendar(badi_calendar)

        assert self._badi_month(badi) == 19

        assert badi.era == Era.bahai
        assert badi.year_of_era == 173

        assert badi.year == 173
        assert not badi_calendar.is_leap_year(173)

        assert self._badi_day(badi) == 4

        assert badi.day_of_week == IsoDayOfWeek.SATURDAY

    @pytest.mark.parametrize(
        "g_year,g_month,g_day,b_year,b_month,b_day",
        [
            (2016, 2, 26, 172, __AYYAMI_HA_MONTH, 1),
            (2016, 2, 29, 172, __AYYAMI_HA_MONTH, 4),
            (2016, 3, 1, 172, 19, 1),
            (2016, 3, 20, 173, 1, 1),
            (2016, 3, 21, 173, 1, 2),
            (2016, 5, 26, 173, 4, 11),
            (2017, 3, 20, 174, 1, 1),
            (2018, 3, 21, 175, 1, 1),
            (2019, 3, 21, 176, 1, 1),
            (2020, 3, 20, 177, 1, 1),
            (2021, 3, 20, 178, 1, 1),
            (2022, 3, 21, 179, 1, 1),
            (2023, 3, 21, 180, 1, 1),
            (2024, 3, 20, 181, 1, 1),
            (2025, 3, 20, 182, 1, 1),
            (2026, 3, 21, 183, 1, 1),
            (2027, 3, 21, 184, 1, 1),
            (2028, 3, 20, 185, 1, 1),
            (2029, 3, 20, 186, 1, 1),
            (2030, 3, 20, 187, 1, 1),
            (2031, 3, 21, 188, 1, 1),
            (2032, 3, 20, 189, 1, 1),
            (2033, 3, 20, 190, 1, 1),
            (2034, 3, 20, 191, 1, 1),
            (2035, 3, 21, 192, 1, 1),
            (2036, 3, 20, 193, 1, 1),
            (2037, 3, 20, 194, 1, 1),
            (2038, 3, 20, 195, 1, 1),
            (2039, 3, 21, 196, 1, 1),
            (2040, 3, 20, 197, 1, 1),
            (2041, 3, 20, 198, 1, 1),
            (2042, 3, 20, 199, 1, 1),
            (2043, 3, 21, 200, 1, 1),
            (2044, 3, 20, 201, 1, 1),
            (2045, 3, 20, 202, 1, 1),
            (2046, 3, 20, 203, 1, 1),
            (2047, 3, 21, 204, 1, 1),
            (2048, 3, 20, 205, 1, 1),
            (2049, 3, 20, 206, 1, 1),
            (2050, 3, 20, 207, 1, 1),
            (2051, 3, 21, 208, 1, 1),
            (2052, 3, 20, 209, 1, 1),
            (2053, 3, 20, 210, 1, 1),
            (2054, 3, 20, 211, 1, 1),
            (2055, 3, 21, 212, 1, 1),
            (2056, 3, 20, 213, 1, 1),
            (2057, 3, 20, 214, 1, 1),
            (2058, 3, 20, 215, 1, 1),
            (2059, 3, 20, 216, 1, 1),
            (2060, 3, 20, 217, 1, 1),
            (2061, 3, 20, 218, 1, 1),
            (2062, 3, 20, 219, 1, 1),
            (2063, 3, 20, 220, 1, 1),
            (2064, 3, 20, 221, 1, 1),
        ],
    )
    def test_general_conversion_near_naw_ruz(
        self, g_year: int, g_month: int, g_day: int, b_year: int, b_month: int, b_day: int
    ) -> None:
        # create in the Badíʿ calendar
        b_date = self.__create_badi_date(b_year, b_month, b_day)
        g_date = b_date.with_calendar(CalendarSystem.gregorian)
        assert g_date.year == g_year
        assert g_date.month == g_month
        assert g_date.day == g_day

        # convert to the Badíʿ calendar
        b_date_2 = LocalDate(year=g_year, month=g_month, day=g_day).with_calendar(CalendarSystem.badi)
        assert b_date_2.year == b_date.year
        assert self._badi_month(b_date_2) == b_month
        assert self._badi_day(b_date_2) == b_day

    @pytest.mark.parametrize(
        "g_year,g_month,g_day,b_year,b_month,b_day",
        [
            (2012, 2, 29, 168, __AYYAMI_HA_MONTH, 4),
            (2012, 3, 1, 168, __AYYAMI_HA_MONTH, 5),
            (2015, 3, 1, 171, __AYYAMI_HA_MONTH, 4),
            (2016, 3, 1, 172, 19, 1),
            (2016, 3, 19, 172, 19, 19),
            (2017, 3, 1, 173, 19, 1),
            (2017, 3, 19, 173, 19, 19),
            (2018, 2, 24, 174, 18, 19),
            (2018, 2, 25, 174, __AYYAMI_HA_MONTH, 1),
            (2018, 3, 1, 174, __AYYAMI_HA_MONTH, 5),
            (2018, 3, 2, 174, 19, 1),
            (2018, 3, 19, 174, 19, 18),
        ],
    )
    def test_special_cases(self, g_year: int, g_month: int, g_day: int, b_year: int, b_month: int, b_day: int) -> None:
        # create in test calendar
        b_date: LocalDate = self.__create_badi_date(b_year, b_month, b_day)

        # convert to gregorian
        g_date: LocalDate = b_date.with_calendar(CalendarSystem.gregorian)

        assert f"{g_date.year}-{g_date.month}-{g_date.day}" == f"{g_year}-{g_month}-{g_day}"

    @pytest.mark.parametrize(
        "b_year,b_month,b_day,g_year,g_month,g_day",
        [
            (1, 1, 1, 1844, 3, 21),
            (169, 1, 1, 2012, 3, 21),
            (170, 1, 1, 2013, 3, 21),
            (171, 1, 1, 2014, 3, 21),
            (172, __AYYAMI_HA_MONTH, 1, 2016, 2, 26),
            (172, __AYYAMI_HA_MONTH, 2, 2016, 2, 27),
            (172, __AYYAMI_HA_MONTH, 3, 2016, 2, 28),
            (172, __AYYAMI_HA_MONTH, 4, 2016, 2, 29),
            (172, 1, 1, 2015, 3, 21),
            (172, 17, 18, 2016, 2, 5),
            (172, 18, 17, 2016, 2, 23),
            (172, 18, 19, 2016, 2, 25),
            (172, 19, 1, 2016, 3, 1),
            (173, 1, 1, 2016, 3, 20),
            (174, 1, 1, 2017, 3, 20),
            (175, 1, 1, 2018, 3, 21),
            (176, 1, 1, 2019, 3, 21),
            (177, 1, 1, 2020, 3, 20),
            (178, 1, 1, 2021, 3, 20),
            (179, 1, 1, 2022, 3, 21),
            (180, 1, 1, 2023, 3, 21),
            (181, 1, 1, 2024, 3, 20),
            (182, 1, 1, 2025, 3, 20),
            (183, 1, 1, 2026, 3, 21),
            (184, 1, 1, 2027, 3, 21),
            (185, 1, 1, 2028, 3, 20),
            (186, 1, 1, 2029, 3, 20),
            (187, 1, 1, 2030, 3, 20),
            (188, 1, 1, 2031, 3, 21),
            (189, 1, 1, 2032, 3, 20),
            (190, 1, 1, 2033, 3, 20),
            (191, 1, 1, 2034, 3, 20),
            (192, 1, 1, 2035, 3, 21),
            (193, 1, 1, 2036, 3, 20),
            (194, 1, 1, 2037, 3, 20),
            (195, 1, 1, 2038, 3, 20),
            (196, 1, 1, 2039, 3, 21),
            (197, 1, 1, 2040, 3, 20),
            (198, 1, 1, 2041, 3, 20),
            (199, 1, 1, 2042, 3, 20),
            (200, 1, 1, 2043, 3, 21),
            (201, 1, 1, 2044, 3, 20),
            (202, 1, 1, 2045, 3, 20),
            (203, 1, 1, 2046, 3, 20),
            (204, 1, 1, 2047, 3, 21),
            (205, 1, 1, 2048, 3, 20),
            (206, 1, 1, 2049, 3, 20),
            (207, 1, 1, 2050, 3, 20),
            (208, 1, 1, 2051, 3, 21),
            (209, 1, 1, 2052, 3, 20),
            (210, 1, 1, 2053, 3, 20),
            (211, 1, 1, 2054, 3, 20),
            (212, 1, 1, 2055, 3, 21),
            (213, 1, 1, 2056, 3, 20),
            (214, 1, 1, 2057, 3, 20),
            (215, 1, 1, 2058, 3, 20),
            (216, 1, 1, 2059, 3, 20),
            (217, 1, 1, 2060, 3, 20),
            (218, 1, 1, 2061, 3, 20),
            (219, 1, 1, 2062, 3, 20),
            (220, 1, 1, 2063, 3, 20),
            (221, 1, 1, 2064, 3, 20),
        ],
    )
    def test_general_w_to_g(self, b_year: int, b_month: int, b_day: int, g_year: int, g_month: int, g_day: int) -> None:
        # create in this calendar
        b_date = self.__create_badi_date(b_year, b_month, b_day)
        g_date = b_date.with_calendar(CalendarSystem.gregorian)
        assert g_date.year == g_year
        assert g_date.month == g_month
        assert g_date.day == g_day

        # convert to this calendar
        b_date_2 = LocalDate(year=g_year, month=g_month, day=g_day).with_calendar(CalendarSystem.badi)
        assert b_date_2.year == b_year
        assert self._badi_month(b_date_2) == b_month
        assert self._badi_day(b_date_2) == b_day

    @pytest.mark.parametrize(
        "b_year,days",
        [
            (172, 4),
            (173, 4),
            (174, 5),
            (175, 4),
            (176, 4),
            (177, 4),
            (178, 5),
            (179, 4),
            (180, 4),
            (181, 4),
            (182, 5),
            (183, 4),
            (184, 4),
            (185, 4),
            (186, 4),
            (187, 5),
            (188, 4),
            (189, 4),
            (190, 4),
            (191, 5),
            (192, 4),
            (193, 4),
            (194, 4),
            (195, 5),
            (196, 4),
            (197, 4),
            (198, 4),
            (199, 5),
            (200, 4),
            (201, 4),
            (202, 4),
            (203, 5),
            (204, 4),
            (205, 4),
            (206, 4),
            (207, 5),
            (208, 4),
            (209, 4),
            (210, 4),
            (211, 5),
            (212, 4),
            (213, 4),
            (214, 4),
            (215, 4),
            (216, 5),
            (217, 4),
            (218, 4),
            (219, 4),
            (220, 5),
            (221, 4),
        ],
    )
    def test_days_in_ayyami_ha(self, b_year: int, days: int) -> None:
        assert _BadiYearMonthDayCalculator._get_days_in_ayyami_ha(b_year) == days

    @pytest.mark.parametrize(
        "b_year,b_month,b_day,day_of_year",
        [
            (165, 1, 1, 1),
            (170, 1, 1, 1),
            (172, 1, 1, 1),
            (175, 1, 1, 1),
            (173, 18, 1, 17 * 19 + 1),
            (173, 18, 19, 18 * 19),
            (173, __AYYAMI_HA_MONTH, 1, 18 * 19 + 1),
            (173, 19, 1, 18 * 19 + 5),
            (220, __AYYAMI_HA_MONTH, 1, 18 * 19 + 1),
            (220, __AYYAMI_HA_MONTH, 5, 18 * 19 + 5),
            (220, 19, 1, 18 * 19 + 6),
        ],
    )
    def test_day_of_year(self, b_year: int, b_month: int, b_day: int, day_of_year: int) -> None:
        badi = _BadiYearMonthDayCalculator()
        assert badi._get_day_of_year(self.__create_badi_date(b_year, b_month, b_day)._year_month_day) == day_of_year

    @pytest.mark.parametrize(
        "year,month,day,eom_month,eom_day",
        [
            (173, 1, 1, 1, 19),
            (173, 18, 1, __AYYAMI_HA_MONTH, 4),
            (173, __AYYAMI_HA_MONTH, 1, __AYYAMI_HA_MONTH, 4),
            (173, 19, 1, 19, 19),
            (220, 19, 1, 19, 19),
            (220, 4, 5, 4, 19),
            (220, 18, 1, __AYYAMI_HA_MONTH, 5),
            (220, __AYYAMI_HA_MONTH, 1, __AYYAMI_HA_MONTH, 5),
        ],
    )
    def test_end_of_month(self, year: int, month: int, day: int, eom_month: int, eom_day: int) -> None:
        start: LocalDate = self.__create_badi_date(year, month, day)
        end: LocalDate = self.__create_badi_date(year, eom_month, eom_day)
        assert self.as_badi_string(DateAdjusters.end_of_month(start)) == self.as_badi_string(end)

    def test_leap_year(self) -> None:
        calendar: CalendarSystem = CalendarSystem.badi
        assert not calendar.is_leap_year(172)
        assert not calendar.is_leap_year(173)
        assert calendar.is_leap_year(207)
        assert calendar.is_leap_year(220)

    def test_get_months_in_year(self) -> None:
        calendar: CalendarSystem = CalendarSystem.badi
        assert calendar.get_months_in_year(180) == 19

    def test_create_date_in_ayyami_ha(self) -> None:
        d1 = self.__create_badi_date(180, 0, 3)
        d3 = self.__create_badi_date(180, 18, 22)

        assert d3 == d1

    @pytest.mark.parametrize(
        "year,month,day",
        [
            (180, -1, 1),
            (180, 1, -1),
            (180, 0, 0),
            (180, 0, 5),
            (182, 0, 6),
            (180, 1, 0),
            (180, 1, 20),
            (180, 20, 1),
        ],
    )
    def test_create_date_invalid(self, year: int, month: int, day: int) -> None:
        with pytest.raises(ValueError):
            self.__create_badi_date(year, month, day)

    # Period-related tests

    @property
    def __test_date_1_167_5_15(self) -> LocalDate:
        return self.__create_badi_date(167, 5, 15)

    @property
    def __test_date_1_167_6_7(self) -> LocalDate:
        return self.__create_badi_date(167, 6, 7)

    @property
    def __test_date_2_167_ayyam_4(self) -> LocalDate:
        return self.__create_badi_date(167, self.__AYYAMI_HA_MONTH, 4)

    @property
    def __test_date_3_168_ayyam_5(self) -> LocalDate:
        return self.__create_badi_date(168, self.__AYYAMI_HA_MONTH, 5)

    def test_between_local_dates_invalid_units(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentException
            Period.between(self.__test_date_1_167_5_15, self.__test_date_2_167_ayyam_4, PeriodUnits.NONE)
        with pytest.raises(ValueError):  # TODO: ArgumentException
            Period.between(self.__test_date_1_167_5_15, self.__test_date_2_167_ayyam_4, PeriodUnits(-1))
        with pytest.raises(ValueError):  # TODO: ArgumentException
            Period.between(self.__test_date_1_167_5_15, self.__test_date_2_167_ayyam_4, PeriodUnits.ALL_TIME_UNITS)
        with pytest.raises(ValueError):  # TODO: ArgumentException
            Period.between(
                self.__test_date_1_167_5_15, self.__test_date_2_167_ayyam_4, PeriodUnits.YEARS | PeriodUnits.HOURS
            )

    def test_set_year(self) -> None:
        # crafted to test SetYear with 0
        d1 = self.__create_badi_date(180, 1, 1)
        result: LocalDate = d1 + Period.from_years(0)
        assert result.year == 180

    def test_between_local_dates_moving_forward_no_leap_years_with_exact_results(self) -> None:
        actual: Period = Period.between(self.__test_date_1_167_5_15, self.__test_date_1_167_6_7)
        expected: Period = Period.from_days(11)
        assert actual == expected

    def test_between_local_dates_moving_forward_no_leap_years_with_exact_results_2(self) -> None:
        actual: Period = Period.between(self.__test_date_1_167_5_15, self.__test_date_2_167_ayyam_4)
        expected: Period = Period.from_months(13) + Period.from_days(8)
        assert actual == expected

    def test_between_local_dates_moving_forward_in_leap_year_with_exact_results(self) -> None:
        actual: Period = Period.between(self.__test_date_1_167_5_15, self.__test_date_3_168_ayyam_5)
        expected: Period = Period.from_years(1) + Period.from_months(13) + Period.from_days(9)
        assert actual == expected

    def test_between_local_dates_moving_backward_no_leap_years_with_exact_results(self) -> None:
        actual: Period = Period.between(self.__test_date_2_167_ayyam_4, self.__test_date_1_167_5_15)
        expected: Period = Period.from_months(-13) + Period.from_days(-8)
        assert actual == expected

    def test_between_local_dates_moving_backward_with_exact_results(self) -> None:
        # should be -1y -13m -9d
        # but system first moves back a year, and in that year, the last day of Ayyam-i-Ha is day 4
        # from there, it is -13m -8d

        expected: Period = Period.from_years(-1) + Period.from_months(-13) + Period.from_days(-8)
        actual: Period = Period.between(self.__test_date_3_168_ayyam_5, self.__test_date_1_167_5_15)
        assert actual == expected

    def test_between_local_dates_moving_forward_with_just_months(self) -> None:
        actual: Period = Period.between(self.__test_date_1_167_5_15, self.__test_date_3_168_ayyam_5, PeriodUnits.MONTHS)
        expected: Period = Period.from_months(32)
        assert actual == expected

    def test_between_local_dates_moving_backward_with_just_months(self) -> None:
        actual: Period = Period.between(self.__test_date_3_168_ayyam_5, self.__test_date_1_167_5_15, PeriodUnits.MONTHS)
        expected: Period = Period.from_months(-32)
        assert actual == expected

    def test_between_local_dates_asymmetric_forward_and_backward(self) -> None:
        d1: LocalDate = self.__create_badi_date(166, 18, 4)
        d2: LocalDate = self.__create_badi_date(167, 1, 10)

        # spanning Ayyam-i-Ha - not counted as a month
        assert Period.between(d1, d2) == Period.from_months(2) + Period.from_days(6)
        assert Period.between(d2, d1) == Period.from_months(-2) + Period.from_days(-6)

    def test_between_local_dates_end_of_month(self) -> None:
        d1: LocalDate = self.__create_badi_date(171, 5, 19)
        d2: LocalDate = self.__create_badi_date(171, 6, 19)
        assert Period.between(d1, d2) == Period.from_months(1)
        assert Period.between(d2, d1) == Period.from_months(-1)

    def test_between_local_dates_on_leap_year(self) -> None:
        d1: LocalDate = LocalDate(year=2012, month=2, day=29).with_calendar(CalendarSystem.badi)
        d2: LocalDate = LocalDate(year=2013, month=2, day=28).with_calendar(CalendarSystem.badi)

        assert self.as_badi_string(d1) == "168-0-4"
        assert self.as_badi_string(d2) == "169-0-3"

        assert Period.between(d1, d2) == Period.from_months(19) + Period.from_days(18)

    def test_between_local_dates_after_leap_year(self) -> None:
        d1: LocalDate = self.__create_badi_date(180, 19, 5)
        d2: LocalDate = self.__create_badi_date(181, 19, 5)
        assert Period.between(d1, d2) == Period.from_years(1)
        assert Period.between(d2, d1) == Period.from_years(-1)

    def test_addition_day_crossing_month_boundary(self) -> None:
        start: LocalDate = self.__create_badi_date(182, 4, 13)
        result: LocalDate = start + Period.from_days(10)
        assert result == self.__create_badi_date(182, 5, 4)

    def test_addition(self) -> None:
        start = self.__create_badi_date(182, 1, 1)

        result = start + Period.from_days(3)
        assert result == self.__create_badi_date(182, 1, 4)

        result = start + Period.from_days(20)
        assert result == self.__create_badi_date(182, 2, 2)

    def test_addition_day_crossing_month_boundary_from_ayyami_ha(self) -> None:
        start = self.__create_badi_date(182, self.__AYYAMI_HA_MONTH, 3)
        result = start + Period.from_days(10)
        # in 182, Ayyam-i-Ha has 5 days
        assert result == self.__create_badi_date(182, 19, 8)

    def test_addition_one_year_on_leap_day(self) -> None:
        start: LocalDate = self.__create_badi_date(182, self.__AYYAMI_HA_MONTH, 5)
        result: LocalDate = start + Period.from_years(1)
        # Ayyam-i-Ha 5 becomes Ayyam-i-Ha 4
        assert result == self.__create_badi_date(183, self.__AYYAMI_HA_MONTH, 4)

    def test_addition_five_years_on_leap_day(self) -> None:
        start: LocalDate = self.__create_badi_date(182, self.__AYYAMI_HA_MONTH, 5)
        result: LocalDate = start + Period.from_years(5)
        assert result == self.__create_badi_date(187, self.__AYYAMI_HA_MONTH, 5)

    def test_addition_year_month_day(self) -> None:
        # One year, one month, two days
        period: Period = Period.from_years(1) + Period.from_months(1) + Period.from_days(2)
        start: LocalDate = self.__create_badi_date(171, 1, 19)
        # Periods are added in order, so this becomes...
        # Add one year: 172.1.19
        # Add one month: 172.2.19
        # Add two days: 172.3.2
        result: LocalDate = start + period
        assert result == self.__create_badi_date(172, 3, 2)

    def test_plus_months_overflow(self) -> None:
        calendar: CalendarSystem = CalendarSystem.badi
        early_date: LocalDate = LocalDate(year=calendar.min_year, month=1, day=1, calendar=calendar)
        late_date: LocalDate = LocalDate(year=calendar.max_year, month=19, day=1, calendar=calendar)

        with pytest.raises(OverflowError):
            early_date.plus_months(-1)
        with pytest.raises(OverflowError):
            late_date.plus_months(1)

    @classmethod
    def __create_badi_date(cls, year: int, month: int, day: int) -> LocalDate:
        """Create a ``LocalDate`` in the Badíʿ calendar, treating 0 as the month containing Ayyam-i-Ha.

        :param year: Year in the Badíʿ calendar
        :param month: Month (use 0 for Ayyam-i-Ha)
        :param day: Day in month
        :return: A ``LocalDate`` in the Badíʿ calendar
        """
        if month == cls.__AYYAMI_HA_MONTH:
            _Preconditions._check_argument_range(
                "day", day, 1, _BadiYearMonthDayCalculator._get_days_in_ayyami_ha(year)
            )
            # Move Ayyam-i-Ha days to fall after the last day of month 18.
            month = _BadiYearMonthDayCalculator._MONTH_18
            day += _BadiYearMonthDayCalculator._DAYS_IN_MONTH
        return LocalDate(year=year, month=month, day=day, calendar=CalendarSystem.badi)

    @classmethod
    def _badi_day(cls, input: LocalDate) -> int:
        _Preconditions._check_argument(
            input.calendar == CalendarSystem.badi, "input", "Only valid when using the Badíʿ calendar"
        )

        if (
            input.month == _BadiYearMonthDayCalculator._MONTH_18
            and input.day > _BadiYearMonthDayCalculator._DAYS_IN_MONTH
        ):
            return input.day - _BadiYearMonthDayCalculator._DAYS_IN_MONTH
        return input.day

    @classmethod
    def _badi_month(cls, input: LocalDate) -> int:
        """Return the month of this date.

        If in Ayyam-i-Ha, returns 0.
        """
        _Preconditions._check_argument(
            input.calendar == CalendarSystem.badi, "input", "Only valid when using the Badíʿ calendar"
        )
        if (
            input.month == _BadiYearMonthDayCalculator._MONTH_18
            and input.day > _BadiYearMonthDayCalculator._DAYS_IN_MONTH
        ):
            return cls.__AYYAMI_HA_MONTH
        return input.month

    @classmethod
    def as_badi_string(cls, input: LocalDate) -> str:
        """Get a text representation of the date."""
        year = input.year
        month = cls._badi_month(input)
        day = cls._badi_day(input)

        return f"{year}-{month}-{day}"

    def test_helper_method_badi_day(self) -> None:
        # ensure that this helper method is working
        assert self._badi_day(self.__create_badi_date(180, 10, 10)) == 10
        assert self._badi_day(self.__create_badi_date(180, 18, 19)) == 19
        assert self._badi_day(self.__create_badi_date(180, 0, 3)) == 3
        assert self._badi_day(self.__create_badi_date(180, 19, 1)) == 1

    def test_helper_method_badi_month(self) -> None:
        # ensure that this helper method is working
        assert self._badi_month(self.__create_badi_date(180, 10, 10)) == 10
        assert self._badi_month(self.__create_badi_date(180, 18, 19)) == 18
        assert self._badi_month(self.__create_badi_date(180, 0, 3)) == 0
        assert self._badi_month(self.__create_badi_date(180, 19, 1)) == 19

    def test_helper_method_as_badi_string(self) -> None:
        # ensure that this helper method is working
        assert self.as_badi_string(self.__create_badi_date(180, 10, 10)) == "180-10-10"
        assert self.as_badi_string(self.__create_badi_date(180, 18, 19)) == "180-18-19"
        assert self.as_badi_string(self.__create_badi_date(180, 0, 3)) == "180-0-3"
        assert self.as_badi_string(self.__create_badi_date(180, 19, 1)) == "180-19-1"
