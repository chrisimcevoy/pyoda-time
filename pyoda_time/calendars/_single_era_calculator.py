# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ..utility import _Preconditions, _private, _sealed
from ._era import Era
from ._era_calculator import _EraCalculator
from ._year_month_day_calculator import _YearMonthDayCalculator


@typing.final
@_sealed
@_private
class _SingleEraCalculator(_EraCalculator):
    """Implementation of EraCalculator for calendars which only have a single era."""

    __min_year: typing.Annotated[int, "Set by internal constructor"]
    __max_year: typing.Annotated[int, "Set by internal constructor"]
    __era: typing.Annotated[Era, "Set by internal constructor"]

    @classmethod
    def _ctor(cls, *, era: Era, ymd_calculator: _YearMonthDayCalculator) -> _SingleEraCalculator:
        self = super().__new__(cls)
        self.__min_year = ymd_calculator._min_year
        self.__max_year = ymd_calculator._max_year
        self.__era = era
        return self

    def __validate_era(self, era: Era) -> None:
        if era != self.__era:
            _Preconditions._check_not_null(era, "era")
            _Preconditions._check_argument(
                era == self.__era, "era", "Only supported era is {}; requested era was {}", self.__era.name, era.name
            )

    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        self.__validate_era(era)
        _Preconditions._check_argument_range("year_of_era", year_of_era, self.__min_year, self.__max_year)
        return year_of_era

    def _get_year_of_era(self, absolute_year: int) -> int:
        return absolute_year

    def _get_min_year_of_era(self, era: Era) -> int:
        self.__validate_era(era)
        return self.__min_year

    def _get_max_year_of_era(self, era: Era) -> int:
        self.__validate_era(era)
        return self.__max_year

    def _get_era(self, absolute_year: int) -> Era:
        return self.__era
