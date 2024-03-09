# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import base64
import typing

from ..utility import _csharp_modulo, _towards_zero_division
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator

if typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay


class _PersianYearMonthDayCalculator(_RegularYearMonthDayCalculator, abc.ABC):
    """Base class for the three variants of the Persian (Solar Hijri) calendar.

    Concrete subclasses are nested to allow different start dates and leap year calculations.

    The constructor uses IsLeapYear to precompute lots of data; it is therefore important that the implementation of
    IsLeapYear in subclasses uses no instance fields.
    """

    __DAYS_PER_NON_LEAP_YEAR: typing.Final[int] = (31 * 6) + (30 * 5) + 29
    __DAYS_PER_LEAP_YEAR: typing.Final[int] = __DAYS_PER_NON_LEAP_YEAR + 1
    # Approximation; it'll be pretty close in all variants.
    __AVERAGE_DAYS_PER_10_YEARS: typing.Final[int] = _towards_zero_division(
        (__DAYS_PER_NON_LEAP_YEAR * 25 + __DAYS_PER_LEAP_YEAR * 8) * 10, 33
    )
    _MAX_PERSIAN_YEAR: typing.Final[int] = 9377

    @staticmethod
    def __generate_total_days_by_month() -> list[int]:
        days = 0
        ret = [0]
        for i in range(1, 13):
            ret.append(days)
            days_in_month = 31 if i <= 6 else 30
            # This doesn't take account of leap years, but that doesn't matter - because
            # it's not used on the last iteration, and leap years only affect the final month
            # in the Persian calendar.
            days += days_in_month
        return ret

    # The number of days preceding the 1-indexed month - so [0, 0, 31, 62, 93, ...]
    __total_days_by_month: list[int] = __generate_total_days_by_month()

    def __init__(self, days_at_start_of_year_1: int) -> None:
        super().__init__(1, self._MAX_PERSIAN_YEAR, 12, self.__AVERAGE_DAYS_PER_10_YEARS, days_at_start_of_year_1)
        self.__start_of_year_in_days_cache: typing.Final[list[int]] = []
        start_of_year = self._days_at_start_of_year_1 - self._get_days_in_year(0)
        for year in range(0, self._max_year + 2):
            self.__start_of_year_in_days_cache.append(start_of_year)
            start_of_year += self._get_days_in_year(year)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return self.__total_days_by_month[month]

    def _get_start_of_year_in_days(self, year: int) -> int:
        # TODO: _Preconditions._debug_check_argument()
        return self.__start_of_year_in_days_cache[year]

    def _calculate_start_of_year_days(self, year: int) -> int:
        # This would only be called from GetStartOfYearInDays, which is overridden.
        raise NotImplementedError

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        day_of_year_zero_based = day_of_year - 1
        month: int
        day: int
        if day_of_year == self.__DAYS_PER_LEAP_YEAR:
            # Last day of a leap year.
            month = 12
            day = 30
        elif day_of_year_zero_based < 6 * 31:
            # In the first 6 months, all of which are 31 days long.
            month = _towards_zero_division(day_of_year_zero_based, 31) + 1
            day = _csharp_modulo(day_of_year_zero_based, 31) + 1
        else:
            # Last 6 months (other than last day of leap year).
            # Work out where we are within that 6 month block, then use simple arithmetic.
            day_of_second_half = day_of_year_zero_based - 6 * 31
            month = _towards_zero_division(day_of_second_half, 30) + 7
            day = _csharp_modulo(day_of_second_half, 30) + 1
        from .._year_month_day import _YearMonthDay

        return _YearMonthDay._ctor(year=year, month=month, day=day)

    def _get_days_in_month(self, year: int, month: int) -> int:
        return 31 if month < 7 else 30 if (month < 12 or self._is_leap_year(year)) else 29

    def _get_days_in_year(self, year: int) -> int:
        return self.__DAYS_PER_LEAP_YEAR if self._is_leap_year(year) else self.__DAYS_PER_NON_LEAP_YEAR

    # Pyoda time implementation note:
    # These methods exist to maintain a similar internal API to Noda Time,
    # where the concrete persian calendars are nested inside the abstract base class.
    @staticmethod
    def Simple() -> _PersianSimpleYearMonthDayCalculator:
        return _PersianSimpleYearMonthDayCalculator()

    @staticmethod
    def Arithmetic() -> _PersianArithmeticYearMonthDayCalculator:
        return _PersianArithmeticYearMonthDayCalculator()

    @staticmethod
    def Astronomical() -> _PersianAstronomicalYearMonthDayCalculator:
        return _PersianAstronomicalYearMonthDayCalculator()


class _PersianSimpleYearMonthDayCalculator(_PersianYearMonthDayCalculator):
    """Persian calendar using the simple 33-year cycle of 1, 5, 9, 13, 17, 22, 26, or 30.

    This corresponds to System.Globalization.PersianCalendar before .NET 4.6.
    """

    __LEAP_YEAR_PATTERN_BITS: typing.Final[int] = (
        (1 << 1) | (1 << 5) | (1 << 9) | (1 << 13) | (1 << 17) | (1 << 22) | (1 << 26) | (1 << 30)
    )
    __LEAP_YEAR_CYCLE_LENGTH: typing.Final[int] = 33

    # The ticks for the epoch of March 21st 622CE.
    __DAYS_AT_START_OF_YEAR_1_CONSTANT: typing.Final[int] = -492268

    def __init__(self) -> None:
        super().__init__(self.__DAYS_AT_START_OF_YEAR_1_CONSTANT)

    def _is_leap_year(self, year: int) -> bool:
        # Handle negative years in order to make calculations near the start of the calendar work cleanly.
        year_of_cycle = (
            _csharp_modulo(year, self.__LEAP_YEAR_CYCLE_LENGTH)
            if year >= 0
            else _csharp_modulo(year, self.__LEAP_YEAR_CYCLE_LENGTH) + self.__LEAP_YEAR_CYCLE_LENGTH
        )
        # Note the shift of 1L rather than 1, to avoid issues where shifting by 32
        # would get us back to 1.
        key = 1 << year_of_cycle
        return (self.__LEAP_YEAR_PATTERN_BITS & key) > 0


class _PersianArithmeticYearMonthDayCalculator(_PersianYearMonthDayCalculator):
    """Persian calendar based on Birashk's subcycle/cycle/grand cycle scheme."""

    def __init__(self) -> None:
        super().__init__(-492267)

    def _is_leap_year(self, year: int) -> bool:
        # Offset the cycles for easier arithmetic.
        offset_year = year - 474 if year > 0 else year - 473
        cycle_year = _csharp_modulo(offset_year, 2820) + 474
        return ((cycle_year + 38) * 31) % 128 < 31


class _PersianAstronomicalYearMonthDayCalculator(_PersianYearMonthDayCalculator):
    """Persian calendar based on stored BCL 4.6 information (avoids complex arithmetic for midday in Tehran)."""

    # Ugly, but the simplest way of embedding a big chunk of binary data...
    __astronomical_leap_year_bits: bytes = base64.b64decode(
        "ICIiIkJERESEiIiICBEREREiIiJCREREhIiIiAgRERERIiIiIkRERISIiIiIEBERESEiIiJEREREiIiI"
        + "iBAREREhIiIiQkRERISIiIgIERERESIiIkJERESEiIiICBEREREiIiIiRERERIiIiIgQERERISIiIkJE"
        + "RESEiIiICBEREREiIiIiREREhIiIiAgRERERISIiIkRERESIiIiIEBERESEiIiJCREREhIiIiAgRERER"
        + "IiIiIkRERISIiIgIERERESEiIiJEREREiIiIiBAREREhIiIiQkRERISIiIgIERERESIiIiJEREREiIiI"
        + "iBAREREhIiIiQkRERIiIiIgQERERISIiIiJERESEiIiICBEREREiIiIiRERERIiIiIgQERERISIiIkJE"
        + "RESEiIiICBEREREiIiIiRERERIiIiAgRERERIiIiIkJERESEiIiIEBERESEiIiJCRERERIiIiAgRERER"
        + "IiIiIkRERESIiIiIEBERESEiIiJCREREhIiIiAgREREhIiIiIkRERESIiIiIEBERESIiIiJEREREiIiI"
        + "iBAREREhIiIiQkRERISIiIgIERERESIiIiJEREREiIiIiBAREREiIiIiRERERIiIiIgQERERISIiIkJE"
        + "RESEiIiICBERESEiIiJCREREhIiIiAgRERERIiIiIkRERESIiIiIEBERESIiIiJEREREiIiIiBAREREh"
        + "IiIiQkRERISIiIgIERERISIiIkJERESEiIiICBEREREiIiIiRERERIiIiAgRERERIiIiIkRERESIiIgI"
        + "ERERESIiIiJEREREiIiIiBAREREhIiIiQkRERIiIiIgQERERISIiIkJERESIiIiIEBERESEiIiJCRERE"
        + "iIiIiBAREREhIiIiQkRERIiIiIgQERERISIiIkRERESIiIiIEBERESIiIiJEREREiIiIiBAREREiIiIi"
        + "RERERIiIiAgRERERIiIiIkRERISIiIgIERERESIiIkJERESEiIiIEBERESEiIiJEREREiIiIiBAREREi"
        + "IiIiRERERIiIiAgRERERIiIiIkRERISIiIgQERERISIiIkJERESIiIiIEBERESEiIiJERESEiIiICBER"
        + "ESEiIiJCREREhIiIiBAREREhIiIiREREhIiIiAgRERERIiIiQkRERIiIiIgQERERIiIiIkRERISIiIgQ"
        + "ERERISIiIkRERESIiIgIERERISIiIkJERESIiIiIEBERESIiIkJERESIiIiIEBERESIiIiJERESEiIiI"
        + "EBERESEiIiJERESEiIiICBERESEiIiJEREREiIiICBERESEiIiJERESEiIiICBERESEiIiJEREREiIiI"
        + "CBERESEiIiJERESEiIiICBERESEiIiJERESEiIiICBERESEiIiJERESEiIiIEBERESIiIiJERESEiIiI"
        + "EBERESIiIkJERESIiIgIERERISIiIkRERESIiIgIERERISIiIkRERISIiIgQERERIiIiQkRERIiIiAgR"
        + "EREhIiIiREREhIiIiBAREREiIiJCREREiIiICBERESEC"
    )

    def __init__(self) -> None:
        super().__init__(-492267)

    def _is_leap_year(self, year: int) -> bool:
        return (self.__astronomical_leap_year_bits[year >> 3] & (1 << (year & 7))) != 0
