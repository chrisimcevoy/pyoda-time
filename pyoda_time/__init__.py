from __future__ import annotations as _annotations

__all__: list[str] = [
    "CalendarSystem",
    "DateAdjusters",
    "DateInterval",
    "DateTimeZone",
    "Duration",
    "Instant",
    "IsoDayOfWeek",
    "LocalDate",
    "LocalTime",
    "LocalDateTime",
    "Offset",
    "OffsetDateTime",
    "OffsetTime",
    "PyodaConstants",
    "ZonedDateTime",
]

import abc as _abc
import datetime as _datetime
import enum as _enum
import typing as _typing

from .calendars import (
    Era as _Era,
)
from .calendars import (
    HebrewMonthNumbering as _HebrewMonthNumbering,
)
from .calendars import (
    IslamicEpoch as _IslamicEpoch,
)
from .calendars import (
    IslamicLeapYearPattern as _IslamicLeapYearPattern,
)
from .calendars import (
    _BadiYearMonthDayCalculator,
    _CopticYearMonthDayCalculator,
    _EraCalculator,
    _GJEraCalculator,
    _GregorianYearMonthDayCalculator,
    _HebrewYearMonthDayCalculator,
    _IslamicYearMonthDayCalculator,
    _JulianYearMonthDayCalculator,
    _PersianYearMonthDayCalculator,
    _SingleEraCalculator,
    _UmAlQuraYearMonthDayCalculator,
    _YearMonthDayCalculator,
)
from .time_zones import ZoneInterval as _ZoneInterval
from .utility import (
    _csharp_modulo,
    _int32_overflow,
    _Preconditions,
    _private,
    _sealed,
    _TickArithmetic,
    _to_ticks,
    _towards_zero_division,
)


class _PyodaConstantsMeta(type):
    """Contains properties of the PyodaConstants class.

    These properties maintain the similarity in our API to that of Noda Time,
    but avoid issues with certain classes not being defined yet when declared
    as class attributes on the `PyodaConstants` class.
    """

    @property
    def BCL_EPOCH(cls) -> Instant:
        return _BCL_EPOCH

    @property
    def UNIX_EPOCH(cls) -> Instant:
        return _UNIX_EPOCH


class PyodaConstants(metaclass=_PyodaConstantsMeta):
    HOURS_PER_DAY: _typing.Final[int] = 24
    SECONDS_PER_MINUTE: _typing.Final[int] = 60
    MINUTES_PER_HOUR: _typing.Final[int] = 60
    MINUTES_PER_DAY: _typing.Final[int] = MINUTES_PER_HOUR * HOURS_PER_DAY
    SECONDS_PER_HOUR: _typing.Final[int] = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
    SECONDS_PER_DAY: _typing.Final[int] = SECONDS_PER_HOUR * HOURS_PER_DAY
    MILLISECONDS_PER_SECOND: _typing.Final[int] = 1000
    MILLISECONDS_PER_MINUTE: _typing.Final[int] = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE
    MILLISECONDS_PER_HOUR: _typing.Final[int] = MILLISECONDS_PER_MINUTE * MINUTES_PER_HOUR
    MILLISECONDS_PER_DAY: _typing.Final[int] = MILLISECONDS_PER_HOUR * HOURS_PER_DAY
    NANOSECONDS_PER_TICK: _typing.Final[int] = 100
    NANOSECONDS_PER_MILLISECOND: _typing.Final[int] = 1000000
    NANOSECONDS_PER_SECOND: _typing.Final[int] = 1000000000
    NANOSECONDS_PER_MINUTE: _typing.Final[int] = NANOSECONDS_PER_SECOND * SECONDS_PER_MINUTE
    NANOSECONDS_PER_HOUR: _typing.Final[int] = NANOSECONDS_PER_MINUTE * MINUTES_PER_HOUR
    NANOSECONDS_PER_DAY: _typing.Final[int] = NANOSECONDS_PER_HOUR * HOURS_PER_DAY
    TICKS_PER_MILLISECOND: _typing.Final[int] = 10_000
    TICKS_PER_SECOND: _typing.Final[int] = TICKS_PER_MILLISECOND * MILLISECONDS_PER_SECOND
    TICKS_PER_MINUTE: _typing.Final[int] = TICKS_PER_SECOND * SECONDS_PER_MINUTE
    TICKS_PER_HOUR: _typing.Final[int] = TICKS_PER_MINUTE * MINUTES_PER_HOUR
    TICKS_PER_DAY: _typing.Final[int] = TICKS_PER_HOUR * HOURS_PER_DAY


class _CalendarOrdinal(_enum.IntEnum):
    """Enumeration of calendar ordinal values.

    Used for converting between a compact integer representation and a calendar system. We use 6 bits to store the
    calendar ordinal in YearMonthDayCalendar, so we can have up to 64 calendars.
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
    ISLAMIC_CIVIL_INDIAN = 15
    ISLAMIC_CIVIL_HABASH_AL_HASIB = 16
    UM_AL_QURA = 17
    BADI = 18
    # Not a real ordinal; just present to keep a count. Increase this as the number increases...
    SIZE = 19


class IsoDayOfWeek(_enum.IntEnum):
    """Equates the days of the week with their numerical value according to ISO-8601."""

    NONE = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class _CalendarSystemMeta(type):
    @property
    def badi(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.BADI)

    @property
    def coptic(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.COPTIC)

    @property
    def gregorian(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.GREGORIAN)

    @property
    def islamic_bcl(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16)

    @property
    def hebrew_civil(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.HEBREW_CIVIL)

    @property
    def hebrew_scriptural(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.HEBREW_SCRIPTURAL)

    @property
    def iso(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.ISO)

    @property
    def julian(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.JULIAN)

    @property
    def persian_arithmetic(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_ARITHMETIC)

    @property
    def persian_astronomical(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_ASTRONOMICAL)

    @property
    def persian_simple(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_SIMPLE)

    @property
    def um_al_qura(cls) -> CalendarSystem:
        return CalendarSystem._for_ordinal(_CalendarOrdinal.UM_AL_QURA)

    @property
    def ids(cls) -> _typing.Iterable[str]:
        """Returns the IDs of all calendar systems available within Pyoda Time.

        The order of the keys is not guaranteed.
        """
        return CalendarSystem._ids()


@_typing.final
@_private
@_sealed
class CalendarSystem(metaclass=_CalendarSystemMeta):
    """Maps the non-calendar-specific "local timeline" to human concepts such as years, months and days.

    Many developers will never need to touch this class, other than to potentially ask a calendar how many days are in a
    particular year/month and the like. Pyoda Time defaults to using the ISO-8601 calendar anywhere that a calendar
    system is required but hasn't been explicitly specified.

    If you need to obtain a CalendarSystem instance, use one of the static properties or methods in this class, such as
    the iso() classmethod or the get_hebrew_calendar(HebrewMonthNumbering)" method.

    Although this class is currently sealed, in the future this decision may be reversed. In any case, there is no
    current intention for third-party developers to be able to implement their own calendar systems (for various
    reasons). If you require a calendar system which is not currently supported, please file a feature request and we'll
    see what we can do.
    """

    # IDs and names are separated out (usually with the ID either being the same as the name,
    # or the base ID being the same as a name and then other IDs being formed from it.) The
    # differentiation is only present for clarity.
    __GREGORIAN_NAME: _typing.Final[str] = "Gregorian"
    __GREGORIAN_ID: _typing.Final[str] = __GREGORIAN_NAME

    __ISO_NAME: _typing.Final[str] = "ISO"
    __ISO_ID: _typing.Final[str] = __ISO_NAME

    __COPTIC_NAME: _typing.Final[str] = "Coptic"
    __COPTIC_ID: _typing.Final[str] = __COPTIC_NAME

    __BADI_NAME: _typing.Final[str] = "Badi"
    __BADI_ID: _typing.Final[str] = __BADI_NAME

    __JULIAN_NAME: _typing.Final[str] = "Julian"
    __JULIAN_ID: _typing.Final[str] = __JULIAN_NAME

    __ISLAMIC_NAME: _typing.Final[str] = "Hijri"
    __ISLAMIC_ID_BASE: _typing.Final[str] = __ISLAMIC_NAME

    @staticmethod
    def _get_islamic_id(base: str, leap_year_pattern: _IslamicLeapYearPattern, epoch: _IslamicEpoch) -> str:
        def to_camel_case(s: str) -> str:
            return "".join(x.capitalize() for x in s.split("_"))

        return f"{base} {to_camel_case(epoch.name)}-{to_camel_case(leap_year_pattern.name)}"

    __PERSIAN_NAME: _typing.Final[str] = "Persian"
    __PERSIAN_ID_BASE: _typing.Final[str] = __PERSIAN_NAME
    __PERSIAN_SIMPLE_ID: _typing.Final[str] = __PERSIAN_ID_BASE + " Simple"
    __PERSIAN_ASTRONOMICAL_ID: _typing.Final[str] = __PERSIAN_ID_BASE + " Algorithmic"
    __PERSIAN_ARITHMETIC_ID: _typing.Final[str] = __PERSIAN_ID_BASE + " Arithmetic"

    __HEBREW_NAME: _typing.Final[str] = "Hebrew"
    __HEBREW_ID_BASE: _typing.Final[str] = __HEBREW_NAME
    __HEBREW_CIVIL_ID: _typing.Final[str] = __HEBREW_ID_BASE + " Civil"
    __HEBREW_SCRIPTURAL_ID: _typing.Final[str] = __HEBREW_ID_BASE + " Scriptural"

    __UM_AL_QURA_NAME: _typing.Final[str] = "Um Al Qura"
    __UM_AL_QURA_ID: _typing.Final[str] = __UM_AL_QURA_NAME

    # While we could implement some of these as auto-props, it probably adds more confusion than convenience.
    __CALENDAR_BY_ORDINAL: _typing.Final[dict[_CalendarOrdinal, CalendarSystem]] = {}

    __ID_ORDINAL_MAP: _typing.Final[dict[str, _CalendarOrdinal]] = {
        __BADI_ID: _CalendarOrdinal.BADI,
        __COPTIC_ID: _CalendarOrdinal.COPTIC,
        __GREGORIAN_ID: _CalendarOrdinal.GREGORIAN,
        __HEBREW_CIVIL_ID: _CalendarOrdinal.HEBREW_CIVIL,
        __HEBREW_SCRIPTURAL_ID: _CalendarOrdinal.HEBREW_SCRIPTURAL,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.BASE15, _IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_BASE15,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.BASE15, _IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.BASE16, _IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_BASE16,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.BASE16, _IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.INDIAN, _IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.INDIAN, _IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.HABASH_AL_HASIB, _IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, _IslamicLeapYearPattern.HABASH_AL_HASIB, _IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_HABASH_AL_HASIB,
        __ISO_ID: _CalendarOrdinal.ISO,
        __JULIAN_ID: _CalendarOrdinal.JULIAN,
        __PERSIAN_SIMPLE_ID: _CalendarOrdinal.PERSIAN_SIMPLE,
        __PERSIAN_ARITHMETIC_ID: _CalendarOrdinal.PERSIAN_ARITHMETIC,
        __PERSIAN_ASTRONOMICAL_ID: _CalendarOrdinal.PERSIAN_ASTRONOMICAL,
        __UM_AL_QURA_ID: _CalendarOrdinal.UM_AL_QURA,
    }

    # region Public factory members for calendars

    @classmethod
    def for_id(cls, id_: str) -> CalendarSystem:
        """Fetches a calendar system by its unique identifier. This provides full round-tripping of a calendar system.
        This method will always return the same reference for the same ID.

        :param id_: The ID of the calendar system. This is case-sensitive.
        :return: The calendar system with the given ID. :exception KeyError: No calendar system for the specified ID can
            be found.
        """
        # TODO: transcribe <exception cref="NotSupportedException" /> in docstring
        _Preconditions._check_not_null(id_, "id_")
        if (ordinal := cls.__ID_ORDINAL_MAP.get(id_)) is None:
            raise KeyError(f"No calendar system for ID {id_} exists")
        return cls._for_ordinal(ordinal)

    @classmethod
    def _for_ordinal(cls, ordinal: _CalendarOrdinal) -> CalendarSystem:
        """Fetches a calendar system by its ordinal value, constructing it if necessary."""

        # TODO Preconditions.DebugCheckArgument

        if calendar := cls.__CALENDAR_BY_ORDINAL.get(ordinal):
            return calendar

        # Not found it in the array. This can happen if the calendar system was initialized in
        # a different thread, and the write to the array isn't visible in this thread yet.
        # A simple switch will do the right thing. This is separated out (directly below) to allow
        # it to be tested separately. (It may also help this method be inlined...) The return
        # statement below is unlikely to ever be hit by code coverage, as it's handling a very
        # unusual and hard-to-provoke situation.
        return cls._for_ordinal_uncached(ordinal)

    @classmethod
    def _ids(cls) -> _typing.Iterable[str]:
        """Returns an iterable of all valid IDs.

        The public static property is implemented in the metaclass. This classmethod just exists to expose the keys of
        the dictionary (internally). This implementation differs somewhat from noda time!
        """
        yield from cls.__ID_ORDINAL_MAP.keys()

    @classmethod
    def get_hebrew_calendar(cls, month_numbering: _HebrewMonthNumbering) -> CalendarSystem:
        _Preconditions._check_argument_range("month_numbering", int(month_numbering), 1, 2)
        match month_numbering:
            case _HebrewMonthNumbering.CIVIL:
                return CalendarSystem.__ctor(
                    ordinal=_CalendarOrdinal.HEBREW_CIVIL,
                    id_=cls.__HEBREW_CIVIL_ID,
                    name=cls.__HEBREW_NAME,
                    year_month_day_calculator=_HebrewYearMonthDayCalculator(month_numbering),
                    single_era=_Era.anno_mundi,
                )
            case _HebrewMonthNumbering.SCRIPTURAL:
                return CalendarSystem.__ctor(
                    ordinal=_CalendarOrdinal.HEBREW_SCRIPTURAL,
                    id_=cls.__HEBREW_SCRIPTURAL_ID,
                    name=cls.__HEBREW_NAME,
                    year_month_day_calculator=_HebrewYearMonthDayCalculator(month_numbering),
                    single_era=_Era.anno_mundi,
                )
            case _:
                raise ValueError(f"Unknown HebrewMonthNumbering: {month_numbering}")

    @classmethod
    def get_islamic_calendar(cls, leap_year_pattern: _IslamicLeapYearPattern, epoch: _IslamicEpoch) -> CalendarSystem:
        _Preconditions._check_argument_range("leap_year_pattern", int(leap_year_pattern), 1, 4)
        _Preconditions._check_argument_range("epoch", int(epoch), 1, 2)
        match (epoch, leap_year_pattern):
            # Civil
            case (_IslamicEpoch.CIVIL, _IslamicLeapYearPattern.BASE15):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_BASE15
            case (_IslamicEpoch.CIVIL, _IslamicLeapYearPattern.BASE16):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_BASE16
            case (_IslamicEpoch.CIVIL, _IslamicLeapYearPattern.INDIAN):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN
            case (_IslamicEpoch.CIVIL, _IslamicLeapYearPattern.HABASH_AL_HASIB):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB
            # Astronomical
            case (_IslamicEpoch.ASTRONOMICAL, _IslamicLeapYearPattern.BASE15):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15
            case (_IslamicEpoch.ASTRONOMICAL, _IslamicLeapYearPattern.BASE16):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16
            case (_IslamicEpoch.ASTRONOMICAL, _IslamicLeapYearPattern.INDIAN):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN
            case (_IslamicEpoch.ASTRONOMICAL, _IslamicLeapYearPattern.HABASH_AL_HASIB):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_HABASH_AL_HASIB
            case _:
                raise KeyError(
                    f"No Islamic Calendar found for leap year pattern {leap_year_pattern.name} and epoch {epoch.name}"
                )
        if ordinal in cls.__CALENDAR_BY_ORDINAL:
            return cls.__CALENDAR_BY_ORDINAL[ordinal]
        calculator = _IslamicYearMonthDayCalculator(leap_year_pattern, epoch)
        return CalendarSystem.__ctor(
            ordinal=ordinal,
            id_=cls._get_islamic_id(cls.__ISLAMIC_ID_BASE, leap_year_pattern=leap_year_pattern, epoch=epoch),
            name=cls.__ISLAMIC_NAME,
            year_month_day_calculator=calculator,
            single_era=_Era.anno_hegirae,
        )

    # endregion

    __ordinal: _typing.Annotated[_CalendarOrdinal, "Set by private constructor"]
    __id: _typing.Annotated[str, "Set by private constructor"]
    __name: _typing.Annotated[str, "Set by private constructor"]
    __year_month_day_calculator: _typing.Annotated[_YearMonthDayCalculator, "Set by private constructor"]
    __era_calculator: _typing.Annotated[_EraCalculator, "Set by private constructor"]
    __min_year: _typing.Annotated[int, "Set by private constructor"]
    __max_year: _typing.Annotated[int, "Set by private constructor"]
    __min_days: _typing.Annotated[int, "Set by private constructor"]
    __max_days: _typing.Annotated[int, "Set by private constructor"]

    @classmethod
    @_typing.overload
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        era_calculator: _EraCalculator,
    ) -> CalendarSystem:
        ...

    @classmethod
    @_typing.overload
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        single_era: _Era,
    ) -> CalendarSystem:
        ...

    @classmethod
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        era_calculator: _EraCalculator | None = None,
        single_era: _Era | None = None,
    ) -> CalendarSystem:
        """Private initialiser which emulates the two private constructors on the corresponding Noda Time class."""
        if ordinal in cls.__CALENDAR_BY_ORDINAL:
            return cls.__CALENDAR_BY_ORDINAL[ordinal]
        self: CalendarSystem = super().__new__(cls)
        self.__ordinal = ordinal
        self.__id = id_
        self.__name = name
        self.__year_month_day_calculator = year_month_day_calculator
        self.__min_year = year_month_day_calculator._min_year
        self.__max_year = year_month_day_calculator._max_year
        self.__min_days = year_month_day_calculator._get_start_of_year_in_days(self.min_year)
        self.__max_days = year_month_day_calculator._get_start_of_year_in_days(self.max_year + 1) - 1

        if era_calculator is None:
            if single_era is None:
                raise TypeError
            era_calculator = _SingleEraCalculator._ctor(era=single_era, ymd_calculator=year_month_day_calculator)

        self.__era_calculator = era_calculator
        self.__CALENDAR_BY_ORDINAL[ordinal] = self
        return self

    @property
    def id(self) -> str:
        """Returns the unique identifier for this calendar system.

        This provides full round-trip capability using for_id() to retrieve the calendar system from the identifier.
        """
        return self.__id

    @property
    def name(self) -> str:
        """The name of this calendar system.

        Each kind of calendar system has a unique name, but this does not usually provide enough information for round-
        tripping. (For example, the name of an Islamic calendar system does not indicate which kind of leap cycle it
        uses.)
        """
        return self.__name

    @property
    def min_year(self) -> int:
        return self.__min_year

    @property
    def max_year(self) -> int:
        return self.__max_year

    @property
    def _min_days(self) -> int:
        return self.__min_days

    @property
    def _max_days(self) -> int:
        return self.__max_days

    @property
    def _ordinal(self) -> _CalendarOrdinal:
        return self.__ordinal

    # region Era-based members

    def eras(self) -> _typing.Iterable[_Era]:
        """Gets a read-only iterable of eras used in this calendar system."""
        yield from self.__era_calculator._eras

    def get_absolute_year(self, year_of_era: int, era: _Era) -> int:
        """Returns the "absolute year" (the one used throughout most of the API, without respect to eras) from a year-
        of-era and an era.

        For example, in the Gregorian and Julian calendar systems, the BCE era starts at year 1, which is equivalent to
        an "absolute year" of 0 (then BCE year 2 has an absolute year of -1, and so on).  The absolute year is the year
        that is used throughout the API; year-of-era is typically used primarily when formatting and parsing date values
        to and from text.

        :param year_of_era: The year within the era.
        :param era: The era in which to consider the year.
        :return: The absolute year represented by the specified year of era.
        """
        return self.__era_calculator._get_absolute_year(year_of_era, era)

    def get_max_year_of_era(self, era: _Era) -> int:
        """Returns the maximum valid year-of-era in the given era.

        Note that depending on the calendar system, it's possible that only part of the returned year falls within the
        given era. It is also possible that the returned value represents the earliest year of the era rather than the
        latest year. (See the BC era in the Gregorian calendar, for example.)

        :param era: The era in which to find the greatest year
        :return: The maximum valid year in the given era. :exception ValueError: era is not an era used in this
            calendar.
        """
        return self.__era_calculator._get_max_year_of_era(era)

    def get_min_year_of_era(self, era: _Era) -> int:
        """Returns the minimum valid year-of-era in the given era.

        Note that depending on the calendar system, it's possible that only part of the returned year falls within the
        given era. It is also possible that the returned value represents the latest year of the era rather than the
        earliest year. (See the BC era in the Gregorian calendar, for example.)

        :param era: The era in which to find the greatest year
        :return: The minimum valid year in the given era. :exception ValueError: era is not an era used in this
            calendar.
        """
        return self.__era_calculator._get_min_year_of_era(era)

    # endregion

    @property
    def _year_month_day_calculator(self) -> _YearMonthDayCalculator:
        return self.__year_month_day_calculator

    def _get_year_month_day_calendar_from_days_since_epoch(self, days_since_epoch: int) -> _YearMonthDayCalendar:
        _Preconditions._check_argument_range("days_since_epoch", days_since_epoch, self._min_days, self._max_days)
        return self._year_month_day_calculator._get_year_month_day(
            days_since_epoch=days_since_epoch
        )._with_calendar_ordinal(self._ordinal)

    # region object overrides

    def __str__(self) -> str:
        """Converts this calendar system to text by simply returning its unique ID."""
        return self.id

    # endregion

    def _get_days_since_epoch(self, year_month_day: _YearMonthDay) -> int:
        """Returns the number of days since the Unix epoch (1970-01-01 ISO) for the given date."""
        return self._year_month_day_calculator._get_days_since_epoch(year_month_day)

    def _get_day_of_week(self, year_month_day: _YearMonthDay) -> IsoDayOfWeek:
        """Returns the IsoDayOfWeek corresponding to the day of week for the given year, month and day.

        :param year_month_day: The year, month and day to use to find the day of the week
        """
        # TODO: DebugValidateYearMonthDay(yearMonthDay);
        days_since_epoch: int = self._year_month_day_calculator._get_days_since_epoch(year_month_day)

        numeric_day_of_week = (
            1 + _csharp_modulo(days_since_epoch + 3, 7)
            if days_since_epoch >= -3
            else 7 + _csharp_modulo(days_since_epoch + 4, 7)
        )

        return IsoDayOfWeek(numeric_day_of_week)

    def get_days_in_year(self, year: int) -> int:
        """Returns the number of days in the given year.

        :param year: The year to determine the number of days in.
        :return: The number of days in the given year.
        """
        _Preconditions._check_argument_range("year", year, self.__min_year, self.__max_year)
        return self._year_month_day_calculator._get_days_in_year(year)

    def get_days_in_month(self, year: int, month: int) -> int:
        """Returns the number of days in the given month within the given year.

        :param year: The year in which to consider the month.
        :param month: The month to determine the number of days in.
        :return: The number of days in the given month and year.
        """
        # Simplest way to validate the year and month. Assume it's quick enough to validate the day...
        self._validate_year_month_day(year, month, 1)
        return self._year_month_day_calculator._get_days_in_month(year, month)

    def is_leap_year(self, year: int) -> bool:
        """Returns True if the given year is a leap year in this calendar."""
        _Preconditions._check_argument_range("year", year, self.__min_year, self.__max_year)
        return self._year_month_day_calculator._is_leap_year(year)

    def get_months_in_year(self, year: int) -> int:
        """Returns the maximum valid month (inclusive) within this calendar in the given year.

        It is assumed that in all calendars, every month between 1 and this month number is valid for the given year.
        This does not necessarily mean that the first month of the year is 1, however. (See the Hebrew calendar system
        using the scriptural month numbering system for example.)

        :param year: The year to consider.
        :return: The maximum month number within the given year.
        """
        _Preconditions._check_argument_range("year", year, self.__min_year, self.__max_year)
        return self._year_month_day_calculator._get_months_in_year(year)

    def _validate_year_month_day(self, year: int, month: int, day: int) -> None:
        self._year_month_day_calculator._validate_year_month_day(year, month, day)

    def _compare(self, lhs: _YearMonthDay, rhs: _YearMonthDay) -> int:
        # TODO: DebugValidateYearMonthDay(lhs)
        # TODO: DebugValidateYearMonthDay(rhs)
        return self._year_month_day_calculator.compare(lhs, rhs)

    # region "Getter" methods which used to be a DateTimeField

    def _get_day_of_year(self, year_month_day: _YearMonthDay) -> int:
        # TODO DebugValidateYearMonthDay(yearMonthDay)
        return self._year_month_day_calculator._get_day_of_year(year_month_day)

    def _get_year_of_era(self, absolute_year: int) -> int:
        # TODO: _Preconditions._debug_check_argument_range()
        return self.__era_calculator._get_year_of_era(absolute_year)

    def _get_era(self, absolute_year: int) -> _Era:
        # TODO: _Preconditions._debug_check_argument_range()
        return self.__era_calculator._get_era(absolute_year)

    # endregion

    @classmethod
    def _for_ordinal_uncached(cls, ordinal: _CalendarOrdinal) -> CalendarSystem:
        # pyoda-time-specic implementation note:
        # This lookup is just in case this method is called directly
        # This shouldn't be the case, but we need to ensure that these are
        # effectively singletons.
        if (calendar := cls.__CALENDAR_BY_ORDINAL.get(ordinal)) is not None:
            return calendar

        match ordinal:
            case _CalendarOrdinal.BADI:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__BADI_ID,
                    name=cls.__BADI_NAME,
                    year_month_day_calculator=_BadiYearMonthDayCalculator(),
                    single_era=_Era.bahai,
                )
            case _CalendarOrdinal.COPTIC:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__COPTIC_ID,
                    name=cls.__COPTIC_NAME,
                    year_month_day_calculator=_CopticYearMonthDayCalculator(),
                    single_era=_Era.anno_martyrum,
                )
            case _CalendarOrdinal.GREGORIAN:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__GREGORIAN_ID,
                    name=cls.__GREGORIAN_NAME,
                    year_month_day_calculator=cls.iso._year_month_day_calculator,
                    era_calculator=cls.iso.__era_calculator,
                )
            case _CalendarOrdinal.HEBREW_CIVIL:
                return cls.get_hebrew_calendar(_HebrewMonthNumbering.CIVIL)
            case _CalendarOrdinal.HEBREW_SCRIPTURAL:
                return cls.get_hebrew_calendar(_HebrewMonthNumbering.SCRIPTURAL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_BASE15:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.BASE15, _IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_BASE16:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.BASE16, _IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.INDIAN, _IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.HABASH_AL_HASIB, _IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.BASE15, _IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.BASE16, _IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.INDIAN, _IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_HABASH_AL_HASIB:
                return cls.get_islamic_calendar(_IslamicLeapYearPattern.HABASH_AL_HASIB, _IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISO:
                gregorian_calculator = _GregorianYearMonthDayCalculator()
                gregorian_era_calculator = _GJEraCalculator(gregorian_calculator)
                return CalendarSystem.__ctor(
                    ordinal=ordinal,
                    id_=cls.__ISO_ID,
                    name=cls.__ISO_NAME,
                    year_month_day_calculator=gregorian_calculator,
                    era_calculator=gregorian_era_calculator,
                )
            case _CalendarOrdinal.JULIAN:
                julian_calculator = _JulianYearMonthDayCalculator()
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__JULIAN_ID,
                    name=cls.__JULIAN_NAME,
                    year_month_day_calculator=julian_calculator,
                    era_calculator=_GJEraCalculator(julian_calculator),
                )
            case _CalendarOrdinal.PERSIAN_ARITHMETIC:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__PERSIAN_ARITHMETIC_ID,
                    name=cls.__PERSIAN_NAME,
                    year_month_day_calculator=_PersianYearMonthDayCalculator.Arithmetic(),
                    single_era=_Era.anno_persico,
                )
            case _CalendarOrdinal.PERSIAN_ASTRONOMICAL:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__PERSIAN_ASTRONOMICAL_ID,
                    name=cls.__PERSIAN_NAME,
                    year_month_day_calculator=_PersianYearMonthDayCalculator.Astronomical(),
                    single_era=_Era.anno_persico,
                )
            case _CalendarOrdinal.PERSIAN_SIMPLE:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__PERSIAN_SIMPLE_ID,
                    name=cls.__PERSIAN_NAME,
                    year_month_day_calculator=_PersianYearMonthDayCalculator.Simple(),
                    single_era=_Era.anno_persico,
                )
            case _CalendarOrdinal.UM_AL_QURA:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__UM_AL_QURA_ID,
                    name=cls.__UM_AL_QURA_NAME,
                    year_month_day_calculator=_UmAlQuraYearMonthDayCalculator(),
                    single_era=_Era.anno_hegirae,
                )
            case _:
                raise RuntimeError(
                    f"CalendarOrdinal '{getattr(ordinal, "name", ordinal)}' not mapped to CalendarSystem."
                )


class DateAdjusters:
    # TODO: In Noda Time, these are properties which return functions. Any reason not to just use staticmethod?

    @staticmethod
    def end_of_month(date: LocalDate) -> LocalDate:
        """A date adjuster to move to the last day of the current month."""
        return LocalDate(
            year=date.year,
            month=date.month,
            day=date.calendar.get_days_in_month(date.year, date.month),
            calendar=date.calendar,
        )


@_sealed
class DateInterval:
    """An interval between two dates."""

    @property
    def start(self) -> LocalDate:
        """The start date of the interval."""
        return self.__start

    @property
    def end(self) -> LocalDate:
        """The end date of the interval."""
        return self.__end

    def __init__(self, start: LocalDate, end: LocalDate) -> None:
        """Constructs a date interval from a start date and an end date, both of which are included in the interval.

        :param start: Start date of the interval
        :param end: End date of the interval
        """
        _Preconditions._check_argument(
            start.calendar == end.calendar, "end", "Calendars of start and end dates must be the same."
        )
        _Preconditions._check_argument(not end < start, "end", "End date must not be earlier than the start date")
        self.__start: LocalDate = start
        self.__end: LocalDate = end


class _DateTimeZoneMeta(_abc.ABCMeta):
    @property
    def utc(cls) -> DateTimeZone:
        return _FixedDateTimeZone(Offset.zero)


class DateTimeZone(_abc.ABC, metaclass=_DateTimeZoneMeta):
    """Represents a time zone - a mapping between UTC and local time.
    A time zone maps UTC instants to local times - or, equivalently, to the offset from UTC at any particular instant.
    """

    _UTC_ID: _typing.Final[str] = "UTC"

    def __init__(self, id_: str, is_fixed: bool, min_offset: Offset, max_offset: Offset) -> None:
        """Initializes a new instance of the DateTimeZone class.

        :param id_: The unique id of this time zone.
        :param is_fixed: Set to True is this time zone has no transitions.
        :param min_offset: Minimum offset applied with this zone
        :param max_offset: Maximum offset applied with this zone
        """
        self.__id: str = _Preconditions._check_not_null(id_, "id_")
        self.__is_fixed: bool = is_fixed
        self.__min_offset: Offset = min_offset
        self.__max_offset: Offset = max_offset

    @property
    def id(self) -> str:
        """The provider's ID for the time zone.

        This identifies the time zone within the current time zone provider; a different provider may provide a
        different time zone with the same ID, or may not provide a time zone with that ID at all.
        """
        return self.__id

    @property
    def _is_fixed(self) -> bool:
        """Indicates whether the time zone is fixed, i.e. contains no transitions.

        This is used as an optimization. If the time zone has no transitions but returns False for this then the
        behavior will be correct but the system will have to do extra work. However if the time zone has transitions and
        this returns <c>true</c> then the transitions will never be examined.
        """
        return self.__is_fixed

    @property
    def min_offset(self) -> Offset:
        """The least (most negative) offset within this time zone, over all time."""
        return self.__min_offset

    @property
    def max_offset(self) -> Offset:
        """The greatest (most positive) offset within this time zone, over all time."""
        return self.__max_offset

    # region Core abstract/virtual methods

    def get_utc_offset(self, instant: Instant) -> Offset:
        return self.get_zone_interval(instant).wall_offset

    @_abc.abstractmethod
    def get_zone_interval(self, instant: Instant) -> _ZoneInterval:
        raise NotImplementedError

    # endregion


@_typing.final
@_sealed
class Duration:
    """Represents a fixed (and calendar-independent) length of time."""

    _MAX_DAYS: _typing.Final[int] = (1 << 24) - 1
    _MIN_DAYS: _typing.Final[int] = ~_MAX_DAYS

    def __init__(self) -> None:
        self.__days = 0
        self.__nano_of_day = 0

    @classmethod
    def _ctor(cls, *, days: int, nano_of_day: int) -> Duration:
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            _Preconditions._check_argument_range("days", days, cls._MIN_DAYS, cls._MAX_DAYS)
        # TODO: _Precondition._debug_check_argument_range()
        self = super().__new__(cls)
        self.__days = days
        self.__nano_of_day = nano_of_day
        return self

    @classmethod
    @_typing.overload
    def __ctor(
        cls,
        *,
        units: int,
        param_name: str,
        min_value: int,
        max_value: int,
        units_per_day: int,
        nanos_per_unit: int,
    ) -> Duration:
        """Constructs an instance from a given number of units.

        This was previously a method (FromUnits) but making it a constructor avoids calling the other constructor which
        validates its "days" parameter. Note that we could compute various parameters from nanosPerUnit, but we know
        them as compile-time constants, so there's no point in recomputing them on each call.
        """
        ...

    @classmethod
    @_typing.overload
    def __ctor(cls, *, days: int, nano_of_day: int, no_validation: bool) -> Duration:
        """Trusted constructor with no validation.

        The value of the noValidation parameter is ignored completely; its name is just to be suggestive.
        """
        ...

    @classmethod
    def __ctor(
        cls,
        *,
        days: int | None = None,
        nano_of_day: int | None = None,
        no_validation: bool | None = None,
        units: int | None = None,
        param_name: str | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
        units_per_day: int | None = None,
        nanos_per_unit: int | None = None,
    ) -> Duration:
        """Internal constructor implementation."""
        self = super().__new__(cls)
        if days is not None and nano_of_day is not None and no_validation is not None:
            self.__days = days
            self.__nano_of_day = nano_of_day
        elif (
            units is not None
            and param_name is not None
            and min_value is not None
            and max_value is not None
            and units_per_day is not None
            and nanos_per_unit is not None
        ):
            self.__days = _towards_zero_division(units, units_per_day)
            unit_of_day = units - (units_per_day * self.__days)
            if unit_of_day < 0:
                self.__days -= 1
                unit_of_day += units_per_day
            self.__nano_of_day = unit_of_day * nanos_per_unit
        else:
            raise TypeError
        return self

    def __le__(self, other: Duration) -> bool:
        if isinstance(other, Duration):
            return self < other or self == other
        return NotImplemented

    def __lt__(self, other: Duration) -> bool:
        if isinstance(other, Duration):
            return self.__days < other.__days or (
                self.__days == other.__days and self.__nano_of_day < other.__nano_of_day
            )
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Duration):
            return self.__days == other.__days and self.__nano_of_day == other.__nano_of_day
        return NotImplemented

    def __neg__(self) -> Duration:
        old_days = self.__days
        old_nano_of_day = self.__nano_of_day
        if old_nano_of_day == 0:
            return Duration._ctor(days=-old_days, nano_of_day=0)
        new_nano_of_day = PyodaConstants.NANOSECONDS_PER_DAY - old_nano_of_day
        return Duration._ctor(days=-old_days - 1, nano_of_day=new_nano_of_day)

    @staticmethod
    def from_ticks(ticks: int) -> Duration:
        """Returns a Duration that represents the given number of ticks."""
        days, tick_of_day = _TickArithmetic.ticks_to_days_and_tick_of_day(ticks)
        return Duration._ctor(days=days, nano_of_day=tick_of_day * PyodaConstants.NANOSECONDS_PER_TICK)

    @staticmethod
    def zero() -> Duration:
        """Gets a zero Duration of 0 nanoseconds."""
        return Duration()

    @property
    def _floor_days(self) -> int:
        """Days portion of this duration."""
        return self.__days

    @property
    def _nanosecond_of_floor_day(self) -> int:
        """Nanosecond within the "floor day".

        This is *always* non-negative, even for negative durations.
        """
        return self.__nano_of_day

    @classmethod
    def from_milliseconds(cls, milliseconds: int) -> Duration:
        """Returns a Duration that represents the given number of milliseconds."""
        return cls.__ctor(
            units=milliseconds,
            param_name="milliseconds",
            min_value=cls._MIN_DAYS * PyodaConstants.MILLISECONDS_PER_DAY,
            max_value=((cls._MAX_DAYS + 1) * PyodaConstants.MILLISECONDS_PER_DAY) - 1,
            units_per_day=PyodaConstants.MILLISECONDS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_MILLISECOND,
        )

    @classmethod
    def from_seconds(cls, seconds: int) -> Duration:
        return cls.__ctor(
            units=seconds,
            param_name="seconds",
            min_value=cls._MIN_DAYS * PyodaConstants.SECONDS_PER_DAY,
            max_value=cls._MAX_DAYS + 1,
            units_per_day=PyodaConstants.SECONDS_PER_DAY,
            nanos_per_unit=PyodaConstants.NANOSECONDS_PER_SECOND,
        )

    def __add__(self, other: Duration) -> Duration:
        if isinstance(other, Duration):
            days = self.__days + other.__days
            nanos = self.__nano_of_day + other.__nano_of_day
            if nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nanos -= PyodaConstants.NANOSECONDS_PER_DAY
            return Duration._ctor(days=days, nano_of_day=nanos)
        return NotImplemented

    def __sub__(self, other: Duration) -> Duration:
        if isinstance(other, Duration):
            days = self.__days - other.__days
            nanos = self.__nano_of_day - other.__nano_of_day
            if nanos < 0:
                days -= 1
                nanos += PyodaConstants.NANOSECONDS_PER_DAY
            return Duration._ctor(days=days, nano_of_day=nanos)
        return NotImplemented

    @classmethod
    def epsilon(cls) -> Duration:
        """Return a Duration representing 1 nanosecond.

        This is the smallest amount by which an instant can vary.
        """
        return cls._ctor(days=0, nano_of_day=1)

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int) -> Duration:  # TODO from_nanoseconds overrides
        """Returns a Duration that represents the given number of nanoseconds."""
        if nanoseconds >= 0:
            # TODO Is divmod compatible with C# integer division?
            quotient, remainder = divmod(nanoseconds, PyodaConstants.NANOSECONDS_PER_DAY)
            return cls._ctor(days=quotient, nano_of_day=remainder)

        # Work out the "floor days"; division truncates towards zero and
        # nanoseconds is definitely negative by now, hence the addition and subtraction here.
        days = _towards_zero_division(nanoseconds + 1, PyodaConstants.NANOSECONDS_PER_DAY) - 1
        nano_of_day = nanoseconds - days * PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=days, nano_of_day=nano_of_day)

    @classmethod
    def from_hours(cls, hours: int) -> Duration:
        """Returns a Duration that represents the given number of hours."""
        # TODO this is a shortcut and differs from Noda Time
        return Duration.from_seconds(hours * PyodaConstants.SECONDS_PER_HOUR)

    def _plus_small_nanoseconds(self, small_nanos: int) -> Duration:
        """Adds a "small" number of nanoseconds to this duration.

        It is trusted to be less or equal to than 24 hours in magnitude.
        """
        _Preconditions._check_argument_range(
            "small_nanos", small_nanos, -PyodaConstants.NANOSECONDS_PER_DAY, PyodaConstants.NANOSECONDS_PER_DAY
        )
        new_days = self.__days
        new_nanos = self.__nano_of_day + small_nanos
        if new_nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
            new_days += 1
            new_nanos -= PyodaConstants.NANOSECONDS_PER_DAY
        elif new_nanos < 0:
            new_days -= 1
            new_nanos += PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=new_days, nano_of_day=new_nanos)

    def _minus_small_nanoseconds(self, small_nanos: int) -> Duration:
        # TODO: unchecked
        # TODO: Preconditions.DebugCheckArgumentRange
        new_days = self.__days
        new_nanos = self.__nano_of_day - small_nanos
        if new_nanos >= PyodaConstants.NANOSECONDS_PER_DAY:
            new_days += 1
            new_nanos -= PyodaConstants.NANOSECONDS_PER_DAY
        elif new_nanos < 0:
            new_days -= 1
            new_nanos += PyodaConstants.NANOSECONDS_PER_DAY
        return Duration._ctor(days=new_days, nano_of_day=new_nanos)

    def __hash__(self) -> int:
        return self.__days ^ hash(self.__nano_of_day)


@_sealed
@_typing.final
class _FixedDateTimeZone(DateTimeZone):
    def __init__(self, offset: Offset, id_: str | None = None, name: str | None = None) -> None:
        if id_ is None:
            id_ = self.__make_id(offset)
        if name is None:
            name = id_
        super().__init__(id_, True, offset, offset)
        self.__interval = _ZoneInterval(
            name=name,
            start=Instant._before_min_value(),
            end=Instant._after_max_value(),
            wall_offset=offset,
            savings=Offset.zero,
        )

    def __make_id(self, offset: Offset) -> str:
        if offset == Offset.zero:
            return self._UTC_ID
        return self._UTC_ID + str(offset)

    @classmethod
    def _get_fixed_zone_or_null(cls, id_: str) -> DateTimeZone | None:
        if not id_.startswith(cls._UTC_ID):
            return None
        if id_ == cls._UTC_ID:
            return cls.utc
        # TODO: requires OffsetPattern
        raise NotImplementedError("OffsetPattern is required")

    def get_zone_interval(self, instant: Instant) -> _ZoneInterval:
        return self.__interval

    def get_utc_offset(self, instant: Instant) -> Offset:
        return self.max_offset


class _OffsetMeta(type):
    @property
    def zero(self) -> Offset:
        """An offset of zero seconds - effectively the permanent offset for UTC."""
        return Offset.from_seconds(0)

    @property
    def min_value(self) -> Offset:
        """The minimum permitted offset; 18 hours before UTC."""
        return Offset.from_hours(-18)

    @property
    def max_value(self) -> Offset:
        """The maximum permitted offset; 18 hours after UTC."""
        return Offset.from_hours(18)


@_typing.final
@_sealed
class Offset(metaclass=_OffsetMeta):
    """An offset from UTC in seconds."""

    __MIN_HOURS: _typing.Final[int] = -18
    __MAX_HOURS: _typing.Final[int] = 18
    __MIN_SECONDS: _typing.Final[int] = -18 * PyodaConstants.SECONDS_PER_HOUR
    __MAX_SECONDS: _typing.Final[int] = 18 * PyodaConstants.SECONDS_PER_HOUR
    __MIN_MILLISECONDS: _typing.Final[int] = -18 * PyodaConstants.MILLISECONDS_PER_HOUR
    __MAX_MILLISECONDS: _typing.Final[int] = 18 * PyodaConstants.MILLISECONDS_PER_HOUR
    __MIN_TICKS: _typing.Final[int] = -18 * PyodaConstants.TICKS_PER_HOUR
    __MAX_TICKS: _typing.Final[int] = 18 * PyodaConstants.TICKS_PER_HOUR
    __MIN_NANOSECONDS: _typing.Final[int] = -18 * PyodaConstants.NANOSECONDS_PER_HOUR
    __MAX_NANOSECONDS: _typing.Final[int] = 18 * PyodaConstants.NANOSECONDS_PER_HOUR

    def __init__(self) -> None:
        self.__seconds = 0

    @classmethod
    def _ctor(cls, *, seconds: int) -> Offset:
        """Internal constructor."""
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        self = super().__new__(cls)
        self.__seconds = seconds
        return self

    @property
    def seconds(self) -> int:
        """Gets the number of seconds represented by this offset, which may be negative."""
        return self.__seconds

    @property
    def milliseconds(self) -> int:
        """Gets the number of milliseconds represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 1,000 to give the
        number of milliseconds.
        """
        return self.__seconds * PyodaConstants.MILLISECONDS_PER_SECOND

    @property
    def ticks(self) -> int:
        """Gets the number of ticks represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 10,000,000 to give
        the number of ticks.
        """
        return self.__seconds * PyodaConstants.TICKS_PER_SECOND

    @property
    def nanoseconds(self) -> int:
        """Gets the number of nanoseconds represented by this offset, which may be negative.

        Offsets are only accurate to second precision; the number of seconds is simply multiplied by 1,000,000,000 to
        give the number of nanoseconds.
        """
        return self.__seconds * PyodaConstants.NANOSECONDS_PER_SECOND

    @staticmethod
    def max(x: Offset, y: Offset) -> Offset:
        """Returns the greater offset of the given two, i.e. the one which will give a later local time when added to an
        instant.

        :param x: The first offset
        :param y: The second offset
        :return: The greater offset of x and y.
        """
        return x if x > y else y

    @staticmethod
    def min(x: Offset, y: Offset) -> Offset:
        """Returns the lower offset of the given two, i.e. the one which will give an earlier local time when added to
        an instant.

        :param x: The first offset
        :param y: The second offset
        :return: The lower offset of x and y.
        """
        return x if x < y else y

    # region Operators

    def __neg__(self) -> Offset:
        """Implements the unary operator - (negation).

        :return: A new ``Offset`` instance with a negated value.
        """
        # Guaranteed to still be in range.
        return Offset._ctor(seconds=-self.seconds)

    @staticmethod
    def negate(offset: Offset) -> Offset:
        """Returns the negation of the specified offset. This is the method form of the unary minus operator.

        :param offset: The offset to negate.
        :return: The negation of the specified offset.
        """
        return -offset

    def __pos__(self) -> Offset:
        """Implements the unary operator + .

        :return: The same ``Offset`` instance

        There is no method form of this operator; the ``plus`` method is an instance
        method for addition, and is more useful than a method form of this would be.
        """
        return self

    def __add__(self, other: Offset) -> Offset:
        """Implements the operator + (addition).

        :param other: The offset to add.
        :return: A new ``Offset`` representing the sum of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        if isinstance(other, Offset):
            return self.from_seconds(self.seconds + other.seconds)
        return NotImplemented

    @staticmethod
    def add(left: Offset, right: Offset) -> Offset:
        """Adds one Offset to another. Friendly alternative to ``+``.

        :param left: The left hand side of the operator.
        :param right: The right hand side of the operator.
        :return: A new ``Offset`` representing the sum of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return left + right

    def plus(self, other: Offset) -> Offset:
        """Returns the result of adding another Offset to this one, for a fluent alternative to ``+``.

        :param other: The offset to add
        :return: THe result of adding the other offset to this one.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return self + other

    def __sub__(self, other: Offset) -> Offset:
        """Implements the operator - (subtraction).

        :param other: The offset to subtract.
        :return: A new ``Offset`` representing the difference of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        if isinstance(other, Offset):
            return self.from_seconds(self.seconds - other.seconds)
        return NotImplemented

    @staticmethod
    def subtract(minuend: Offset, subtrahend: Offset) -> Offset:
        """Subtracts one Offset from another. Friendly alternative to ``-``.

        :param minuend: The left hand side of the operator.
        :param subtrahend: The right hand side of the operator.
        :return: A new ``Offset`` representing the difference of the given values.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return minuend - subtrahend

    def minus(self, other: Offset) -> Offset:
        """Returns the result of subtracting another Offset from this one, for a fluent alternative to ``-``.

        :param other: The offset to subtract
        :return: The result of subtracting the other offset from this one.
        :raises ValueError: The result of the operation is outside the range of Offset.
        """
        return self - other

    def __eq__(self, other: object) -> bool:
        """Implements the operator == (equality). See the type documentation for a description of equality semantics.

        :param other: The object to compare this one to for equality.
        :return: ``True`` if values are equal to each other, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.equals(other)

    def __ne__(self, other: object) -> bool:
        """Implements the operator != (inequality). See the type documentation for a description of equality semantics.

        :param other: The object to compare with this one.
        :return: ``True`` if values are not equal to each other, otherwise ``False``.
        """
        return not (self == other)

    def __lt__(self, other: Offset | None) -> bool:
        """Implements the operator ``<`` (less than). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is less than ``other``, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.compare_to(other) < 0

    def __le__(self, other: Offset) -> bool:
        """Implements the operator ``<=`` (less than or equal). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is less than or equal to ``other``, otherwise ``False``.
        """
        return isinstance(other, Offset) and self.compare_to(other) <= 0

    def __gt__(self, other: Offset | None) -> bool:
        """Implements the operator ``>`` (greater than). See the type documentation for a description of ordering
        semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is greater than ``other``, otherwise ``False``.
        """
        return other is None or (isinstance(other, Offset) and self.compare_to(other) > 0)

    def __ge__(self, other: Offset) -> bool:
        """Implements the operator ``>=`` (greater than or equal). See the type documentation for a description of
        ordering semantics.

        :param other: The offset to compare with this one.
        :return: ``True`` if this offset is greater than or equal to ``other``, otherwise ``False``.
        """
        return other is None or (isinstance(other, Offset) and self.compare_to(other) >= 0)

    # endregion

    # region IComparable<Offset> Members

    def compare_to(self, other: Offset) -> int:
        """Compares the current object with another object of the same type. See the type documentation for a
        description of ordering semantics.

        :param other: An object to compare with this object.
        :return: An integer that indicates the relative order of the objects being compared.
        :exception TypeError: An object of an incompatible type was passed to this method.

        The return value has the following meanings:

        =====  ======
        Value  Meaning
        =====  ======
        < 0    This object is less than the ``other`` parameter.
        0      This object is equal to ``other``.
        > 0    This object is greater than ``other``.
        =====  ======
        """
        if not isinstance(other, Offset):
            raise TypeError(f"Offset can only be compared_to another Offset, not {other.__class__.__name__}")
        return self.seconds - other.seconds

    # endregion

    # region IEquatable<Offset> Members

    def equals(self, other: Offset) -> bool:
        """Indicates whether the current object is equal to another object of the same type. See the type documentation
        for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: true if the current object is equal to the ``other`` parameter; otherwise, false.
        """
        return self.seconds == other.seconds

    # endregion

    # region object overrides

    def __hash__(self) -> int:
        return hash(self.seconds)

    # endregion

    # region Construction

    @classmethod
    def from_seconds(cls, seconds: int) -> Offset:
        """Returns an offset for the given seconds value, which may be negative.

        :param seconds: The int seconds value.
        :return: An offset representing the given number of seconds.
        :raises ValueError: The specified number of seconds is outside the range of [-18, +18] hours.
        """
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        return cls._ctor(seconds=seconds)

    @classmethod
    def from_milliseconds(cls, milliseconds: int) -> Offset:
        """Returns an offset for the given milliseconds value, which may be negative.

        :param milliseconds: The int milliseconds value.
        :return: An offset representing the given number of milliseconds, to the (truncated) second.
        :raises ValueError: The specified number of milliseconds is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of milliseconds is simply divided by 1,000 to
        give the number of seconds - any remainder is truncated.
        """
        _Preconditions._check_argument_range(
            "milliseconds", milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS
        )
        return cls._ctor(seconds=_towards_zero_division(milliseconds, PyodaConstants.MILLISECONDS_PER_SECOND))

    @classmethod
    def from_ticks(cls, ticks: int) -> Offset:
        """Returns an offset for the given number of ticks, which may be negative.

        :param ticks: The number of ticks specifying the length of the new offset.
        :return: An offset representing the given number of ticks, to the (truncated) second.
        :raises ValueError: The specified number of ticks is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of ticks is simply divided
        by 10,000,000 to give the number of seconds - any remainder is truncated.
        """
        _Preconditions._check_argument_range("ticks", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return cls._ctor(seconds=_towards_zero_division(ticks, PyodaConstants.TICKS_PER_SECOND))

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int) -> Offset:
        """Returns an offset for the given number of nanoseconds, which may be negative.

        :param nanoseconds: The number of nanoseconds specifying the length of the new offset.
        :return: An offset representing the given number of nanoseconds, to the (truncated) second.
        :raises ValueError: The specified number of nanoseconds is outside the range of [-18, +18] hours.

        Offsets are only accurate to second precision; the given number of nanoseconds is simply divided by
        1,000,000,000 to give the number of seconds - any remainder is truncated towards zero.
        """
        _Preconditions._check_argument_range("nanoseconds", nanoseconds, cls.__MIN_NANOSECONDS, cls.__MAX_NANOSECONDS)
        return cls._ctor(seconds=_towards_zero_division(nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND))

    @classmethod
    def from_hours(cls, hours: int) -> Offset:
        """Returns an offset for the specified number of hours, which may be negative.

        :param hours: The number of hours to represent in the new offset.
        :return: An offset representing the given value.
        :raises ValueError: The specified number of hours is outside the range of [-18, +18].
        """
        _Preconditions._check_argument_range("hours", hours, cls.__MIN_HOURS, cls.__MAX_HOURS)
        return cls._ctor(seconds=hours * PyodaConstants.SECONDS_PER_HOUR)

    @classmethod
    def from_hours_and_minutes(cls, hours: int, minutes: int) -> Offset:
        """Returns an offset for the specified number of hours and minutes.

        :param hours: The number of hours to represent in the new offset.
        :param minutes: The number of minutes to represent in the new offset.
        :return: An offset representing the given value.
        :raises ValueError: The result of the operation is outside the range of Offset.

        The result simply takes the hours and minutes and converts each component into milliseconds
        separately. As a result, a negative offset should usually be obtained by making both arguments
        negative. For example, to obtain "three hours and ten minutes behind UTC" you might call
        ``Offset.from_hours_and_minutes(-3, -10)``.
        """
        return cls.from_seconds(hours * PyodaConstants.SECONDS_PER_HOUR + minutes * PyodaConstants.SECONDS_PER_MINUTE)

    # endregion

    # region Conversion

    def to_timedelta(self) -> _datetime.timedelta:
        """Converts this offset to a stdlib ``datetime.timedelta`` value.

        :return: An equivalent ``datetime.timedelta`` to this value.
        """
        return _datetime.timedelta(seconds=self.seconds)

    @classmethod
    def from_timedelta(cls, timedelta: _datetime.timedelta) -> Offset:
        """Converts the given ``timedelta`` to an offset, with fractional seconds truncated.

        :param timedelta: The timedelta to convert
        :returns: An offset for the same time as the given time span. :exception ValueError: The given timedelta falls
            outside the range of +/- 18 hours.
        """
        # TODO: Consider introducing a "from_microseconds" constructor?

        # Convert to ticks first, then divide that float by 1 using our special
        # function to convert to a rounded-towards-zero int.
        ticks = _towards_zero_division(timedelta.total_seconds() * PyodaConstants.TICKS_PER_SECOND, 1)
        _Preconditions._check_argument_range("timedelta", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Offset.from_ticks(ticks)

    # endregion

    # region XML serialization

    # TODO: XML serialization???

    # endregion

    def __str__(self) -> str:
        hours = int(self.seconds / PyodaConstants.SECONDS_PER_HOUR)
        symbol = "+" if hours >= 0 else "-"
        return "Z" if self == Offset.zero else f"{symbol}{hours:0>2}"


class OffsetDateTime:
    def __init__(self, local_date_time: LocalDateTime, offset: Offset) -> None:
        self.__local_date = local_date_time.date
        self.__offset_time = OffsetTime._ctor(
            nanosecond_of_day=local_date_time.nanosecond_of_day, offset_seconds=offset.seconds
        )

    @classmethod
    @_typing.overload
    def _ctor(cls, *, local_date: LocalDate, offset_time: OffsetTime) -> OffsetDateTime:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, instant: Instant, offset: Offset) -> OffsetDateTime:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, instant: Instant, offset: Offset, calendar: CalendarSystem) -> OffsetDateTime:
        ...

    @classmethod
    def _ctor(
        cls,
        *,
        local_date: LocalDate | None = None,
        offset_time: OffsetTime | None = None,
        instant: Instant | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> OffsetDateTime:
        if instant is not None and offset is not None:
            days = instant._days_since_epoch
            nano_of_day = instant._nanosecond_of_day + offset.nanoseconds
            if nano_of_day >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nano_of_day -= PyodaConstants.NANOSECONDS_PER_DAY
            elif nano_of_day < 0:
                days -= 1
                nano_of_day += PyodaConstants.NANOSECONDS_PER_DAY
            local_date = (
                LocalDate._ctor(days_since_epoch=days)
                if calendar is None
                else LocalDate._ctor(days_since_epoch=days, calendar=calendar)
            )
            offset_time = OffsetTime._ctor(nanosecond_of_day=nano_of_day, offset_seconds=offset.seconds)
        if local_date is not None and offset_time is not None:
            self = super().__new__(cls)
            self.__local_date = local_date
            self.__offset_time = offset_time
            return self
        raise TypeError

    @property
    def nanosecond_of_day(self) -> int:
        return self.__offset_time.nanosecond_of_day

    @property
    def local_date_time(self) -> LocalDateTime:
        return LocalDateTime._ctor(local_date=self.date, local_time=self.time_of_day)

    @property
    def date(self) -> LocalDate:
        return self.__local_date

    @property
    def time_of_day(self) -> LocalTime:
        return LocalTime._ctor(nanoseconds=self.nanosecond_of_day)


class OffsetTime:
    __NANOSECONDS_BITS: _typing.Final[int] = 47
    __NANOSECONDS_MASK: _typing.Final[int] = (1 << __NANOSECONDS_BITS) - 1

    def __init__(self, time: LocalTime, offset: Offset) -> None:
        nanosecond_of_day = time.nanosecond_of_day
        offset_seconds = offset.seconds
        self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)

    @classmethod
    @_typing.overload
    def _ctor(cls, *, nanosecond_of_day_zero_offset: int) -> OffsetTime:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, nanosecond_of_day: int, offset_seconds: int) -> OffsetTime:
        ...

    @classmethod
    def _ctor(
        cls,
        *,
        nanosecond_of_day_zero_offset: int | None = None,
        nanosecond_of_day: int | None = None,
        offset_seconds: int | None = None,
    ) -> OffsetTime:
        self = super().__new__(cls)
        if nanosecond_of_day_zero_offset is not None:
            # TODO: Preconditions.DebugCheckArgument
            self.__nanoseconds_and_offset = nanosecond_of_day_zero_offset
        elif nanosecond_of_day is not None and offset_seconds is not None:
            self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)
        else:
            raise ValueError
        return self

    @property
    def nanosecond_of_day(self) -> int:
        return self.__nanoseconds_and_offset & self.__NANOSECONDS_MASK


@_typing.final
@_sealed
class Instant:
    """Represents an instant on the global timeline, with nanosecond resolution.

    An Instant has no concept of a particular time zone or calendar: it simply represents a point in
    time that can be globally agreed-upon.
    Equality and ordering comparisons are defined in the natural way, with earlier points on the timeline
    being considered "less than" later points.
    """

    # These correspond to -9998-01-01 and 9999-12-31 respectively.
    _MIN_DAYS: _typing.Final[int] = -4371222
    _MAX_DAYS: _typing.Final[int] = 2932896

    __MIN_TICKS: _typing.Final[int] = _MIN_DAYS * PyodaConstants.TICKS_PER_DAY
    __MAX_TICKS: _typing.Final[int] = (_MAX_DAYS + 1) * PyodaConstants.TICKS_PER_DAY - 1
    __MIN_MILLISECONDS: _typing.Final[int] = _MIN_DAYS * PyodaConstants.MILLISECONDS_PER_DAY
    __MAX_MILLISECONDS: _typing.Final[int] = (_MAX_DAYS + 1) * PyodaConstants.MILLISECONDS_PER_DAY - 1
    __MIN_SECONDS: _typing.Final[int] = _MIN_DAYS * PyodaConstants.SECONDS_PER_DAY
    __MAX_SECONDS: _typing.Final[int] = (_MAX_DAYS + 1) * PyodaConstants.SECONDS_PER_DAY - 1

    def __init__(self) -> None:
        self.__duration = Duration.zero()

    @classmethod
    def _ctor(cls, *, days: int, nano_of_day: int) -> Instant:
        self = super().__new__(cls)
        self.__duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        return self

    @classmethod
    @_typing.overload
    def __ctor(cls, *, duration: Duration) -> Instant:
        """Constructor which constructs a new instance with the given duration, which is trusted to be valid.

        Should only be called from FromTrustedDuration and FromUntrustedDuration.
        """
        ...

    @classmethod
    @_typing.overload
    def __ctor(cls, *, days: int, deliberately_invalid: bool) -> Instant:
        """Constructor which should *only* be used to construct the invalid instances."""
        ...

    @classmethod
    def __ctor(
        cls, duration: Duration | None = None, days: int | None = None, deliberately_invalid: bool | None = None
    ) -> Instant:
        """Private constructors implementation."""
        self = super().__new__(cls)
        if duration is not None and days is None and deliberately_invalid is None:
            self.__duration = duration
        elif duration is None and days is not None and deliberately_invalid is not None:
            self.__duration = Duration._ctor(days=days, nano_of_day=0)
        else:
            raise TypeError
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Instant):
            return self.__duration == other.__duration
        return NotImplemented

    def __lt__(self, other: Instant) -> bool:
        if isinstance(other, Instant):
            return self.__duration < other.__duration
        return NotImplemented

    def __le__(self, other: Instant) -> bool:
        if isinstance(other, Instant):
            return self < other or self == other
        return NotImplemented

    def __add__(self, other: Duration) -> Instant:
        if isinstance(other, Duration):
            return self._from_untrusted_duration(self.__duration + other)
        return NotImplemented

    @_typing.overload
    def __sub__(self, other: Instant) -> Duration:
        ...

    @_typing.overload
    def __sub__(self, other: Duration) -> Instant:
        ...

    def __sub__(self, other: Instant | Duration) -> Instant | Duration:
        if isinstance(other, Instant):
            return self.__duration - other.__duration
        if isinstance(other, Duration):
            return self._from_trusted_duration(self.__duration - other)
        return NotImplemented

    @classmethod
    def min_value(cls) -> Instant:
        """Represents the smallest possible Instant.

        This value is equivalent to -9998-01-01T00:00:00Z
        """
        return Instant._ctor(days=cls._MIN_DAYS, nano_of_day=0)

    @classmethod
    def max_value(cls) -> Instant:
        """Represents the largest possible Instant.

        This value is equivalent to 9999-12-31T23:59:59.999999999Z
        """
        return Instant._ctor(days=cls._MAX_DAYS, nano_of_day=PyodaConstants.NANOSECONDS_PER_DAY - 1)

    @classmethod
    def _before_min_value(cls) -> _typing.Self:
        """Instant which is invalid *except* for comparison purposes; it is earlier than any valid value.

        This must never be exposed.
        """
        return cls.__ctor(days=Duration._MIN_DAYS, deliberately_invalid=True)

    @classmethod
    def _after_max_value(cls) -> _typing.Self:
        """Instant which is invalid *except* for comparison purposes; it is later than any valid value.

        This must never be exposed.
        """
        return cls.__ctor(days=Duration._MAX_DAYS, deliberately_invalid=True)

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.__duration._floor_days

    @classmethod
    def from_unix_time_ticks(cls, ticks: int) -> Instant:
        """Initializes a new Instant based on a number of ticks since the Unix epoch."""
        _Preconditions._check_argument_range("ticks", ticks, cls.__MIN_TICKS, cls.__MAX_TICKS)
        return Instant._from_trusted_duration(Duration.from_ticks(ticks))

    @classmethod
    def _from_trusted_duration(cls, duration: Duration) -> Instant:
        """Creates an Instant with the given duration, with no validation (in release mode)."""
        # TODO Preconditions.DebugCheckArgumentRange
        return Instant.__ctor(duration=duration)

    @classmethod
    def _from_untrusted_duration(cls, duration: Duration) -> Instant:
        """Creates an Instant with the given duration, validating that it has a suitable "day" part.

        (It is assumed that the nanoOfDay is okay.)
        """
        days = duration._floor_days
        if days < cls._MIN_DAYS or days > cls._MAX_DAYS:
            raise OverflowError("Operation would overflow range of Instant")
        return Instant.__ctor(duration=duration)

    def to_unix_time_ticks(self) -> int:
        """Gets the number of ticks since the Unix epoch.

        Negative values represent instants before the Unix epoch. A tick is equal to 100 nanoseconds. There are 10,000
        ticks in a millisecond. If the number of nanoseconds in this instant is not an exact number of ticks, the value
        is truncated towards the start of time.
        """
        return _TickArithmetic.bounded_days_and_tick_of_day_to_ticks(
            self.__duration._floor_days,
            _towards_zero_division(self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_TICK),
        )

    @classmethod
    def from_unix_time_milliseconds(cls, milliseconds: int) -> Instant:
        """Initializes a new Instant struct based on a number of milliseconds since the Unix epoch of (ISO) January 1st
        1970, midnight, UTC."""
        _Preconditions._check_argument_range(
            "milliseconds", milliseconds, cls.__MIN_MILLISECONDS, cls.__MAX_MILLISECONDS
        )
        return Instant._from_trusted_duration(Duration.from_milliseconds(milliseconds))

    @classmethod
    def from_unix_time_seconds(cls, seconds: int) -> Instant:
        """Initializes a new Instant based on a number of seconds since the Unix epoch of (ISO) January 1st 1970,
        midnight, UTC."""
        _Preconditions._check_argument_range("seconds", seconds, cls.__MIN_SECONDS, cls.__MAX_SECONDS)
        return cls._from_trusted_duration(Duration.from_seconds(seconds))

    def to_unix_time_seconds(self) -> int:
        """Gets the number of seconds since the Unix epoch.

        Negative values represent instants before the Unix epoch. If the number of nanoseconds in this instant is not an
        exact number of seconds, the value is truncated towards the start of time.
        """
        return self.__duration._floor_days * PyodaConstants.SECONDS_PER_DAY + _towards_zero_division(
            self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_SECOND
        )

    def to_unix_time_milliseconds(self) -> int:
        """Gets the number of milliseconds since the Unix epoch.

        Negative values represent instants before the Unix epoch. If the number of nanoseconds in this instant is not an
        exact number of milliseconds, the value is truncated towards the start of time.
        """
        return self.__duration._floor_days * PyodaConstants.MILLISECONDS_PER_DAY + _towards_zero_division(
            self.__duration._nanosecond_of_floor_day, PyodaConstants.NANOSECONDS_PER_MILLISECOND
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
    def from_datetime_utc(cls, datetime: _datetime.datetime) -> Instant:
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
        return PyodaConstants.BCL_EPOCH.plus_ticks(_to_ticks(datetime))

    @classmethod
    def from_utc(
        cls,
        year: int,
        month_of_year: int,
        day_of_month: int,
        hour_of_day: int,
        minute_of_hour: int,
        second_of_minute: int = 0,
    ) -> Instant:
        """Returns a new Instant corresponding to the given UTC date and time in the ISO calendar.

        In most cases applications should use ZonedDateTime to represent a date and time, but this method is useful in
        some situations where an Instant is required, such as time zone testing.
        """
        days = LocalDate(year=year, month=month_of_year, day=day_of_month)._days_since_epoch
        nano_of_day = LocalTime(hour=hour_of_day, minute=minute_of_hour, second=second_of_minute).nanosecond_of_day
        return Instant._ctor(days=days, nano_of_day=nano_of_day)

    def __hash__(self) -> int:
        return hash(self.__duration)

    def plus_ticks(self, ticks: int) -> Instant:
        """Returns a new value of this instant with the given number of ticks added to it."""
        return self._from_untrusted_duration(self.__duration + Duration.from_ticks(ticks))

    def plus_nanoseconds(self, nanoseconds: int) -> Instant:
        return self._from_untrusted_duration(self.__duration + Duration.from_nanoseconds(nanoseconds))

    @property
    def _is_valid(self) -> bool:
        """Returns whether or not this is a valid instant.

        Returns true for all but before_min_value and after_max_value.
        """
        return self._MIN_DAYS <= self._days_since_epoch <= self._MAX_DAYS

    def _plus(self, offset: Offset) -> _LocalInstant:
        """Adds the given offset to this instant, to return a LocalInstant.

        A positive offset indicates that the local instant represents a "later local time" than the UTC representation
        of this instant.
        """
        return _LocalInstant._ctor(nanoseconds=self.__duration._plus_small_nanoseconds(offset.nanoseconds))

    def plus(self, other: Duration) -> Instant:
        """Returns the result of adding a duration to this instant, for a fluent alternative to the + operator."""
        return self + other

    def _safe_plus(self, offset: Offset) -> _LocalInstant:
        """Adds the given offset to this instant, either returning a normal LocalInstant, or
        LocalInstant.before_min_value() or LocalInstant.after_max_value() if the value would overflow."""
        days = self.__duration._floor_days
        if self._MIN_DAYS < days < self._MAX_DAYS:
            return self._plus(offset)
        if days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        as_duration = self.__duration._plus_small_nanoseconds(offset.nanoseconds)
        if as_duration._floor_days < self._MIN_DAYS:
            return _LocalInstant.before_min_value()
        if as_duration._floor_days > self._MAX_DAYS:
            return _LocalInstant.after_max_value()
        return _LocalInstant._ctor(nanoseconds=as_duration)

    def in_zone(self, zone: DateTimeZone, calendar: CalendarSystem) -> ZonedDateTime:
        _Preconditions._check_not_null(zone, "zone")
        _Preconditions._check_not_null(calendar, "calendar")
        return ZonedDateTime(instant=self, zone=zone, calendar=calendar)

    @property
    def _nanosecond_of_day(self) -> int:
        return self.__duration._nanosecond_of_floor_day

    def in_utc(self) -> ZonedDateTime:
        offset_date_time = OffsetDateTime._ctor(
            local_date=LocalDate._ctor(days_since_epoch=self.__duration._floor_days),
            offset_time=OffsetTime._ctor(nanosecond_of_day_zero_offset=self.__duration._nanosecond_of_floor_day),
        )
        return ZonedDateTime._ctor(offset_date_time=offset_date_time, zone=DateTimeZone.utc)

    def __str__(self) -> str:
        if not self._is_valid:
            if self == self._before_min_value():
                # TODO: Instant._before_min_value.__str__()
                return super().__str__()
            if self == self._after_max_value():
                # TODO: Instant._after_max_value.__str__()
                return super().__str__()
        ldt = self.in_utc().local_date_time
        return f"{ldt.year:0>4}-{ldt.month:0>2}-{ldt.day:0>2}T{ldt.hour:0>2}:{ldt.minute:0>2}:{ldt.second:0>2}Z"


@_typing.final
@_sealed
class _LocalInstant:
    """Represents a local date and time without reference to a calendar system. Essentially.

    this is a duration since a Unix epoch shifted by an offset (but we don't store what that
    offset is). This class has been slimmed down considerably over time - it's used much less
    than it used to be... almost solely for time zones.
    """

    @classmethod
    def before_min_value(cls) -> _LocalInstant:
        # TODO: In Noda Time this is a public static readonly field
        return _LocalInstant.__ctor(days=Instant._before_min_value()._days_since_epoch, deliberately_invalid=True)

    @classmethod
    def after_max_value(cls) -> _LocalInstant:
        # TODO: In Noda Time this is a public static readonly field
        return _LocalInstant.__ctor(days=Instant._after_max_value()._days_since_epoch, deliberately_invalid=True)

    def __init__(self) -> None:
        self.__duration = Duration()

    @classmethod
    @_typing.overload
    def _ctor(cls, *, nanoseconds: Duration) -> _LocalInstant:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, days: int, nano_of_day: int) -> _LocalInstant:
        ...

    @classmethod
    def _ctor(cls, nanoseconds: Duration | None = None, days: int | None = None, nano_of_day: int = 0) -> _LocalInstant:
        self = super().__new__(cls)
        if nanoseconds is not None:
            days = nanoseconds._floor_days
            if days < Instant._MIN_DAYS or days > Instant._MAX_DAYS:
                raise OverflowError("Operation would overflow bounds of local date/time")
            self.__duration = nanoseconds
        elif days is not None:
            self.__duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        else:
            raise TypeError
        return self

    @classmethod
    def __ctor(cls, *, days: int, deliberately_invalid: bool) -> _LocalInstant:
        """Constructor which should *only* be used to construct the invalid instances."""
        self = super().__new__(cls)
        self.__duration = Duration._ctor(days=days, nano_of_day=0)
        return self

    @property
    def _is_valid(self) -> bool:
        return Instant._MIN_DAYS < self._days_since_epoch < Instant._MAX_DAYS

    @property
    def _time_since_local_epoch(self) -> Duration:
        """Number of nanoseconds since the local unix epoch."""
        return self.__duration

    @property
    def _days_since_epoch(self) -> int:
        return self.__duration._floor_days

    @property
    def _nanosecond_of_day(self) -> int:
        return self.__duration._nanosecond_of_floor_day

    # region Operators

    def minus(self, offset: Offset) -> Instant:
        return Instant._from_untrusted_duration(self.__duration._minus_small_nanoseconds(offset.nanoseconds))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _LocalInstant):
            return self.__duration == other.__duration
        return NotImplemented

    def __lt__(self, other: _LocalInstant) -> bool:
        if isinstance(other, _LocalInstant):
            return self.__duration < other.__duration
        return NotImplemented

    def __le__(self, other: _LocalInstant) -> bool:
        if isinstance(other, _LocalInstant):
            return self.__duration <= other.__duration
        return NotImplemented

    # endregion

    # region Object overrides

    # endregion

    # region IEquatable<LocalInstant> Members

    # endregion


@_typing.final
@_sealed
class LocalDate:
    """LocalDate is an immutable struct representing a date within the calendar, with no reference to a particular time
    zone or time of day."""

    @_typing.overload
    def __init__(self) -> None:
        ...

    @_typing.overload
    def __init__(self, *, year: int, month: int, day: int):
        ...

    @_typing.overload
    def __init__(self, *, year: int, month: int, day: int, calendar: CalendarSystem):
        ...

    @_typing.overload
    def __init__(self, *, era: _Era, year_of_era: int, month: int, day: int):
        ...

    @_typing.overload
    def __init__(self, *, era: _Era, year_of_era: int, month: int, day: int, calendar: CalendarSystem):
        ...

    def __init__(
        self,
        year: int = 1,
        month: int = 1,
        day: int = 1,
        calendar: CalendarSystem | None = None,
        era: _Era | None = None,
        year_of_era: int | None = None,
    ):
        calendar = calendar or CalendarSystem.iso

        if era is not None and year_of_era is not None and month is not None and day is not None:
            year = calendar.get_absolute_year(year_of_era, era)

        if year is not None and month is not None and day is not None:
            calendar._validate_year_month_day(year, month, day)
            self.__year_month_day_calendar = _YearMonthDayCalendar._ctor(
                year=year, month=month, day=day, calendar_ordinal=calendar._ordinal
            )
        else:
            raise TypeError

    @classmethod
    @_typing.overload
    def _ctor(cls, *, year_month_day_calendar: _YearMonthDayCalendar) -> LocalDate:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, days_since_epoch: int) -> LocalDate:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, days_since_epoch: int, calendar: CalendarSystem) -> LocalDate:
        ...

    @classmethod
    def _ctor(
        cls,
        *,
        year_month_day_calendar: _YearMonthDayCalendar | None = None,
        days_since_epoch: int | None = None,
        calendar: CalendarSystem | None = None,
    ) -> LocalDate:
        self = super().__new__(cls)
        if year_month_day_calendar is not None:
            self.__year_month_day_calendar = year_month_day_calendar
        elif days_since_epoch is not None:
            if calendar is None:
                self.__year_month_day_calendar = (
                    _GregorianYearMonthDayCalculator._get_gregorian_year_month_day_calendar_from_days_since_epoch(
                        days_since_epoch
                    )
                )
            else:
                self.__year_month_day_calendar = calendar._get_year_month_day_calendar_from_days_since_epoch(
                    days_since_epoch
                )
        else:
            raise TypeError
        return self

    @property
    def calendar(self) -> CalendarSystem:
        """The calendar system associated with this local date."""
        return CalendarSystem._for_ordinal(self.__calendar_ordinal)

    @property
    def __calendar_ordinal(self) -> _CalendarOrdinal:
        return self.__year_month_day_calendar._calendar_ordinal

    @property
    def year(self) -> int:
        """The year of this local date.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.
        """
        return self.__year_month_day_calendar._year

    @property
    def month(self) -> int:
        """The month of this local date within the year."""
        return self.__year_month_day_calendar._month

    @property
    def day(self) -> int:
        return self.__year_month_day_calendar._day

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.calendar._get_days_since_epoch(self.__year_month_day_calendar._to_year_month_day())

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """The week day of this local date expressed as an ``IsoDayOfWeek``."""
        return self.calendar._get_day_of_week(self._year_month_day)

    @property
    def year_of_era(self) -> int:
        """The year of this local date within the era."""
        return self.calendar._get_year_of_era(self.__year_month_day_calendar._year)

    @property
    def era(self) -> _Era:
        """The era of this local date."""
        return self.calendar._get_era(self.__year_month_day_calendar._year)

    @property
    def day_of_year(self) -> int:
        """The day of this local date within the year."""
        return self.calendar._get_day_of_year(self._year_month_day)

    @property
    def _year_month_day(self) -> _YearMonthDay:
        return self.__year_month_day_calendar._to_year_month_day()

    def __add__(self, other: LocalTime) -> LocalDateTime:
        # TODO: overload for LocalDate + Period
        if isinstance(other, LocalTime):
            return LocalDateTime._ctor(local_date=self, local_time=other)
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LocalDate):
            return self.__year_month_day_calendar == other.__year_month_day_calendar
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, LocalDate):
            return not self == other
        return NotImplemented

    def __lt__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) < 0
        return NotImplemented

    def __le__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) <= 0

    def __gt__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) > 0
        return NotImplemented

    def __ge__(self, other: LocalDate) -> bool:
        if isinstance(other, LocalDate):
            _Preconditions._check_argument(
                self.__calendar_ordinal == other.__calendar_ordinal,
                "other",
                "Only values in the same calendar can be compared",
            )
            return self.__trusted_compare_to(other) >= 0

    def __trusted_compare_to(self, other: LocalDate) -> int:
        """Performs a comparison with another date, trusting that the calendar of the other date is already correct.

        This avoids duplicate calendar checks.
        """
        return self.calendar._compare(self._year_month_day, other._year_month_day)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDate:
        """Creates a new LocalDate representing the same physical date, but in a different calendar.

        The returned LocalDate is likely to have different field values to this one. For example, January 1st 1970 in
        the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this local date to.
        :return: The converted LocalDate
        """
        _Preconditions._check_not_null(calendar, "calendar")
        return LocalDate._ctor(days_since_epoch=self._days_since_epoch, calendar=calendar)

    def plus_years(self, years: int) -> LocalDate:
        """Returns a new LocalDate representing the current value with the given number of years added.

        If the resulting date is invalid, lower fields (typically the day of month) are reduced to find a valid value.
        For example, adding one year to February 29th 2012 will return February 28th 2013; subtracting one year from
        February 29th 2012 will return February 28th 2011.

        :param years: The number of years to add.
        :return: The current value plus the given number of years.
        """
        from .fields import _DatePeriodFields

        return _DatePeriodFields._years_field.add(self, years)

    def plus_months(self, months: int) -> LocalDate:
        """Returns a new LocalDate representing the current value with the given number of months added.

        This method does not try to maintain the year of the current value, so adding four months to a value in October
        will result in a value in the following February.

        If the resulting date is invalid, the day of month is reduced to find a valid value. For example, adding one
        month to January 30th 2011 will return February 28th 2011; subtracting one month from March 30th 2011 will
        return February 28th 2011.

        :param months: The number of months to add
        :return: The current date plus the given number of months
        """
        from .fields import _DatePeriodFields

        return _DatePeriodFields._months_field.add(self, months)

    def plus_days(self, days: int) -> LocalDate:
        from .fields import _DatePeriodFields

        return _DatePeriodFields._days_field.add(self, days)

    def at(self, time: LocalTime) -> LocalDateTime:
        """Combines this <see ``LocalDate`` with the given ``LocalTime`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param time: The time to combine with this date.
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return self + time

    # region Formatting

    # TODO: def __str__(self): [requires LocalDatePattern.BclSupport]

    # endregion


@_typing.final
@_sealed
class LocalTime:
    """LocalTime is an immutable struct representing a time of day, with no reference to a particular calendar, time
    zone or date."""

    @_typing.overload
    def __init__(self, *, hour: int, minute: int) -> None:
        ...

    @_typing.overload
    def __init__(self, *, hour: int, minute: int, second: int) -> None:
        ...

    @_typing.overload
    def __init__(self, *, hour: int, minute: int, second: int, millisecond: int) -> None:
        ...

    def __init__(self, *, hour: int, minute: int, second: int = 0, millisecond: int = 0):
        if (
            hour < 0
            or hour > PyodaConstants.HOURS_PER_DAY - 1
            or minute < 0
            or minute > PyodaConstants.MINUTES_PER_HOUR - 1
            or second < 0
            or second > PyodaConstants.SECONDS_PER_MINUTE - 1
            or millisecond < 0
            or millisecond > PyodaConstants.MILLISECONDS_PER_SECOND - 1
        ):
            _Preconditions._check_argument_range("hour", hour, 0, PyodaConstants.HOURS_PER_DAY - 1)
            _Preconditions._check_argument_range("minute", minute, 0, PyodaConstants.MINUTES_PER_HOUR - 1)
            _Preconditions._check_argument_range("second", second, 0, PyodaConstants.SECONDS_PER_MINUTE - 1)
            _Preconditions._check_argument_range(
                "millisecond", millisecond, 0, PyodaConstants.MILLISECONDS_PER_SECOND - 1
            )
        self.__nanoseconds = (
            hour * PyodaConstants.NANOSECONDS_PER_HOUR
            + minute * PyodaConstants.NANOSECONDS_PER_MINUTE
            + second * PyodaConstants.NANOSECONDS_PER_SECOND
            + millisecond * PyodaConstants.NANOSECONDS_PER_MILLISECOND
        )

    @classmethod
    def _ctor(cls, *, nanoseconds: int) -> LocalTime:
        """Constructor only called from other parts of Noda Time - trusted to be the range [0, NanosecondsPerDay)."""
        # TODO: _Preconditions._check_debug_argument_range()
        self = super().__new__(cls)
        self.__nanoseconds = nanoseconds
        return self

    @classmethod
    def from_nanoseconds_since_midnight(cls, nanoseconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of nanoseconds which have elapsed since midnight.

        :param nanoseconds: The number of nanoseconds, in the range [0, 86,399,999,999,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if nanoseconds < 0 or nanoseconds > PyodaConstants.NANOSECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range("nanoseconds", nanoseconds, 0, PyodaConstants.NANOSECONDS_PER_DAY - 1)
        return LocalTime._ctor(nanoseconds=nanoseconds)

    @classmethod
    def from_ticks_since_midnight(cls, ticks: int) -> LocalTime:
        """Factory method for creating a local time from the number of ticks which have elapsed since midnight.

        :param ticks: The number of ticks, in the range [0, 863,999,999,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if ticks < 0 or ticks > PyodaConstants.TICKS_PER_DAY - 1:
            _Preconditions._check_argument_range("ticks", ticks, 0, PyodaConstants.TICKS_PER_DAY - 1)
        return LocalTime._ctor(nanoseconds=_int32_overflow(ticks * PyodaConstants.NANOSECONDS_PER_TICK))

    @classmethod
    def from_milliseconds_since_midnight(cls, milliseconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of milliseconds which have elapsed since midnight.

        :param milliseconds: The number of milliseconds, in the range [0, 86,399,999]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if milliseconds < 0 or milliseconds > PyodaConstants.MILLISECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range(
                "milliseconds", milliseconds, 0, PyodaConstants.MILLISECONDS_PER_DAY - 1
            )
        return cls._ctor(nanoseconds=_int32_overflow(milliseconds * PyodaConstants.NANOSECONDS_PER_MILLISECOND))

    @classmethod
    def from_seconds_since_midnight(cls, seconds: int) -> LocalTime:
        """Factory method for creating a local time from the number of seconds which have elapsed since midnight.

        :param seconds: The number of seconds, in the range [0, 86,399]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if seconds < 0 or seconds > PyodaConstants.SECONDS_PER_DAY - 1:
            _Preconditions._check_argument_range("seconds", seconds, 0, PyodaConstants.SECONDS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(seconds * PyodaConstants.NANOSECONDS_PER_SECOND))

    @classmethod
    def from_minutes_since_midnight(cls, minutes: int) -> LocalTime:
        """Factory method for creating a local time from the number of minutes which have elapsed since midnight.

        :param minutes: The number of minutes, in the range [0, 1439]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if minutes < 0 or minutes > PyodaConstants.MINUTES_PER_DAY - 1:
            _Preconditions._check_argument_range("minutes", minutes, 0, PyodaConstants.MINUTES_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(minutes * PyodaConstants.NANOSECONDS_PER_MINUTE))

    @classmethod
    def from_hours_since_midnight(cls, hours: int) -> LocalTime:
        """Factory method for creating a local time from the number of hours which have elapsed since midnight.

        :param hours: The number of hours, in the range [0, 23]
        :return: The resulting time.
        """
        # Avoid the method calls which give a decent exception unless we're actually going to fail.
        if hours < 0 or hours > PyodaConstants.HOURS_PER_DAY - 1:
            _Preconditions._check_argument_range("hours", hours, 0, PyodaConstants.HOURS_PER_DAY - 1)
        return cls._ctor(nanoseconds=_int32_overflow(hours * PyodaConstants.NANOSECONDS_PER_HOUR))

    @property
    def hour(self) -> int:
        """The hour of day of this local time, in the range 0 to 23 inclusive."""
        # Effectively nanoseconds / NanosecondsPerHour, but apparently rather more efficient.
        return _towards_zero_division((self.__nanoseconds >> 13), 439453125)

    @property
    def clock_hour_of_half_day(self) -> int:
        """The hour of the half-day of this local time, in the range 1 to 12 inclusive."""
        # TODO: unchecked
        hour_of_half_day = _int32_overflow(_csharp_modulo(self.hour, 12))
        return 12 if hour_of_half_day == 0 else hour_of_half_day

    @property
    def minute(self) -> int:
        """The minute of this local time, in the range 0 to 59 inclusive."""
        # TODO: unchecked
        # Effectively nanoseconds / NanosecondsPerMinute, but apparently rather more efficient.
        minute_of_day = _towards_zero_division((self.__nanoseconds >> 11), 29296875)
        return _csharp_modulo(minute_of_day, PyodaConstants.MINUTES_PER_HOUR)

    @property
    def second(self) -> int:
        """The second of this local time within the minute, in the range 0 to 59 inclusive."""
        # TODO: unchecked
        second_of_day = _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND)
        return _csharp_modulo(second_of_day, PyodaConstants.SECONDS_PER_MINUTE)

    @property
    def millisecond(self) -> int:
        """The millisecond of this local time within the second, in the range 0 to 999 inclusive."""
        # TODO: unchecked
        millisecond_of_day = _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_MILLISECOND)
        return _csharp_modulo(millisecond_of_day, PyodaConstants.MILLISECONDS_PER_SECOND)

    @property
    def tick_of_second(self) -> int:
        """The tick of this local time within the second, in the range 0 to 9,999,999 inclusive."""
        # TODO: unchecked
        return _int32_overflow(_csharp_modulo(self.tick_of_day, PyodaConstants.TICKS_PER_SECOND))

    @property
    def tick_of_day(self) -> int:
        """The tick of this local time within the day, in the range 0 to 863,999,999,999 inclusive.

        If the value does not fall on a tick boundary, it will be truncated towards zero.
        """
        return _towards_zero_division(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_TICK)

    @property
    def nanosecond_of_second(self) -> int:
        """The nanosecond of this local time within the second, in the range 0 to 999,999,999 inclusive."""
        # TODO: unchecked
        return _int32_overflow(_csharp_modulo(self.__nanoseconds, PyodaConstants.NANOSECONDS_PER_SECOND))

    @property
    def nanosecond_of_day(self) -> int:
        """The nanosecond of this local time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__nanoseconds

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LocalTime):
            return self.__nanoseconds == other.__nanoseconds
        return NotImplemented

    def on(self, date: LocalDate) -> LocalDateTime:
        """Combines this ``LocalTime`` with the given ``LocalDate`` into a single ``LocalDateTime``.

        Fluent alternative to ``+``.

        :param date: The date to combine with this time
        :return: The ``LocalDateTime`` representation of the given time on this date.
        """
        return date + self


class _LocalDateTimeMeta(type):
    pass


@_typing.final
@_sealed
class LocalDateTime(metaclass=_LocalDateTimeMeta):
    def __init__(
        self,
        year: int = 1,
        month: int = 1,
        day: int = 1,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        millisecond: int = 0,
        calendar: CalendarSystem = CalendarSystem.iso,
    ) -> None:
        self.__date = LocalDate(year=year, month=month, day=day, calendar=calendar)
        self.__time = LocalTime(hour=hour, minute=minute, second=second, millisecond=millisecond)

    @classmethod
    @_typing.overload
    def _ctor(cls, *, local_instant: _LocalInstant) -> LocalDateTime:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, local_date: LocalDate, local_time: LocalTime) -> LocalDateTime:
        ...

    @classmethod
    def _ctor(
        cls,
        *,
        local_instant: _LocalInstant | None = None,
        local_date: LocalDate | None = None,
        local_time: LocalTime | None = None,
    ) -> LocalDateTime:
        self = super().__new__(cls)
        if local_instant is not None and local_time is None and local_date is None:
            self.__date = LocalDate._ctor(days_since_epoch=local_instant._days_since_epoch)
            self.__time = LocalTime._ctor(nanoseconds=local_instant._nanosecond_of_day)
        elif local_instant is None and local_date is not None and local_time is not None:
            self.__date = local_date
            self.__time = local_time
        else:
            raise TypeError
        return self

    @property
    def year(self) -> int:
        """The year of this local date and time.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.
        """
        return self.__date.year

    @property
    def year_of_era(self) -> int:
        """The year of this local date and time within its era."""
        return self.__date.year_of_era

    @property
    def era(self) -> _Era:
        """The era of this local date and time."""
        return self.__date.era

    @property
    def month(self) -> int:
        """The month of this local date and time within the year."""
        return self.__date.month

    @property
    def day_of_year(self) -> int:
        """The day of this local date and time within the year."""
        return self.__date.day_of_year

    @property
    def day(self) -> int:
        """The day of this local date and time within the month."""
        return self.__date.day

    @property
    def day_of_week(self) -> IsoDayOfWeek:
        """The week day of this local date and time expressed as an ``IsoDayOfWeek``."""
        return self.__date.day_of_week

    @property
    def hour(self) -> int:
        """The hour of day of this local date and time, in the range 0 to 23 inclusive."""
        return self.__time.hour

    @property
    def clock_hour_of_half_day(self) -> int:
        """The hour of the half-day of this local date and time, in the range 1 to 12 inclusive."""
        return self.__time.clock_hour_of_half_day

    @property
    def minute(self) -> int:
        """The minute of this local date and time, in the range 0 to 59 inclusive."""
        return self.__time.minute

    @property
    def second(self) -> int:
        """The second of this local date and time within the minute, in the range 0 to 59 inclusive."""
        return self.__time.second

    @property
    def millisecond(self) -> int:
        """The millisecond of this local date and time within the second, in the range 0 to 999 inclusive."""
        return self.__time.millisecond

    @property
    def tick_of_second(self) -> int:
        """The tick of this local time within the second, in the range 0 to 9,999,999 inclusive."""
        return self.__time.tick_of_second

    @property
    def tick_of_day(self) -> int:
        """The tick of this local date and time within the day, in the range 0 to 863,999,999,999 inclusive."""
        return self.__time.tick_of_day

    @property
    def nanosecond_of_second(self) -> int:
        """The nanosecond of this local time within the second, in the range 0 to 999,999,999 inclusive."""
        return self.__time.nanosecond_of_second

    @property
    def nanosecond_of_day(self) -> int:
        """The nanosecond of this local date and time within the day, in the range 0 to 86,399,999,999,999 inclusive."""
        return self.__time.nanosecond_of_day

    @property
    def time_of_day(self) -> LocalTime:
        """The time portion of this local date and time as a ``LocalTime``."""
        return self.__time

    @property
    def date(self) -> LocalDate:
        """The date portion of this local date and time as a ``LocalDate``."""
        return self.__date

    # TODO def to_datetime_unspecified(self):

    def _to_local_instant(self) -> _LocalInstant:
        return _LocalInstant._ctor(days=self.date._days_since_epoch, nano_of_day=self.__time.nanosecond_of_day)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDateTime:
        """Creates a new LocalDateTime representing the same physical date and time, but in a different calendar. The
        returned LocalDateTime is likely to have different date field values to this one. For example, January 1st 1970
        in the Gregorian calendar was December 19th 1969 in the Julian calendar.

        :param calendar: The calendar system to convert this local date to.
        :return: The converted LocalDateTime.
        """
        _Preconditions._check_not_null(calendar, "calendar")
        return LocalDateTime._ctor(local_date=self.date.with_calendar(calendar), local_time=self.__time)

    def plus_years(self, years: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of years added.

        If the resulting date is invalid, lower fields (typically the day of month) are reduced to find a valid value.
        For example, adding one year to February 29th 2012 will return February 28th 2013; subtracting one year from
        February 29th 2012 will return February 28th 2011.

        :param years: The number of years to add
        :return: The current value plus the given number of years.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_years(years), local_time=self.__time)

    def plus_months(self, months: int) -> LocalDateTime:
        """Returns a new LocalDateTime representing the current value with the given number of months added.

        This method does not try to maintain the year of the current value, so adding four months to a value in October
        will result in a value in the following February.

        If the resulting date is invalid, the day of month is reduced to find a valid value. For example, adding one
        month to January 30th 2011 will return February 28th 2011; subtracting one month from March 30th 2011 will
        return February 28th 2011.

        :param months: The number of months to add
        :return: The current value plus the given number of months.
        """
        return LocalDateTime._ctor(local_date=self.__date.plus_months(months), local_time=self.__time)

    def plus_ticks(self, ticks: int) -> LocalDateTime:
        from .fields import _TimePeriodField

        return _TimePeriodField._ticks._add_local_date_time(self, ticks)

    # @classmethod
    # TODO: def from_datetime(cls, datetime: _datetime.datetime) -> LocalDateTime:

    # @classmethod
    # TODO: def from_datetime(cls, datetime: _datetime.datetime, calendar: CalendarSystem) -> LocalDateTime:

    # region Implementation of IEquatable<LocalDateTime>

    def equals(self, other: LocalDateTime) -> bool:
        """Indicates whether the current object is equal to another object of the same type. See the type documentation
        for a description of equality semantics.

        :param other: An object to compare with this object.
        :return: True if the current object is equal to the ``other`` parameter; otherwise, False.
        """
        return self.__date == other.__date and self.__time == other.__time

    # endregion

    # region Operators

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LocalDateTime):
            return self.equals(other)
        return NotImplemented

    # endregion


@_typing.final
@_sealed
class _YearMonthDayCalendar:
    """A compact representation of a year, month, day and calendar ordinal (integer ID) in a single 32-bit integer."""

    # These constants are internal so they can be used in YearMonthDay
    _CALENDAR_BITS: _typing.Final[int] = 6  # Up to 64 calendars.
    _DAY_BITS: _typing.Final[int] = 6  # Up to 64 days in a month.
    _MONTH_BITS: _typing.Final[int] = 5  # Up to 32 months per year.
    _YEAR_BITS: _typing.Final[int] = 15  # 32K range; only need -10K to +10K.

    # Just handy constants to use for shifting and masking.
    __CALENDAR_DAY_BITS: _typing.Final[int] = _CALENDAR_BITS + _DAY_BITS
    __CALENDAR_DAY_MONTH_BITS: _typing.Final[int] = __CALENDAR_DAY_BITS + _MONTH_BITS

    __CALENDAR_MASK: _typing.Final[int] = (1 << _CALENDAR_BITS) - 1
    __DAY_MASK: _typing.Final[int] = ((1 << _DAY_BITS) - 1) << _CALENDAR_BITS
    __MONTH_MASK: _typing.Final[int] = ((1 << _MONTH_BITS) - 1) << __CALENDAR_DAY_BITS
    __YEAR_MASK: _typing.Final[int] = ((1 << _YEAR_BITS) - 1) << __CALENDAR_DAY_MONTH_BITS

    def __init__(self) -> None:
        self.__value: int = 0

    @classmethod
    @_typing.overload
    def _ctor(cls, *, year_month_day: int, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, year: int, month: int, day: int, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar:
        ...

    @classmethod
    def _ctor(
        cls,
        *,
        year_month_day: int | None = None,
        calendar_ordinal: _CalendarOrdinal | None = None,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> _YearMonthDayCalendar:
        """Implementation of internal constructors (see overloads)."""
        self = super().__new__(cls)
        if year is not None and month is not None and day is not None and calendar_ordinal is not None:
            self.__value = (
                ((year - 1) << self.__CALENDAR_DAY_MONTH_BITS)
                | ((month - 1) << self.__CALENDAR_DAY_BITS)
                | ((day - 1) << self._CALENDAR_BITS)
                | int(calendar_ordinal)
            )
        elif year_month_day is not None and calendar_ordinal is not None:
            year_month_day = year_month_day
            calendar_ordinal = calendar_ordinal
            self.__value = (year_month_day << cls._CALENDAR_BITS) | int(calendar_ordinal)
        else:
            raise TypeError
        return self

    @property
    def _calendar_ordinal(self) -> _CalendarOrdinal:
        return _CalendarOrdinal(self.__value & self.__CALENDAR_MASK)

    @property
    def _year(self) -> int:
        return (_int32_overflow(self.__value & self.__YEAR_MASK) >> self.__CALENDAR_DAY_MONTH_BITS) + 1

    @property
    def _month(self) -> int:
        return ((self.__value & self.__MONTH_MASK) >> self.__CALENDAR_DAY_BITS) + 1

    @property
    def _day(self) -> int:
        return ((self.__value & self.__DAY_MASK) >> self._CALENDAR_BITS) + 1

    @classmethod
    def _parse(cls, text: str) -> _YearMonthDayCalendar:
        # Handle a leading - to negate the year
        if text[0] == "-":
            ymdc = cls._parse(text[1:])
            return _YearMonthDayCalendar._ctor(
                year=-ymdc._year,
                month=ymdc._month,
                day=ymdc._day,
                calendar_ordinal=ymdc._calendar_ordinal,
            )

        bits = text.split("-")
        return _YearMonthDayCalendar._ctor(
            year=int(bits[0]),
            month=int(bits[1]),
            day=int(bits[2]),
            calendar_ordinal=getattr(_CalendarOrdinal, bits[3]),
        )

    def _to_year_month_day(self) -> _YearMonthDay:
        return _YearMonthDay._ctor(raw_value=self.__value >> self._CALENDAR_BITS)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDayCalendar):
            return self.__value == other.__value
        return NotImplemented


@_typing.final
@_sealed
class _YearMonthDay:
    """A compact representation of a year, month and day in a single 32-bit integer."""

    __DAY_MASK: _typing.Final[int] = (1 << _YearMonthDayCalendar._DAY_BITS) - 1
    __MONTH_MASK: _typing.Final[int] = ((1 << _YearMonthDayCalendar._MONTH_BITS) - 1) << _YearMonthDayCalendar._DAY_BITS

    def __init__(self) -> None:
        self.__value: int = 0

    @classmethod
    @_typing.overload
    def _ctor(cls, *, raw_value: int) -> _YearMonthDay:
        ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, year: int, month: int, day: int) -> _YearMonthDay:
        ...

    @classmethod
    def _ctor(
        cls, *, raw_value: int | None = None, year: int | None = None, month: int | None = None, day: int | None = None
    ) -> _YearMonthDay:
        """Internal constructor implementation."""
        self = super().__new__(cls)

        if raw_value is not None and year is None and month is None and day is None:
            self.__value = raw_value
        elif raw_value is None and year is not None and month is not None and day is not None:
            self.__value = (
                ((year - 1) << (_YearMonthDayCalendar._DAY_BITS + _YearMonthDayCalendar._MONTH_BITS))
                | ((month - 1) << _YearMonthDayCalendar._DAY_BITS)
                | (day - 1)
            )
        else:
            raise TypeError
        return self

    @property
    def _year(self) -> int:
        return (self.__value >> (_YearMonthDayCalendar._DAY_BITS + _YearMonthDayCalendar._MONTH_BITS)) + 1

    @property
    def _month(self) -> int:
        return ((self.__value & self.__MONTH_MASK) >> _YearMonthDayCalendar._DAY_BITS) + 1

    @property
    def _day(self) -> int:
        return (self.__value & self.__DAY_MASK) + 1

    def _with_calendar(self, calendar: CalendarSystem) -> _YearMonthDayCalendar:
        return _YearMonthDayCalendar._ctor(year_month_day=self.__value, calendar_ordinal=calendar._ordinal)

    def _with_calendar_ordinal(self, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar:
        return _YearMonthDayCalendar._ctor(year_month_day=self.__value, calendar_ordinal=calendar_ordinal)

    def compare_to(self, other: _YearMonthDay) -> int:
        # In Noda Time, this method calls `int.CompareTo(otherInt)`
        return self.__value - other.__value

    def equals(self, other: _YearMonthDay) -> bool:
        return isinstance(other, _YearMonthDay) and self.__value == other.__value

    def __hash__(self) -> int:
        return self.__value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value == other.__value
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDay):
            return not (self == other)
        return NotImplemented

    def __lt__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value < other.__value
        return NotImplemented

    def __le__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value <= other.__value
        return NotImplemented

    def __gt__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value > other.__value
        return NotImplemented

    def __ge__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value >= other.__value
        return NotImplemented


class ZonedDateTime:
    @classmethod
    def _ctor(cls, offset_date_time: OffsetDateTime, zone: DateTimeZone) -> ZonedDateTime:
        self = super().__new__(cls)
        self.__offset_date_time = offset_date_time
        self.__zone = zone
        return self

    @_typing.overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone) -> None:
        ...

    @_typing.overload
    def __init__(self, *, local_date_time: LocalDateTime, zone: DateTimeZone, offset: Offset) -> None:
        ...

    @_typing.overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone, calendar: CalendarSystem) -> None:
        ...

    def __init__(
        self,
        *,
        zone: DateTimeZone,
        instant: Instant | None = None,
        local_date_time: LocalDateTime | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> None:
        if offset is not None and calendar is not None:
            raise ValueError("offset and calendar are mutually exclusive")

        offset_date_time: OffsetDateTime
        if local_date_time is not None and offset is not None:
            candidate_instant = local_date_time._to_local_instant().minus(offset)
            correct_offset: Offset = zone.get_utc_offset(candidate_instant)
            if correct_offset != offset:
                raise ValueError(
                    f"Offset {offset} is invalid for local date and time {local_date_time} in time zone {zone.id}"
                )
            offset_date_time = OffsetDateTime(local_date_time=local_date_time, offset=offset)
        elif calendar is not None and instant is not None:
            offset_date_time = OffsetDateTime._ctor(
                instant=instant, offset=zone.get_utc_offset(instant), calendar=calendar
            )
        elif instant is not None:
            offset_date_time = OffsetDateTime._ctor(instant=instant, offset=zone.get_utc_offset(instant))
        else:
            raise ValueError

        self.__offset_date_time: OffsetDateTime = offset_date_time
        self.__zone: DateTimeZone = _Preconditions._check_not_null(zone, "zone")

    @property
    def local_date_time(self) -> LocalDateTime:
        return self.__offset_date_time.local_date_time


_BCL_EPOCH: _typing.Final[Instant] = Instant.from_utc(1, 1, 1, 0, 0)
_UNIX_EPOCH: _typing.Final[Instant] = Instant.from_unix_time_ticks(0)
