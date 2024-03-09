# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from .._year_month_day import _YearMonthDay
from ..utility import _Preconditions, _towards_zero_division
from ._year_start_cache_entry import _YearStartCacheEntry


class _YearMonthDayCalculator(abc.ABC):
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
        self.__year_cache: typing.Final[dict[int, _YearStartCacheEntry]] = _YearStartCacheEntry._create_cache()

    # region Abstract methods

    @abc.abstractmethod
    def _get_days_from_start_of_year_to_start_of_month(self, year: int, month: int) -> int:
        """Returns the number of days from the start of the given year to the start of the given month."""
        raise NotImplementedError

    @abc.abstractmethod
    def _calculate_start_of_year_days(self, year: int) -> int:
        """Compute the start of the given year in days since 1970-01-01 ISO.

        The year may be outside the bounds advertised by the calendar, but only by a single year. This method is only
        called by get_start_of_year_in_days (unless the calendar chooses to call it itself), so calendars which override
        that method and don't call the original implementation may leave this unimplemented (e.g. by throwing an
        exception if it's ever called).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_months_in_year(self, year: int) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_days_in_month(self, year: int, month: int) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def _is_leap_year(self, year: int) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _add_months(self, year_month_day: _YearMonthDay, months: int) -> _YearMonthDay:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_year_month_day_from_year_and_day_of_year(self, year: int, day_of_year: int) -> _YearMonthDay:
        """This is supposed to be an abstract overload of YearMonthDayCalendar.GetYearMonthDay.

        In Python, we can't quite do that, so this method has a different name. The signature in C# is:     `abstract
        YearMonthDay GetYearMonthDay([Trusted] int year, [Trusted] int dayOfYear);`
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_days_in_year(self, year: int) -> int:
        """Returns the number of days in the given year, which will always be within 1 year of the valid range for the
        calculator."""
        raise NotImplementedError

    @abc.abstractmethod
    def _months_between(self, start: _YearMonthDay, end: _YearMonthDay) -> int:
        """Find the months between ``start`` and ``end``.

        (If start is earlier than end, the result will be non-negative.)
        """
        raise NotImplementedError

    @abc.abstractmethod
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

    @typing.overload
    def _get_year_month_day(self, *, year: int, day_of_year: int) -> _YearMonthDay: ...

    @typing.overload
    def _get_year_month_day(self, *, days_since_epoch: int) -> _YearMonthDay: ...

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
