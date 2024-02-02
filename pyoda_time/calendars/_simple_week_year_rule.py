# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

if _typing.TYPE_CHECKING:
    from .._calendar_system import CalendarSystem as _CalendarSystem
    from .._local_date import LocalDate as _LocalDate
from .._iso_day_of_week import IsoDayOfWeek as _IsoDayOfWeek
from ..utility import _Preconditions, _sealed, _towards_zero_division
from ._hebrew_year_month_day_calculator import _YearMonthDayCalculator
from ._i_week_year_rule import IWeekYearRule


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
            from .. import CalendarSystem

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
        from .. import LocalDate

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
            from .. import CalendarSystem

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
