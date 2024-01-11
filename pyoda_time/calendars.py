from __future__ import annotations as _annotations

__all__: list[str] = [
    "CalendarWeekRule",
    "Era",
    "HebrewMonthNumbering",
    "IslamicEpoch",
    "IslamicLeapYearPattern",
    "IWeekYearRule",
    "WeekYearRules",
]

import abc as _abc
import base64 as _base64
import enum as _enum
import functools as _functools
import typing as _typing

if _typing.TYPE_CHECKING:
    from . import (
        CalendarSystem as _CalendarSystem,
    )
    from . import (
        IsoDayOfWeek as _IsoDayOfWeek,
    )
    from . import (
        LocalDate as _LocalDate,
    )
    from . import (
        _YearMonthDay,
        _YearMonthDayCalendar,
    )
from .utility import _csharp_modulo, _Preconditions, _private, _sealed, _towards_zero_division


class _YearStartCacheEntry:
    """Type containing as much logic as possible for how the cache of "start of year" data works."""

    __CACHE_INDEX_BITS: _typing.Final[int] = 10
    __CACHE_SIZE: _typing.Final[int] = 1 << __CACHE_INDEX_BITS
    __CACHE_INDEX_MASK: _typing.Final[int] = __CACHE_SIZE - 1
    __ENTRY_VALIDATION_BITS: _typing.Final[int] = 7
    __ENTRY_VALIDATION_MASK: _typing.Final[int] = (1 << __ENTRY_VALIDATION_BITS) - 1
    _INVALID_ENTRY_YEAR: _typing.Final[int] = (__ENTRY_VALIDATION_MASK >> 1) << __CACHE_INDEX_BITS

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
        return _YearStartCacheEntry(cls._INVALID_ENTRY_YEAR, 0)

    def _is_valid_for_year(self, year: int) -> bool:
        """Returns whether this cache entry is valid for the given year, and so is safe to use.

        (We assume that we have located this entry via the correct cache index.)
        """
        return self.__get_validator(year) == (self.__value & self.__ENTRY_VALIDATION_MASK)

    @property
    def _start_of_year_days(self) -> int:
        """Returns the (signed) number of days since the Unix epoch for the cache entry."""
        return self.__value >> self.__ENTRY_VALIDATION_BITS


class _YearMonthDayCalculator(_abc.ABC):
    """The core of date calculations in Pyoda Time.

    This class *only* cares about absolute years, and only
    dates - it has no time aspects at all, nor era-related aspects.
    """

    @property
    def _min_year(self) -> int:
        return self.__min_year

    @property
    def _max_year(self) -> int:
        return self.__max_year

    @property
    def _days_at_start_of_year_1(self) -> int:
        return self.__days_at_start_of_year_1

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        # We should really check the minimum year as well, but constructing it hurts my brain.
        _Preconditions._check_argument(
            max_year < _YearStartCacheEntry._INVALID_ENTRY_YEAR,
            "max_year",
            "Calendar year range would invalidate caching.",
        )
        self.__min_year = min_year
        self.__max_year = max_year
        # We add an extra day to make sure that
        # approximations using days-since-epoch are conservative, to avoid going out of bounds.
        self.__average_days_per_10_years = average_days_per_10_years + 1
        self.__days_at_start_of_year_1 = days_at_start_of_year_1
        # Cache to speed up working out when a particular year starts.
        # See the ``YearStartCacheEntry`` documentation and ``GetStartOfYearInDays`` for more details.
        self.__year_cache: _typing.Final[dict[int, _YearStartCacheEntry]] = _YearStartCacheEntry._create_cache()

    # region Abstract methods

    @_abc.abstractmethod
    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        """Returns the number of days from the start of the given year to the start of the given month."""
        raise NotImplementedError

    @_abc.abstractmethod
    def _calculate_start_of_year_days(self, year: int) -> int:
        """Compute the start of the given year in days since 1970-01-01 ISO.

        The year may be outside the bounds advertised by the calendar, but only by a single year. This method is only
        called by get_start_of_year_in_days (unless the calendar chooses to call it itself), so calendars which override
        that method and don't call the original implementation may leave this unimplemented (e.g. by throwing an
        exception if it's ever called).
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_months_in_year(self, year: int) -> int:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_days_in_month(self, year: int, month: int) -> int:
        raise NotImplementedError

    @_abc.abstractmethod
    def _is_leap_year(self, year: int) -> bool:
        raise NotImplementedError

    @_abc.abstractmethod
    def _add_months(self, year_month_day: _YearMonthDay, months: int) -> _YearMonthDay:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        """This is supposed to be an abstract overload of YearMonthDayCalendar.GetYearMonthDay.

        In Python, we can't quite do that, so this method has a different name. The signature in C# is:     `abstract
        YearMonthDay GetYearMonthDay([Trusted] int year, [Trusted] int dayOfYear);`
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_days_in_year(self, year: int) -> int:
        """Returns the number of days in the given year, which will always be within 1 year of the valid range for the
        calculator."""
        raise NotImplementedError

    @_abc.abstractmethod
    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        """Find the months between ``start`` and ``end``.

        (If start is earlier than end, the result will be non-negative.)
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def _set_year(self, year_month_day: _YearMonthDay, year: int) -> _YearMonthDay:
        """Adjusts the given YearMonthDay to the specified year, potentially adjusting other fields as required."""
        raise NotImplementedError

    # endregion

    # region Virtual methods (subclasses should override for performance or correctness)

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

    def compare(self, lhs: _YearMonthDay, rhs: _YearMonthDay) -> int:
        """Compares two YearMonthDay values according to the rules of this calendar. The default implementation simply
        uses a naive comparison of the values, as this is suitable for most calendars (where the first month of the year
        is month 1).

        Although the parameters are trusted (as in, they'll be valid in this calendar),
        the method being public isn't a problem - this type is never exposed.
        """
        return lhs.compare_to(rhs)

    def _validate_year_month_day(self, year: int, month: int, day: int) -> None:
        """Catch-all year/month/day validation.

        Subclasses can optimize further - currently this is only done for
        Gregorian/Julian calendars, which are the most performance-critical.
        """
        _Preconditions._check_argument_range("year", year, self._min_year, self._max_year)
        _Preconditions._check_argument_range("month", month, 1, self._get_months_in_year(year))
        _Preconditions._check_argument_range("day", day, 1, self._get_days_in_month(year, month))

    # endregion

    # region Concrete methods (convenience methods delegating to virtual/abstract ones primarily)

    def _get_day_of_year(self, year_month_day: _YearMonthDay) -> int:
        """Converts from a YearMonthDay representation to "day of year".

        This assumes the parameter have been validated previously.
        """
        return (
            self._get_days_from_start_of_year_to_start_of_month(year_month_day._year, year_month_day._month)
            + year_month_day._day
        )

    @_typing.overload
    def _get_year_month_day(self, *, year: int, day_of_year: int) -> _YearMonthDay:
        ...

    @_typing.overload
    def _get_year_month_day(self, *, days_since_epoch: int) -> _YearMonthDay:
        ...

    def _get_year_month_day(
        self, *, year: int | None = None, day_of_year: int | None = None, days_since_epoch: int | None = None
    ) -> _YearMonthDay:
        """This method is in place to preserve some semblance of parity with Noda Time.

        Currently, typing.overload does not allow for some overloads to be implemented and some to be abstract. So I
        have split them out into separate methods with an appropriate suffix.
        """
        if year is not None and day_of_year is not None:
            return self._get_year_month_day_from_year_and_day_of_year(year, day_of_year)
        elif days_since_epoch is not None:
            return self._get_year_month_day_from_days_since_epoch(days_since_epoch)
        raise RuntimeError("_get_year_month_day called with incorrect arguments")

    def _get_year_month_day_from_days_since_epoch(self, days_since_epoch: int) -> _YearMonthDay:
        """Works out the year/month/day of a given days-since-epoch by first computing the year and day of year, then
        getting the month and day from those two.

        This is how almost all calendars are naturally implemented anyway.
        """
        year, zero_based_day = self._get_year(days_since_epoch)
        return self._get_year_month_day(year=year, day_of_year=zero_based_day + 1)

    def _get_year(self, days_since_epoch: int) -> tuple[int, int]:
        """Work out the year from the number of days since the epoch, as well as the day of that year (0-based).

        :param days_since_epoch: The number of days since the epoch.
        :return: A 2-tuple of (year, zero_based_day_of_year)
        """
        # Get an initial estimate of the year, and the days-since-epoch value that
        # represents the start of that year. Then verify estimate and fix if
        # necessary. We have the average days per 100 years to avoid getting bad candidates
        # pretty quickly.
        days_since_year_1 = days_since_epoch - self._days_at_start_of_year_1
        candidate = _towards_zero_division(days_since_year_1 * 10, self.__average_days_per_10_years) + 1

        # Most of the time we'll get the right year straight away, and we'll almost
        # always get it after one adjustment - but it's safer (and easier to think about)
        # if we just keep going until we know we're right.
        candidate_start = self._get_start_of_year_in_days(candidate)
        days_from_candidate_start_to_target = days_since_epoch - candidate_start
        if days_from_candidate_start_to_target < 0:
            # Our candidate year is later than we want. Keep going backwards until we've got
            # a non-negative result, which must then be correct.
            while days_from_candidate_start_to_target < 0:
                candidate -= 1
                days_from_candidate_start_to_target += self._get_days_in_year(candidate)
            zero_based_day_of_year = days_from_candidate_start_to_target
            return candidate, zero_based_day_of_year
        # Our candidate year is correct or earlier than the right one. Find out which by
        # comparing it with the length of the candidate year.
        candidate_length = self._get_days_in_year(candidate)
        while days_from_candidate_start_to_target >= candidate_length:
            # Our candidate year is earlier than we want, so fast forward a year,
            # removing the current candidate length from the "remaining days" and
            # working out the length of the new candidate.
            candidate += 1
            days_from_candidate_start_to_target -= candidate_length
            candidate_length = self._get_days_in_year(candidate)
        zero_based_day_of_year = days_from_candidate_start_to_target
        return candidate, zero_based_day_of_year

    # endregion


@_sealed
class _BadiYearMonthDayCalculator(_YearMonthDayCalculator):
    # named constants to avoid use of raw numbers in the code
    __AVERAGE_DAYS_PER_10_years: _typing.Final[int] = 3652
    __DAYS_IN_AYYAMI_HA_IN_LEAP_YEAR: _typing.Final[int] = 5
    __DAYS_IN_AYYAMI_HA_IN_NORMAL_YEAR: _typing.Final[int] = 4

    _DAYS_IN_MONTH: _typing.Final[int] = 19
    __FIRST_YEAR_OF_STANDARDIZED_CALENDAR: _typing.Final[int] = 172
    __GREGORIAN_YEAR_OF_FIRST_BADI_YEAR: _typing.Final[int] = 1844

    # There are 19 months in a year. Between the 18th and 19th month are the "days of Ha" (Ayyam-i-Ha).
    # In order to make everything else in Noda Time work appropriately, Ayyam-i-Ha are counted as
    # extra days at the end of month 18.
    _MONTH_18: _typing.Final[int] = 18
    __MONTH_19: _typing.Final[int] = 19
    __MONTHS_IN_YEAR: _typing.Final[int] = 19

    __UNIX_EPOCH_DAY_AT_START_OF_YEAR_1: _typing.Final[int] = -45941
    __BADI_MAX_YEAR: _typing.Final[int] = 1000  # current lookup tables are pre-calculated for a thousand years
    __BADI_MIN_YEAR: _typing.Final[int] = 1

    # This is the base64 representation of information for years 172 to 1000.
    # NazRuzDate falls on March 19, 20, 21, or 22.
    # DaysInAyymiHa can be 4,5.
    # For each year, the value in the array is (NawRuzDate - 19) + 10 * (DaysInAyyamiHa - 4)
    year_info_raw = _base64.b64decode(
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
        from . import CalendarSystem

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
        from . import LocalDate

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
        from . import _YearMonthDay

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


class _EraMeta(type):
    """Class properties for ``Era``.

    This implementation mimics the API of Noda Time by providing attribute-like
    access against the ``Era`` class.

    An important implementation detail is that equality checks in the codebase
    depend on these properties returning the same instance, because __eq__ is not
    implemented (so we rely on reference equality). Era._ctor() is called from
    each of these properties, and is decorated with `@functools.cache` to provide
    just that behaviour.

    Why not use functools.cached_property?
    https://discuss.python.org/t/finding-a-path-forward-for-functools-cached-property/23757
    """

    @property
    def common(cls) -> Era:
        """The "Common" era (CE), also known as Anno Domini (AD).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return Era._ctor("CE", "Eras_Common")

    @property
    def before_common(cls) -> Era:
        """The "before common" era (BCE), also known as Before Christ (BC).

        This is used in the ISO, Gregorian and Julian calendars.
        """
        return Era._ctor("BCE", "Eras_BeforeCommon")

    @property
    def anno_martyrum(self) -> Era:
        """The "Anno Martyrum" or "Era of the Martyrs".

        This is the sole era used in the Coptic calendar.
        """
        return Era._ctor("AM", "Eras_AnnoMartyrum")

    @property
    def anno_hegirae(self) -> Era:
        """The "Anno Hegira" era.

        This is the sole era used in the Hijri (Islamic) calendar.
        """
        return Era._ctor("EH", "Eras_AnnoHegirae")

    @property
    def anno_mundi(self) -> Era:
        """The "Anno Mundi" era.

        This is the sole era used in the Hebrew calendar.
        """
        return Era._ctor("AM", "Eras_AnnoMundi")

    @property
    def anno_persico(self) -> Era:
        """The "Anno Persico" era.

        This is the sole era used in the Persian calendar.
        """
        return Era._ctor("AP", "Eras_AnnoPersico")

    @property
    def bahai(cls) -> Era:
        """The "Bahá'í" era.

        This is the sole era used in the Badi calendar.
        """
        return Era._ctor("BE", "Eras_Bahai")


@_typing.final
@_private
@_sealed
class Era(metaclass=_EraMeta):
    """Represents an era used in a calendar.

    All the built-in calendars in Pyoda Time use the values specified by the classmethods in this class. These may be
    compared for reference equality to check for specific eras.
    """

    @property
    def _resource_identifier(self) -> str:
        return self.__resource_identifier

    @property
    def name(self) -> str:
        """Return the name of this era, e.g. "CE" or "BCE"."""
        return self.__name

    __name: str
    __resource_identifier: str

    @classmethod
    @_functools.cache
    def _ctor(cls, name: str, resource_identifier: str) -> Era:
        """Internal constructor implementation.

        Note: This constructor is cached and will return the same instance each
        time it is called with the same arguments.

        This is an implementation detail which is particular to pyoda-time and is
        not present in the mother project. (Although it is intended to mimic the
        characteristics of the static read-only properties in that world).

        The reason is that the class-level properties of _EraMeta all call this constructor.
        There are several places in the codebase where Eras are evaluated for equality,
        but as Era does not implement __eq__(), referential equality is relied upon
        hence the need to return the same instance each time this is called.

        Why not use functools.cached_property? Well, maybe in future:
        https://discuss.python.org/t/finding-a-path-forward-for-functools-cached-property/23757
        """
        self = super().__new__(cls)
        self.__name = name
        self.__resource_identifier = resource_identifier
        return self

    def __str__(self) -> str:
        """Return the name of this era."""
        return self.name


class _EraCalculator(_abc.ABC):
    """Takes responsibility for all era-based calculations for a calendar.

    YearMonthDay arguments can be assumed to be valid for the relevant calendar, but other arguments should be
    validated. (Eras should be validated for nullity as well as for the presence of a particular era.)
    """

    def __init__(self, *eras: Era):
        self._eras = eras

    @_abc.abstractmethod
    def _get_min_year_of_era(self, era: Era) -> int:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_max_year_of_era(self, era: Era) -> int:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_era(self, absolute_year: int) -> Era:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_year_of_era(self, absolute_year: int) -> int:
        raise NotImplementedError

    @_abc.abstractmethod
    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        raise NotImplementedError


@_typing.final
@_sealed
@_private
class _SingleEraCalculator(_EraCalculator):
    """Implementation of EraCalculator for calendars which only have a single era."""

    __min_year: _typing.Annotated[int, "Set by internal constructor"]
    __max_year: _typing.Annotated[int, "Set by internal constructor"]
    __era: _typing.Annotated[Era, "Set by internal constructor"]

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


@_typing.final
class _GJEraCalculator(_EraCalculator):
    """Era calculator for Gregorian and Julian calendar systems, which use BC and AD."""

    def __init__(self, ymd_calculator: _YearMonthDayCalculator):
        super().__init__(Era.before_common, Era.common)
        self.__max_year_of_bc = 1 - ymd_calculator._min_year
        self.__max_year_of_ad = ymd_calculator._max_year

    def __validate_era(self, era: Era) -> None:
        if era != Era.common and era != Era.before_common:
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


class _RegularYearMonthDayCalculator(_YearMonthDayCalculator, _abc.ABC):
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

    def _set_year(self, year_month_day: _YearMonthDay, year: int) -> _YearMonthDay:
        """Implements a simple year-setting policy, truncating the day if necessary."""
        # If this ever becomes a bottleneck due to GetDaysInMonth, it can be overridden in subclasses.
        current_month: int = year_month_day._month
        current_day: int = year_month_day._day
        new_day: int = self._get_days_in_month(year, current_month)
        from pyoda_time import _YearMonthDay

        return _YearMonthDay._ctor(year=year, month=current_month, day=min(current_day, new_day))

    def _add_months(self, year_month_day: _YearMonthDay, months: int) -> _YearMonthDay:
        if months == 0:
            return year_month_day
        # Get the year and month
        this_year = year_month_day._year
        this_month = year_month_day._month

        # Do not refactor without careful consideration.
        # Order of calculation is important.

        year_to_use: int
        # Initially, monthToUse is zero-based
        month_to_use = this_month - 1 + months
        if month_to_use >= 0:
            year_to_use = this_year + _towards_zero_division(month_to_use, self.__months_in_year)
            month_to_use = (month_to_use % self.__months_in_year) + 1
        else:
            year_to_use = this_year + _towards_zero_division(month_to_use, self.__months_in_year) - 1
            month_to_use = abs(month_to_use)
            rem_month_to_use = month_to_use % self.__months_in_year
            # Take care of the boundary condition
            if rem_month_to_use == 0:
                rem_month_to_use = self.__months_in_year
            month_to_use = self.__months_in_year - rem_month_to_use + 1
            # Take care of the boundary condition
            if month_to_use == 1:
                year_to_use += 1
        # End of do not refactor

        # Quietly force DOM to nearest sane value.
        day_to_use = year_month_day._day
        max_day = self._get_days_in_month(year_to_use, month_to_use)
        day_to_use = min(day_to_use, max_day)
        if (year_to_use < self._min_year) or (year_to_use > self._max_year):
            raise OverflowError("Date computation would overflow calendar bounds.")
        from pyoda_time import _YearMonthDay

        return _YearMonthDay._ctor(year=year_to_use, month=month_to_use, day=day_to_use)

    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        start_month: int = start._month
        start_year: int = start._year
        end_month: int = end._month
        end_year: int = end._year

        diff: int = (end_year - start_year) * self.__months_in_year + end_month - start_month

        # If we just add the difference in months to start, what do we get?
        simple_addition: _YearMonthDay = self._add_months(start, diff)

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


class _GJYearMonthDayCalculator(_RegularYearMonthDayCalculator, _abc.ABC):
    _NON_LEAP_DAYS_PER_MONTH: _typing.Final[tuple] = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    _LEAP_DAYS_PER_MONTH: _typing.Final[tuple] = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    @staticmethod
    def __generate_total_days_by_month(*month_lengths: int) -> list[int]:
        ret = [0]
        for i in range(len(month_lengths)):
            ret.append(ret[i] + month_lengths[i])
        return ret

    __NON_LEAP_TOTAL_DAYS_BY_MONTH: _typing.Final[list[int]] = __generate_total_days_by_month(*_NON_LEAP_DAYS_PER_MONTH)
    __LEAP_TOTAL_DAYS_BY_MONTH: _typing.Final[list[int]] = __generate_total_days_by_month(*_LEAP_DAYS_PER_MONTH)

    def __init__(
        self,
        min_year: int,
        max_year: int,
        average_days_per_10_years: int,
        days_at_start_of_year_1: int,
    ):
        super().__init__(min_year, max_year, 12, average_days_per_10_years, days_at_start_of_year_1)

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, d: int) -> _YearMonthDay:
        is_leap: bool = self._is_leap_year(year)

        start_of_month: int
        # Perform a hard-coded binary search to get the 0-based start day of the month. We can
        # then use that to work out the month... without ever hitting the heap. The values
        # are still MinTotalDaysPerMonth and MaxTotalDaysPerMonth (-1 for convenience), just hard-coded.
        if is_leap:
            start_of_month = (
                (0 if d < 32 else 31 if d < 61 else 60)
                if d < 92
                else (91 if d < 122 else 121 if d < 153 else 152)
                if d < 183
                else (182 if d < 214 else 213 if d < 245 else 244)
                if d < 275
                else (274 if d < 306 else 305 if d < 336 else 335)
            )
        else:
            start_of_month = (
                (0 if d < 32 else 31 if d < 60 else 59)
                if d < 91
                else (90 if d < 121 else 120 if d < 152 else 151)
                if d < 182
                else (181 if d < 213 else 212 if d < 244 else 243)
                if d < 274
                else (273 if d < 305 else 304 if d < 335 else 334)
            )

        day_of_month: int = d - start_of_month
        from . import _YearMonthDay

        return _YearMonthDay._ctor(year=year, month=_towards_zero_division(start_of_month, 29) + 1, day=day_of_month)

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self._is_leap_year(year) else 365

    @_typing.final
    def _get_days_in_month(self, year: int, month: int) -> int:
        # February is awkward
        if month == 2:
            if self._is_leap_year(year):
                return 29
            return 28
        # The lengths of months alternate between 30 and 31, but skip a beat for August.
        # By dividing the month by 8, we effectively handle that skip.
        return 30 + ((month + (month >> 3)) & 1)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return (
            self.__LEAP_TOTAL_DAYS_BY_MONTH[month]
            if self._is_leap_year(year)
            else self.__NON_LEAP_TOTAL_DAYS_BY_MONTH[month]
        )


@_typing.final
class _GregorianYearMonthDayCalculator(_GJYearMonthDayCalculator):
    _MIN_GREGORIAN_YEAR: _typing.Final[int] = -9998
    _MAX_GREGORIAN_YEAR: _typing.Final[int] = 9999

    __FIRST_OPTIMIZED_YEAR: _typing.Final[int] = 1900
    __LAST_OPTIMIZED_YEAR: _typing.Final[int] = 2100
    __FIRST_OPTIMIZED_DAY: _typing.Final[int] = -25567
    __LAST_OPTIMIZED_DAY: _typing.Final[int] = 47846
    # The 0-based days-since-unix-epoch for the start of each month
    __MONTH_START_DAYS: _typing.Final[list[int]] = list(
        range((__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR) * 12 + 1)
    )
    # The 1-based days-since-unix-epoch for the start of each year
    __YEAR_START_DAYS: _typing.Final[list[int]] = list(range(__LAST_OPTIMIZED_YEAR + 1 - __FIRST_OPTIMIZED_YEAR))

    __DAYS_FROM_0000_to_1970: _typing.Final[int] = 719527
    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = 3652

    @classmethod
    def _get_gregorian_year_month_day_calendar_from_days_since_epoch(
        cls, days_since_epoch: int
    ) -> _YearMonthDayCalendar:
        from . import CalendarSystem, _CalendarOrdinal, _YearMonthDayCalendar

        # TODO: unchecked
        if days_since_epoch < cls.__FIRST_OPTIMIZED_DAY or days_since_epoch > cls.__LAST_OPTIMIZED_DAY:
            return CalendarSystem.iso._get_year_month_day_calendar_from_days_since_epoch(days_since_epoch)
        # Divide by more than we need to, in order to guarantee that we only need to move forward.
        # We can still only be out by 1 year.
        year_index = _towards_zero_division(days_since_epoch - cls.__FIRST_OPTIMIZED_DAY, 366)
        index_value = cls.__YEAR_START_DAYS[year_index]
        # Zero-based day of year
        d: int = days_since_epoch - index_value
        year: int = year_index + cls.__FIRST_OPTIMIZED_YEAR
        is_leap: bool = cls.__is_gregorian_leap_year(year)
        days_in_year: int = 366 if is_leap else 365
        if d >= days_in_year:
            year += 1
            d -= days_in_year
            is_leap = cls.__is_gregorian_leap_year(year)

        # The remaining code is copied from GJYearMonthDayCalculator (and tweaked)

        start_of_month: int = 0
        # Perform a hard-coded binary search to get the month.
        if is_leap:
            start_of_month = (
                -1
                if d < 31
                else 30
                if d < 60
                else 59
                if d < 91
                else 90
                if d < 121
                else 120
                if d < 152
                else 151
                if d < 182
                else 181
                if d < 213
                else 212
                if d < 244
                else 243
                if d < 274
                else 273
                if d < 305
                else 304
                if d < 335
                else 334
            )
        else:
            start_of_month = (
                -1
                if d < 31
                else 30
                if d < 59
                else 58
                if d < 90
                else 89
                if d < 120
                else 119
                if d < 151
                else 150
                if d < 181
                else 180
                if d < 212
                else 211
                if d < 243
                else 242
                if d < 273
                else 272
                if d < 304
                else 303
                if d < 334
                else 333
            )
        month: int = _towards_zero_division(start_of_month, 29) + 1
        day_of_month: int = d - start_of_month
        return _YearMonthDayCalendar._ctor(
            year=year,
            month=month,
            day=day_of_month,
            calendar_ordinal=_CalendarOrdinal.ISO,
        )

    def __init__(self) -> None:
        super().__init__(
            self._MIN_GREGORIAN_YEAR,
            self._MAX_GREGORIAN_YEAR,
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

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self.__is_gregorian_leap_year(year) else 365

    def _is_leap_year(self, year: int) -> bool:
        return self.__is_gregorian_leap_year(year)

    @staticmethod
    def __is_gregorian_leap_year(year: int) -> bool:
        return ((year & 3) == 0) and ((year % 100) != 0 or (year % 400) == 0)


class HebrewMonthNumbering(_enum.IntEnum):
    """The month numbering to use for the Hebrew calendar.

    When requesting a Hebrew calendar with ``CalendarSystem.get_hebrew_calendar()``, a month numbering
    system needs to be specified. There are two main ways of numbering the Hebrew months: the civil
    system where month 1 is the start of the new year (Tishri) and scriptural system where month 1 is
    Nisan, according to biblical custom.
    """

    # The numbering system where month 1 is Tishri. This has the advantage of familiarity with other
    # calendars where the first month is 1; it is easier to tell which date comes before which, aside
    # from anything else. It is also the numbering system used by the BCL.
    #
    # The main disadvantage is that due to leap years effectively "splitting" Adar into Adar I
    # and Adar II, the months after that (Nisan, Iyyar and so on) have month numberings which depend
    # on the year.
    CIVIL = 1
    # The numbering system where month 1 is Nisan. This is the numbering system which matches biblical
    # custom (such as Leviticus 23:5). This has the advantage that the split of Adar is at the end of the
    # numbering system, so all other month names are stable.
    #
    # The primary disadvantage of this numbering system is that months 1-6 come after months 7-12 (or 13),
    # which is counter-intuitive.
    SCRIPTURAL = 2


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


class _HebrewScripturalCalculator:
    """Implementation of the algorithms described in
    https://www.cs.tau.ac.il/~nachum/calendar-book/papers/calendar.ps, using scriptural
    month numbering.
    """

    _MAX_YEAR: _typing.Final[int] = 9999
    _MIN_YEAR: _typing.Final[int] = 1
    # Use the bottom two bits of the day value to indicate Heshvan/Kislev.
    # Using the top bits causes issues for negative day values (only relevant for
    # invalid years, but still problematic in general).
    __IS_HESHVAN_LONG_CACHE_BIT: _typing.Final[int] = 1 << 0
    __IS_KISLEV_SHORT_CACHE_BIT: _typing.Final[int] = 1 << 1
    # Number of bits to shift the elapsed days in order to get the cache value.
    __ELAPSED_DAYS_CACHE_SHIFT: _typing.Final[int] = 2

    # Cache of when each year starts (in  terms of absolute days). This is the heart of
    # the algorithm, so just caching this is highly effective.
    # Each entry additionally encodes the length of Heshvan and Kislev. We could encode
    # more information too, but those are the tricky bits.
    __YEAR_CACHE: _typing.Final[dict[int, _YearStartCacheEntry]] = _YearStartCacheEntry._create_cache()

    @staticmethod
    def _is_leap_year(year: int) -> bool:
        return ((year * 7) + 1) % 19 < 7

    @classmethod
    def _get_year_month_day(cls, year: int, day_of_year: int) -> _YearMonthDay:
        from . import _YearMonthDay

        # TODO: unchecked

        # Work out everything about the year in one go.
        cache: int = cls.__get_or_populate_cache(year)
        heshvan_length: int = 30 if (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0 else 29
        kislev_length: int = 29 if (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0 else 30
        is_leap: bool = cls._is_leap_year(year)
        first_adar_length = 30 if is_leap else 29

        if day_of_year < 31:
            # Tishri
            return _YearMonthDay._ctor(year=year, month=7, day=day_of_year)
        if day_of_year < 31 + heshvan_length:
            # Heshvan
            return _YearMonthDay._ctor(year=year, month=8, day=day_of_year - 30)
        # Now "day of year without Heshvan"...
        day_of_year -= heshvan_length
        if day_of_year < 31 + kislev_length:
            # Kislev
            return _YearMonthDay._ctor(year=year, month=9, day=day_of_year - 30)
        # Now "day of year without Heshvan or Kislev"...
        day_of_year -= kislev_length
        if day_of_year < 31 + 29:
            # Tevet
            return _YearMonthDay._ctor(year=year, month=10, day=day_of_year - 30)
        if day_of_year < 31 + 29 + 30:
            # Shevat
            return _YearMonthDay._ctor(year=year, month=11, day=day_of_year - (30 + 29))
        if day_of_year < 31 + 29 + 30 + first_adar_length:
            # Adar / Adar I
            return _YearMonthDay._ctor(year=year, month=12, day=day_of_year - (30 + 29 + 30))
        # Now "day of year without first month of Adar"
        day_of_year -= first_adar_length
        if is_leap:
            if day_of_year < 31 + 29 + 30 + 29:
                return _YearMonthDay._ctor(year=year, month=13, day=day_of_year - (30 + 29 + 30))
            # Now "day of year without any Adar"
            day_of_year -= 29
        # We could definitely do a binary search from here, but it would only
        # a few comparisons at most, and simplicity trumps optimization.
        if day_of_year < 31 + 29 + 30 + 30:
            # Nisan
            return _YearMonthDay._ctor(year=year, month=1, day=day_of_year - (30 + 29 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29:
            # Iyar
            return _YearMonthDay._ctor(year=year, month=2, day=day_of_year - (30 + 29 + 30 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30:
            # Sivan
            return _YearMonthDay._ctor(year=year, month=3, day=day_of_year - (30 + 29 + 30 + 30 + 29))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30 + 29:
            # Tamuz
            return _YearMonthDay._ctor(year=year, month=4, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30))
        if day_of_year < 31 + 29 + 30 + 30 + 29 + 30 + 29 + 30:
            # Av
            return _YearMonthDay._ctor(year=year, month=5, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30 + 29))
        # Elul
        return _YearMonthDay._ctor(year=year, month=6, day=day_of_year - (30 + 29 + 30 + 30 + 29 + 30 + 29 + 30))

    @classmethod
    def _get_days_from_start_of_year_to_start_of_month(cls, year: int, month: int) -> int:  # type: ignore[return]
        # Work out everything about the year in one go. (Admittedly we don't always need it all... but for
        # anything other than Tishri and Heshvan, we at least need the length of Heshvan...)

        # TODO: unchecked

        cache: int = cls.__get_or_populate_cache(year)
        heshvan_length = 30 if (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0 else 29
        kislev_length = 29 if (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0 else 30
        is_leap = cls._is_leap_year(year)
        first_adar_length = 30 if is_leap else 29
        second_adar_length = 29 if is_leap else 0
        match month:
            case 1:  # Nisan
                return 30 + heshvan_length + kislev_length + (29 + 30) + first_adar_length + second_adar_length
            case 2:  # Iyar
                return 30 + heshvan_length + kislev_length + (29 + 30) + first_adar_length + second_adar_length + 30
            case 3:  # Sivan
                return (
                    30 + heshvan_length + kislev_length + 29 + 30 + first_adar_length + second_adar_length + (30 + 29)
                )
            case 4:  # Tamuz
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30)
                )
            case 5:  # Av
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30 + 29)
                )
            case 6:  # Elul
                return (
                    30
                    + heshvan_length
                    + kislev_length
                    + 29
                    + 30
                    + first_adar_length
                    + second_adar_length
                    + (30 + 29 + 30 + 29 + 30)
                )
            case 7:  # Tishri
                return 0
            case 8:  # Heshvan
                return 30
            case 9:  # Kislev
                return 30 + heshvan_length
            case 10:  # Tevet
                return 30 + heshvan_length + kislev_length
            case 11:  # Shevet
                return 30 + heshvan_length + kislev_length + 29
            case 12:  # Adar / Adar I
                return 30 + heshvan_length + kislev_length + 29 + 30
            case 13:  # Adar II
                return 30 + heshvan_length + kislev_length + 29 + 30 + first_adar_length

        _Preconditions._throw_argument_out_of_range_exception("month", month, 1, 13)

    @classmethod
    def _days_in_month(cls, year: int, month: int) -> int:
        match month:
            case 2 | 4 | 6 | 10 | 13:
                return 29
            case 8:
                return 30 if cls.__is_heshvan_long(year) else 29
            case 9:
                return 29 if cls.__is_kislev_short(year) else 30
            case 12:
                return 30 if cls._is_leap_year(year) else 29
            case _:  # 1, 3, 5, 7, 11
                return 30

    @classmethod
    def __is_heshvan_long(cls, year: int) -> bool:
        cache: int = cls.__get_or_populate_cache(year)
        return (cache & cls.__IS_HESHVAN_LONG_CACHE_BIT) != 0

    @classmethod
    def __is_kislev_short(cls, year: int) -> bool:
        cache: int = cls.__get_or_populate_cache(year)
        return (cache & cls.__IS_KISLEV_SHORT_CACHE_BIT) != 0

    @classmethod
    def _elapsed_days(cls, year: int) -> int:
        cache: int = cls.__get_or_populate_cache(year)
        return cache >> cls.__ELAPSED_DAYS_CACHE_SHIFT

    @classmethod
    def __elapsed_days_no_cache(cls, year: int) -> int:
        months_elapsed: int = (
            # Months in complete cycles so far
            (235 * _towards_zero_division((year - 1), 19))
            # Regular months in this cycle
            + (12 * _csharp_modulo((year - 1), 19))
            # Leap months this cycle
            + (_towards_zero_division(_csharp_modulo((year - 1), 19) * 7 + 1, 19))
        )
        # Second option in the paper, which keeps values smaller
        parts_elapsed: int = 204 + (793 * _csharp_modulo(months_elapsed, 1080))
        hours_elapsed: int = (
            5
            + (12 * months_elapsed)
            + (793 * _towards_zero_division(months_elapsed, 1080))
            + _towards_zero_division(parts_elapsed, 1080)
        )
        day: int = 1 + (29 * months_elapsed) + _towards_zero_division(hours_elapsed, 24)
        parts: int = (_csharp_modulo(hours_elapsed, 24) * 1080) + _csharp_modulo(parts_elapsed, 1080)
        postpone_rosh_ha_shanah: bool = (
            (parts >= 19440)
            or (_csharp_modulo(day, 7) == 2 and parts >= 9924 and not cls._is_leap_year(year))
            or (_csharp_modulo(day, 7) == 1 and parts >= 16789 and cls._is_leap_year(year - 1))
        )
        alternative_day: int = 1 + day if postpone_rosh_ha_shanah else day
        alternative_day_mod_7: int = _csharp_modulo(alternative_day, 7)
        return alternative_day + 1 if alternative_day_mod_7 in (0, 3, 5) else alternative_day

    @classmethod
    def __get_or_populate_cache(cls, year: int) -> int:
        """Returns the cached "elapsed day at start of year / IsHeshvanLong / IsKislevShort" combination, populating the
        cache if necessary.

        Bits 2-24 are the "elapsed days start of year"; bit 0 is "is Heshvan long"; bit 1 is "is Kislev short". If the
        year is out of the range for the cache, the value is populated but not cached.
        """
        if year < cls._MIN_YEAR or year > cls._MAX_YEAR:
            return cls.__compute_cache_entry(year)
        cache_index: int = _YearStartCacheEntry._get_cache_index(year)
        cache_entry: _YearStartCacheEntry = cls.__YEAR_CACHE[cache_index]
        if not cache_entry._is_valid_for_year(year):
            days: int = cls.__compute_cache_entry(year)
            cache_entry = _YearStartCacheEntry(year, days)
            cls.__YEAR_CACHE[cache_index] = cache_entry
        return cache_entry._start_of_year_days

    @classmethod
    def __compute_cache_entry(cls, year: int) -> int:
        """Computes the cache entry value for the given year, but without populating the cache."""
        days: int = cls.__elapsed_days_no_cache(year)
        # We want the elapsed days for the next year as well. Check the cache if possible.
        next_year = year + 1
        next_year_days: int
        if next_year < cls._MAX_YEAR:
            cache_index: int = _YearStartCacheEntry._get_cache_index(next_year)
            cache_entry: _YearStartCacheEntry = cls.__YEAR_CACHE[cache_index]
            next_year_days = (
                cache_entry._start_of_year_days >> cls.__ELAPSED_DAYS_CACHE_SHIFT
                if cache_entry._is_valid_for_year(next_year)
                else cls.__elapsed_days_no_cache(next_year)
            )
        else:
            next_year_days = cls.__elapsed_days_no_cache(year + 1)
        days_in_year = next_year_days - days
        is_heshvan_long = _csharp_modulo(days_in_year, 10) == 5
        is_kislev_short = _csharp_modulo(days_in_year, 10) == 3
        return (
            (days << cls.__ELAPSED_DAYS_CACHE_SHIFT)
            | (cls.__IS_HESHVAN_LONG_CACHE_BIT if is_heshvan_long else 0)
            | (cls.__IS_KISLEV_SHORT_CACHE_BIT if is_kislev_short else 0)
        )

    @classmethod
    def _days_in_year(cls, year: int) -> int:
        return cls._elapsed_days(year + 1) - cls._elapsed_days(year)


@_sealed
class _HebrewYearMonthDayCalculator(_YearMonthDayCalculator):
    __UNIX_EPOCH_DAY_AT_START_OF_YEAR_1: _typing.Final[int] = -2092590
    __MONTHS_PER_LEAP_CYCLE: _typing.Final[int] = 235
    __YEARS_PER_LEAP_CYCLE: _typing.Final[int] = 19

    def __init__(self, month_numbering: HebrewMonthNumbering) -> None:
        super().__init__(
            _HebrewScripturalCalculator._MIN_YEAR,
            _HebrewScripturalCalculator._MAX_YEAR,
            3654,  # Average length of 10 years
            self.__UNIX_EPOCH_DAY_AT_START_OF_YEAR_1,
        )
        self.__month_numbering: _typing.Final[HebrewMonthNumbering] = month_numbering

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
        from . import _YearMonthDay

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


class IslamicEpoch(_enum.IntEnum):
    """The epoch to use when constructing an Islamic calendar.

    The Islamic, or Hijri, calendar can either be constructed starting on July 15th 622CE (in the Julian calendar) or on
    the following day. The former is the "astronomical" or "Thursday" epoch; the latter is the "civil" or "Friday"
    epoch.
    """

    # Epoch beginning on July 15th 622CE (Julian), which is July 18th 622 CE in the Gregorian calendar.
    # This is the epoch used by the BCL HijriCalendar.
    ASTRONOMICAL = 1
    # Epoch beginning on July 16th 622CE (Julian), which is July 19th 622 CE in the Gregorian calendar.
    CIVIL = 2


class IslamicLeapYearPattern(_enum.IntEnum):
    """The pattern of leap years to use when constructing an Islamic calendar.

    The Islamic, or Hijri, calendar is a lunar calendar of 12 months, each of 29 or 30 days. The calendar can be defined
    in either observational or tabular terms; Noda Time implements a tabular calendar, where a pattern of leap years (in
    which the last month has an extra day) repeats every 30 years, according to one of the patterns within this enum.

    While the patterns themselves are reasonably commonly documented (see e.g.
    https://en.wikipedia.org/wiki/Tabular_Islamic_calendar)
    there is little standardization in terms of naming the patterns. I hope the current names do not
    cause offence to anyone; suggestions for better names would be welcome.
    """

    # A pattern of leap years in 2, 5, 7, 10, 13, 15, 18, 21, 24, 26 and 29.
    # This pattern and <see cref="Base16"/> are the most commonly used ones,
    # and only differ in whether the 15th or 16th year is deemed leap.
    BASE15 = 1
    # A pattern of leap years in 2, 5, 7, 10, 13, 16, 18, 21, 24, 26 and 29.
    # This pattern and <see cref="Base15"/> are the most commonly used ones,
    # and only differ in whether the 15th or 16th year is deemed leap. This is
    # the pattern used by the BCL HijriCalendar.
    BASE16 = 2
    # A pattern of leap years in 2, 5, 8, 10, 13, 16, 19, 21, 24, 27 and 29.
    INDIAN = 3
    # A pattern of leap years in 2, 5, 8, 11, 13, 16, 19, 21, 24, 27 and 30.
    HABASH_AL_HASIB = 4


@_sealed
class _IslamicYearMonthDayCalculator(_RegularYearMonthDayCalculator):
    # Days in a pair of months, in days.
    __MONTH_PAIR_LENGTH: _typing.Final[int] = 59

    # The length of a long month, in days.
    __LONG_MONTH_LENGTH: _typing.Final[int] = 30

    # The length of a short month, in days.
    __SHORT_MONTH_LENGTH: _typing.Final[int] = 29

    # The typical number of days in 10 years.
    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = 3544  # Ideally 354.36667 per year

    # The number of days in a non-leap year.
    __DAYS_PER_NON_LEAP_YEAR: _typing.Final[int] = 354

    # The number of days in a leap year.
    __DAYS_PER_LEAP_YEAR: _typing.Final[int] = 355

    # The days for the civil (Friday) epoch of July 16th 622CE.
    __DAYS_AT_CIVIL_EPOCH: _typing.Final[int] = -492148

    # The days for the civil (Thursday) epoch of July 15th 622CE.
    __DAYS_AT_ASTRONOMICAL_EPOCH: _typing.Final[int] = __DAYS_AT_CIVIL_EPOCH - 1

    # The length of the cycle of two leap years.
    __LEAP_YEAR_CYCLE_LENGTH: _typing.Final[int] = 30

    # The number of days in a leap cycle.
    __DAYS_PER_LEAP_CYCLE = 19 * __DAYS_PER_NON_LEAP_YEAR + 11 * __DAYS_PER_LEAP_YEAR

    @staticmethod
    def __generate_total_days_by_month(
        long_month_length: int, short_month_length: int
    ) -> _typing.Generator[int, _typing.Any, None]:
        days = 0
        for i in range(1, 13):
            yield days
            days_in_month = long_month_length if (i & 1) == 1 else short_month_length
            days += days_in_month

    # The number of days preceding the 1-indexed month - so [0, 0, 30, 59, ...]
    __TOTAL_DAYS_BY_MONTH: _typing.Final[list[int]] = [
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
        self.__leap_year_pattern_bits: _typing.Final[int] = self.__get_leap_year_pattern_bits(leap_year_pattern)

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        # The number of days at the *start* of a month isn't affected by
        # the year as the only month length which varies by year is the last one.
        return self.__TOTAL_DAYS_BY_MONTH[month]

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from . import _YearMonthDay

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
                raise ValueError(f"Epoch {getattr(epoch, "name", epoch)} not recognised")


@_sealed
class _JulianYearMonthDayCalculator(_GJYearMonthDayCalculator):
    __AVERAGE_DAYS_PER_10_JULIAN_YEARS: _typing.Final[int] = 3653  # Ideally 365.25 per year

    def __init__(self) -> None:
        super().__init__(-9997, 9998, self.__AVERAGE_DAYS_PER_10_JULIAN_YEARS, -719164)

    def _is_leap_year(self, year: int) -> bool:
        return (year & 3) == 0

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Unix epoch is 1970-01-01 Gregorian which is 1969-12-19 Julian.
        # Calculate relative to the nearest leap year and account for the
        # difference later.

        relative_year = year - 1968
        if relative_year <= 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers.
            leap_years = (relative_year + 3) >> 2
        else:
            leap_years = relative_year >> 2
            # For post 1968 an adjustment is needed as jan1st is before leap day
            if not self._is_leap_year(year):
                leap_years += 1

        # Accounts for the difference between January 1st 1968 and December 19th 1969.
        return relative_year * 365 + leap_years - (366 + 352)


class _FixedMonthYearMonthDayCalculator(_RegularYearMonthDayCalculator, _abc.ABC):
    """Abstract implementation of a year/month/day calculator based around months which always have 30 days.

    As the month length is fixed various calculations can be optimised. This implementation assumes any additional days
    after twelve months fall into a thirteenth month.
    """

    __DAYS_IN_MONTH: _typing.Final[int] = 30

    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = 3653  # Ideally 365.25 days per year...

    def __init__(self, min_year: int, max_year: int, days_at_start_of_year_1: int) -> None:
        super().__init__(min_year, max_year, 13, self.__AVERAGE_DAYS_PER_10_YEARS, days_at_start_of_year_1)

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        # Just inline the arithmetic that would be done via various methods.
        return (
            self._get_start_of_year_in_days(year_month_day._year)
            + (year_month_day._month - 1) * self.__DAYS_IN_MONTH
            + (year_month_day._day - 1)
        )

    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        return (month - 1) * self.__DAYS_IN_MONTH

    def _is_leap_year(self, year: int) -> bool:
        return (year & 3) == 3

    def _get_days_in_year(self, year: int) -> int:
        return 366 if self._is_leap_year(year) else 365

    def _get_days_in_month(self, year: int, month: int) -> int:
        return self.__DAYS_IN_MONTH if month != 13 else 6 if self._is_leap_year(year) else 5

    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        from . import _YearMonthDay

        zero_based_day_of_year = day_of_year - 1
        month = _towards_zero_division(zero_based_day_of_year, self.__DAYS_IN_MONTH) + 1
        day = zero_based_day_of_year % self.__DAYS_IN_MONTH + 1
        return _YearMonthDay._ctor(year=year, month=month, day=day)


class _CopticYearMonthDayCalculator(_FixedMonthYearMonthDayCalculator):
    def __init__(self) -> None:
        super().__init__(1, 9715, -615558)

    def _calculate_start_of_year_days(self, year: int) -> int:
        # Unix epoch is 1970-01-01 Gregorian which is 1686-04-23 Coptic.
        # Calculate relative to the nearest leap year and account for the
        # difference later.

        relative_year = year - 1687
        leap_years: int
        if relative_year <= 0:
            # Add 3 before shifting right since /4 and >>2 behave differently
            # on negative numbers.
            leap_years = (relative_year + 3) >> 2
        else:
            leap_years = relative_year >> 2
            # For post 1687 an adjustment is needed as jan1st is before leap day
            if not self._is_leap_year(year):
                leap_years += 1

        ret: int = relative_year * 365 + leap_years

        # Adjust to account for difference between 1687-01-01 and 1686-04-23.
        return ret + (365 - 112)


class _PersianYearMonthDayCalculator(_RegularYearMonthDayCalculator, _abc.ABC):
    """Base class for the three variants of the Persian (Solar Hijri) calendar.

    Concrete subclasses are nested to allow different start dates and leap year calculations.

    The constructor uses IsLeapYear to precompute lots of data; it is therefore important that the implementation of
    IsLeapYear in subclasses uses no instance fields.
    """

    __DAYS_PER_NON_LEAP_YEAR: _typing.Final[int] = (31 * 6) + (30 * 5) + 29
    __DAYS_PER_LEAP_YEAR: _typing.Final[int] = __DAYS_PER_NON_LEAP_YEAR + 1
    # Approximation; it'll be pretty close in all variants.
    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = _towards_zero_division(
        (__DAYS_PER_NON_LEAP_YEAR * 25 + __DAYS_PER_LEAP_YEAR * 8) * 10, 33
    )
    _MAX_PERSIAN_YEAR: _typing.Final[int] = 9377

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
        self.__start_of_year_in_days_cache: _typing.Final[list[int]] = []
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
        from . import _YearMonthDay

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

    __LEAP_YEAR_PATTERN_BITS: _typing.Final[int] = (
        (1 << 1) | (1 << 5) | (1 << 9) | (1 << 13) | (1 << 17) | (1 << 22) | (1 << 26) | (1 << 30)
    )
    __LEAP_YEAR_CYCLE_LENGTH: _typing.Final[int] = 33

    # The ticks for the epoch of March 21st 622CE.
    __DAYS_AT_START_OF_YEAR_1_CONSTANT: _typing.Final[int] = -492268

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
    __astronomical_leap_year_bits: bytes = _base64.b64decode(
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


class _UmAlQuraYearMonthDayCalculator(_RegularYearMonthDayCalculator):
    """Implementation of the Um Al Qura calendar, using the tabular data in the BCL.

    This is fetched on construction and cached - we just need to know the length of each month of each year, which is
    cheap as the current implementation only covers 183 years.
    """

    __AVERAGE_DAYS_PER_10_YEARS: _typing.Final[int] = 3544

    # These four members are generated by UmAlQuraYearMonthDayCalculatorTest.GenerateData.
    __COMPUTED_MIN_YEAR: _typing.Final[int] = 1318
    __COMPUTED_MAX_YEAR: _typing.Final[int] = 1500
    __COMPUTED_DAYS_AT_START_OF_MIN_YEAR: _typing.Final[int] = -25448
    __GENERATED_DATA: _typing.Final[str] = (
        "AAAF1A3SHaQdSBqUFSwKbBVqG1QXSBaSFSYKVhSuCWwVagtUGqoaVBSsCVwSugXYDaoNVAqqCVYStgV0"
        + "CuoXZA7IDpIMqgVWCrYVtA2oHZIbJBpKFJoFWgraFtQWpBVKFJYJLhJuBWwK6hrUGqQVLBJaBLoJuhW0"
        + "C6gbUhqkFVQJrBNsBugO0g6kDUoKlhVWCrQVqhukG0gakhUqCloUugq0FaoNVA0qClYUrglcEuwK2Baq"
        + "FVQUqglaEroFtAuyG2QXSBaUFKoFagrqFtQXpBeIFxIVKgpaC1oW1A2oG5IbJBVMEqwFXAraBtQWqhVU"
        + "EpoJOhK6BXQLagtUGqoVNBJcBNwKuhW0DagNSgqWFS4KnBVcC1gXUhskFkoMlhlWCrQWqg2kHUoclBUq"
        + "CloVWgbYDrINpA0qCloUtgl0E3QHaBbSFqQVTAlsEtoF2A2yHWQaqBpUFKwJXBLaGtQWqBZSFSYKVhSu"
        + "CmwVag1UHSYAAA=="
    )

    __COMPUTED_DAYS_AT_START_OF_YEAR_1: _typing.Final[int] = __COMPUTED_DAYS_AT_START_OF_MIN_YEAR + (
        int(((1 - __COMPUTED_MIN_YEAR) / 10.0) * __AVERAGE_DAYS_PER_10_YEARS)
    )

    __MONTH_LENGTHS: _typing.ClassVar[dict[int, int]] = dict()
    __YEAR_LENGTHS: _typing.ClassVar[dict[int, int]] = dict()
    __YEAR_START_DAYS: _typing.ClassVar[dict[int, int]] = dict()

    @staticmethod
    def _ctor(
        generated_data: str,
        month_lengths: dict[int, int],
        year_lengths: dict[int, int],
        year_start_days: dict[int, int],
        computed_days_at_start_of_min_year: int,
    ) -> None:
        """Simulates the static constructor on the equivalent noda time class."""
        data = _base64.b64decode(generated_data)
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
        from . import _YearMonthDay

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


class IWeekYearRule(_typing.Protocol):
    def get_local_date(
        self,
        week_year: int,
        week_of_week_year: int,
        day_of_week: _IsoDayOfWeek,
        calendar: _CalendarSystem | None = None,
    ) -> _LocalDate:
        ...

    def get_week_year(self, date: _LocalDate) -> int:
        ...

    def get_week_of_week_year(self, date: _LocalDate) -> int:
        ...

    def get_weeks_in_week_year(self, week_year: int, calendar: _CalendarSystem | None = None) -> int:
        ...


class _WeekYearRulesMeta(type):
    @property
    def iso(cls) -> IWeekYearRule:
        from . import IsoDayOfWeek

        return _SimpleWeekYearRule(4, IsoDayOfWeek.MONDAY, False)


class CalendarWeekRule(_enum.IntEnum):
    FIRST_DAY = 0
    FIRST_FULL_WEEK = 1
    FIRST_FOUR_DAY_WEEK = 2


class WeekYearRules(metaclass=_WeekYearRulesMeta):
    """Factory methods to construct week-year rules supported by Noda Time."""

    @staticmethod
    def for_min_days_in_first_week(
        min_days_in_first_week: int, first_day_of_week: _IsoDayOfWeek | None = None
    ) -> IWeekYearRule:
        if first_day_of_week is None:
            from . import IsoDayOfWeek

            first_day_of_week = IsoDayOfWeek.MONDAY
        return _SimpleWeekYearRule(min_days_in_first_week, first_day_of_week, False)

    @staticmethod
    def from_calendar_week_rule(
        # TODO: We are using IsoDayOfWeek here, whereas Noda Time uses System.DayOfWeek from the bcl.
        #   I *think* it should be ok given that the argument in Noda Time is converted to IsoDayOfWeek.
        calendar_week_rule: CalendarWeekRule,
        first_day_of_week: _IsoDayOfWeek,
    ) -> IWeekYearRule:
        min_days_in_first_week: int
        match calendar_week_rule:
            case CalendarWeekRule.FIRST_DAY:
                min_days_in_first_week = 1
            case CalendarWeekRule.FIRST_FOUR_DAY_WEEK:
                min_days_in_first_week = 4
            case CalendarWeekRule.FIRST_FULL_WEEK:
                min_days_in_first_week = 7
            case _:
                raise ValueError(f"Unsupported CalendarWeekRule: {calendar_week_rule}")
        return _SimpleWeekYearRule(min_days_in_first_week, first_day_of_week, True)


@_sealed
@_typing.final
class _SimpleWeekYearRule(IWeekYearRule):
    def __init__(self, min_days_in_first_week: int, first_day_of_week: _IsoDayOfWeek, irregular_weeks: bool) -> None:
        # TODO: Preconditions.DebugCheckArgumentRange
        _Preconditions._check_argument_range("first_day_of_week", int(first_day_of_week), 1, 7)
        self.__min_days_in_first_week: _typing.Final[int] = min_days_in_first_week
        self.__first_day_of_week: _typing.Final[_IsoDayOfWeek] = first_day_of_week
        self.__irregular_weeks: _typing.Final[bool] = irregular_weeks

    def get_local_date(
        self,
        week_year: int,
        week_of_week_year: int,
        day_of_week: _IsoDayOfWeek,
        calendar: _CalendarSystem | None = None,
    ) -> _LocalDate:
        if calendar is None:
            from . import CalendarSystem

            calendar = CalendarSystem.iso
        _Preconditions._check_not_null(calendar, "calendar")
        self.__validate_week_year(week_year, calendar)

        # The actual message for this won't be ideal, but it's clear enough.
        _Preconditions._check_argument_range("day_of_week", int(day_of_week), 1, 7)

        year_month_day_calculator = calendar._year_month_day_calculator
        max_weeks = self.get_weeks_in_week_year(week_year, calendar)
        if week_of_week_year < 1 or week_of_week_year > max_weeks:
            # TODO: ArgumentOutOfRangeException
            raise ValueError(f"week_of_week_year {week_of_week_year} is out of range (1, {max_weeks})")

        # TODO: unchecked
        start_of_week_year = self.__get_week_year_days_since_epoch(year_month_day_calculator, week_year)
        # 0 for "already on the first day of the week" up to 6 "it's the last day of the week".
        days_into_week = ((day_of_week - self.__first_day_of_week) + 7) % 7
        days = start_of_week_year + (week_of_week_year - 1) * 7 + days_into_week
        if days < calendar._min_days or days > calendar._max_days:
            # TODO: ArgumentOutOfRangeException
            raise ValueError("The combination of week_year, week_of_week_year and day_of_week is invalid")
        from . import LocalDate

        ret = LocalDate._ctor(
            year_month_day_calendar=year_month_day_calculator._get_year_month_day(days_since_epoch=days)._with_calendar(
                calendar
            )
        )

        # For rules with irregular weeks, the calculation so far may end up computing a date which isn't
        # in the right week-year. This will happen if the caller has specified a "short" week (i.e. one
        # at the start or end of the week-year which is not seven days long due to the week year changing
        # part way through a week) and a day-of-week which corresponds to the "missing" part of the week.
        # Examples are in SimpleWeekYearRuleTest.GetLocalDate_Invalid.
        # The simplest way to find out is just to check what the week year is, but we only need to do
        # the full check if the requested week-year is different to the calendar year of the result.
        # We don't need to check for this in regular rules, because the computation we've already performed
        # will always be right.
        if self.__irregular_weeks and week_year != ret.year:
            if self.get_week_year(ret) != week_year:
                # TODO: ArgumentOutOfRangeException
                raise ValueError("The combination of week_year, week_of_week_year and day_of_week is invalid")
        return ret

    def get_week_of_week_year(self, date: _LocalDate) -> int:
        year_month_day = date._year_month_day
        year_month_day_calculator = date.calendar._year_month_day_calculator
        # This is a bit inefficient, as we'll be converting forms several times. However, it's
        # understandable... we might want to optimize in the future if it's reported as a bottleneck.
        week_year = self.get_week_year(date)
        # Even if this is before the *real* start of the week year due to the rule
        # having short weeks, that doesn't change the week-of-week-year, as we've definitely
        # got the right week-year to start with.
        start_of_week_year = self.__get_week_year_days_since_epoch(year_month_day_calculator, week_year)
        days_since_epoch = year_month_day_calculator._get_days_since_epoch(year_month_day)
        zero_based_day_of_week_year = days_since_epoch - start_of_week_year
        zero_based_week = _towards_zero_division(zero_based_day_of_week_year, 7)
        return zero_based_week + 1

    def get_weeks_in_week_year(self, week_year: int, calendar: _CalendarSystem | None = None) -> int:
        if calendar is None:
            from . import CalendarSystem

            calendar = CalendarSystem.iso
        _Preconditions._check_not_null(calendar, "calendar")
        year_month_day_calculator = calendar._year_month_day_calculator
        self.__validate_week_year(week_year, calendar)
        # TODO: unchecked
        start_of_week_year = self.__get_week_year_days_since_epoch(year_month_day_calculator, week_year)
        start_of_calendar_year = year_month_day_calculator._get_start_of_year_in_days(week_year)
        # The number of days gained or lost in the week year compared with the calendar year.
        # So if the week year starts on December 31st of the previous calendar year, this will be +1.
        # If the week year starts on January 2nd of this calendar year, this will be -1.
        extra_days_at_start = start_of_calendar_year - start_of_week_year

        # At the end of the year, we may have some extra days too.
        # In a non-regular rule, we just round up, so assume we effectively have 6 extra days.
        # In a regular rule, there can be at most minDaysInFirstWeek - 1 days "borrowed"
        # from the following year - because if there were any more, those days would be in the
        # the following year instead.
        extra_days_at_end = 6 if self.__irregular_weeks else self.__min_days_in_first_week - 1

        days_in_this_year = year_month_day_calculator._get_days_in_year(week_year)

        # We can have up to "minDaysInFirstWeek - 1" days of the next year, too.
        return _towards_zero_division((days_in_this_year + extra_days_at_start + extra_days_at_end), 7)

    def get_week_year(self, date: _LocalDate) -> int:
        year_month_day = date._year_month_day
        year_month_day_calculator = date.calendar._year_month_day_calculator
        # TODO: unchecked
        # Let's guess that it's in the same week year as calendar year, and check that.
        calendar_year = year_month_day._year
        start_of_week_year = self.__get_week_year_days_since_epoch(year_month_day_calculator, calendar_year)
        days_since_epoch = year_month_day_calculator._get_days_since_epoch(year_month_day)
        if days_since_epoch < start_of_week_year:
            # No, the week-year hadn't started yet. For example, we've been given January 1st 2011...
            # and the first week of week-year 2011 starts on January 3rd 2011. Therefore the date
            # must belong to the last week of the previous week-year.
            return calendar_year - 1

        # By now, we know it's either calendarYear or calendarYear + 1.

        # In irregular rules, a day can belong to the *previous* week year, but never the *next* week year.
        # So at this point, we're done.
        if self.__irregular_weeks:
            return calendar_year

        # Otherwise, check using the number of
        # weeks in the year. Note that this will fetch the start of the calendar year and the week year
        # again, so could be optimized by copying some logic here - but only when we find we need to.
        weeks_in_week_year = self.get_weeks_in_week_year(calendar_year, date.calendar)

        # We assume that even for the maximum year, we've got just about enough leeway to get to the
        # start of the week year. (If not, we should adjust the maximum.)
        start_of_next_week_year = start_of_week_year + weeks_in_week_year * 7
        return calendar_year if days_since_epoch < start_of_next_week_year else calendar_year + 1

    def __validate_week_year(self, week_year: int, calendar: _CalendarSystem) -> None:
        """Validate that at least one day in the calendar falls in the given week year."""
        if calendar.min_year < week_year < calendar.max_year:
            return
        min_calendar_year_days = self.__get_week_year_days_since_epoch(
            calendar._year_month_day_calculator, calendar.min_year
        )
        # If week year X started after calendar year X, then the first days of the calendar year are in the
        # previous week year.
        min_week_year = calendar.min_year - 1 if min_calendar_year_days > calendar._min_days else calendar.min_year
        max_calendar_year_days = self.__get_week_year_days_since_epoch(
            calendar._year_month_day_calculator, calendar.max_year + 1
        )
        # If week year X + 1 started after the last day in the calendar, then everything is within week year X.
        # For irregular rules, we always just use calendar.MaxYear.
        max_week_year = (
            calendar.max_year
            if self.__irregular_weeks or max_calendar_year_days > calendar._max_days
            else calendar.max_year + 1
        )
        _Preconditions._check_argument_range("week_year", week_year, min_week_year, max_week_year)

    def __get_week_year_days_since_epoch(
        self, year_month_day_calculator: _YearMonthDayCalculator, week_year: int
    ) -> int:
        """Returns the days at the start of the given week-year.

        The week-year may be 1 higher or lower than the max/min calendar year. For non-regular rules (i.e. where some
        weeks can be short) it returns the day when the week-year *would* have started if it were regular. So this
        *always* returns a date on firstDayOfWeek.
        """

        # TODO: unchecked

        # Need to be slightly careful here, as the week-year can reasonably be (just) outside the calendar year range.
        # However, YearMonthDayCalculator.GetStartOfYearInDays already handles min/max -/+ 1.
        start_of_calendar_year = year_month_day_calculator._get_start_of_year_in_days(week_year)
        start_of_year_day_of_week = (
            1 + ((start_of_calendar_year + 3) % 7)
            if start_of_calendar_year >= -3
            else 7 + ((start_of_calendar_year + 4) % 7)
        )

        # How many days have there been from the start of the week containing
        # the first day of the year, until the first day of the year? To put it another
        # way, how many days in the week *containing* the start of the calendar year were
        # in the previous calendar year.
        # (For example, if the start of the calendar year is Friday and the first day of the week is Monday,
        # this will be 4.)
        days_into_week = ((start_of_year_day_of_week - self.__first_day_of_week) + 7) % 7
        start_of_week_containing_start_of_calendar_year = start_of_calendar_year - days_into_week

        start_of_year_is_in_week_1 = 7 - days_into_week >= self.__min_days_in_first_week
        return (
            start_of_week_containing_start_of_calendar_year
            if start_of_year_is_in_week_1
            else start_of_week_containing_start_of_calendar_year + 7
        )
