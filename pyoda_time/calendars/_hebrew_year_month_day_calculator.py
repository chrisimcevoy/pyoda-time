# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ..utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from ._hebrew_month_converter import _HebrewMonthConverter
from ._hebrew_month_numbering import HebrewMonthNumbering
from ._hebrew_scriptural_calculator import _HebrewScripturalCalculator
from ._year_month_day_calculator import _YearMonthDayCalculator

if typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay


@_sealed
class _HebrewYearMonthDayCalculator(_YearMonthDayCalculator):
    __UNIX_EPOCH_DAY_AT_START_OF_YEAR_1: typing.Final[int] = -2092590
    __MONTHS_PER_LEAP_CYCLE: typing.Final[int] = 235
    __YEARS_PER_LEAP_CYCLE: typing.Final[int] = 19

    def __init__(self, month_numbering: HebrewMonthNumbering) -> None:
        super().__init__(
            _HebrewScripturalCalculator._MIN_YEAR,
            _HebrewScripturalCalculator._MAX_YEAR,
            3654,  # Average length of 10 years
            self.__UNIX_EPOCH_DAY_AT_START_OF_YEAR_1,
        )
        self.__month_numbering: typing.Final[HebrewMonthNumbering] = month_numbering

    def __calendar_to_civil_month(self, year: int, month: int) -> int:
        return (
            month
            if self.__month_numbering == HebrewMonthNumbering.CIVIL
            else _HebrewMonthConverter._scriptural_to_civil(year, month)
        )

    def __calendar_to_scriptural_month(self, year: int, month: int) -> int:
        return (
            month
            if self.__month_numbering == HebrewMonthNumbering.SCRIPTURAL
            else _HebrewMonthConverter._civil_to_scriptural(year, month)
        )

    def __civil_to_calendar_month(self, year: int, month: int) -> int:
        return (
            month
            if self.__month_numbering is HebrewMonthNumbering.CIVIL
            else _HebrewMonthConverter._civil_to_scriptural(year, month)
        )

    def __scriptural_to_calendar_month(self, year: int, month: int) -> int:
        return (
            month
            if self.__month_numbering is HebrewMonthNumbering.SCRIPTURAL
            else _HebrewMonthConverter._scriptural_to_civil(year, month)
        )

    def _is_leap_year(self, year: int) -> bool:
        """Returns whether or not the given year is a leap year - that is, one with 13 months. This is
        not quite the same as a leap year in (say) the Gregorian calendar system..."""
        return _HebrewScripturalCalculator._is_leap_year(year)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        scriptural_month: int = self.__calendar_to_scriptural_month(year, month)
        return _HebrewScripturalCalculator._get_days_from_start_of_year_to_start_of_month(year, scriptural_month)

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Note that we might get called with a year of 0 here.
        # I think that will still be okay, given how HebrewScripturalCalculator works.
        days_since_hebrew_epoch = (
            _HebrewScripturalCalculator._elapsed_days(year) - 1
        )  # ElapsedDays returns 1 for year 1.
        return days_since_hebrew_epoch + self.__UNIX_EPOCH_DAY_AT_START_OF_YEAR_1

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        scriptural: _YearMonthDay = _HebrewScripturalCalculator._get_year_month_day(year, day_of_year)
        return (
            scriptural
            if self.__month_numbering == HebrewMonthNumbering.SCRIPTURAL
            else _YearMonthDay._ctor(
                year=year,
                month=_HebrewMonthConverter._scriptural_to_civil(year, scriptural._month),
                day=scriptural._day,
            )
        )

    def _get_days_in_year(self, year: int) -> int:
        return _HebrewScripturalCalculator._days_in_year(year)

    def _get_months_in_year(self, year: int) -> int:
        return 13 if _HebrewScripturalCalculator._is_leap_year(year) else 12

    def _set_year(self, year_month_day: _YearMonthDay, year: int) -> _YearMonthDay:
        """Change the year, maintaining month and day as well as possible.

        This doesn't work in the same way as other calendars; see
        https://judaism.stackexchange.com/questions/39053
        for the reasoning behind the rules.
        """

        current_year = year_month_day._year
        current_month = year_month_day._month
        target_day = year_month_day._day
        target_scriptural_month = self.__calendar_to_scriptural_month(current_month, current_month)
        if target_scriptural_month == 13 and not self._is_leap_year(year):
            # If we were in Adar II and the target year is not a leap year, map to Adar.
            target_scriptural_month = 12
        elif target_scriptural_month == 12 and self._is_leap_year(year) and not self._is_leap_year(current_year):
            # If we were in Adar (non-leap year), go to Adar II rather than Adar I in a leap year.
            target_scriptural_month = 13
        # If we're aiming for the 30th day of Heshvan, Kislev or an Adar, it's possible that the change in year
        # has meant the day becomes invalid. In that case, roll over to the 1st of the subsequent month.
        if target_day == 30 and target_scriptural_month in (8, 9, 12):
            if _HebrewScripturalCalculator._days_in_month(year, target_scriptural_month) != 30:
                target_day = 1
                target_scriptural_month += 1
                # From Adar, roll to Nisan
                if target_scriptural_month == 13:
                    target_scriptural_month = 1
        target_calendar_month = self.__scriptural_to_calendar_month(year, target_scriptural_month)
        return _YearMonthDay._ctor(year=year, month=target_calendar_month, day=target_day)

    def _get_days_in_month(self, year: int, month: int) -> int:
        return _HebrewScripturalCalculator._days_in_month(year, self.__calendar_to_scriptural_month(year, month))

    def _add_months(self, year_month_day: _YearMonthDay, months: int) -> _YearMonthDay:
        # Note: this method gives the same result regardless of the month numbering used
        # by the instance. The method works in terms of civil month numbers for most of
        # the time in order to simplify the logic.
        if months == 0:
            return year_month_day
        year = year_month_day._year
        month = self.__calendar_to_civil_month(year, year_month_day._month)
        # This arithmetic works the same both backwards and forwards
        year += _towards_zero_division(months, self.__MONTHS_PER_LEAP_CYCLE) * self.__YEARS_PER_LEAP_CYCLE
        months = _csharp_modulo(months, self.__MONTHS_PER_LEAP_CYCLE)
        if months > 0:
            # Add as many months as we need to in order to act as if we'd begun at the start
            # of the year, for simplicity.
            months += month - 1
            # Add a year at a time
            while months >= self._get_months_in_year(year):
                months -= self._get_months_in_year(year)
                year += 1
            # However many months we've got left to add tells us the final month.
            month = months + 1
        else:
            # Pretend we were given the month at the end of the years.
            months -= self._get_months_in_year(year) - month
            # Subtract a year at a time
            while months + self._get_months_in_year(year) <= 0:
                months += self._get_months_in_year(year)
                year -= 1
            # However many months we've got left to add (which will still be negative...)
            # tells us the final month.
            month = self._get_months_in_year(year) + months

        # Convert back to calendar month
        month = self.__civil_to_calendar_month(year, month)
        day = min(self._get_days_in_month(year, month), year_month_day._day)
        if (year < self._min_year) or (year > self._max_year):
            raise OverflowError("Date computation would overflow calendar bounds.")
        return _YearMonthDay._ctor(year=year, month=month, day=day)

    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        start_civil_month: int = self.__calendar_to_civil_month(start._year, start._month)
        start_total_months: float = start_civil_month + (start._year * self.__MONTHS_PER_LEAP_CYCLE) / float(
            self.__YEARS_PER_LEAP_CYCLE
        )
        end_civil_month: int = self.__calendar_to_civil_month(end._year, end._month)
        end_total_months: float = end_civil_month + (end._year * self.__MONTHS_PER_LEAP_CYCLE) / float(
            self.__YEARS_PER_LEAP_CYCLE
        )
        diff: int = int(end_total_months - start_total_months)

        if (self.compare(start, end)) <= 0:
            # Go backwards untill we've got a tight upper bound...
            while self.compare(self._add_months(start, diff), end) > 0:
                diff -= 1
            # Go forwards until we've overshot
            while self.compare(self._add_months(start, diff), end) <= 0:
                diff += 1
            # Take account of the overshoot
            return diff - 1
        else:
            # Moving backwards, so we need to end up with a result greater than or equal to end...
            # Go forwards until we've got a tight upper bound...
            while self.compare(self._add_months(start, diff), end) < 0:
                diff += 1
            # Go backwards until we've overshot
            while self.compare(self._add_months(start, diff), end) >= 0:
                diff += 1
            # Take account of the overshoot
            return diff + 1

    def compare(self, lhs: _YearMonthDay, rhs: _YearMonthDay) -> int:
        # The civil month numbering system allows a naive comparison.
        if self.__month_numbering == HebrewMonthNumbering.CIVIL:
            return lhs.compare_to(rhs)
        # Otherwise, try one component at a time. (We could benchmark this
        # against creating a new pair of YearMonthDay values in the civil month numbering,
        # and comparing them...)
        year_comparison = lhs._year - rhs._year
        if year_comparison != 0:
            return year_comparison
        lhs_civil_month: int = self.__calendar_to_civil_month(lhs._year, lhs._month)
        rhs_civil_month: int = self.__calendar_to_civil_month(rhs._year, rhs._month)
        month_comparison: int = lhs_civil_month - rhs_civil_month
        if month_comparison != 0:
            return month_comparison
        return lhs._day - rhs._day
