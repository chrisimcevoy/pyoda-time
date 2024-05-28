# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Callable, final

from ._iso_day_of_week import IsoDayOfWeek
from ._local_date import LocalDate
from ._period import Period
from .utility._csharp_compatibility import _private, _sealed
from .utility._preconditions import _Preconditions


class __DateAdjustersMeta(type):
    @property
    def start_of_month(self) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the first day of the current month.

        :return: A date adjuster to move to the first day of the current month.
        """
        return lambda date: LocalDate(date.year, date.month, 1, date.calendar)

    @property
    def end_of_month(self) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the last day of the current month.

        :return: A date adjuster to move to the last day of the current month.
        """
        return lambda date: LocalDate(
            year=date.year,
            month=date.month,
            day=date.calendar.get_days_in_month(date.year, date.month),
            calendar=date.calendar,
        )


@final
@_sealed
@_private
class DateAdjusters(metaclass=__DateAdjustersMeta):
    """Factory class for date adjusters: functions from ``LocalDate`` to ``LocalDate``,
    which can be applied to ``LocalDate``, ``LocalDateTime``, and ``OffsetDateTime``.
    """

    @staticmethod
    def day_of_month(day: int) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the specified day of the current month.

        The returned adjuster will throw an exception if it is applied to a date that would create an invalid result.

        :param day: The day of month to adjust dates to.
        :return: An adjuster which changes the day to ``day`` retaining the same year and month.
        """
        return lambda date: LocalDate(date.year, date.month, day, date.calendar)

    @staticmethod
    def month(month: int) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the same day of the specified month.

        The returned adjuster will throw an exception if it is applied to a date that would create an invalid result.

        :param month: The month to adjust dates to.
        :return: An adjuster which changes the month to ``month`` retaining the same year and day of month.
        """
        return lambda date: LocalDate(date.year, month, date.day, date.calendar)

    @staticmethod
    def next_or_same(day_of_week: IsoDayOfWeek) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the next specified day-of-week, but return the original date if the day is already
        correct.

        :param day_of_week: The day-of-week to adjust dates to.
        :return: An adjuster which advances a date to the next occurrence of the specified day-of-week, or the original
            date if the day is already correct.
        """
        if day_of_week < IsoDayOfWeek.MONDAY or day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(f"day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]")
        return lambda date: date if date.day_of_week == day_of_week else date.next(day_of_week)

    @staticmethod
    def previous_or_same(day_of_week: IsoDayOfWeek) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the previous specified day-of-week, but return the original date if the day is
        already correct.

        :param day_of_week: The day-of-week to adjust dates to.
        :return: An adjuster which advances a date to the previous occurrence of the specified day-of-week, or the
            original date if the day is already correct.
        """
        if day_of_week < IsoDayOfWeek.MONDAY or day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(f"day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]")
        return lambda date: date if date.day_of_week == day_of_week else date.previous(day_of_week)

    @staticmethod
    def next(day_of_week: IsoDayOfWeek) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the next specified day-of-week, adding a week if the day is already correct.

        This is the adjuster equivalent of ``LocalDate.next``.

        :param day_of_week: The day-of-week to adjust dates to.
        :return: An adjuster which advances a date to the next occurrence of the specified day-of-week.
        """
        if day_of_week < IsoDayOfWeek.MONDAY or day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(f"day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]")
        return lambda date: date.next(day_of_week)

    @staticmethod
    def previous(day_of_week: IsoDayOfWeek) -> Callable[[LocalDate], LocalDate]:
        """A date adjuster to move to the previous specified day-of-week, subtracting a week if the day is already
        correct.

        This is the adjuster equivalent of ``LocalDate.previous``.

        :param day_of_week: The day-of-week to adjust dates to.
        :return: An adjuster which advances a date to the previous occurrence of the specified day-of-week.
        """
        if day_of_week < IsoDayOfWeek.MONDAY or day_of_week > IsoDayOfWeek.SUNDAY:
            raise ValueError(f"day_of_week must be in the range [{IsoDayOfWeek.MONDAY} to {IsoDayOfWeek.SUNDAY}]")
        return lambda date: date.previous(day_of_week)

    @staticmethod
    def add_period(period: Period) -> Callable[[LocalDate], LocalDate]:
        """Creates a date adjuster to add the specified period to the date.

        This is the adjuster equivalent of ``LocalDate.plus(Period)``.

        :param period: The period to add when the adjuster is invoked. Must not contain any (non-zero) time units.
        :return: An adjuster which adds the specified period.
        """
        _Preconditions._check_not_null(period, "period")
        # Perform this validation eagerly. It will be performed on each invocation as well,
        # but it's good to throw an exception now rather than waiting for the first invocation.
        _Preconditions._check_argument(
            not period.has_time_component, "period", "Cannot add a period with a time component to a date"
        )
        return lambda date: date + period
