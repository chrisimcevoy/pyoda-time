from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_DOWN
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import YearMonthDay


class YearMonthDayCalculator(ABC):
    _DAY_BITS = 6

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        # TODO Preconditions.CheckArgument(...)
        self.min_year = min_year
        self.max_year = max_year
        # We add an extra day to make sure that
        # approximations using days-since-epoch are conservative, to avoid going out of bounds.
        self.average_days_per_10_years = average_days_per_10_years + 1
        self.days_at_start_of_year_1 = days_at_start_of_year_1
        self.__year_cache = YearStartCacheEntry.create_cache()

    def get_start_of_year_in_days(self, year: int):
        # TODO Preconditions.DebugCheckArgumentRange(...)
        cache_index = YearStartCacheEntry.get_cache_index(year)
        cache_entry = self.__year_cache[cache_index]
        if not cache_entry.is_valid_for_year(year):
            days = self._calculate_start_of_year_days(year)
            cache_entry = YearStartCacheEntry(year, days)
            self.__year_cache[cache_index] = cache_entry
        return cache_entry.start_of_year_days

    @abstractmethod
    def _calculate_start_of_year_days(self, year: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def _get_days_in_month(self, year: int, month: int):
        raise NotImplementedError

    @abstractmethod
    def _is_leap_year(self, year: int) -> bool:
        raise NotImplementedError

    def get_days_since_epoch(self, year_month_day: YearMonthDay) -> int:
        year = year_month_day.year
        start_of_year = self.get_start_of_year_in_days(year)
        start_of_month = (
            start_of_year
            + self._get_days_from_start_of_year_to_start_of_month(
                year, year_month_day.month
            )
        )
        return start_of_month + year_month_day.day - 1

    def _get_days_from_start_of_year_to_start_of_month(
        self, year: int, month: int
    ) -> int:
        raise NotImplementedError


class Era:
    def __init__(self, name: str, resource_identifier: str):
        self.name = property(lambda _: name)
        self._resource_identifier = property(lambda _: resource_identifier)

    def __str__(self):
        return self.name

    @classmethod
    def common(cls):
        return cls("CE", "Eras_Common")

    @classmethod
    def before_common(cls):
        return cls("BCE", "Eras_BeforeCommon")


class EraCalculator(ABC):
    def __init__(self, *eras: Era):
        self.eras = eras


class GJEraCalculator(EraCalculator):
    def __init__(self, ymd_calculator: YearMonthDayCalculator):
        super().__init__(Era.before_common(), Era.common())
        self.__max_year_of_bc = 1 - ymd_calculator.min_year
        self.__max_year_of_ad = ymd_calculator.max_year


class RegularYearMonthDayCalculator(YearMonthDayCalculator, ABC):
    """Subclass of YearMonthDayCalculator for calendars with the following attributes:
    - A fixed number of months
    - Occasional leap years which are always 1 day longer than non-leap years
    - The year starting with month 1, day 1 (i.e. naive YearMonthDay comparisons work)
    """

    def __init__(
        self,
        min_year: int,
        max_year: int,
        months_in_year: int,
        aveage_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(
            min_year, max_year, aveage_days_per_10_years, days_at_start_of_year_1
        )

        def months_in_year_fget(_):
            return months_in_year

        self.__months_in_year = property(months_in_year_fget)


class GJYearMonthDayCalculator(RegularYearMonthDayCalculator, ABC):
    _NON_LEAP_DAYS_PER_MONTH = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    _LEAP_DAYS_PER_MONTH = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    @staticmethod
    def __generate_total_days_by_month(*month_lengths: int):
        ret = [0]
        for i in range(len(month_lengths)):
            ret.append(ret[i] + month_lengths[i])
        return ret

    __NON_LEAP_TOTAL_DAYS_BY_MONTH = __generate_total_days_by_month(
        *_NON_LEAP_DAYS_PER_MONTH
    )
    __LEAP_TOTAL_DAYS_BY_MONTH = __generate_total_days_by_month(*_LEAP_DAYS_PER_MONTH)

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(
            min_year, max_year, 12, average_days_per_10_years, days_at_start_of_year_1
        )

    def _get_days_from_start_of_year_to_start_of_month(
        self, year: int, month: int
    ) -> int:
        return (
            self.__LEAP_TOTAL_DAYS_BY_MONTH[month]
            if self._is_leap_year(year)
            else self.__NON_LEAP_TOTAL_DAYS_BY_MONTH[month]
        )

    def _get_days_in_month(self, year: int, month: int):
        # February is awkward
        if month == 2:
            if self._is_leap_year(year):
                return 29
            return 28
        # The lengths of months alternate between 30 and 31, but skip a beat for August.
        # By dividing the month by 8, we effectively handle that skip.
        return 30 + ((month + (month >> 3)) & 1)


class GregorianYearMonthDayCalculator(GJYearMonthDayCalculator):
    __MIN_GREGORIAN_YEAR = -9998
    __MAX_GREGORIAN_YEAR = 9999

    __FIRST_OPTIMIZED_YEAR = 1900
    __LAST_OPTIMIZED_YEAR = 2100

    __MONTH_START_DAYS = list(
        range((__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR) * 12 + 1)
    )
    __YEAR_START_DAYS = list(range(__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR))

    __DAYS_FROM_0000_to_1970 = 719527
    __AVERAGE_DAYS_PER_10_YEARS = 3652

    def __init__(self):
        super().__init__(
            self.__MIN_GREGORIAN_YEAR,
            self.__MAX_GREGORIAN_YEAR,
            self.__AVERAGE_DAYS_PER_10_YEARS,
            -719162,
        )

        # TODO: In Noda Time this is inside a static ctor. Perf? Can we do it once?
        for year in range(self.__FIRST_OPTIMIZED_YEAR, self.__LAST_OPTIMIZED_YEAR + 1):
            year_start = self._calculate_start_of_year_days(year)
            self.__YEAR_START_DAYS[year - self.__FIRST_OPTIMIZED_YEAR] = year_start
            month_start_day = year_start - 1
            year_month_index = (year - self.__FIRST_OPTIMIZED_YEAR) * 12
            for month in range(1, 13):
                year_month_index += 1
                month_length = self._get_days_in_month(year, month)
                self.__MONTH_START_DAYS[year_month_index] = month_start_day
                month_start_day += month_length

    @staticmethod
    def __is_gregorian_leap_year(year: int) -> bool:
        return ((year & 3) == 0) and ((year % 100) != 0 or (year % 400) == 0)

    def _is_leap_year(self, year: int) -> bool:
        return self.__is_gregorian_leap_year(year)

    def _calculate_start_of_year_days(self, year: int) -> int:
        leap_years = int((year / Decimal(100)).quantize(0, ROUND_DOWN))
        if year < 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers. When the expression is written as
            # (year / 4) - (year / 100) + (year / 400),
            # it works for both positive and negative values, except this optimization
            # eliminates two divisions.
            leap_years = ((year + 3) >> 2) - leap_years + ((leap_years + 3) >> 2) - 1
        else:
            leap_years = (year >> 2) - leap_years + (leap_years >> 2)
            if self._is_leap_year(year):
                leap_years -= 1
        return year * 365 + (leap_years - self.__DAYS_FROM_0000_to_1970)

    def get_start_of_year_in_days(self, year: int):
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super().get_start_of_year_in_days(year)
        return self.__YEAR_START_DAYS[year - self.__FIRST_OPTIMIZED_YEAR]

    def get_days_since_epoch(self, year_month_day: YearMonthDay) -> int:
        year = year_month_day.year
        month_of_year = year_month_day.month
        day_of_month = year_month_day.day
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super().get_days_since_epoch(year_month_day)
        year_month_index = (year - self.__FIRST_OPTIMIZED_YEAR) * 12 + month_of_year
        return self.__MONTH_START_DAYS[year_month_index] + day_of_month


class YearStartCacheEntry:
    __CACHE_INDEX_BITS = 10
    __CACHE_SIZE = 1 << __CACHE_INDEX_BITS
    __CACHE_INDEX_MASK = __CACHE_SIZE - 1
    __ENTRY_VALIDATION_BITS = 7
    __ENTRY_VALIDATION_MASK = (1 << __ENTRY_VALIDATION_BITS) - 1
    __INVALID_ENTRY_YEAR = (__ENTRY_VALIDATION_MASK >> 1) << __CACHE_INDEX_BITS

    def __init__(self, year: int, days: int) -> None:
        self.__value = (days << self.__ENTRY_VALIDATION_BITS) | self.__get_validator(
            year
        )

    @classmethod
    def __get_validator(cls, year: int) -> int:
        """Returns the validator to use for a given year,
        a non-negative number containing at most __ENTRY_VALIDATION_BITS bits."""
        return (year >> cls.__CACHE_INDEX_BITS) & cls.__ENTRY_VALIDATION_MASK

    @classmethod
    def get_cache_index(cls, year: int) -> int:
        """Returns the cache index, in [0, CacheSize), that should be used to store the given year's cache entry."""
        return year & cls.__CACHE_INDEX_MASK

    @classmethod
    def create_cache(cls) -> dict[int, YearStartCacheEntry]:
        cache = {i: YearStartCacheEntry.invalid() for i in range(cls.__CACHE_SIZE)}
        return cache

    @classmethod
    def invalid(cls) -> YearStartCacheEntry:
        return YearStartCacheEntry(cls.__INVALID_ENTRY_YEAR, 0)

    def is_valid_for_year(self, year: int) -> bool:
        # Returns whether this cache entry is valid for the given year, and so is safe to use.  (We assume that we
        # have located this entry via the correct cache index.)
        return self.__get_validator(year) == (
            self.__value & self.__ENTRY_VALIDATION_MASK
        )

    @property
    def start_of_year_days(self) -> int:
        return self.__value >> self.__ENTRY_VALIDATION_BITS
