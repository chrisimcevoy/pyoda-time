from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Self, overload

from .calendars import (
    _EraCalculator,
    _GJEraCalculator,
    _GregorianYearMonthDayCalculator,
    _YearMonthDayCalculator,
)
from .utility import _Preconditions, _TickArithmetic, _to_ticks, _towards_zero_division

HOURS_PER_DAY = 24
SECONDS_PER_MINUTE = 60
MINUTES_PER_HOUR = 60
SECONDS_PER_HOUR = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
SECONDS_PER_DAY = SECONDS_PER_HOUR * HOURS_PER_DAY
MILLISECONDS_PER_SECOND = 1000
MILLISECONDS_PER_MINUTE = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE
MILLISECONDS_PER_HOUR = MILLISECONDS_PER_MINUTE * MINUTES_PER_HOUR
MILLISECONDS_PER_DAY = MILLISECONDS_PER_HOUR * HOURS_PER_DAY
MINUTES_PER_HOUR = 60
NANOSECONDS_PER_TICK = 100
NANOSECONDS_PER_MILLISECOND = 1000000
NANOSECONDS_PER_SECOND = 1000000000
NANOSECONDS_PER_MINUTE = NANOSECONDS_PER_SECOND * SECONDS_PER_MINUTE
NANOSECONDS_PER_HOUR = NANOSECONDS_PER_MINUTE * MINUTES_PER_HOUR
NANOSECONDS_PER_DAY = NANOSECONDS_PER_HOUR * HOURS_PER_DAY
TICKS_PER_MILLISECOND = 10_000
TICKS_PER_SECOND = TICKS_PER_MILLISECOND * MILLISECONDS_PER_SECOND
TICKS_PER_MINUTE = TICKS_PER_SECOND * SECONDS_PER_MINUTE
TICKS_PER_HOUR = TICKS_PER_MINUTE * MINUTES_PER_HOUR
TICKS_PER_DAY = TICKS_PER_HOUR * HOURS_PER_DAY


class CalendarOrdinal(IntEnum):
    """Enumeration of calendar ordinal values.
    Used for converting between a compact integer representation and a calendar system.
    """

    ISO = 0
    GREGORIAN = 1
    JULIAN = 2
    COPTIC = 3
    HEBREW_CIVIL = 4
    HEBREW_SCRIPTURAL = 5
    PERSIAN_SIMPLE = 6
    PERSIAN_ARITHMETIC = 7
    PERSIAN_ASTRONOMICAL = 8
    ISLAMIC_ASTRONOMICAL_BASE15 = 9
    ISLAMIC_ASTRONOMICAL_BASE16 = 10
    ISLAMIC_ASTRONOMICAL_INDIAN = 11
    ISLAMIC_ASTRONOMICAL_HABASH_AL_HASIB = 12
    ISLAMIC_CIVIL_BASE15 = 13
    ISLAMIC_CIVIL_BASE16 = 14
    ISLAMIC_CIVIL_Indian = 15
    ISLAMIC_CIVIL_HASBASH_AL_HASIB = 16
    UM_AL_QURA = 17
    BADI = 18
    # Not a real ordinal; just present to keep a count. Increase this as the number increases...
    SIZE = 19


class CalendarSystem:
    """Maps the non-calendar-specific "local timeline" to human concepts such as years, months and days."""

    __ISO_NAME = "ISO"
    __ISO_ID = __ISO_NAME

    __CALENDAR_BY_ORDINAL: dict[int, CalendarSystem] = {}

    def __init__(
        self,
        ordinal: CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        era_calculator: _EraCalculator,
    ):
        self.ordinal = ordinal
        self.id = id_
        self.name = name
        self.year_month_day_calculator = year_month_day_calculator
        self.min_year = year_month_day_calculator._min_year
        self.max_year = year_month_day_calculator._max_year
        self.min_days = year_month_day_calculator._get_start_of_year_in_days(self.min_year)
        self.max_days = year_month_day_calculator._get_start_of_year_in_days(self.max_year + 1) - 1

        self.era_calculator = era_calculator
        self.__CALENDAR_BY_ORDINAL[int(ordinal)] = self

    @classmethod
    def _for_ordinal(cls, ordinal: CalendarOrdinal) -> CalendarSystem:
        """Fetches a calendar system by its ordinal value, constructing it if necessary."""

        # TODO Preconditions.DebugCheckArgument

        # Avoid an array lookup for the overwhelmingly common case.
        if ordinal == CalendarOrdinal.ISO:
            return cls.iso()

        if calendar := cls.__CALENDAR_BY_ORDINAL.get(int(ordinal)):
            return calendar

        return cls._for_ordinal_uncached(ordinal)

    @classmethod
    def _for_ordinal_uncached(cls, ordinal: CalendarOrdinal):
        match ordinal:
            case CalendarOrdinal.ISO:
                return cls.iso()
            case _:
                # TODO map all CalendarOrdinals to CalendarSystems and rephrase this error
                raise ValueError(f"CalendarOrdinal '{ordinal.name}' not mapped to CalendarSystem yet")

    @classmethod
    def iso(cls):
        """Returns a calendar system that follows the rules of the ISO-8601 standard,
        which is compatible with Gregorian for all modern dates.
        """
        gregorian_calculator = _GregorianYearMonthDayCalculator()
        gregorian_era_calculator = _GJEraCalculator(gregorian_calculator)
        return CalendarSystem(
            CalendarOrdinal.ISO,
            cls.__ISO_ID,
            cls.__ISO_NAME,
            gregorian_calculator,
            gregorian_era_calculator,
        )

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        """Returns the number of days since the Unix epoch (1970-01-01 ISO) for the given date."""
        return self.year_month_day_calculator._get_days_since_epoch(year_month_day)


class Duration:
    """Represents a fixed (and calendar-independent) length of time."""

    _MAX_DAYS = (1 << 24) - 1
    _MIN_DAYS = ~_MAX_DAYS

    def __init__(self, days: int = 0, nano_of_day: int = 0) -> None:
        self.days = days
        self.nano_of_day = nano_of_day

    def __le__(self, other):
        if isinstance(other, Duration):
            return self < other or self == other
        raise TypeError("Unsupported operand type")

    def __lt__(self, other):
        if isinstance(other, Duration):
            return self.days < other.days or (self.days == other.days and self.nano_of_day < other.nano_of_day)
        raise TypeError("Unsupported operand type")

    def __eq__(self, other):
        if isinstance(other, Duration):
            return self.days == other.days and self.nano_of_day == other.nano_of_day
        raise TypeError("Unsupported operand type")

    def __neg__(self) -> Duration:
        old_days = self.days
        old_nano_of_day = self.nano_of_day
        if old_nano_of_day == 0:
            return Duration(-old_days, 0)
        new_nano_of_day = NANOSECONDS_PER_DAY - old_nano_of_day
        return Duration(-old_days - 1, new_nano_of_day)

    @staticmethod
    def from_ticks(ticks: int) -> Duration:
        """Returns a Duration that represents the given number of ticks."""
        days, tick_of_day = _TickArithmetic.ticks_to_days_and_tick_of_day(ticks)
        return Duration(days, tick_of_day * NANOSECONDS_PER_TICK)

    @staticmethod
    def zero() -> Duration:
        """Gets a zero Duration of 0 nanoseconds."""
        return Duration()

    @property
    def _floor_days(self) -> int:
        """Days portion of this duration."""
        return self.days

    @property
    def _nanosecond_of_floor_day(self):
        """Nanosecond within the "floor day". This is *always* non-negative, even for negative durations."""
        return self.nano_of_day

    @classmethod
    def from_milliseconds(cls, milliseconds):
        """Returns a Duration that represents the given number of milliseconds."""
        return cls.__from_units(
            units=milliseconds,
            param_name="milliseconds",
            min_value=cls._MIN_DAYS * MILLISECONDS_PER_DAY,
            max_value=((cls._MAX_DAYS + 1) * MILLISECONDS_PER_DAY) - 1,
            units_per_day=MILLISECONDS_PER_DAY,
            nanos_per_unit=NANOSECONDS_PER_MILLISECOND,
        )

    @classmethod
    def __from_units(
        cls,
        units: int,
        param_name: str,
        min_value: int,
        max_value: int,
        units_per_day: int,
        nanos_per_unit: int,
    ):
        """Constructs an instance from a given number of units.
        This is a private constructor in Noda Time; its name here is derived from
        that constructor's past life as a method (FromUnits).
        """
        days = _towards_zero_division(units, units_per_day)
        unit_of_day = units - (units_per_day * days)
        if unit_of_day < 0:
            days -= 1
            unit_of_day += units_per_day
        nano_of_day = unit_of_day * nanos_per_unit
        # In Noda Time, the private constructor avoids calling the
        # public constructor which validates its "days" parameter.
        # Here, we just call the public initialiser once we've worked
        # out the parameters.
        return cls(days, nano_of_day)

    @classmethod
    def from_seconds(cls, seconds):
        return cls.__from_units(
            seconds,
            "seconds",
            cls._MIN_DAYS * SECONDS_PER_DAY,
            cls._MAX_DAYS + 1,
            SECONDS_PER_DAY,
            NANOSECONDS_PER_SECOND,
        )

    def __add__(self, other):
        if isinstance(other, Duration):
            days = self.days + other.days
            nanos = self.nano_of_day + other.nano_of_day
            if nanos >= NANOSECONDS_PER_DAY:
                days += 1
                nanos -= NANOSECONDS_PER_DAY
            return Duration(days, nanos)
        raise TypeError("Unsupported operand type")

    def __sub__(self, other):
        if isinstance(other, Duration):
            days = self.days - other.days
            nanos = self.nano_of_day - other.nano_of_day
            if nanos < 0:
                days -= 1
                nanos += NANOSECONDS_PER_DAY
            return Duration(days, nanos)
        raise TypeError("Unsupported operand type")

    @classmethod
    def epsilon(cls) -> Duration:
        """Return a Duration representing 1 nanosecond.
        This is the smallest amount by which an instant can vary.
        """
        return cls(0, 1)

    @classmethod
    def from_nanoseconds(cls, nanoseconds):  # TODO from_nanoseconds overrides
        """Returns a Duration that represents the given number of nanoseconds."""
        if nanoseconds >= 0:
            # TODO Is divmod compatible with C# integer division?
            quotient, remainder = divmod(nanoseconds, NANOSECONDS_PER_DAY)
            return cls(days=quotient, nano_of_day=remainder)

        # Work out the "floor days"; division truncates towards zero and
        # nanoseconds is definitely negative by now, hence the addition and subtraction here.
        days = _towards_zero_division(nanoseconds + 1, NANOSECONDS_PER_DAY) - 1
        nano_of_day = nanoseconds - days * NANOSECONDS_PER_DAY
        return Duration(days, nano_of_day)

    @classmethod
    def from_hours(cls, hours: int) -> Duration:
        """Returns a Duration that represents the given number of hours."""
        # TODO this is a shortcut and differs from Noda Time
        return Duration.from_seconds(hours * SECONDS_PER_HOUR)

    def _plus_small_nanoseconds(self, small_nanos) -> Duration:
        """Adds a "small" number of nanoseconds to this duration.
        It is trusted to be less or equal to than 24 hours in magnitude.
        """
        _Preconditions._check_argument_range(small_nanos, -NANOSECONDS_PER_DAY, NANOSECONDS_PER_DAY)
        new_days = self.days
        new_nanos = self.nano_of_day + small_nanos
        if new_nanos >= NANOSECONDS_PER_DAY:
            new_days += 1
            new_nanos -= NANOSECONDS_PER_DAY
        elif new_nanos < 0:
            new_days -= 1
            new_nanos += NANOSECONDS_PER_DAY
        return Duration(new_days, new_nanos)


class Offset:
    """An offset from UTC in seconds."""

    __MIN_HOURS = -18
    __MAX_HOURS = 18
    __MIN_SECONDS = -18 * SECONDS_PER_HOUR
    __MAX_SECONDS = 18 * SECONDS_PER_HOUR

    def __init__(self, seconds: int):
        _Preconditions._check_argument_range(seconds, self.__MIN_SECONDS, self.__MAX_SECONDS)
        self.seconds = seconds

    @classmethod
    def from_hours(cls, hours: int) -> Offset:
        """Returns an offset for the specified number of hours, which may be negative."""
        _Preconditions._check_argument_range(hours, cls.__MIN_HOURS, cls.__MAX_HOURS)
        return cls(hours * SECONDS_PER_HOUR)

    @property
    def nanoseconds(self) -> int:
        return self.seconds * NANOSECONDS_PER_SECOND


class Instant:
    """Represents an instant on the global timeline, with nanosecond resolution.
    An Instant has no concept of a particular time zone or calendar: it simply represents a point in
    time that can be globally agreed-upon.
    Equality and ordering comparisons are defined in the natural way, with earlier points on the timeline
    being considered "less than" later points.
    """

    # These correspond to -9998-01-01 and 9999-12-31 respectively.
    _MIN_DAYS = -4371222
    _MAX_DAYS = 2932896

    __MIN_TICKS = _MIN_DAYS * TICKS_PER_DAY
    __MAX_TICKS = (_MAX_DAYS + 1) * TICKS_PER_DAY - 1
    __MIN_MILLISECONDS = _MIN_DAYS * MILLISECONDS_PER_DAY
    __MAX_MILLISECONDS = (_MAX_DAYS + 1) * MILLISECONDS_PER_DAY - 1
    __MIN_SECONDS = _MIN_DAYS * SECONDS_PER_DAY
    __MAX_SECONDS = (_MAX_DAYS + 1) * SECONDS_PER_DAY - 1

    def __init__(self, days: int = 0, nano_of_day: int = 0) -> None:
        self.duration = Duration(days, nano_of_day)

    def __eq__(self, other) -> bool:
        if isinstance(other, Instant):
            return self.duration == other.duration
        raise TypeError("Unsupported operand type")

    def __lt__(self, other):
        if isinstance(other, Instant):
            return self.duration < other.duration
        raise TypeError("Unsupported operand type")

    def __le__(self, other):
        if isinstance(other, Instant):
            return self < other or self == other
        raise TypeError("Unsupported operand type")

    @overload
    def __add__(self, offset: Offset) -> _LocalInstant:
        ...

    @overload
    def __add__(self, duration: Duration) -> Instant:
        ...

    def __add__(self, other):
        if isinstance(other, Duration):
            return self._from_untrusted_duration(self.duration + other)
        raise TypeError("Unsupported operand type")

    @overload
    def __sub__(self, other: Instant) -> Duration:
        ...

    @overload
    def __sub__(self, other: Duration) -> Instant:
        ...

    def __sub__(self, other: Instant | Duration) -> Instant | Duration:
        if isinstance(other, Instant):
            return self.duration - other.duration
        if isinstance(other, Duration):
            return self._from_trusted_duration(self.duration - other)
        raise TypeError("Unsupported operand type")

    @classmethod
    def min_value(cls) -> Instant:
        """Represents the smallest possible Instant.
        This value is equivalent to -9998-01-01T00:00:00Z
        """
        return Instant(cls._MIN_DAYS, 0)

    @classmethod
    def max_value(cls) -> Instant:
        """Represents the largest possible Instant.
        This value is equivalent to 9999-12-31T23:59:59.999999999Z
        """
        return Instant(cls._MAX_DAYS, NANOSECONDS_PER_DAY - 1)

    @classmethod
    def _before_min_value(cls) -> Self:
        """Instant which is invalid *except* for comparison purposes; it is earlier than any valid value.
        This must never be exposed.
        """
        return cls(Duration._MIN_DAYS)

    @classmethod
    def _after_max_value(cls) -> Self:
        """Instant which is invalid *except* for comparison purposes; it is later than any valid value.
        This must never be exposed.
        """
        return cls(Duration._MAX_DAYS)

    @classmethod
    def __from_duration(cls, duration: Duration) -> Instant:
        """Constructor which constructs a new instance with the given duration, which
        is trusted to be valid. Should only be called from from_trusted_duration and
        from_untrusted_duration."""
        # In Noda Time this is a private constructor, with the body:
        # `this.duration = duration;`
        # This is probably about as close as we can get in Python without
        # exposing an additional parameter in the initialiser.
        return cls(duration.days, duration.nano_of_day)

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.duration._floor_days

    @classmethod
    def from_unix_time_ticks(cls, ticks) -> Instant:
        """Initializes a new Instant based on a number of ticks since the Unix epoch."""
        _Preconditions._check_argument_range(ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Instant._from_trusted_duration(Duration.from_ticks(ticks))

    @classmethod
    def _from_trusted_duration(cls, duration) -> Instant:
        """Creates an Instant with the given duration, with no validation (in release mode)."""
        # TODO Preconditions.DebugCheckArgumentRange
        return Instant.__from_duration(duration)

    @classmethod
    def _from_untrusted_duration(cls, duration: Duration) -> Instant:
        """Creates an Instant with the given duration, validating that it has a suitable
        "day" part. (It is assumed that the nanoOfDay is okay.)"""
        days = duration._floor_days
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            raise OverflowError("Operation would overflow range of Instant")
        return Instant.__from_duration(duration)

    def to_unix_time_ticks(self) -> int:
        """Gets the number of ticks since the Unix epoch. Negative values represent instants before the Unix epoch.
        A tick is equal to 100 nanoseconds. There are 10,000 ticks in a millisecond. If the number of nanoseconds
        in this instant is not an exact number of ticks, the value is truncated towards the start of time.
        """
        return _TickArithmetic.bounded_days_and_tick_of_day_to_ticks(
            self.duration._floor_days,
            _towards_zero_division(self.duration._nanosecond_of_floor_day, NANOSECONDS_PER_TICK),
        )

    @classmethod
    def from_unix_time_milliseconds(cls, milliseconds: int) -> Instant:
        """Initializes a new Instant struct based on a number of milliseconds
        since the Unix epoch of (ISO) January 1st 1970, midnight, UTC.
        """
        _Preconditions._check_argument_range(milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS)
        return Instant._from_trusted_duration(Duration.from_milliseconds(milliseconds))

    @classmethod
    def from_unix_time_seconds(cls, seconds) -> Instant:
        """Initializes a new Instant based on a number of seconds since the
        Unix epoch of (ISO) January 1st 1970, midnight, UTC.
        """
        _Preconditions._check_argument_range(seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        return cls._from_trusted_duration(Duration.from_seconds(seconds))

    def to_unix_time_seconds(self):
        """Gets the number of seconds since the Unix epoch.
        Negative values represent instants before the Unix epoch.
        If the number of nanoseconds in this instant is not an exact
        number of seconds, the value is truncated towards the start of time.
        """
        return self.duration._floor_days * SECONDS_PER_DAY + _towards_zero_division(
            self.duration._nanosecond_of_floor_day, NANOSECONDS_PER_SECOND
        )

    def to_unix_time_milliseconds(self):
        """Gets the number of milliseconds since the Unix epoch.
        Negative values represent instants before the Unix epoch.
        If the number of nanoseconds in this instant is not an exact
        number of milliseconds, the value is truncated towards the start of time.
        """
        return self.duration._floor_days * MILLISECONDS_PER_DAY + _towards_zero_division(
            self.duration._nanosecond_of_floor_day, NANOSECONDS_PER_MILLISECOND
        )

    @staticmethod
    def max(x: Instant, y: Instant) -> Instant:
        """Returns the later instant of the given two."""
        return max(x, y)

    @staticmethod
    def min(x: Instant, y: Instant) -> Instant:
        """Returns the earlier instant of the given two."""
        return min(x, y)

    @classmethod
    def from_datetime_utc(cls, datetime: datetime) -> Instant:
        """Converts a datetime.datetime into a new Instant representing the same instant in time.
        The datetime must have a truthy tzinfo, and must have a UTC offset of 0.
        """
        # TODO Precondition.CheckArgument
        # TODO Better exceptions?
        # Roughly equivalent to DateTimeKind.Local
        if (utc_offset := datetime.utcoffset()) is not None and utc_offset.total_seconds() != 0:
            raise ValueError()
        # Roughly equivalent to DateTimeKind.Unspecified
        if datetime.tzinfo is None:
            raise ValueError()
        return BCL_EPOCH.plus_ticks(_to_ticks(datetime))

    @classmethod
    def from_utc(
        cls,
        year: int,
        month_of_year: int,
        day_of_month: int,
        hour_of_day: int,
        minute_of_hour: int,
    ) -> Instant:
        """Returns a new Instant corresponding to the given UTC date and time in the ISO calendar.
        In most cases applications should use ZonedDateTime to represent a date
        and time, but this method is useful in some situations where an Instant is
        required, such as time zone testing."""
        days = LocalDate(year, month_of_year, day_of_month)._days_since_epoch
        nano_of_day = LocalTime(hour_of_day, minute_of_hour).nanosecond_of_day
        return Instant(days, nano_of_day)

    def plus_ticks(self, ticks: int) -> Instant:
        """Returns a new value of this instant with the given number of ticks added to it."""
        return self._from_untrusted_duration(self.duration + Duration.from_ticks(ticks))

    @property
    def _is_valid(self) -> bool:
        """Returns whether or not this is a valid instant. Returns true for all but
        before_min_value and after_max_value.
        """
        return self._MIN_DAYS <= self._days_since_epoch <= self._MAX_DAYS

    def _plus(self, offset: Offset) -> _LocalInstant:
        """Adds the given offset to this instant, to return a LocalInstant.
        A positive offset indicates that the local instant represents a "later local time" than the UTC
        representation of this instant."""
        return _LocalInstant(self.duration._plus_small_nanoseconds(offset.nanoseconds))

    def plus(self, other: Duration) -> Instant:
        """Returns the result of adding a duration to this instant, for a fluent alternative to the + operator."""
        return self + other

    def _safe_plus(self, offset: Offset):
        """Adds the given offset to this instant, either returning a normal LocalInstant,
        or LocalInstant.before_min_value() or LocalInstant.after_max_value()
        if the value would overflow."""
        days = self.duration._floor_days
        if self._MIN_DAYS < days < self._MAX_DAYS:
            return self._plus(offset)
        if days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        as_duration = self.duration._plus_small_nanoseconds(offset.nanoseconds)
        if as_duration._floor_days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if as_duration._floor_days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        return _LocalInstant(as_duration)


class _LocalInstant:
    """Represents a local date and time without reference to a calendar system. Essentially
    this is a duration since a Unix epoch shifted by an offset (but we don't store what that
    offset is). This class has been slimmed down considerably over time - it's used much less
    than it used to be... almost solely for time zones."""

    def __init__(self, nanoseconds: Duration):
        days = nanoseconds._floor_days
        if days < Instant._MIN_DAYS or days > Instant._MAX_DAYS:
            raise ValueError("Operation would overflow bounds of local date/time")
        self._duration = nanoseconds

    def __eq__(self, other):
        if isinstance(other, _LocalInstant):
            return self._duration == other._duration
        TypeError("Unsupported operand type")

    @property
    def _time_since_local_epoch(self) -> Duration:
        """Number of nanoseconds since the local unix epoch."""
        return self._duration

    @classmethod
    def before_min_value(cls):
        # In Noda Time this is a public static readonly field
        return _LocalInstant.__invalid_constructor(Instant._before_min_value()._days_since_epoch)

    @classmethod
    def after_max_value(cls):
        # In Noda Time this is a public static readonly field
        return _LocalInstant.__invalid_constructor(Instant._after_max_value()._days_since_epoch)

    @classmethod
    def __invalid_constructor(cls, days: int) -> _LocalInstant:
        """Constructor which should *only* be used to construct the invalid instances."""
        # Hack:
        # To emulate the private constructor on this class, here we just instantiate a
        # valid LocalInstant, then swap out the _duration with a potentially-invalid one.
        local_instant = _LocalInstant(Duration.zero())
        local_instant._duration = Duration(days)
        return local_instant


class LocalDate:
    """LocalDate is an immutable struct representing a date within the calendar,
    with no reference to a particular time zone or time of day."""

    def __init__(self, year: int, month: int, day: int):
        self.__year_month_day_calendar = _YearMonthDayCalendar(year, month, day, CalendarOrdinal.ISO)

    @property
    def __calendar_ordinal(self) -> CalendarOrdinal:
        return self.__year_month_day_calendar._calendar_ordinal

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system associated with this local date."""
        return CalendarSystem._for_ordinal(self.__calendar_ordinal)

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.calendar._get_days_since_epoch(self.__year_month_day_calendar._to_year_month_day())


class LocalTime:
    """LocalTime is an immutable struct representing a time of day, with no reference
    to a particular calendar, time zone or date."""

    def __init__(self, hour: int, minute: int):
        if hour < 0 or hour > HOURS_PER_DAY - 1 or minute < 0 or minute > MINUTES_PER_HOUR - 1:
            _Preconditions._check_argument_range(hour, 0, HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range(minute, 0, MINUTES_PER_HOUR - 1)
        self.__nanoseconds = hour * NANOSECONDS_PER_HOUR + minute * NANOSECONDS_PER_MINUTE

    @property
    def nanosecond_of_day(self) -> int:
        """The nanosecond of this local time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__nanoseconds


class _YearMonthDayCalendar:
    """A compact representation of a year, month, day and calendar ordinal (integer ID) in a single 32-bit integer."""

    # These constants are internal so they can be used in YearMonthDay
    _CALENDAR_BITS = 6  # Up to 64 calendars.
    _DAY_BITS = 6  # Up to 64 days in a month.
    _MONTH_BITS = 5  # Up to 32 months per year.
    _YEAR_BITS = 15  # 32K range; only need -10K to +10K.

    # Just handy constants to use for shifting and masking.
    __CALENDAR_DAY_BITS = _CALENDAR_BITS + _DAY_BITS
    __CALENDAR_DAY_MONTH_BITS = __CALENDAR_DAY_BITS + _MONTH_BITS

    __CALENDAR_MASK = (1 << _CALENDAR_BITS) - 1
    __DAY_MASK = ((1 << _DAY_BITS) - 1) << _CALENDAR_BITS
    __MONTH_MASK = ((1 << _MONTH_BITS) - 1) << __CALENDAR_DAY_BITS
    __YEAR_MASK = ((1 << _YEAR_BITS) - 1) << __CALENDAR_DAY_MONTH_BITS

    def __init__(self, year: int, month: int, day: int, calendar_ordinal: CalendarOrdinal):
        self.__value = (
            ((year - 1) << self.__CALENDAR_DAY_MONTH_BITS)
            | ((month - 1) << self.__CALENDAR_DAY_BITS)
            | ((day - 1) << self._CALENDAR_BITS)
            | int(calendar_ordinal)
        )

    @property
    def _calendar_ordinal(self) -> CalendarOrdinal:
        return CalendarOrdinal(self.__value & self.__CALENDAR_MASK)

    def _to_year_month_day(self) -> _YearMonthDay:
        return _YearMonthDay(self.__value >> self._CALENDAR_BITS)


class _YearMonthDay:
    """A compact representation of a year, month and day in a single 32-bit integer."""

    __DAY_MASK = (1 << _YearMonthDayCalendar._DAY_BITS) - 1
    __MONTH_MASK = ((1 << _YearMonthDayCalendar._MONTH_BITS) - 1) << _YearMonthDayCalendar._DAY_BITS

    def __init__(self, raw_value: int):
        self.__value = raw_value

    @property
    def _year(self) -> int:
        return (self.__value >> (_YearMonthDayCalendar._DAY_BITS + _YearMonthDayCalendar._MONTH_BITS)) + 1

    @property
    def _month(self) -> int:
        return ((self.__value & self.__MONTH_MASK) >> _YearMonthDayCalendar._DAY_BITS) + 1

    @property
    def _day(self) -> int:
        return (self.__value & self.__DAY_MASK) + 1


BCL_EPOCH: Instant = Instant.from_utc(1, 1, 1, 0, 0)
UNIX_EPOCH: Instant = Instant.from_unix_time_ticks(0)
