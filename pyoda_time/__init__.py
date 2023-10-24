from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Self, overload

from .calendars import (
    GJEraCalculator,
    YearMonthDayCalculator,
    GregorianYearMonthDayCalculator,
    EraCalculator,
)
from .utility import TickArithmetic, Preconditions
from .compatibility import to_ticks, towards_zero_division

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
    __ISO_NAME = "ISO"
    __ISO_ID = __ISO_NAME

    @classmethod
    def ISO(cls):
        """
        In Noda Time, this is a public static get-only property which is initialised in a static constructor.
        """
        gregorian_calculator = GregorianYearMonthDayCalculator()
        gregorian_era_calculator = GJEraCalculator(gregorian_calculator)
        return CalendarSystem(
            CalendarOrdinal.ISO,
            cls.__ISO_ID,
            cls.__ISO_NAME,
            gregorian_calculator,
            gregorian_era_calculator,
        )

    __CALENDAR_BY_ORDINAL: dict[int, CalendarSystem] = {}

    def __init__(
        self,
        ordinal: CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: YearMonthDayCalculator,
        era_calculator: EraCalculator,
    ):
        self.ordinal = ordinal
        self.id = id_
        self.name = name
        self.year_month_day_calculator = year_month_day_calculator
        self.min_year = year_month_day_calculator.min_year
        self.max_year = year_month_day_calculator.max_year
        self.min_days = year_month_day_calculator.get_start_of_year_in_days(
            self.min_year
        )
        self.max_days = (
            year_month_day_calculator.get_start_of_year_in_days(self.max_year + 1) - 1
        )

        self.era_calculator = era_calculator
        self.__CALENDAR_BY_ORDINAL[int(ordinal)] = self

    @classmethod
    def for_ordinal(cls, ordinal: CalendarOrdinal) -> CalendarSystem:
        # TODO Preconditions.DebugCheckArgument

        # Avoid an array lookup for the overwhelmingly common case.
        if ordinal == CalendarOrdinal.ISO:
            return cls.ISO()

        # TODO This doesn't work for some reason
        return cls.__CALENDAR_BY_ORDINAL[int(ordinal)]

    def get_days_since_epoch(self, year_month_day: YearMonthDay):
        return self.year_month_day_calculator.get_days_since_epoch(year_month_day)


class Duration:
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
            return self.days < other.days or (
                self.days == other.days and self.nano_of_day < other.nano_of_day
            )
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

    @classmethod
    def from_ticks(cls, ticks: int) -> Duration:
        """Returns a Duration that represents the given number of ticks."""
        days, tick_of_day = TickArithmetic.ticks_to_days_and_tick_of_day(ticks)
        return Duration(days, tick_of_day * NANOSECONDS_PER_TICK)

    @classmethod
    def zero(cls) -> Duration:
        return Duration()

    @property
    def floor_days(self) -> int:
        """Days portion of this duration."""
        return self.days

    @property
    def nanosecond_of_floor_day(self):
        return self.nano_of_day

    @classmethod
    def from_milliseconds(cls, milliseconds):
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
        days = towards_zero_division(units, units_per_day)
        unit_of_day = units - (units_per_day * days)
        if unit_of_day < 0:
            days -= 1
            unit_of_day += units_per_day
        nano_of_day = unit_of_day * nanos_per_unit
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
    def from_nanoseconds(cls, nanoseconds):
        if nanoseconds >= 0:
            # TODO Is divmod compatible with C# integer division?
            quotient, remainder = divmod(nanoseconds, NANOSECONDS_PER_DAY)
            return cls(days=quotient, nano_of_day=remainder)

        # Work out the "floor days"; division truncates towards zero and
        # nanoseconds is definitely negative by now, hence the addition and subtraction here.
        days = towards_zero_division(nanoseconds + 1, NANOSECONDS_PER_DAY) - 1
        nano_of_day = nanoseconds - days * NANOSECONDS_PER_DAY
        return Duration(days, nano_of_day)

    @classmethod
    def from_hours(cls, hours: int) -> Duration:
        # TODO this is a shortcut and differs from Noda Time
        return Duration.from_seconds(hours * SECONDS_PER_HOUR)

    def plus_small_nanoseconds(self, small_nanos):
        Preconditions.check_argument_range(
            small_nanos, -NANOSECONDS_PER_DAY, NANOSECONDS_PER_DAY
        )
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
    __MIN_HOURS = -18
    __MAX_HOURS = 18
    __MIN_SECONDS = -18 * SECONDS_PER_HOUR
    __MAX_SECONDS = 18 * SECONDS_PER_HOUR

    def __init__(self, seconds: int):
        Preconditions.check_argument_range(
            seconds, self.__MIN_SECONDS, self.__MAX_SECONDS
        )
        self.seconds = seconds

    @classmethod
    def from_hours(cls, hours: int) -> Offset:
        Preconditions.check_argument_range(hours, cls.__MIN_HOURS, cls.__MAX_HOURS)
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
    def __add__(self, offset: Offset) -> LocalInstant:
        ...

    @overload
    def __add__(self, duration: Duration) -> Instant:
        ...

    def __add__(self, other):
        if isinstance(other, Duration):
            return self._from_untrusted_duration(self.duration + other)
        if isinstance(other, Offset):
            return LocalInstant(self.duration.plus_small_nanoseconds(other.nanoseconds))
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
        return Instant(cls._MIN_DAYS, 0)

    @classmethod
    def max_value(cls) -> Instant:
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
    def from_duration(cls, duration: Duration) -> Instant:
        return cls(duration.days, duration.nano_of_day)

    @property
    def days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.duration.floor_days

    @classmethod
    def from_unix_time_ticks(cls, ticks) -> Instant:
        Preconditions.check_argument_range(ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Instant._from_trusted_duration(Duration.from_ticks(ticks))

    @classmethod
    def _from_trusted_duration(cls, duration) -> Instant:
        # TODO Preconditions.DebugCheckArgumentRange
        return Instant.from_duration(duration)

    @classmethod
    def _from_untrusted_duration(cls, duration: Duration) -> Instant:
        days = duration.floor_days
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            raise OverflowError("Operation would overflow range of Instant")
        return Instant.from_duration(duration)

    def to_unix_time_ticks(self) -> int:
        return TickArithmetic.bounded_days_and_tick_of_day_to_ticks(
            self.duration.floor_days,
            towards_zero_division(
                self.duration.nanosecond_of_floor_day, NANOSECONDS_PER_TICK
            ),
        )

    @classmethod
    def from_unix_time_milliseconds(cls, milliseconds: int) -> Instant:
        Preconditions.check_argument_range(
            milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS
        )
        return Instant._from_trusted_duration(Duration.from_milliseconds(milliseconds))

    @classmethod
    def from_unix_time_seconds(cls, seconds) -> Instant:
        Preconditions.check_argument_range(
            seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS
        )
        return cls._from_trusted_duration(Duration.from_seconds(seconds))

    def to_unix_time_seconds(self):
        return self.duration.floor_days * SECONDS_PER_DAY + towards_zero_division(
            self.duration.nanosecond_of_floor_day, NANOSECONDS_PER_SECOND
        )

    def to_unix_time_milliseconds(self):
        return self.duration.floor_days * MILLISECONDS_PER_DAY + towards_zero_division(
            self.duration.nanosecond_of_floor_day, NANOSECONDS_PER_MILLISECOND
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
        # TODO Precondition.CheckArgument
        # TODO Better exceptions?
        # Roughly equivalent to DateTimeKind.Local
        if (
            utc_offset := datetime.utcoffset()
        ) is not None and utc_offset.total_seconds() != 0:
            raise ValueError()
        # Roughly equivalent to DateTimeKind.Unspecified
        if datetime.tzinfo is None:
            raise ValueError()
        return cls.bcl_epoch().plus_ticks(to_ticks(datetime))

    @staticmethod
    def bcl_epoch() -> Instant:
        return Instant.from_utc(1, 1, 1, 0, 0)

    @classmethod
    def from_utc(
        cls,
        year: int,
        month_of_year: int,
        day_of_month: int,
        hour_of_day: int,
        minute_of_hour: int,
    ) -> Instant:
        days = LocalDate(year, month_of_year, day_of_month).days_since_epoch
        nano_of_day = LocalTime(hour_of_day, minute_of_hour).nanosecond_of_day
        return Instant(days, nano_of_day)

    def plus_ticks(self, ticks: int) -> Instant:
        return self._from_untrusted_duration(self.duration + Duration.from_ticks(ticks))

    @property
    def is_valid(self) -> bool:
        return self._MIN_DAYS <= self.days_since_epoch <= self._MAX_DAYS

    @overload
    def plus(self, other: Duration) -> Instant:
        return self + other

    @overload
    def plus(self, other: Offset) -> LocalInstant:
        return self + other

    def plus(self, other: Duration | Offset) -> Instant | LocalInstant:
        return self + other


class LocalInstant:
    def __init__(self, nanoseconds: Duration):
        days = nanoseconds.floor_days
        if days < Instant._MIN_DAYS or days > Instant._MAX_DAYS:
            raise ValueError("Operation would overflow bounds of local date/time")
        self.duration = nanoseconds

    @property
    def time_since_local_epoch(self) -> Duration:
        """Number of nanoseconds since the local unix epoch."""
        return self.duration


class LocalDate:
    def __init__(self, year: int, month: int, day: int):
        self.__year_month_day_calendar = YearMonthDayCalendar(
            year, month, day, CalendarOrdinal.ISO
        )

    @property
    def __calendar_ordinal(self) -> CalendarOrdinal:
        return self.__year_month_day_calendar.calendar_ordinal

    @property
    def calendar(self) -> CalendarSystem:
        return CalendarSystem.for_ordinal(self.__calendar_ordinal)

    @property
    def days_since_epoch(self):
        """Number of days since the local unix epoch."""
        return self.calendar.get_days_since_epoch(
            self.__year_month_day_calendar.to_year_month_day()
        )


class LocalTime:
    def __init__(self, hour: int, minute: int):
        if (
            hour < 0
            or hour > HOURS_PER_DAY - 1
            or minute < 0
            or minute > MINUTES_PER_HOUR - 1
        ):
            Preconditions.check_argument_range(hour, 0, HOURS_PER_DAY - 1)
            Preconditions.check_argument_range(minute, 0, MINUTES_PER_HOUR - 1)
        self.__nanoseconds = (
            hour * NANOSECONDS_PER_HOUR + minute * NANOSECONDS_PER_MINUTE
        )

    @property
    def nanosecond_of_day(self):
        """Gets the nanosecond of this local time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__nanoseconds


class YearMonthDayCalendar:
    # These constants are internal so they can be used in YearMonthDay
    __CALENDAR_BITS = 6  # Up to 64 calendars.
    _DAY_BITS = 6  # Up to 64 days in a month.
    _MONTH_BITS = 5  # Up to 32 months per year.
    __YEAR_BITS = 15  # 32K range; only need -10K to +10K.

    # Just handy constants to use for shifting and masking.
    __CALENDAR_DAY_BITS = __CALENDAR_BITS + _DAY_BITS
    __CALENDAR_DAY_MONTH_BITS = __CALENDAR_DAY_BITS + _MONTH_BITS

    __CALENDAR_MASK = (1 << __CALENDAR_BITS) - 1
    __DAY_MASK = ((1 << _DAY_BITS) - 1) << __CALENDAR_BITS
    __MONTH_MASK = ((1 << _MONTH_BITS) - 1) << __CALENDAR_DAY_BITS
    __YEAR_MASK = ((1 << __YEAR_BITS) - 1) << __CALENDAR_DAY_MONTH_BITS

    def __init__(
        self, year: int, month: int, day: int, calendar_ordinal: CalendarOrdinal
    ):
        self.__value = (
            ((year - 1) << self.__CALENDAR_DAY_MONTH_BITS)
            | ((month - 1) << self.__CALENDAR_DAY_BITS)
            | ((day - 1) << self.__CALENDAR_BITS)
            | int(calendar_ordinal)
        )

    @property
    def calendar_ordinal(self):
        return CalendarOrdinal(self.__value & self.__CALENDAR_MASK)

    def to_year_month_day(self):
        return YearMonthDay(self.__value >> self.__CALENDAR_BITS)


class YearMonthDay:
    __DAY_MASK = (1 << YearMonthDayCalendar._DAY_BITS) - 1
    __MONTH_MASK = (
        (1 << YearMonthDayCalendar._MONTH_BITS) - 1
    ) << YearMonthDayCalendar._DAY_BITS

    def __init__(self, raw_value: int):
        self._value = raw_value

    @property
    def year(self) -> int:
        return (
            self._value
            >> (YearMonthDayCalendar._DAY_BITS + YearMonthDayCalendar._MONTH_BITS)
        ) + 1

    @property
    def month(self) -> int:
        return ((self._value & self.__MONTH_MASK) >> YearMonthDayCalendar._DAY_BITS) + 1

    @property
    def day(self) -> int:
        return (self._value & self.__DAY_MASK) + 1


UNIX_EPOCH: Instant = Instant.from_unix_time_ticks(0)
