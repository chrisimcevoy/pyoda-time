__all__: list[str] = []

import abc as _abc
import typing as _typing

from pyoda_time import LocalDate as _LocalDate
from pyoda_time.utility import _Preconditions, _sealed


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

    # TODO: DaysField
    # TODO: WeeksField
    _months_field: _typing.Final[_IDatePeriodField] = _MonthsPeriodField()
    _years_field: _typing.Final[_IDatePeriodField] = _YearsPeriodField()
