# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from ._hebrew_scriptural_calculator import _HebrewScripturalCalculator


class _HebrewMonthConverter:
    """Conversions between civil and scriptural month numbers in the Hebrew calendar system."""

    @staticmethod
    def _civil_to_scriptural(year: int, month: int) -> int:
        """Given a civil month number and a year in which it occurs, this method returns the equivalent scriptural month
        number.

         No validation is performed in this method:
         an input month number of 13 in a non-leap-year will return a result of 7.

        :param year: Year during which the month occurs.
        :param month: Civil month number.
        :return: The scriptural month number.
        """
        if month < 7:
            return month + 6
        leap_year = _HebrewScripturalCalculator._is_leap_year(year)
        if month == 7:
            return 13 if leap_year else 1
        return month - 7 if leap_year else month - 6

    @staticmethod
    def _scriptural_to_civil(year: int, month: int) -> int:
        """Given a scriptural month number and a year in which it occurs, this method returns the equivalent scriptural
        month number.

        No validation is performed in this method: an input month number of 13 in a non-leap-year will return 7.

        :param year: Year during which the month occurs.
        :param month: Civil month number.
        :return: The scriptural month number.
        """
        if month >= 7:
            return month - 6
        return month + 7 if _HebrewScripturalCalculator._is_leap_year(year) else month + 6
