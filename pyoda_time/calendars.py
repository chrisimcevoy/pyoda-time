from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated, Final, final

if TYPE_CHECKING:
    from . import _YearMonthDay
from .utility import _Preconditions, _towards_zero_division, private, sealed


class _YearMonthDayCalculator(ABC):
    """The core of date calculations in Pyoda Time.

    This class *only* cares about absolute years, and only
    dates - it has no time aspects at all, nor era-related aspects.
    """

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        # TODO Preconditions.CheckArgument(...)
        self._min_year = min_year
        self._max_year = max_year
        # We add an extra day to make sure that
        # approximations using days-since-epoch are conservative, to avoid going out of bounds.
        self.__average_days_per_10_years = average_days_per_10_years + 1
        self._days_at_start_of_year_1 = days_at_start_of_year_1
        self.__year_cache = _YearStartCacheEntry._create_cache()

    def _get_start_of_year_in_days(self, year: int) -> int:
        """Fetches the start of the year (in days since 1970-01-01 ISO) from the cache, or calculates and caches it."""
        # TODO Preconditions.DebugCheckArgumentRange(...)
        cache_index = _YearStartCacheEntry._get_cache_index(year)
        cache_entry = self.__year_cache[cache_index]
        if not cache_entry._is_valid_for_year(year):
            days = self._calculate_start_of_year_days(year)
            cache_entry = _YearStartCacheEntry(year, days)
            self.__year_cache[cache_index] = cache_entry
        return cache_entry._start_of_year_days

    @abstractmethod
    def _calculate_start_of_year_days(self, year: int) -> int:
        """Compute the start of the given year in days since 1970-01-01 ISO.

        The year may be outside the bounds advertised by the calendar, but only by a single year. This method is only
        called by get_start_of_year_in_days (unless the calendar chooses to call it itself), so calendars which override
        that method and don't call the original implementation may leave this unimplemented (e.g. by throwing an
        exception if it's ever called).
        """
        raise NotImplementedError

    @abstractmethod
    def _get_days_in_month(self, year: int, month: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def _is_leap_year(self, year: int) -> bool:
        raise NotImplementedError

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        """Computes the days since the Unix epoch at the start of the given year/month/day.

        This is the opposite of _get_year_month_day(int). This assumes the parameter have been validated previously.
        """
        year = year_month_day._year
        start_of_year = self._get_start_of_year_in_days(year)
        start_of_month = start_of_year + self._get_days_from_start_of_year_to_start_of_month(
            year, year_month_day._month
        )
        return start_of_month + year_month_day._day - 1

    @abstractmethod
    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def _get_months_in_year(self, year: int) -> int:
        raise NotImplementedError

    def _validate_year_month_day(self, year: int, month: int, day: int) -> None:
        _Preconditions._check_argument_range(year, self._min_year, self._max_year)
        _Preconditions._check_argument_range(month, 1, self._get_months_in_year(year))
        _Preconditions._check_argument_range(day, 1, self._get_days_in_month(year, month))


@final
class Era:
    """Represents an era used in a calendar.

    All the built-in calendars in Pyoda Time use the values specified by the classmethods in this class. These may be
    compared for reference equality to check for specific eras.
    """

    def __init__(self, name: str, resource_identifier: str):
        # Note: in Noda Time this is an internal constructor...
        self.__name = name
        self._resource_identifier = property(lambda _: resource_identifier)

    def __str__(self) -> str:
        """Returns the name of this era."""
        return self.name

    @classmethod
    def common(cls) -> Era:
        """The "Common" era (CE), also known as Anno Domini (AD).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return cls("CE", "Eras_Common")

    @classmethod
    def before_common(cls) -> Era:
        """The "before common" era (BCE), also known as Before Christ (BC).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return cls("BCE", "Eras_BeforeCommon")

    @property
    def name(self) -> str:
        return self.__name


class _EraCalculator(ABC):
    """Takes responsibility for all era-based calculations for a calendar.

    YearMonthDay arguments can be assumed to be valid for the relevant calendar, but other arguments should be
    validated. (Eras should be validated for nullity as well as for the presence of a particular era.)
    """

    def __init__(self, *eras: Era):
        self._eras = eras

    @abstractmethod
    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        raise NotImplementedError


@final
@sealed
@private
class _SingleEraCalculator(_EraCalculator):
    """Implementation of EraCalculator for calendars which only have a single era."""

    __min_year: Annotated[int, "Set by internal constructor"]
    __max_year: Annotated[int, "Set by internal constructor"]
    __era: Annotated[Era, "Set by internal constructor"]

    @classmethod
    def _ctor(cls, *, era: Era, ymd_calculator: _YearMonthDayCalculator) -> _SingleEraCalculator:
        self = super().__new__(cls)
        self.__min_year = ymd_calculator._min_year
        self.__max_year = ymd_calculator._max_year
        self.__era = era
        return self

    def __validate_era(self, era: Era) -> None:
        # TODO: _Preconditions._check_not_null()
        # TODO: _Preconditions._check_argument()
        raise NotImplementedError

    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        self.__validate_era(era)
        _Preconditions._check_argument_range(year_of_era, self.__min_year, self.__max_year)
        return year_of_era


@final
class _GJEraCalculator(_EraCalculator):
    """Era calculator for Gregorian and Julian calendar systems, which use BC and AD."""

    def __init__(self, ymd_calculator: _YearMonthDayCalculator):
        super().__init__(Era.before_common(), Era.common())
        self.__max_year_of_bc = 1 - ymd_calculator._min_year
        self.__max_year_of_ad = ymd_calculator._max_year

    def __validate_era(self, era: Era) -> None:
        if era != era.common() and era != Era.before_common():
            # TODO: _Preconditions.check_not_null(era)
            # TODO: _Preconditions._check_argument()
            ...
        raise NotImplementedError

    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        self.__validate_era(era)
        if era == Era.common():
            _Preconditions._check_argument_range(year_of_era, 1, self.__max_year_of_ad)
            return year_of_era
        _Preconditions._check_argument_range(year_of_era, 1, self.__max_year_of_bc)
        return 1 - year_of_era


class _RegularYearMonthDayCalculator(_YearMonthDayCalculator, ABC):
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
        super().__init__(min_year, max_year, aveage_days_per_10_years, days_at_start_of_year_1)
        self.__months_in_year = months_in_year

    def _get_months_in_year(self, year: int) -> int:
        return self.__months_in_year


class _GJYearMonthDayCalculator(_RegularYearMonthDayCalculator, ABC):
    _NON_LEAP_DAYS_PER_MONTH: Final[tuple] = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    _LEAP_DAYS_PER_MONTH: Final[tuple] = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    @staticmethod
    def __generate_total_days_by_month(*month_lengths: int) -> list[int]:
        ret = [0]
        for i in range(len(month_lengths)):
            ret.append(ret[i] + month_lengths[i])
        return ret

    __NON_LEAP_TOTAL_DAYS_BY_MONTH: Final[list[int]] = __generate_total_days_by_month(*_NON_LEAP_DAYS_PER_MONTH)
    __LEAP_TOTAL_DAYS_BY_MONTH: Final[list[int]] = __generate_total_days_by_month(*_LEAP_DAYS_PER_MONTH)

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(min_year, max_year, 12, average_days_per_10_years, days_at_start_of_year_1)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return (
            self.__LEAP_TOTAL_DAYS_BY_MONTH[month]
            if self._is_leap_year(year)
            else self.__NON_LEAP_TOTAL_DAYS_BY_MONTH[month]
        )

    @final
    def _get_days_in_month(self, year: int, month: int) -> int:
        # February is awkward
        if month == 2:
            if self._is_leap_year(year):
                return 29
            return 28
        # The lengths of months alternate between 30 and 31, but skip a beat for August.
        # By dividing the month by 8, we effectively handle that skip.
        return 30 + ((month + (month >> 3)) & 1)


@final
class _GregorianYearMonthDayCalculator(_GJYearMonthDayCalculator):
    __MIN_GREGORIAN_YEAR: Final[int] = -9998
    __MAX_GREGORIAN_YEAR: Final[int] = 9999

    __FIRST_OPTIMIZED_YEAR: Final[int] = 1900
    __LAST_OPTIMIZED_YEAR: Final[int] = 2100

    __MONTH_START_DAYS: Final[list[int]] = list(range((__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR) * 12 + 1))
    __YEAR_START_DAYS: Final[list[int]] = list(range(__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR))

    __DAYS_FROM_0000_to_1970: Final[int] = 719527
    __AVERAGE_DAYS_PER_10_YEARS: Final[int] = 3652

    def __init__(self) -> None:
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
        leap_years = _towards_zero_division(year, 100)
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

    def _get_start_of_year_in_days(self, year: int) -> int:
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super()._get_start_of_year_in_days(year)
        return self.__YEAR_START_DAYS[year - self.__FIRST_OPTIMIZED_YEAR]

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        year = year_month_day._year
        month_of_year = year_month_day._month
        day_of_month = year_month_day._day
        if year < self.__FIRST_OPTIMIZED_YEAR or year > self.__LAST_OPTIMIZED_YEAR:
            return super()._get_days_since_epoch(year_month_day)
        year_month_index = (year - self.__FIRST_OPTIMIZED_YEAR) * 12 + month_of_year
        return self.__MONTH_START_DAYS[year_month_index] + day_of_month


class _YearStartCacheEntry:
    """Type containing as much logic as possible for how the cache of "start of year" data works."""

    __CACHE_INDEX_BITS: Final[int] = 10
    __CACHE_SIZE: Final[int] = 1 << __CACHE_INDEX_BITS
    __CACHE_INDEX_MASK: Final[int] = __CACHE_SIZE - 1
    __ENTRY_VALIDATION_BITS: Final[int] = 7
    __ENTRY_VALIDATION_MASK: Final[int] = (1 << __ENTRY_VALIDATION_BITS) - 1
    __INVALID_ENTRY_YEAR: Final[int] = (__ENTRY_VALIDATION_MASK >> 1) << __CACHE_INDEX_BITS

    def __init__(self, year: int, days: int) -> None:
        self.__value = (days << self.__ENTRY_VALIDATION_BITS) | self.__get_validator(year)

    @classmethod
    def __get_validator(cls, year: int) -> int:
        """Returns the validator to use for a given year, a non-negative number containing at most
        __ENTRY_VALIDATION_BITS bits."""
        return (year >> cls.__CACHE_INDEX_BITS) & cls.__ENTRY_VALIDATION_MASK

    @classmethod
    def _get_cache_index(cls, year: int) -> int:
        """Returns the cache index, in [0, CacheSize), that should be used to store the given year's cache entry."""
        return year & cls.__CACHE_INDEX_MASK

    @classmethod
    def _create_cache(cls) -> dict[int, _YearStartCacheEntry]:
        cache = {i: _YearStartCacheEntry.__invalid() for i in range(cls.__CACHE_SIZE)}
        return cache

    @classmethod
    def __invalid(cls) -> _YearStartCacheEntry:
        """Entry which is guaranteed to be obviously invalid for any real date, by having a validation value which is
        larger than any valid year number."""
        return _YearStartCacheEntry(cls.__INVALID_ENTRY_YEAR, 0)

    def _is_valid_for_year(self, year: int) -> bool:
        """Returns whether this cache entry is valid for the given year, and so is safe to use.

        (We assume that we have located this entry via the correct cache index.)
        """
        return self.__get_validator(year) == (self.__value & self.__ENTRY_VALIDATION_MASK)

    @property
    def _start_of_year_days(self) -> int:
        """Returns the (signed) number of days since the Unix epoch for the cache entry."""
        return self.__value >> self.__ENTRY_VALIDATION_BITS
