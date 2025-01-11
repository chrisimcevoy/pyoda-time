# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, final

from ..utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from ._islamic_epoch import IslamicEpoch
from ._islamic_leap_year_pattern import IslamicLeapYearPattern
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator

if TYPE_CHECKING:
    from collections.abc import Generator

    from .._year_month_day import _YearMonthDay


@_sealed
@final
class _IslamicYearMonthDayCalculator(_RegularYearMonthDayCalculator):
    # Days in a pair of months, in days.
    __MONTH_PAIR_LENGTH: Final[int] = 59

    # The length of a long month, in days.
    __LONG_MONTH_LENGTH: Final[int] = 30

    # The length of a short month, in days.
    __SHORT_MONTH_LENGTH: Final[int] = 29

    # The typical number of days in 10 years.
    __AVERAGE_DAYS_PER_10_YEARS: Final[int] = 3544  # Ideally 354.36667 per year

    # The number of days in a non-leap year.
    __DAYS_PER_NON_LEAP_YEAR: Final[int] = 354

    # The number of days in a leap year.
    __DAYS_PER_LEAP_YEAR: Final[int] = 355

    # The days for the civil (Friday) epoch of July 16th 622CE.
    __DAYS_AT_CIVIL_EPOCH: Final[int] = -492148

    # The days for the civil (Thursday) epoch of July 15th 622CE.
    __DAYS_AT_ASTRONOMICAL_EPOCH: Final[int] = __DAYS_AT_CIVIL_EPOCH - 1

    # The length of the cycle of two leap years.
    __LEAP_YEAR_CYCLE_LENGTH: Final[int] = 30

    # The number of days in a leap cycle.
    __DAYS_PER_LEAP_CYCLE = 19 * __DAYS_PER_NON_LEAP_YEAR + 11 * __DAYS_PER_LEAP_YEAR

    @staticmethod
    def __generate_total_days_by_month(long_month_length: int, short_month_length: int) -> Generator[int, Any, None]:
        days = 0
        for i in range(1, 13):
            yield days
            days_in_month = long_month_length if (i & 1) == 1 else short_month_length
            days += days_in_month

    # The number of days preceding the 1-indexed month - so [0, 0, 30, 59, ...]
    __TOTAL_DAYS_BY_MONTH: Final[list[int]] = [
        # Here, the month number is 1-based, so odd months are long.
        # This doesn't take account of leap years, but that doesn't matter - because
        # it's not used on the last iteration, and leap years only affect the final month
        # in the Islamic calendar.
        0,
        *__generate_total_days_by_month(__LONG_MONTH_LENGTH, __SHORT_MONTH_LENGTH),
    ]

    def __init__(self, leap_year_pattern: IslamicLeapYearPattern, epoch: IslamicEpoch) -> None:
        super().__init__(1, 9665, 12, self.__AVERAGE_DAYS_PER_10_YEARS, self.__get_year_10_days(epoch))

        # The pattern of leap years within a cycle, one bit per year, for this calendar.
        self.__leap_year_pattern_bits: Final[int] = self.__get_leap_year_pattern_bits(leap_year_pattern)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        # The number of days at the *start* of a month isn't affected by
        # the year as the only month length which varies by year is the last one.
        return self.__TOTAL_DAYS_BY_MONTH[month]

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        month: int
        day: int
        # Special case the last day in a leap year
        if day_of_year == self.__DAYS_PER_LEAP_YEAR:
            month = 12
            day = 30
        else:
            day_of_year_zero_based = day_of_year - 1
            month = _towards_zero_division((day_of_year_zero_based * 2), self.__MONTH_PAIR_LENGTH) + 1
            day = ((day_of_year_zero_based % self.__MONTH_PAIR_LENGTH) % self.__LONG_MONTH_LENGTH) + 1
        return _YearMonthDay._ctor(year=year, month=month, day=day)

    def _is_leap_year(self, year: int) -> bool:
        # Handle negative years in order to make calculations near the start of the calendar work cleanly.
        year_of_cycle = (
            _csharp_modulo(year, self.__LEAP_YEAR_CYCLE_LENGTH)
            if year >= 0
            else _csharp_modulo(year, self.__LEAP_YEAR_CYCLE_LENGTH) + self.__LEAP_YEAR_CYCLE_LENGTH
        )
        key: int = 1 << year_of_cycle
        return (self.__leap_year_pattern_bits & key) > 0

    def _get_days_in_year(self, year: int) -> int:
        return self.__DAYS_PER_LEAP_YEAR if self._is_leap_year(year) else self.__DAYS_PER_NON_LEAP_YEAR

    def _get_days_in_month(self, year: int, month: int) -> int:
        if month == 12 and self._is_leap_year(year):
            return self.__LONG_MONTH_LENGTH
        # Note: month is 1-based here, so even months are the short ones
        return self.__SHORT_MONTH_LENGTH if (month & 1) == 0 else self.__LONG_MONTH_LENGTH

    def _calculate_start_of_year_days(self, year: int) -> int:
        # The first cycle starts in year 1, not year 0.
        # We try to cope with years outside the normal range, in order to allow arithmetic at the boundaries.
        cycle: int = (
            _towards_zero_division(year - 1, self.__LEAP_YEAR_CYCLE_LENGTH)
            if year > 0
            else _towards_zero_division(year - self.__LEAP_YEAR_CYCLE_LENGTH, self.__LEAP_YEAR_CYCLE_LENGTH)
        )
        year_at_start_of_cycle = (cycle * self.__LEAP_YEAR_CYCLE_LENGTH) + 1
        days = self._days_at_start_of_year_1 + cycle * self.__DAYS_PER_LEAP_CYCLE

        # We've got the days at the start of the cycle (e.g. at the start of year 1, 31, 61 etc).
        # Now go from that year to (but not including) the year we're looking for, adding the right
        # number of days in each year. So if we're trying to find the start of year 34, we would
        # find the days at the start of year 31, then add the days *in* year 31, the days in year 32,
        # and the days in year 33.
        # If this ever proves to be a bottleneck, we could create an array for each IslamicLeapYearPattern
        # with "the number of days for the first n years in a cycle".
        for i in range(year_at_start_of_cycle, year):
            days += self._get_days_in_year(i)
        return days

    @staticmethod
    def __get_leap_year_pattern_bits(leap_year_pattern: IslamicLeapYearPattern) -> int:
        """Returns the pattern of leap years within a cycle, one bit per year, for the specified pattern.

        Note that although cycle years are usually numbered 1-30, the bit pattern is for 0-29; cycle year 30 is
        represented by bit 0.
        """
        # When reading bit patterns, don't forget to read right to left...
        match leap_year_pattern:
            case IslamicLeapYearPattern.BASE15:
                return 623158436  # 0b100101001001001010010010100100
            case IslamicLeapYearPattern.BASE16:
                return 623191204  # 0b100101001001010010010010100100
            case IslamicLeapYearPattern.INDIAN:
                return 690562340  # 0b101001001010010010010100100100
            case IslamicLeapYearPattern.HABASH_AL_HASIB:
                return 153692453  # 0b001001001010010010100100100101
            case _:
                # TODO: ArgumentOutOfRangeException? leap_year_pattern.name?
                raise ValueError(f"Leap year pattern {leap_year_pattern} not recognised")

    @classmethod
    def __get_year_10_days(cls, epoch: IslamicEpoch) -> int:
        match epoch:
            case IslamicEpoch.ASTRONOMICAL:
                return cls.__DAYS_AT_ASTRONOMICAL_EPOCH
            case IslamicEpoch.CIVIL:
                return cls.__DAYS_AT_CIVIL_EPOCH
            case _:
                # TODO: ArgumentOutOfRangeException?
                raise ValueError(f"Epoch {getattr(epoch, 'name', epoch)} not recognised")
