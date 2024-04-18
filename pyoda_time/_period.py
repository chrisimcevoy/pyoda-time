# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, final, overload

from ._period_units import PeriodUnits
from ._pyoda_constants import PyodaConstants
from .fields._time_period_field import _TimePeriodField
from .utility._csharp_compatibility import _csharp_modulo, _private, _sealed, _towards_zero_division
from .utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from . import Duration, LocalDate, LocalDateTime, LocalTime, PeriodBuilder, YearMonth

__all__ = ["Period"]


class _PeriodMeta(type):
    @property
    @functools.cache
    def zero(cls) -> Period:
        """A period containing only zero-valued properties."""
        return Period._ctor()


@_sealed
@final
@_private
class Period(metaclass=_PeriodMeta):
    # TODO: public static IEqualityComparer<Period?> NormalizingEqualityComparer

    @property
    def nanoseconds(self) -> int:
        """The number of nanoseconds within this period."""
        return self.__nanoseconds

    @property
    def ticks(self) -> int:
        """The number of ticks within this period."""
        return self.__ticks

    @property
    def milliseconds(self) -> int:
        """The number of milliseconds within this period."""
        return self.__milliseconds

    @property
    def seconds(self) -> int:
        """The number of seconds within this period."""
        return self.__seconds

    @property
    def minutes(self) -> int:
        """The number of minutes within this period."""
        return self.__minutes

    @property
    def hours(self) -> int:
        """The number of hours within this period."""
        return self.__hours

    @property
    def days(self) -> int:
        """The number of days within this period."""
        return self.__days

    @property
    def weeks(self) -> int:
        """The number of weeks within this period."""
        return self.__weeks

    @property
    def months(self) -> int:
        """The number of months within this period."""
        return self.__months

    @property
    def years(self) -> int:
        """The number of years within this period."""
        return self.__years

    __years: int
    __months: int
    __weeks: int
    __days: int
    __hours: int
    __minutes: int
    __seconds: int
    __milliseconds: int
    __ticks: int
    __nanoseconds: int

    @classmethod
    def _ctor(
        cls,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        ticks: int = 0,
        nanoseconds: int = 0,
    ) -> Period:
        """Creates a new period from the given values.

        In Pyoda Time, this constructor emulates both the internal and the two private constructors in Noda Time.
        """
        self = super().__new__(cls)
        self.__years = years
        self.__months = months
        self.__weeks = weeks
        self.__days = days
        self.__hours = hours
        self.__minutes = minutes
        self.__seconds = seconds
        self.__milliseconds = milliseconds
        self.__ticks = ticks
        self.__nanoseconds = nanoseconds
        return self

    @classmethod
    def from_years(cls, years: int) -> Period:
        """Creates a period representing the specified number of years.

        :param years: The number of years in the new period
        :return: A period consisting of the given number of years.
        """
        return Period._ctor(years=years)

    @classmethod
    def from_months(cls, months: int) -> Period:
        """Creates a period representing the specified number of months.

        :param months: The number of months in the new period
        :return: A period consisting of the given number of months.
        """
        return Period._ctor(months=months)

    @classmethod
    def from_weeks(cls, weeks: int) -> Period:
        """Creates a period representing the specified number of weeks.

        :param weeks: The number of weeks in the new period
        :return: A period consisting of the given number of weeks.
        """
        return Period._ctor(weeks=weeks)

    @classmethod
    def from_days(cls, days: int) -> Period:
        """Creates a period representing the specified number of days.

        :param days: The number of days in the new period
        :return: A period consisting of the given number of days.
        """
        return Period._ctor(days=days)

    @classmethod
    def from_hours(cls, hours: int) -> Period:
        """Creates a period representing the specified number of hours.

        :param hours: The number of hours in the new period
        :return: A period consisting of the given number of hours.
        """
        return Period._ctor(hours=hours)

    @classmethod
    def from_minutes(cls, minutes: int) -> Period:
        """Creates a period representing the specified number of minutes.

        :param minutes: The number of minutes in the new period
        :return: A period consisting of the given number of minutes.
        """
        return Period._ctor(minutes=minutes)

    @classmethod
    def from_seconds(cls, seconds: int) -> Period:
        """Creates a period representing the specified number of seconds.

        :param seconds: The number of seconds in the new period
        :return: A period consisting of the given number of seconds.
        """
        return Period._ctor(seconds=seconds)

    @classmethod
    def from_milliseconds(cls, milliseconds: int) -> Period:
        """Creates a period representing the specified number of milliseconds.

        :param milliseconds: The number of milliseconds in the new period
        :return: A period consisting of the given number of milliseconds.
        """
        return Period._ctor(milliseconds=milliseconds)

    @classmethod
    def from_ticks(cls, ticks: int) -> Period:
        """Creates a period representing the specified number of ticks.

        :param ticks: The number of ticks in the new period
        :return: A period consisting of the given number of ticks.
        """
        return Period._ctor(ticks=ticks)

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int) -> Period:
        """Creates a period representing the specified number of nanoseconds.

        :param nanoseconds: The number of nanoseconds in the new period
        :return: A period consisting of the given number of nanoseconds.
        """
        return Period._ctor(nanoseconds=nanoseconds)

    def __add__(self, other: Period) -> Period:
        if isinstance(other, Period):
            return Period._ctor(
                years=self.years + other.years,
                months=self.months + other.months,
                weeks=self.weeks + other.weeks,
                days=self.days + other.days,
                hours=self.hours + other.hours,
                minutes=self.minutes + other.minutes,
                seconds=self.seconds + other.seconds,
                milliseconds=self.milliseconds + other.milliseconds,
                ticks=self.ticks + other.ticks,
                nanoseconds=self.nanoseconds + other.nanoseconds,
            )
        return NotImplemented  # type: ignore[unreachable]

    def add(self, other: Period) -> Period:
        """Return the sum of the two periods.

        The units of the result will be the union of those in both periods.
        """
        return self + other

    # TODO def create_comparer

    def __sub__(self, other: Period) -> Period:
        if isinstance(other, Period):
            return Period._ctor(
                years=self.years - other.years,
                months=self.months - other.months,
                weeks=self.weeks - other.weeks,
                days=self.days - other.days,
                hours=self.hours - other.hours,
                minutes=self.minutes - other.minutes,
                seconds=self.seconds - other.seconds,
                milliseconds=self.milliseconds - other.milliseconds,
                ticks=self.ticks - other.ticks,
                nanoseconds=self.nanoseconds - other.nanoseconds,
            )
        return NotImplemented  # type: ignore[unreachable]

    def subtract(self, other: Period) -> Period:
        """Subtracts one period from another, by simply subtracting each property value.

        The units of the result will be the union of both periods, even if the subtraction caused some properties to
        become zero (so "2 weeks, 1 days" minus "2 weeks" is "zero weeks, 1 days", not "1 days").

        :param other: The period to subtract this one.
        :return: The result of subtracting all the values in the second operand from the values in the first.
        """
        return self - other

    @classmethod
    def days_between(cls, start: LocalDate, end: LocalDate) -> int:
        """Returns the number of days between two ``LocalDate`` objects.

        :param start: Start date/time
        :param end: End date/time
        :return: The number of days between the given dates.
        """
        _Preconditions._check_argument(
            start.calendar == end.calendar, "end", "start and end must use the same calendar system"
        )
        return cls._internal_days_between(start, end)

    @classmethod
    @overload
    def between(
        cls, start: LocalDateTime, end: LocalDateTime, units: PeriodUnits = PeriodUnits.DATE_AND_TIME
    ) -> Period: ...

    @classmethod
    @overload
    def between(cls, start: LocalDate, end: LocalDate, units: PeriodUnits = PeriodUnits.YEAR_MONTH_DAY) -> Period: ...

    @classmethod
    @overload
    def between(cls, start: LocalTime, end: LocalTime, units: PeriodUnits = PeriodUnits.ALL_TIME_UNITS) -> Period: ...

    @classmethod
    @overload
    def between(
        cls, start: YearMonth, end: YearMonth, units: PeriodUnits = PeriodUnits.YEARS | PeriodUnits.MONTHS
    ) -> Period: ...

    @classmethod
    def between(
        cls,
        start: LocalDateTime | LocalDate | LocalTime | YearMonth,
        end: LocalDateTime | LocalDate | LocalTime | YearMonth,
        units: PeriodUnits | None = None,
    ) -> Period:
        """Returns the period between a start and an end date/time, using only the given units.

        If ``end`` is before ``start``, each property in the returned period
        will be negative. If the given set of units cannot exactly reach the end point (e.g. finding
        the difference between 1am and 3:15am in hours) the result will be such that adding it to ``start``
        will give a value between ``start`` and ``end``. In other words,
        any rounding is "towards start"; this is true whether the resulting period is negative or positive.

        :param start: Start date/time
        :param end: End date/time
        :param units: Units to use for calculations
        :return: The period between the given date/times, using the given units.
        """
        from . import YearMonth
        from ._calendar_system import CalendarSystem
        from ._local_date import LocalDate
        from ._local_date_time import LocalDateTime
        from ._local_time import LocalTime
        from .fields._date_period_fields import _DatePeriodFields

        # public static Period Between(LocalDateTime start, LocalDateTime end, PeriodUnits units)
        if isinstance(start, LocalDateTime) and isinstance(end, LocalDateTime):
            if units is None:
                units = PeriodUnits.DATE_AND_TIME

            _Preconditions._check_argument(units != PeriodUnits.NONE, "units", "Units must not be empty")
            _Preconditions._check_argument(
                (units & ~PeriodUnits.ALL_UNITS) == PeriodUnits.NONE,
                "units",
                f"Units contains an unknown value: {units}",
            )
            calendar: CalendarSystem = start.calendar
            _Preconditions._check_argument(
                calendar == end.calendar, "end", "start and end must use the same calendar system"
            )

            if start == end:
                return cls.zero

            # Adjust for situations like "days between 5th January 10am and 7th January 5am" which should be one
            # day, because if we actually reach 7th January with date fields, we've overshot.
            # The date adjustment will always be valid, because it's just moving it towards start.
            # We need this for all date-based period fields. We could potentially optimize by not doing this
            # in cases where we've only got time fields...
            end_date = end.date
            if start < end:
                if start.time_of_day > end.time_of_day:
                    end_date = end_date.plus_days(-1)
            elif start > end and start.time_of_day < end.time_of_day:
                end_date = end_date.plus_days(1)

            # Optimization for single field
            match units:
                case PeriodUnits.YEARS:
                    return cls.from_years(_DatePeriodFields._years_field.units_between(start.date, end_date))
                case PeriodUnits.MONTHS:
                    return cls.from_months(_DatePeriodFields._months_field.units_between(start.date, end_date))
                case PeriodUnits.WEEKS:
                    return cls.from_weeks(_DatePeriodFields._weeks_field.units_between(start.date, end_date))
                case PeriodUnits.DAYS:
                    return cls.from_days(cls._internal_days_between(start.date, end_date))
                case PeriodUnits.HOURS:
                    return cls.from_hours(_TimePeriodField._hours._units_between(start, end))
                case PeriodUnits.MINUTES:
                    return cls.from_minutes(_TimePeriodField._minutes._units_between(start, end))
                case PeriodUnits.SECONDS:
                    return cls.from_seconds(_TimePeriodField._seconds._units_between(start, end))
                case PeriodUnits.MILLISECONDS:
                    return cls.from_milliseconds(_TimePeriodField._milliseconds._units_between(start, end))
                case PeriodUnits.TICKS:
                    return cls.from_ticks(_TimePeriodField._ticks._units_between(start, end))
                case PeriodUnits.NANOSECONDS:
                    return cls.from_nanoseconds(_TimePeriodField._nanoseconds._units_between(start, end))

            # Multiple fields
            remaining = start
            years = months = weeks = days = 0
            if (units & PeriodUnits.ALL_DATE_UNITS) != PeriodUnits.NONE:
                remaining_date, years, months, weeks, days = cls.__date_components_between(start.date, end_date, units)
                remaining = LocalDateTime._ctor(local_date=remaining_date, local_time=start.time_of_day)
            if (units & PeriodUnits.ALL_TIME_UNITS) == PeriodUnits.NONE:
                return Period._ctor(years=years, months=months, weeks=weeks, days=days)

            # The remainder of the computation is with fixed-length units, so we can do it all with
            # Duration instead of Local* values. We don't know for sure that this is small though - we *could*
            # be trying to find the difference between 9998 BC and 9999 CE in nanoseconds...
            # Where we can optimize, do everything with long arithmetic (as we do for Between(LocalTime, LocalTime)).
            # Otherwise (rare case), use duration arithmetic.
            duration = (
                end._to_local_instant()._time_since_local_epoch - remaining._to_local_instant()._time_since_local_epoch
            )
            # TODO in Noda Time there is some conditional optimization here to use long arithmetic
            #  (as opposed to int) if the total nanoseconds of the duration is within the range of
            #  that type. That optimization doesn't make sense in Python, so we don't do it.

            hours, minutes, seconds, milliseconds, ticks, nanoseconds = cls.__time_components_between(
                duration.to_nanoseconds(), units
            )
            return Period._ctor(
                years=years,
                months=months,
                weeks=weeks,
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                milliseconds=milliseconds,
                ticks=ticks,
                nanoseconds=nanoseconds,
            )

        # public static Period Between(LocalDate start, LocalDate end)
        elif isinstance(start, LocalDate) and isinstance(end, LocalDate):
            if units is None:
                units = PeriodUnits.YEAR_MONTH_DAY
            _Preconditions._check_argument(
                (units & PeriodUnits.ALL_TIME_UNITS) == PeriodUnits.NONE,
                "units",
                "Units contains time units",  # TODO: str representation of enum
            )
            _Preconditions._check_argument(
                units != PeriodUnits.NONE,
                "units",
                "Units must not be empty",
            )
            _Preconditions._check_argument(
                (units & ~PeriodUnits.ALL_UNITS) == PeriodUnits.NONE,
                "units",
                "Units contains an unknown value",  # TODO: str representation of enum
            )
            calendar = start.calendar
            _Preconditions._check_argument(
                calendar == end.calendar,
                "end",
                "start and end must use the same calendar system",
            )

            if start == end:
                return cls.zero

            # Optimization for single field

            match units:
                case PeriodUnits.YEARS:
                    return cls.from_years(_DatePeriodFields._years_field.units_between(start, end))
                case PeriodUnits.MONTHS:
                    return cls.from_months(_DatePeriodFields._months_field.units_between(start, end))
                case PeriodUnits.WEEKS:
                    return cls.from_weeks(_DatePeriodFields._weeks_field.units_between(start, end))
                case PeriodUnits.DAYS:
                    return cls.from_days(_DatePeriodFields._days_field.units_between(start, end))

            # Multiple fields
            _, years, months, weeks, days = cls.__date_components_between(start, end, units)
            return Period._ctor(years, months, weeks, days)

        # public static Period Between(LocalTime start, LocalTime end)
        elif isinstance(start, LocalTime) and isinstance(end, LocalTime):
            if units is None:
                units = PeriodUnits.ALL_TIME_UNITS
            _Preconditions._check_argument(
                (units & PeriodUnits.ALL_DATE_UNITS) == PeriodUnits.NONE,
                "units",
                "Units contains date units",  # TODO: f-string error message
            )
            _Preconditions._check_argument(
                units != PeriodUnits.NONE,
                "units",
                "Units must not be empty",
            )
            _Preconditions._check_argument(
                (units & ~PeriodUnits.ALL_UNITS) == PeriodUnits.NONE,
                "units",
                "Units contains an unknown value",  # TODO: str representation of enum
            )

            # We know that the difference is in the range of +/- 1 day, which is a relatively small
            # number of nanoseconds. All the operations can be done with simple long division/remainder ops,
            # so we don't need to delegate to TimePeriodField.

            # TODO: unchecked

            remaining_ = end.nanosecond_of_day - start.nanosecond_of_day

            # Optimization for a single unit
            match units:
                case PeriodUnits.HOURS:
                    return cls.from_hours(_towards_zero_division(remaining_, PyodaConstants.NANOSECONDS_PER_HOUR))
                case PeriodUnits.MINUTES:
                    return cls.from_minutes(_towards_zero_division(remaining_, PyodaConstants.NANOSECONDS_PER_MINUTE))
                case PeriodUnits.SECONDS:
                    return cls.from_seconds(_towards_zero_division(remaining_, PyodaConstants.NANOSECONDS_PER_SECOND))
                case PeriodUnits.MILLISECONDS:
                    return cls.from_milliseconds(
                        _towards_zero_division(remaining_, PyodaConstants.NANOSECONDS_PER_MILLISECOND)
                    )
                case PeriodUnits.TICKS:
                    return cls.from_ticks(_towards_zero_division(remaining_, PyodaConstants.NANOSECONDS_PER_TICK))
                case PeriodUnits.NANOSECONDS:
                    return cls.from_nanoseconds(remaining_)

            hours, minutes, seconds, milliseconds, ticks, nanoseconds = cls.__time_components_between(remaining_, units)

            return Period._ctor(
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                milliseconds=milliseconds,
                ticks=ticks,
                nanoseconds=nanoseconds,
            )

        # public static Period Between(YearMonth start, YearMonth end)
        elif isinstance(start, YearMonth) and isinstance(end, YearMonth):
            if units is None:
                units = PeriodUnits.YEARS | PeriodUnits.MONTHS
            _Preconditions._check_argument(
                (units & (PeriodUnits.ALL_UNITS ^ PeriodUnits.YEARS ^ PeriodUnits.MONTHS)) == PeriodUnits.NONE,
                "units",
                "Units can only contain year and month units",  # TODO: f-string error message
            )
            _Preconditions._check_argument(
                units != PeriodUnits.NONE,
                "units",
                "Units must not be empty",
            )
            _Preconditions._check_argument(
                (units & ~PeriodUnits.ALL_UNITS) == PeriodUnits.NONE,
                "units",
                "Units contains an unknown value",  # TODO: str representation of enum
            )
            calendar = start.calendar
            _Preconditions._check_argument(
                calendar == end.calendar,
                "end",
                "start and end must use the same calendar system",
            )

            if start == end:
                return cls.zero

            start_date: LocalDate = start._start_date
            end_date_: LocalDate = end._start_date

            # Optimization for single field
            from .fields._date_period_fields import _DatePeriodFields

            match units:
                case PeriodUnits.YEARS:
                    return cls.from_years(_DatePeriodFields._years_field.units_between(start_date, end_date_))
                case PeriodUnits.MONTHS:
                    return cls.from_years(_DatePeriodFields._months_field.units_between(start_date, end_date_))

            # Multiple fields
            _, years, months, _, _ = cls.__date_components_between(start_date, end_date_, units)

            return Period._ctor(years, months)

        raise ValueError("Called with incorrect arguments")

    @classmethod
    def __date_components_between(
        cls, start: LocalDate, end: LocalDate, units: PeriodUnits
    ) -> tuple[LocalDate, int, int, int, int]:
        from .fields._date_period_fields import _DatePeriodFields
        from .fields._i_date_period_field import _IDatePeriodField

        def units_between(
            masked_units: PeriodUnits, start_date: LocalDate, end_date: LocalDate, date_field: _IDatePeriodField
        ) -> tuple[int, LocalDate]:
            if masked_units == PeriodUnits.NONE:
                return 0, start_date
            value: int = date_field.units_between(start_date, end_date)
            start_date = date_field.add(start_date, value)
            return value, start_date

        result = start
        years, result = units_between(units & PeriodUnits.YEARS, result, end, _DatePeriodFields._years_field)
        months, result = units_between(units & PeriodUnits.MONTHS, result, end, _DatePeriodFields._months_field)
        weeks, result = units_between(units & PeriodUnits.WEEKS, result, end, _DatePeriodFields._weeks_field)
        days, result = units_between(units & PeriodUnits.DAYS, result, end, _DatePeriodFields._days_field)
        return result, years, months, weeks, days

    @classmethod
    def __time_components_between(
        cls, total_nanoseconds: int, units: PeriodUnits
    ) -> tuple[int, int, int, int, int, int]:
        def units_between(mask: PeriodUnits, nanoseconds_per_unit: int) -> tuple[int, int]:
            if (mask & units) == PeriodUnits.NONE:
                return 0, total_nanoseconds
            # Pyoda Time implementation note:
            # NodaTime does the following here:
            # `return Math.DivRem(totalNanoseconds, nanosecondsPerUnit, out totalNanoseconds);`
            # You might think to use divmod() here, but it doesn't round towards
            # zero as Math.DivRem() does in C#.
            # Python rounds towards the nearest whole number, whereas C# rounds
            # towards zero.
            ret = _towards_zero_division(total_nanoseconds, nanoseconds_per_unit)
            new_total_nanoseconds = total_nanoseconds - (ret * nanoseconds_per_unit)
            return ret, new_total_nanoseconds

        hours, total_nanoseconds = units_between(PeriodUnits.HOURS, PyodaConstants.NANOSECONDS_PER_HOUR)
        minutes, total_nanoseconds = units_between(PeriodUnits.MINUTES, PyodaConstants.NANOSECONDS_PER_MINUTE)
        seconds, total_nanoseconds = units_between(PeriodUnits.SECONDS, PyodaConstants.NANOSECONDS_PER_SECOND)
        milliseconds, total_nanoseconds = units_between(
            PeriodUnits.MILLISECONDS, PyodaConstants.NANOSECONDS_PER_MILLISECOND
        )
        ticks, total_nanoseconds = units_between(PeriodUnits.TICKS, PyodaConstants.NANOSECONDS_PER_TICK)
        nanoseconds, total_nanoseconds = units_between(PeriodUnits.NANOSECONDS, 1)

        return hours, minutes, seconds, milliseconds, ticks, nanoseconds

    @classmethod
    def _internal_days_between(cls, start: LocalDate, end: LocalDate) -> int:
        """Returns the number of days between two dates.

        This allows optimizations in DateInterval,
        and for date calculations which just use days - we don't need state or a virtual method invocation.
        """

        # We already assume the calendars are the same
        if start._year_month_day == end._year_month_day:
            return 0

        # Note: I've experimented with checking for the dates being in the same year and optimizing that.
        # It helps a little if they're in the same month, but just that test has a cost for other situations.
        # Being able to find the day of year if they're in the same year but different months doesn't help,
        # somewhat surprisingly.
        start_days: int = start._days_since_epoch
        end_days: int = end._days_since_epoch
        return end_days - start_days

    @property
    def has_time_component(self) -> bool:
        """True if the period contains any non-zero-valued time-based properties (hours or lower); false otherwise."""
        return (
            self.hours != 0
            or self.minutes != 0
            or self.seconds != 0
            or self.milliseconds != 0
            or self.ticks != 0
            or self.nanoseconds != 0
        )

    @property
    def has_date_component(self) -> bool:
        """True if this period contains any non-zero date-based properties (days or higher); false otherwise."""
        return self.years != 0 or self.months != 0 or self.weeks != 0 or self.days != 0

    def to_duration(self) -> Duration:
        """Return the duration of the period.

        For periods that do not contain a non-zero number of years or months, returns a duration for this period
        assuming a standard 7-day week, 24-hour day, 60-minute hour etc.
        """
        if self.months != 0 or self.years != 0:
            raise RuntimeError("Cannot construct duration of period with non-zero months or years.")
        from ._duration import Duration

        return Duration.from_nanoseconds(self.__total_nanoseconds)

    @property
    def __total_nanoseconds(self) -> int:
        """Return the total number of nanoseconds duration for the 'standard' properties (all bar years and months)."""
        return (
            self.nanoseconds
            + self.ticks * PyodaConstants.NANOSECONDS_PER_TICK
            + self.milliseconds * PyodaConstants.NANOSECONDS_PER_MILLISECOND
            + self.seconds * PyodaConstants.NANOSECONDS_PER_SECOND
            + self.minutes * PyodaConstants.NANOSECONDS_PER_MINUTE
            + self.hours * PyodaConstants.NANOSECONDS_PER_HOUR
            + self.days * PyodaConstants.NANOSECONDS_PER_DAY
            + self.weeks * PyodaConstants.NANOSECONDS_PER_WEEK
        )

    def to_builder(self) -> PeriodBuilder:
        """Creates a ``PeriodBuilder`` from this instance.

        The new builder is populated with the values from this period,
        but is then detached from it:
        changes made to the builder are not reflected in this period.

        :return: A builder with the same values and units as this period.
        """
        from . import PeriodBuilder

        return PeriodBuilder.from_period(self)

    def normalize(self) -> Period:
        """Returns a normalized version of this period, such that equivalent (but potentially non-equal) periods are
        changed to the same representation.

        Months and years are unchanged (as they can vary in length), but weeks are multiplied by 7 and added to the Days
        property, and all time properties are normalized to their natural range. Subsecond values are normalized to
        millisecond and "nanosecond within millisecond" values. So for example, a period of 25 hours becomes a period of
        1 day and 1 hour. A period of 1,500,750,000 nanoseconds becomes 1 second, 500 milliseconds and 750,000
        nanoseconds. Aside from months and years, either all the properties end up positive, or they all end up
        negative. "Week" and "tick" units in the returned period are always 0.

        :return: The normalized period.
        """
        # Simplest way to normalize: grab all the fields up to "week" and sum them.
        total_nanoseconds = self.__total_nanoseconds
        days = _towards_zero_division(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_DAY)
        hours = _csharp_modulo(
            _towards_zero_division(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_HOUR), PyodaConstants.HOURS_PER_DAY
        )
        minutes = _csharp_modulo(
            _towards_zero_division(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_MINUTE),
            PyodaConstants.MINUTES_PER_HOUR,
        )
        seconds = _csharp_modulo(
            _towards_zero_division(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND),
            PyodaConstants.SECONDS_PER_MINUTE,
        )
        milliseconds = _csharp_modulo(
            _towards_zero_division(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_MILLISECOND),
            PyodaConstants.MILLISECONDS_PER_SECOND,
        )
        nanoseconds = _csharp_modulo(total_nanoseconds, PyodaConstants.NANOSECONDS_PER_MILLISECOND)

        return Period._ctor(self.years, self.months, 0, days, hours, minutes, seconds, milliseconds, 0, nanoseconds)

    # region Object overrides

    def __repr__(self) -> str:
        # TODO: PeriodPattern.RoundTrip.Format(this)
        #  This implementation is a very rough approximation of that...
        if self == Period.zero:
            return "P0D"
        s = "P"
        date_components = {
            "Y": self.years,
            "M": self.months,
            "W": self.weeks,
            "D": self.days,
        }
        for suffix, value in date_components.items():
            if value != 0:
                s += f"{value}{suffix}"
        if self.has_time_component:
            s += "T"
            time_components = {
                "H": self.hours,
                "M": self.minutes,
                "S": self.seconds,
                "s": self.milliseconds,
                "t": self.ticks,
                "n": self.nanoseconds,
            }
            for suffix, value in time_components.items():
                if value != 0:
                    s += f"{value}{suffix}"
        return s

    def __hash__(self) -> int:
        return hash(
            (
                self.years,
                self.months,
                self.weeks,
                self.days,
                self.hours,
                self.minutes,
                self.seconds,
                self.milliseconds,
                self.ticks,
                self.nanoseconds,
            )
        )

    def equals(self, other: Period) -> bool:
        return self == other

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if isinstance(other, Period):
            return (
                self.years == other.years
                and self.months == other.months
                and self.weeks == other.weeks
                and self.days == other.days
                and self.hours == other.hours
                and self.minutes == other.minutes
                and self.seconds == other.seconds
                and self.milliseconds == other.milliseconds
                and self.ticks == other.ticks
                and self.nanoseconds == other.nanoseconds
            )
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        return not (self == other)

    # endregion
