# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import base64
from typing import Final, final

from .._year_month_day import _YearMonthDay
from ..utility._csharp_compatibility import _sealed, _towards_zero_division
from ..utility._preconditions import _Preconditions
from ._year_month_day_calculator import _YearMonthDayCalculator


@_sealed
@final
class _BadiYearMonthDayCalculator(_YearMonthDayCalculator):
    # named constants to avoid use of raw numbers in the code
    __AVERAGE_DAYS_PER_10_years: Final[int] = 3652
    __DAYS_IN_AYYAMI_HA_IN_LEAP_YEAR: Final[int] = 5
    __DAYS_IN_AYYAMI_HA_IN_NORMAL_YEAR: Final[int] = 4

    _DAYS_IN_MONTH: Final[int] = 19
    __FIRST_YEAR_OF_STANDARDIZED_CALENDAR: Final[int] = 172
    __GREGORIAN_YEAR_OF_FIRST_BADI_YEAR: Final[int] = 1844

    # There are 19 months in a year. Between the 18th and 19th month are the "days of Ha" (Ayyam-i-Ha).
    # In order to make everything else in Noda Time work appropriately, Ayyam-i-Ha are counted as
    # extra days at the end of month 18.
    _MONTH_18: Final[int] = 18
    __MONTH_19: Final[int] = 19
    __MONTHS_IN_YEAR: Final[int] = 19

    __UNIX_EPOCH_DAY_AT_START_OF_YEAR_1: Final[int] = -45941
    __BADI_MAX_YEAR: Final[int] = 1000  # current lookup tables are pre-calculated for a thousand years
    __BADI_MIN_YEAR: Final[int] = 1

    # This is the base64 representation of information for years 172 to 1000.
    # NazRuzDate falls on March 19, 20, 21, or 22.
    # DaysInAyymiHa can be 4,5.
    # For each year, the value in the array is (NawRuzDate - 19) + 10 * (DaysInAyyamiHa - 4)
    year_info_raw = base64.b64decode(
        "AgELAgIBCwICAQsCAgEBCwIBAQsCAQELAgEBCwIBAQsCAQELAgEBCwIBAQELAQEBCwEBAQsBAQELAQEB"
        "CwEBAQsBAQELAQEBCwEBAQEKAQEBCgEBAQsCAgILAgICCwICAgsCAgILAgICCwICAgELAgIBCwICAQsC"
        "AgELAgIBCwICAQsCAgELAgIBCwICAQELAgEBCwIBAQsCAQELAgEBCwIBAQsCAQELAgEBCwIBAQELAQEB"
        "CwEBAQsCAgIMAgICDAICAgwCAgIMAgICDAICAgILAgICCwICAgsCAgILAgICCwICAgsCAgILAgICCwIC"
        "AgELAgIBCwICAQsCAgELAgIBCwICAQsCAgELAgIBCwICAQELAgEBCwIBAQsCAgIMAwICDAMCAgwDAgIM"
        "AwICDAMCAgIMAgICDAICAgwCAgIMAgICDAICAgwCAgIMAgICDAICAgILAgICCwICAgsCAgILAgICCwIC"
        "AgsCAgILAgICAQsCAgELAgIBCwICAQsCAgELAgIBCwICAQsCAgELAgIBCwICAQELAgEBCwIBAQsCAQEL"
        "AgEBCwIBAQsCAQELAgEBCwIBAQELAQEBCwEBAQsBAQELAQEBCwEBAQsBAQELAQEBCwEBAQEKAQEBCgEB"
        "AQoBAQELAgICCwICAgsCAgILAgICAQsCAgELAgIBCwICAQsCAgELAgIBCwICAQsCAgELAgIBAQsCAQEL"
        "AgEBCwIBAQsCAQELAgEBCwIBAQsCAQELAgEBAQsBAQELAQEBCwEBAQsBAQELAgICDAICAgwCAgIMAgIC"
        "AgsCAgILAgICCwICAgsCAgILAgICCwICAgsCAgILAgICAQsCAgELAgIBCwICAQsCAgELAgIBCwICAQsC"
        "AgELAgIBAQsCAQELAgEBCwIBAQsCAQELAgICDAMCAgwDAgIMAwICAgwCAgIMAgICDAICAgwCAgIMAgIC"
        "DAICAgwCAgIMAgICAgsCAgILAgICCwICAgsCAgILAgICCwICAgsCAgILAgICAQsCAgELAgIBCwICAQsC"
        "AgELAgIBCwICAQsCAgELAgIBAQsCAQELAgEBCwIBAQsCAQELAgEBCwIBAQsCAQELAg=="
    )

    # TODO static ctor - Preconditions.DebugCheckState()

    def __init__(self) -> None:
        super().__init__(
            self.__BADI_MIN_YEAR,
            self.__BADI_MAX_YEAR - 1,
            self.__AVERAGE_DAYS_PER_10_years,
            self.__UNIX_EPOCH_DAY_AT_START_OF_YEAR_1,
        )

    @classmethod
    def _get_days_in_ayyami_ha(cls, year: int) -> int:
        from .. import CalendarSystem

        _Preconditions._check_argument_range("year", year, cls.__BADI_MIN_YEAR, cls.__BADI_MAX_YEAR)
        if year < cls.__FIRST_YEAR_OF_STANDARDIZED_CALENDAR:
            return (
                cls.__DAYS_IN_AYYAMI_HA_IN_LEAP_YEAR
                if CalendarSystem.iso._year_month_day_calculator._is_leap_year(
                    year + cls.__GREGORIAN_YEAR_OF_FIRST_BADI_YEAR
                )
                else cls.__DAYS_IN_AYYAMI_HA_IN_NORMAL_YEAR
            )
        num = cls.year_info_raw[year - cls.__FIRST_YEAR_OF_STANDARDIZED_CALENDAR]
        return cls.__DAYS_IN_AYYAMI_HA_IN_LEAP_YEAR if num > 10 else cls.__DAYS_IN_AYYAMI_HA_IN_NORMAL_YEAR

    @classmethod
    def __get_naw_ruz_day_in_march(cls, year: int) -> int:
        _Preconditions._check_argument_range("year", year, cls.__BADI_MIN_YEAR, cls.__BADI_MAX_YEAR)
        if year < cls.__FIRST_YEAR_OF_STANDARDIZED_CALENDAR:
            return 21
        day_in_march_for_offset_to_naw_ruz = 19
        num = cls.year_info_raw[year - cls.__FIRST_YEAR_OF_STANDARDIZED_CALENDAR]
        return day_in_march_for_offset_to_naw_ruz + (num % 10)

    def _calculate_start_of_year_days(self, year: int) -> int:
        from .. import LocalDate

        _Preconditions._check_argument_range("year", year, self.__BADI_MIN_YEAR, self.__BADI_MAX_YEAR)
        # The epoch is the same regardless of calendar system, so if we work out when the
        # start of the Badíʿ year is in terms of the Gregorian year, we can just use that
        # date's days-since-epoch value.
        gregorian_year = year + self.__GREGORIAN_YEAR_OF_FIRST_BADI_YEAR - 1
        naw_ruz = LocalDate(year=gregorian_year, month=3, day=self.__get_naw_ruz_day_in_march(year))
        return naw_ruz._days_since_epoch

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        days_from_start_of_year_to_start_of_month = self._DAYS_IN_MONTH * (month - 1)

        if month == self.__MONTH_19:
            days_from_start_of_year_to_start_of_month += self._get_days_in_ayyami_ha(year)

        return days_from_start_of_year_to_start_of_month

    def _add_months(self, start: _YearMonthDay, months: int) -> _YearMonthDay:
        if months == 0:
            return start

        moving_backwards = months < 0

        this_month = start._month
        this_year = start._year
        this_day = start._day

        next_day = this_day

        # TODO: It's not clear that this is correct. If we add 19 months, it's probably okay to stay in Ayyam-i-Ha.
        if self.__is_in_ayyami_ha(start):
            next_day = this_day - self._DAYS_IN_MONTH

            if moving_backwards:
                this_month += 1

        next_year = this_year
        next_month_num = this_month + months

        if next_month_num > self.__MONTHS_IN_YEAR:
            next_year = this_year + _towards_zero_division(next_month_num, self.__MONTHS_IN_YEAR)
            next_month_num = next_month_num % self.__MONTHS_IN_YEAR
        elif next_month_num < 1:
            next_month_num = self.__MONTHS_IN_YEAR - next_month_num
            next_year = this_year - _towards_zero_division(next_month_num, self.__MONTHS_IN_YEAR)
            next_month_num = self.__MONTHS_IN_YEAR - next_month_num % self.__MONTHS_IN_YEAR

        if next_year < self._min_year or next_year > self._max_year:
            raise OverflowError("Date computation would overflow calendar bounds.")

        result = _YearMonthDay._ctor(year=next_year, month=next_month_num, day=next_day)

        return result

    def _get_days_in_month(self, year: int, month: int) -> int:
        _Preconditions._check_argument_range("year", year, self.__BADI_MIN_YEAR, self.__BADI_MAX_YEAR)
        return (
            self._DAYS_IN_MONTH + self._get_days_in_ayyami_ha(year) if month == self._MONTH_18 else self._DAYS_IN_MONTH
        )

    def _get_days_in_year(self, year: int) -> int:
        return 361 + self._get_days_in_ayyami_ha(year)

    def _get_days_since_epoch(self, target: _YearMonthDay) -> int:
        month = target._month
        year = target._year

        first_day_0_of_year = self._calculate_start_of_year_days(year) - 1

        days_since_epoch = first_day_0_of_year + (month - 1) * self._DAYS_IN_MONTH + target._day

        if month == self.__MONTH_19:
            days_since_epoch += self._get_days_in_ayyami_ha(year)

        return days_since_epoch

    def _get_months_in_year(self, year: int) -> int:
        return self.__MONTHS_IN_YEAR

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        _Preconditions._check_argument_range("day_of_year", day_of_year, 1, self._get_days_in_year(year))

        first_of_loftiness = 1 + self._DAYS_IN_MONTH * self._MONTH_18 + self._get_days_in_ayyami_ha(year)

        if day_of_year >= first_of_loftiness:
            return _YearMonthDay._ctor(year=year, month=self.__MONTH_19, day=day_of_year - first_of_loftiness + 1)

        month = min(int(1 + (day_of_year - 1) / self._DAYS_IN_MONTH), self._MONTH_18)
        day = day_of_year - (month - 1) * self._DAYS_IN_MONTH

        return _YearMonthDay._ctor(year=year, month=month, day=day)

    @classmethod
    def __is_in_ayyami_ha(cls, ymd: _YearMonthDay) -> bool:
        return (ymd._month == cls._MONTH_18) and (ymd._day > cls._DAYS_IN_MONTH)

    def _is_leap_year(self, year: int) -> bool:
        return self._get_days_in_ayyami_ha(year) != self.__DAYS_IN_AYYAMI_HA_IN_NORMAL_YEAR

    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        start_month = start._month
        start_year = start._year

        end_month = end._month
        end_year = end._year

        diff = (end_year - start_year) * self.__MONTHS_IN_YEAR + end_month - start_month

        # If we just add the difference in months to start, what do we get?
        simple_addition = self._add_months(start, diff)

        # Note: this relies on naive comparison of year/month/date values.
        if start <= end:
            # Moving forward: if the result of the simple addition is before or equal to the end,
            # we're done. Otherwise, rewind a month because we've overshot.
            return diff if simple_addition <= end else diff - 1
        else:
            # Moving backward: if the result of the simple addition (of a non-positive number)
            # is after or equal to the end, we're done. Otherwise, increment by a month because
            # we've overshot backwards.
            return diff if simple_addition >= end else diff + 1

    def _set_year(self, start: _YearMonthDay, new_year: int) -> _YearMonthDay:
        _Preconditions._check_argument_range("new_year", new_year, self.__BADI_MIN_YEAR, self.__BADI_MAX_YEAR)

        month = start._month
        day = start._day

        if self.__is_in_ayyami_ha(start):
            days_in_this_ayyami_ha = self._get_days_in_ayyami_ha(new_year)
            return _YearMonthDay._ctor(
                year=new_year, month=month, day=min(day, self._DAYS_IN_MONTH + days_in_this_ayyami_ha)
            )

        return _YearMonthDay._ctor(year=new_year, month=month, day=day)

    def _validate_year_month_day(self, year: int, month: int, day: int) -> None:
        _Preconditions._check_argument_range("year", year, self.__BADI_MIN_YEAR, self.__BADI_MAX_YEAR)
        _Preconditions._check_argument_range("month", month, 1, self.__MONTHS_IN_YEAR)

        days_in_month = (
            self._DAYS_IN_MONTH + self._get_days_in_ayyami_ha(year) if month == self._MONTH_18 else self._DAYS_IN_MONTH
        )
        _Preconditions._check_argument_range("day", day, 1, days_in_month)
