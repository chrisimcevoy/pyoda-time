# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, ClassVar, Final

from ..utility._preconditions import _Preconditions
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator

if TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay


class _UmAlQuraYearMonthDayCalculator(_RegularYearMonthDayCalculator):
    """Implementation of the Um Al Qura calendar, using the tabular data in the BCL.

    This is fetched on construction and cached - we just need to know the length of each month of each year, which is
    cheap as the current implementation only covers 183 years.
    """

    __AVERAGE_DAYS_PER_10_YEARS: Final[int] = 3544

    # These four members are generated by UmAlQuraYearMonthDayCalculatorTest.GenerateData.
    __COMPUTED_MIN_YEAR: Final[int] = 1318
    __COMPUTED_MAX_YEAR: Final[int] = 1500
    __COMPUTED_DAYS_AT_START_OF_MIN_YEAR: Final[int] = -25448
    __GENERATED_DATA: Final[str] = (
        "AAAF1A3SHaQdSBqUFSwKbBVqG1QXSBaSFSYKVhSuCWwVagtUGqoaVBSsCVwSugXYDaoNVAqqCVYStgV0"
        + "CuoXZA7IDpIMqgVWCrYVtA2oHZIbJBpKFJoFWgraFtQWpBVKFJYJLhJuBWwK6hrUGqQVLBJaBLoJuhW0"
        + "C6gbUhqkFVQJrBNsBugO0g6kDUoKlhVWCrQVqhukG0gakhUqCloUugq0FaoNVA0qClYUrglcEuwK2Baq"
        + "FVQUqglaEroFtAuyG2QXSBaUFKoFagrqFtQXpBeIFxIVKgpaC1oW1A2oG5IbJBVMEqwFXAraBtQWqhVU"
        + "EpoJOhK6BXQLagtUGqoVNBJcBNwKuhW0DagNSgqWFS4KnBVcC1gXUhskFkoMlhlWCrQWqg2kHUoclBUq"
        + "CloVWgbYDrINpA0qCloUtgl0E3QHaBbSFqQVTAlsEtoF2A2yHWQaqBpUFKwJXBLaGtQWqBZSFSYKVhSu"
        + "CmwVag1UHSYAAA=="
    )

    __COMPUTED_DAYS_AT_START_OF_YEAR_1: Final[int] = __COMPUTED_DAYS_AT_START_OF_MIN_YEAR + (
        int(((1 - __COMPUTED_MIN_YEAR) / 10.0) * __AVERAGE_DAYS_PER_10_YEARS)
    )

    __MONTH_LENGTHS: ClassVar[dict[int, int]] = {}
    __YEAR_LENGTHS: ClassVar[dict[int, int]] = {}
    __YEAR_START_DAYS: ClassVar[dict[int, int]] = {}

    @staticmethod
    def _ctor(
        generated_data: str,
        month_lengths: dict[int, int],
        year_lengths: dict[int, int],
        year_start_days: dict[int, int],
        computed_days_at_start_of_min_year: int,
    ) -> None:
        """Simulates the static constructor on the equivalent noda time class."""
        data = base64.b64decode(generated_data)
        for i in range(int(len(data) / 2)):
            month_lengths[i] = (data[i * 2] << 8) | (data[i * 2 + 1])

        # Populate arrays from index 1
        total_days = 0
        for year in range(1, len(month_lengths)):
            year_start_days[year] = computed_days_at_start_of_min_year + total_days
            month_bits = month_lengths[year]
            year_length = 29 * 12
            for month in range(1, 13):
                year_length += (month_bits >> month) & 1
            year_lengths[year] = year_length
            total_days += year_length

        # Fill in the cache with dummy data for before/after the min/max year, pretending
        # that both of the "extra" years were 354 days long.
        year_start_days[0] = computed_days_at_start_of_min_year - 354
        year_start_days[len(year_start_days) - 1] = computed_days_at_start_of_min_year + total_days
        year_lengths[0] = 354
        year_lengths[len(year_start_days) - 1] = 354

    _ctor(
        generated_data=__GENERATED_DATA,
        month_lengths=__MONTH_LENGTHS,
        year_lengths=__YEAR_LENGTHS,
        year_start_days=__YEAR_START_DAYS,
        computed_days_at_start_of_min_year=__COMPUTED_DAYS_AT_START_OF_MIN_YEAR,
    )

    del _ctor

    def __init__(self) -> None:
        super().__init__(
            self.__COMPUTED_MIN_YEAR,
            self.__COMPUTED_MAX_YEAR,
            12,
            self.__AVERAGE_DAYS_PER_10_YEARS,
            self.__COMPUTED_DAYS_AT_START_OF_YEAR_1,
        )

    def _get_start_of_year_in_days(self, year: int) -> int:
        # No need to use the YearMonthDayCalculator cache, given that we've got the value in array already.
        return self.__YEAR_START_DAYS[year - self.__COMPUTED_MIN_YEAR + 1]

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Only called from the base GetStartOfYearInDays implementation.
        raise NotImplementedError

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        # While we could do something clever to find the Hamming distance on the masked value here,
        # it's considerably simpler just to iterate...
        month_bits = self.__MONTH_LENGTHS[year - self.__COMPUTED_MIN_YEAR + 1]
        extra_days = 0
        for i in range(1, month):
            extra_days += (month_bits >> i) & 1
        return (month - 1) * 29 + extra_days

    def _get_days_in_month(self, year: int, month: int) -> int:
        month_bits = self.__MONTH_LENGTHS[year - self.__COMPUTED_MIN_YEAR + 1]
        return 29 + ((month_bits >> month) & 1)

    def _get_days_in_year(self, year: int) -> int:
        # Fine for one year either side of min/max.
        return self.__YEAR_LENGTHS[year - self.__COMPUTED_MIN_YEAR + 1]

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from .._year_month_day import _YearMonthDay

        days_left = day_of_year
        month_bits = self.__MONTH_LENGTHS[year - self.__COMPUTED_MIN_YEAR + 1]
        for month in range(1, 13):
            month_length = 29 + ((month_bits >> month) & 1)
            if days_left <= month_length:
                return _YearMonthDay._ctor(year=year, month=month, day=days_left)
            days_left -= month_length
        # This should throw...
        _Preconditions._check_argument_range("day_of_year", day_of_year, 1, self._get_days_in_year(year))
        raise RuntimeError(
            f"Bug in Pyoda Time: year {year} has {self._get_days_in_year(year)} days but {day_of_year} isn't valid"
        )

    def _is_leap_year(self, year: int) -> bool:
        return self.__YEAR_LENGTHS[year - self.__COMPUTED_MIN_YEAR + 1] == 355
