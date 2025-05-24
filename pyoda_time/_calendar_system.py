# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Final, final, overload

from .calendars._badi_year_month_day_calculator import _BadiYearMonthDayCalculator
from .calendars._coptic_year_month_day_calculator import _CopticYearMonthDayCalculator
from .calendars._g_j_era_calculator import _GJEraCalculator
from .calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from .calendars._hebrew_year_month_day_calculator import _HebrewYearMonthDayCalculator
from .calendars._islamic_year_month_day_calculator import _IslamicYearMonthDayCalculator
from .calendars._julian_year_month_day_calculator import _JulianYearMonthDayCalculator
from .calendars._persian_year_month_day_calculator import _PersianYearMonthDayCalculator
from .calendars._single_era_calculator import _SingleEraCalculator
from .calendars._um_al_qura_year_month_day_calculator import _UmAlQuraYearMonthDayCalculator

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ._year_month_day import _YearMonthDay
    from ._year_month_day_calendar import _YearMonthDayCalendar
    from .calendars._era_calculator import _EraCalculator
    from .calendars._year_month_day_calculator import _YearMonthDayCalculator

from ._calendar_ordinal import _CalendarOrdinal
from ._iso_day_of_week import IsoDayOfWeek
from .utility._csharp_compatibility import _csharp_modulo, _private, _sealed
from .utility._preconditions import _Preconditions

__all__ = ["CalendarSystem"]
from .calendars import (
    Era,
    HebrewMonthNumbering,
    IslamicEpoch,
    IslamicLeapYearPattern,
)


class _CalendarSystemMeta(type):
    @property
    def badi(cls) -> CalendarSystem:
        """Returns the Badíʿ (meaning "wondrous" or "unique") calendar, as described at https://en.wikipedia.org/wiki/Badi_calendar.

        This is a purely solar calendar with years starting at the vernal equinox.

        The Badíʿ calendar was developed and defined by the founders of the Bahá'í Faith in the mid to late
        1800's A.D. The first year in the calendar coincides with 1844 A.D. Years are labeled "B.E." for Bahá'í Era.

        A year consists of 19 months, each with 19 days. Each day starts at sunset. Years are grouped into sets
        of 19 "Unities" (Váḥid) and 19 Unities make up 1 "All Things" (Kull-i-Shay').

        A period of days (usually 4 or 5, called Ayyám-i-Há) occurs between the 18th and 19th months. The length of this
        period of intercalary days is solely determined by the date of the following vernal equinox. The vernal equinox
        is a momentary point in time, so the "date" of the equinox is determined by the date (beginning
        at sunset) in effect in Tehran, Iran at the moment of the equinox.

        In this Pyoda Time implementation, days start at midnight and lookup tables are used to determine vernal equinox
        dates. Ayyám-i-Há is internally modelled as extra days added to the 18th month. As a result, a few functions
        will not work as expected for Ayyám-i-Há, such as EndOfMonth.

        :returns: The Badíʿ calendar system.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.BADI)

    @property
    def coptic(cls) -> CalendarSystem:
        """Returns a Coptic calendar system, which defines every fourth year as leap, much like the Julian calendar.

        The year is broken down into 12 months, each 30 days in length. An extra period at the end of the year is either
        5 or 6 days in length. In this implementation, it is considered a 13th month.

        Year 1 in the Coptic calendar began on August 29, 284 CE (Julian), thus Coptic years do not begin at the same
        time as Julian years. This calendar is not proleptic, as it does not allow dates before the first Coptic year.

        This implementation defines a day as midnight to midnight exactly as per the ISO calendar. Some references
        indicate that a Coptic day starts at sunset on the previous ISO day, but this has not been confirmed and is not
        implemented.

        :return: The Coptic calendar system.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.COPTIC)

    @property
    def gregorian(cls) -> CalendarSystem:
        """The Gregorian calendar system defines every fourth year as leap, unless the year is divisible by 100 and not
        by 400. This improves upon the Julian calendar leap year rule.

        Although the Gregorian calendar did not exist before 1582 CE, this calendar system assumes it did, thus it is
        proleptic. This implementation also fixes the start of the year at January 1.

        :return: The Gregorian calendar system.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.GREGORIAN)

    @property
    def islamic_bcl(cls) -> CalendarSystem:
        """Returns an Islamic calendar system equivalent to the one used by the BCL HijriCalendar.

        This uses the ``IslamicLeapYearPattern.Base16`` leap year pattern and the
        ``IslamicEpoch.Astronomical`` epoch. This is equivalent to HijriCalendar
        when the ``HijriCalendar.HijriAdjustment`` is 0.

        :return: An Islamic calendar system equivalent to the one used by the BCL.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16)

    @property
    def hebrew_civil(cls) -> CalendarSystem:
        """Returns a Hebrew calendar system using the civil month numbering, equivalent to the one used by the BCL
        HebrewCalendar.

        :return: A Hebrew calendar system using the civil month numbering, equivalent to the one used by the BCL.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.HEBREW_CIVIL)

    @property
    def hebrew_scriptural(cls) -> CalendarSystem:
        """Returns a Hebrew calendar system using the scriptural month numbering.

        :return: A Hebrew calendar system using the scriptural month numbering.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.HEBREW_SCRIPTURAL)

    @property
    def iso(cls) -> CalendarSystem:
        """Returns a calendar system that follows the rules of the ISO-8601 standard, which is compatible with Gregorian
        for all modern dates.

        This calendar system is effectively equivalent to ``CalendarSystem.gregorian``.

        :return: The ISO calendar system.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.ISO)

    @property
    def julian(cls) -> CalendarSystem:
        """Returns a pure proleptic Julian calendar system, which defines every fourth year as a leap year. This
        implementation follows the leap year rule strictly, even for dates before 8 CE, where leap years were actually
        irregular.

        Although the Julian calendar did not exist before 45 BCE, this calendar assumes it did, thus it is proleptic.
        This implementation also fixes the start of the year at January 1.

        :return: The Julian calendar system.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.JULIAN)

    @property
    def persian_arithmetic(cls) -> CalendarSystem:
        """Returns a Persian (also known as Solar Hijri) calendar system implementing the behaviour proposed by Ahmad
        Birashk with nested cycles of years determining which years are leap years.

        This calendar is also known as the algorithmic Solar Hijri calendar.

        :return: A Persian calendar system using cycles-within-cycles of years to determine leap years.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_ARITHMETIC)

    @property
    def persian_astronomical(cls) -> CalendarSystem:
        """Returns a Persian (also known as Solar Hijri) calendar system implementing the behaviour of the BCL
        ``PersianCalendar`` from .NET 4.6 onwards (and Windows 10), and the astronomical system described in Wikipedia
        and Calendrical Calculations.

        This implementation uses data derived from the .NET 4.6 implementation (with the data built into Pyoda Time, so
        there's no BCL dependency) for simplicity; the actual implementation involves computing the time of noon in
        Iran, and is complex.

        :return: A Persian calendar system using astronomical calculations to determine leap years.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_ASTRONOMICAL)

    @property
    def persian_simple(cls) -> CalendarSystem:
        """Returns a Persian (also known as Solar Hijri) calendar system implementing the behaviour of the BCL
        ``PersianCalendar`` before .NET 4.6, and the sole Persian calendar in Noda Time 1.3.

        This implementation uses a simple 33-year leap cycle, where years  1, 5, 9, 13, 17, 22, 26, and 30 in each cycle
        are leap years.

        :return: A Persian calendar system using a simple 33-year leap cycle.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.PERSIAN_SIMPLE)

    @property
    def um_al_qura(cls) -> CalendarSystem:
        """Returns an Um Al Qura calendar system - an Islamic calendar system primarily used by Saudi Arabia.

        This is a tabular calendar, relying on pregenerated data.

        :return: A calendar system for the Um Al Qura calendar.
        """
        return CalendarSystem._for_ordinal(_CalendarOrdinal.UM_AL_QURA)

    @property
    def ids(cls) -> Iterable[str]:
        """Returns the IDs of all calendar systems available within Pyoda Time.

        The order of the keys is not guaranteed.
        """
        return CalendarSystem._ids()


@final
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
    __GREGORIAN_NAME: Final[str] = "Gregorian"
    __GREGORIAN_ID: Final[str] = __GREGORIAN_NAME

    __ISO_NAME: Final[str] = "ISO"
    __ISO_ID: Final[str] = __ISO_NAME

    __COPTIC_NAME: Final[str] = "Coptic"
    __COPTIC_ID: Final[str] = __COPTIC_NAME

    __BADI_NAME: Final[str] = "Badi"
    __BADI_ID: Final[str] = __BADI_NAME

    __JULIAN_NAME: Final[str] = "Julian"
    __JULIAN_ID: Final[str] = __JULIAN_NAME

    __ISLAMIC_NAME: Final[str] = "Hijri"
    __ISLAMIC_ID_BASE: Final[str] = __ISLAMIC_NAME

    @staticmethod
    def _get_islamic_id(base: str, leap_year_pattern: IslamicLeapYearPattern, epoch: IslamicEpoch) -> str:
        def to_camel_case(s: str) -> str:
            return "".join(x.capitalize() for x in s.split("_"))

        return f"{base} {to_camel_case(epoch.name)}-{to_camel_case(leap_year_pattern.name)}"

    __PERSIAN_NAME: Final[str] = "Persian"
    __PERSIAN_ID_BASE: Final[str] = __PERSIAN_NAME
    __PERSIAN_SIMPLE_ID: Final[str] = __PERSIAN_ID_BASE + " Simple"
    __PERSIAN_ASTRONOMICAL_ID: Final[str] = __PERSIAN_ID_BASE + " Algorithmic"
    __PERSIAN_ARITHMETIC_ID: Final[str] = __PERSIAN_ID_BASE + " Arithmetic"

    __HEBREW_NAME: Final[str] = "Hebrew"
    __HEBREW_ID_BASE: Final[str] = __HEBREW_NAME
    __HEBREW_CIVIL_ID: Final[str] = __HEBREW_ID_BASE + " Civil"
    __HEBREW_SCRIPTURAL_ID: Final[str] = __HEBREW_ID_BASE + " Scriptural"

    __UM_AL_QURA_NAME: Final[str] = "Um Al Qura"
    __UM_AL_QURA_ID: Final[str] = __UM_AL_QURA_NAME

    # While we could implement some of these as auto-props, it probably adds more confusion than convenience.
    __CALENDAR_BY_ORDINAL: Final[dict[_CalendarOrdinal, CalendarSystem]] = {}

    __ID_ORDINAL_MAP: Final[dict[str, _CalendarOrdinal]] = {
        __BADI_ID: _CalendarOrdinal.BADI,
        __COPTIC_ID: _CalendarOrdinal.COPTIC,
        __GREGORIAN_ID: _CalendarOrdinal.GREGORIAN,
        __HEBREW_CIVIL_ID: _CalendarOrdinal.HEBREW_CIVIL,
        __HEBREW_SCRIPTURAL_ID: _CalendarOrdinal.HEBREW_SCRIPTURAL,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_BASE15,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.BASE16, IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_BASE16,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.BASE16, IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.INDIAN, IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.INDIAN, IslamicEpoch.ASTRONOMICAL
        ): _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.CIVIL
        ): _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB,
        _get_islamic_id(
            __ISLAMIC_ID_BASE, IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.ASTRONOMICAL
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
        :return: The calendar system with the given ID.
        :exception KeyError: No calendar system for the specified ID can be found.
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
    def _ids(cls) -> Iterable[str]:
        """Returns an iterable of all valid IDs.

        The public static property is implemented in the metaclass. This classmethod just exists to expose the keys of
        the dictionary (internally). This implementation differs somewhat from noda time!
        """
        yield from cls.__ID_ORDINAL_MAP.keys()

    @classmethod
    def get_hebrew_calendar(cls, month_numbering: HebrewMonthNumbering) -> CalendarSystem:
        _Preconditions._check_argument_range("month_numbering", int(month_numbering), 1, 2)
        match month_numbering:
            case HebrewMonthNumbering.CIVIL:
                return CalendarSystem.__ctor(
                    ordinal=_CalendarOrdinal.HEBREW_CIVIL,
                    id_=cls.__HEBREW_CIVIL_ID,
                    name=cls.__HEBREW_NAME,
                    year_month_day_calculator=_HebrewYearMonthDayCalculator(month_numbering),
                    single_era=Era.anno_mundi,
                )
            case HebrewMonthNumbering.SCRIPTURAL:
                return CalendarSystem.__ctor(
                    ordinal=_CalendarOrdinal.HEBREW_SCRIPTURAL,
                    id_=cls.__HEBREW_SCRIPTURAL_ID,
                    name=cls.__HEBREW_NAME,
                    year_month_day_calculator=_HebrewYearMonthDayCalculator(month_numbering),
                    single_era=Era.anno_mundi,
                )
            case _:
                raise ValueError(f"Unknown HebrewMonthNumbering: {month_numbering}")

    @classmethod
    def get_islamic_calendar(cls, leap_year_pattern: IslamicLeapYearPattern, epoch: IslamicEpoch) -> CalendarSystem:
        _Preconditions._check_argument_range("leap_year_pattern", int(leap_year_pattern), 1, 4)
        _Preconditions._check_argument_range("epoch", int(epoch), 1, 2)
        match (epoch, leap_year_pattern):
            # Civil
            case (IslamicEpoch.CIVIL, IslamicLeapYearPattern.BASE15):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_BASE15
            case (IslamicEpoch.CIVIL, IslamicLeapYearPattern.BASE16):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_BASE16
            case (IslamicEpoch.CIVIL, IslamicLeapYearPattern.INDIAN):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN
            case (IslamicEpoch.CIVIL, IslamicLeapYearPattern.HABASH_AL_HASIB):
                ordinal = _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB
            # Astronomical
            case (IslamicEpoch.ASTRONOMICAL, IslamicLeapYearPattern.BASE15):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15
            case (IslamicEpoch.ASTRONOMICAL, IslamicLeapYearPattern.BASE16):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16
            case (IslamicEpoch.ASTRONOMICAL, IslamicLeapYearPattern.INDIAN):
                ordinal = _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN
            case (IslamicEpoch.ASTRONOMICAL, IslamicLeapYearPattern.HABASH_AL_HASIB):
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
            single_era=Era.anno_hegirae,
        )

    # endregion

    __ordinal: Annotated[_CalendarOrdinal, "Set by private constructor"]
    __id: Annotated[str, "Set by private constructor"]
    __name: Annotated[str, "Set by private constructor"]
    __year_month_day_calculator: Annotated[_YearMonthDayCalculator, "Set by private constructor"]
    __era_calculator: Annotated[_EraCalculator, "Set by private constructor"]
    __min_year: Annotated[int, "Set by private constructor"]
    __max_year: Annotated[int, "Set by private constructor"]
    __min_days: Annotated[int, "Set by private constructor"]
    __max_days: Annotated[int, "Set by private constructor"]

    @classmethod
    @overload
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        era_calculator: _EraCalculator,
    ) -> CalendarSystem: ...

    @classmethod
    @overload
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        single_era: Era,
    ) -> CalendarSystem: ...

    @classmethod
    def __ctor(
        cls,
        *,
        ordinal: _CalendarOrdinal,
        id_: str,
        name: str,
        year_month_day_calculator: _YearMonthDayCalculator,
        era_calculator: _EraCalculator | None = None,
        single_era: Era | None = None,
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

    def eras(self) -> Iterable[Era]:
        """Gets a read-only iterable of eras used in this calendar system."""
        yield from self.__era_calculator._eras

    def get_absolute_year(self, year_of_era: int, era: Era) -> int:
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

    def get_max_year_of_era(self, era: Era) -> int:
        """Returns the maximum valid year-of-era in the given era.

        Note that depending on the calendar system, it's possible that only part of the returned year falls within the
        given era. It is also possible that the returned value represents the earliest year of the era rather than the
        latest year. (See the BC era in the Gregorian calendar, for example.)

        :param era: The era in which to find the greatest year
        :return: The maximum valid year in the given era.
        :exception ValueError: era is not an era used in this calendar.
        """
        return self.__era_calculator._get_max_year_of_era(era)

    def get_min_year_of_era(self, era: Era) -> int:
        """Returns the minimum valid year-of-era in the given era.

        Note that depending on the calendar system, it's possible that only part of the returned year falls within the
        given era. It is also possible that the returned value represents the latest year of the era rather than the
        earliest year. (See the BC era in the Gregorian calendar, for example.)

        :param era: The era in which to find the greatest year
        :return: The minimum valid year in the given era.
        :exception ValueError: era is not an era used in this calendar.
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

    def __repr__(self) -> str:
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

    def _get_era(self, absolute_year: int) -> Era:
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
                    single_era=Era.bahai,
                )
            case _CalendarOrdinal.COPTIC:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__COPTIC_ID,
                    name=cls.__COPTIC_NAME,
                    year_month_day_calculator=_CopticYearMonthDayCalculator(),
                    single_era=Era.anno_martyrum,
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
                return cls.get_hebrew_calendar(HebrewMonthNumbering.CIVIL)
            case _CalendarOrdinal.HEBREW_SCRIPTURAL:
                return cls.get_hebrew_calendar(HebrewMonthNumbering.SCRIPTURAL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_BASE15:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_BASE16:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.BASE16, IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_INDIAN:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.INDIAN, IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_CIVIL_HABASH_AL_HASIB:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.CIVIL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.BASE15, IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE16:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.BASE16, IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_INDIAN:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.INDIAN, IslamicEpoch.ASTRONOMICAL)
            case _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_HABASH_AL_HASIB:
                return cls.get_islamic_calendar(IslamicLeapYearPattern.HABASH_AL_HASIB, IslamicEpoch.ASTRONOMICAL)
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
                    single_era=Era.anno_persico,
                )
            case _CalendarOrdinal.PERSIAN_ASTRONOMICAL:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__PERSIAN_ASTRONOMICAL_ID,
                    name=cls.__PERSIAN_NAME,
                    year_month_day_calculator=_PersianYearMonthDayCalculator.Astronomical(),
                    single_era=Era.anno_persico,
                )
            case _CalendarOrdinal.PERSIAN_SIMPLE:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__PERSIAN_SIMPLE_ID,
                    name=cls.__PERSIAN_NAME,
                    year_month_day_calculator=_PersianYearMonthDayCalculator.Simple(),
                    single_era=Era.anno_persico,
                )
            case _CalendarOrdinal.UM_AL_QURA:
                return cls.__ctor(
                    ordinal=ordinal,
                    id_=cls.__UM_AL_QURA_ID,
                    name=cls.__UM_AL_QURA_NAME,
                    year_month_day_calculator=_UmAlQuraYearMonthDayCalculator(),
                    single_era=Era.anno_hegirae,
                )
            case _:
                raise RuntimeError(
                    f"CalendarOrdinal '{getattr(ordinal, 'name', ordinal)}' not mapped to CalendarSystem."
                )
