from __future__ import annotations as _annotations

__all__: list[str] = []

import abc as _abc
import typing as _typing

from pyoda_time import Duration as _Duration
from pyoda_time import (
    LocalDate as _LocalDate,
)
from pyoda_time import (
    LocalDateTime as _LocalDateTime,
)
from pyoda_time import (
    LocalTime as _LocalTime,
)
from pyoda_time import (
    PyodaConstants as _PyodaConstants,
)
from pyoda_time import (
    _YearMonthDayCalendar,
)
from pyoda_time.utility import _csharp_modulo, _Preconditions, _sealed, _towards_zero_division


class _IDatePeriodField:
    """General representation of the difference between two dates in a particular time unit, such as "days" or
    "months"."""

    @_abc.abstractmethod
    def add(self, local_date: _LocalDate, value: int) -> _LocalDate:
        """Adds a duration value (which may be negative) to the date. This may not be reversible; for example, adding a
        month to January 30th will result in February 28th or February 29th.

        :param local_date: The local date to add to.
        :param value: The value to add, in the units of the field.
        :return: The updated local date.
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def units_between(self, start: _LocalDate, end: _LocalDate) -> int:
        """Computes the difference between two local dates, as measured in the units of this field, rounding towards
        zero. This rounding means that unit.Add(start, unit.UnitsBetween(start, end)) always ends up with a date between
        start and end. (Ideally equal to end, but importantly, it never overshoots.)

        :param start: The start date.
        :param end: The end date.
        :return: The difference in the units of this field.
        """
        raise NotImplementedError


@_sealed
@_typing.final
class _FixedLengthDatePeriodField(_IDatePeriodField):
    """Date period field for fixed-length periods (weeks and days)."""

    def __init__(self, unit_days: int) -> None:
        self.__unit_days = unit_days

    def add(self, local_date: _LocalDate, value: int) -> _LocalDate:
        if value == 0:
            return local_date
        days_to_add = value * self.__unit_days
        calendar = local_date.calendar
        # If we know it will be in this year, next year, or the previous year...
        if 300 > days_to_add > -300:
            calculator = calendar._year_month_day_calculator
            year_month_day = local_date._year_month_day
            year = local_date.year
            month = local_date.month
            day = local_date.day
            new_day_of_month = day + days_to_add
            if 1 <= new_day_of_month <= calculator._get_days_in_month(year, month):
                return _LocalDate._ctor(
                    year_month_day_calendar=_YearMonthDayCalendar._ctor(
                        year=year, month=month, day=new_day_of_month, calendar_ordinal=calendar._ordinal
                    )
                )
            day_of_year = calculator._get_day_of_year(year_month_day)
            new_day_of_year = day_of_year + days_to_add

            if new_day_of_year < 1:
                new_day_of_year += calculator._get_days_in_year(year - 1)
                year -= 1
                if year < calculator._min_year:
                    raise OverflowError("Date computation would underflow the minimum year of the calendar")
            else:
                days_in_year = calculator._get_days_in_year(year)
                if new_day_of_year > days_in_year:
                    new_day_of_year -= days_in_year
                    year += 1
                    if year > calculator._max_year:
                        raise OverflowError("Date computation would overflow the maximum year of the calendar")
            return _LocalDate._ctor(
                year_month_day_calendar=calculator._get_year_month_day(
                    year=year, day_of_year=new_day_of_year
                )._with_calendar_ordinal(calendar._ordinal)
            )
        # LocalDate constructor will validate
        days = local_date._days_since_epoch + days_to_add
        return _LocalDate._ctor(days_since_epoch=days, calendar=calendar)

    def units_between(self, start: _LocalDate, end: _LocalDate) -> int:
        from . import Period

        return _towards_zero_division(Period._internal_days_between(start, end), self.__unit_days)


@_sealed
@_typing.final
class _MonthsPeriodField(_IDatePeriodField):
    def add(self, local_date: _LocalDate, value: int) -> _LocalDate:
        from pyoda_time import LocalDate

        calendar = local_date.calendar
        calculator = calendar._year_month_day_calculator
        year_month_day = calculator._add_months(local_date._year_month_day, value)
        return LocalDate._ctor(year_month_day_calendar=year_month_day._with_calendar(calendar))

    def units_between(self, start: _LocalDate, end: _LocalDate) -> int:
        return start.calendar._year_month_day_calculator._months_between(start._year_month_day, end._year_month_day)


@_sealed
class _YearsPeriodField(_IDatePeriodField):
    def add(self, local_date: _LocalDate, value: int) -> _LocalDate:
        from pyoda_time import LocalDate

        if value == 0:
            return local_date
        year_month_day = local_date._year_month_day
        calendar = local_date.calendar
        calculator = calendar._year_month_day_calculator
        current_year = year_month_day._year
        # Adjust argument range based on current year
        _Preconditions._check_argument_range(
            "value", value, calculator._min_year - current_year, calculator._max_year - current_year
        )
        return LocalDate._ctor(
            year_month_day_calendar=calculator._set_year(year_month_day, current_year + value)._with_calendar_ordinal(
                calendar._ordinal
            )
        )

    def units_between(self, start: _LocalDate, end: _LocalDate) -> int:
        diff: int = end.year - start.year

        # If we just add the difference in years to subtrahendInstant, what do we get?
        simple_addition = self.add(start, diff)

        if start <= end:
            # Moving forward: if the result of the simple addition is before or equal to the end,
            # we're done. Otherwise, rewind a year because we've overshot.
            return diff if simple_addition <= end else diff - 1
        else:
            # Moving backward: if the result of the simple addition (of a non-positive number)
            # is after or equal to the end, we're done. Otherwise, increment by a year because
            # we've overshot backwards.
            return diff if simple_addition >= end else diff + 1


class _DatePeriodFields:
    """All the period fields."""

    _days_field: _typing.Final[_IDatePeriodField] = _FixedLengthDatePeriodField(1)
    _weeks_field: _typing.Final[_IDatePeriodField] = _FixedLengthDatePeriodField(7)
    _months_field: _typing.Final[_IDatePeriodField] = _MonthsPeriodField()
    _years_field: _typing.Final[_IDatePeriodField] = _YearsPeriodField()


class _TimePeriodFieldMeta(type):
    @property
    def _nanoseconds(cls) -> _TimePeriodField:
        return _TimePeriodField(1)

    @property
    def _ticks(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_TICK)

    @property
    def _milliseconds(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_MILLISECOND)

    @property
    def _seconds(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_SECOND)

    @property
    def _minutes(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_MINUTE)

    @property
    def _hours(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_HOUR)


class _TimePeriodField(metaclass=_TimePeriodFieldMeta):
    def __init__(self, unit_nanoseconds: int) -> None:
        self.__unit_nanoseconds = unit_nanoseconds
        self.__units_per_day = int(_PyodaConstants.NANOSECONDS_PER_DAY / unit_nanoseconds)

    def _add_local_date_time(self, start: _LocalDateTime, units: int) -> _LocalDateTime:
        time, extra_days = self._add_local_time_with_extra_days(start.time_of_day, units)
        date = start.date if extra_days == 0 else start.date.plus_days(extra_days)
        return _LocalDateTime._ctor(local_date=date, local_time=time)

    # TODO: def _add_local_time(self, local_time: _LocalTime, value: int) -> _LocalTime:

    def _add_local_time_with_extra_days(self, local_time: _LocalTime, value: int) -> tuple[_LocalTime, int]:
        extra_days = 0
        # TODO: unchecked
        if value == 0:
            return local_time, extra_days
        days = 0
        # It's possible that there are better ways to do this, but this at least feels simple.
        if value >= 0:
            if value >= self.__units_per_day:
                # TODO: checked
                # If this overflows, that's fine. (An OverflowException is a reasonable outcome.)
                # days = checked((int) longDays);
                value = _csharp_modulo(value, self.__units_per_day)
            nanos_to_add = value * self.__unit_nanoseconds
            new_nanos = local_time.nanosecond_of_day + nanos_to_add
            if new_nanos >= _PyodaConstants.NANOSECONDS_PER_DAY:
                new_nanos -= _PyodaConstants.NANOSECONDS_PER_DAY
                # TODO: checked
                days += 1
            # TODO: checked
            extra_days += days
            return _LocalTime._ctor(nanoseconds=new_nanos), extra_days
        else:
            if value <= self.__units_per_day:
                long_days = _towards_zero_division(value, self.__units_per_day)  # noqa
                # TODO: checked
                # If this overflows, that's fine. (An OverflowException is a reasonable outcome.)
                # days = checked((int) longDays);
                value = _csharp_modulo(value, self.__units_per_day)
            nanos_to_add = value * self.__unit_nanoseconds
            new_nanos = local_time.nanosecond_of_day + nanos_to_add
            if new_nanos < 0:
                new_nanos += _PyodaConstants.NANOSECONDS_PER_DAY
                # TODO: checked
                days -= 1
            # TODO: checked
            extra_days += days
            return _LocalTime._ctor(nanoseconds=new_nanos), extra_days

    def _units_between(self, start: _LocalDateTime, end: _LocalDateTime) -> int:
        start_local_instant = start._to_local_instant()
        end_local_instant = end._to_local_instant()
        duration = end_local_instant._time_since_local_epoch - start_local_instant._time_since_local_epoch
        return self._get_units_in_duration(duration)

    def _get_units_in_duration(self, duration: _Duration) -> int:
        return _towards_zero_division(duration.to_nanoseconds(), self.__unit_nanoseconds)
