# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import final

from ..utility._preconditions import _Preconditions
from ._era import Era
from ._era_calculator import _EraCalculator
from ._year_month_day_calculator import _YearMonthDayCalculator


@final
class _GJEraCalculator(_EraCalculator):
    """Era calculator for Gregorian and Julian calendar systems, which use BC and AD."""

    def __init__(self, ymd_calculator: _YearMonthDayCalculator):
        super().__init__(Era.before_common, Era.common)
        self.__max_year_of_bc = 1 - ymd_calculator._min_year
        self.__max_year_of_ad = ymd_calculator._max_year

    def __validate_era(self, era: Era) -> None:
        if era not in (Era.common, Era.before_common):
            _Preconditions._check_not_null(era, "era")
            _Preconditions._check_argument(
                False, "era", "Era {} is not supported by this calendar; only BC and AD are supported", era.name
            )

    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        self.__validate_era(era)
        if era == Era.common:
            _Preconditions._check_argument_range("year_of_era", year_of_era, 1, self.__max_year_of_ad)
            return year_of_era
        _Preconditions._check_argument_range("year_of_era", year_of_era, 1, self.__max_year_of_bc)
        return 1 - year_of_era

    def _get_year_of_era(self, absolute_year: int) -> int:
        return absolute_year if absolute_year > 0 else 1 - absolute_year

    def _get_era(self, absolute_year: int) -> Era:
        return Era.common if absolute_year > 0 else Era.before_common

    def _get_min_year_of_era(self, era: Era) -> int:
        self.__validate_era(era)
        return 1

    def _get_max_year_of_era(self, era: Era) -> int:
        self.__validate_era(era)
        return self.__max_year_of_ad if era == Era.common else self.__max_year_of_bc
