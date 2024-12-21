# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Final, TypeVar, cast, final

from .._compatibility._culture_info import CultureInfo
from .._compatibility._date_time_format_info import DateTimeFormatInfo
from ..calendars import Era
from ..utility._cache import _Cache

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .._annual_date import AnnualDate
    from .._compatibility._i_format_provider import IFormatProvider
    from .._duration import Duration
    from .._instant import Instant
    from .._local_date import LocalDate
    from .._local_date_time import LocalDateTime
    from .._local_time import LocalTime
    from .._offset import Offset
    from .._offset_date_time import OffsetDateTime
    from .._offset_time import OffsetTime
    from .._year_month import YearMonth
    from .._zoned_date_time import ZonedDateTime
    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from ..utility._csharp_compatibility import _sealed
from ..utility._preconditions import _Preconditions
from ._pattern_resources import _PatternResources

T = TypeVar("T")


class _PyodaFormatInfoMeta(type):
    @property
    def invariant_info(self) -> _PyodaFormatInfo:
        """A ``_PyodaFormatInfo`` wrapping the invariant culture."""
        return _PyodaFormatInfo(CultureInfo.invariant_culture)

    @property
    def current_info(cls) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` object for the current thread."""
        return _PyodaFormatInfo.get_instance(CultureInfo.current_culture)


@final
@_sealed
class _PyodaFormatInfo(metaclass=_PyodaFormatInfoMeta):
    """An ``IFormatProvider`` for Pyoda Time types, usually initialised from a ``CultureInfo``. This provides a single
    place defining how Pyoda Time values are formatted and displayed, depending on the culture.

    Currently, this is "shallow-immutable" - although none of these properties can be changed, the
    CultureInfo itself may be mutable. If the CultureInfo is mutated after initialization, results are not
    guaranteed: some aspects of the CultureInfo may be extracted at initialization time, others may be
    extracted on first demand but cached, and others may be extracted on-demand each time.

    Instances which use read-only CultureInfo instances are immutable,
    and may be used freely between threads. Instances with mutable cultures should not be shared between threads
    without external synchronization.
    See the thread safety section of the user guide for more information.
    """

    # Names that we can use to check for broken Mono behaviour.
    __SHORT_INVARIANT_MONTH_NAMES: Final[Sequence[str]] = list(
        CultureInfo.invariant_culture.date_time_format.abbreviated_month_names
    )
    __LONG_INVARIANT_MONTH_NAMES: Final[Sequence[str]] = list(
        CultureInfo.invariant_culture.date_time_format.month_names
    )

    __FIELD_LOCK: Final[threading.Lock] = threading.Lock()

    __CACHE: Final[_Cache[CultureInfo, _PyodaFormatInfo]] = _Cache(500, lambda culture: _PyodaFormatInfo(culture))

    def __init__(self, culture_info: CultureInfo, date_time_format: DateTimeFormatInfo | None = None) -> None:
        _Preconditions._check_not_null(culture_info, "culture_info")
        # _Preconditions._check_not_null(date_time_format, "date_time_format")
        self.__culture_info: CultureInfo = culture_info
        self.__date_time_format: DateTimeFormatInfo = (
            culture_info.date_time_format if date_time_format is None else date_time_format
        )
        self.__era_descriptions: dict[Era, _EraDescription] = dict()
        self.__short_month_names: list[str] | None = None
        self.__short_month_genitive_names: list[str] | None = None
        self.__long_month_names: list[str] | None = None
        self.__long_month_genitive_names: list[str] | None = None
        self.__long_day_names: list[str] | None = None

        self.__duration_pattern_parser: _FixedFormatInfoPatternParser[Duration] | None = None
        self.__offset_pattern_parser: _FixedFormatInfoPatternParser[Offset] | None = None
        self.__instant_pattern_parser: _FixedFormatInfoPatternParser[Instant] | None = None
        self.__local_time_pattern_parser: _FixedFormatInfoPatternParser[LocalTime] | None = None
        self.__local_date_pattern_parser: _FixedFormatInfoPatternParser[LocalDate] | None = None
        self.__local_date_time_pattern_parser: _FixedFormatInfoPatternParser[LocalDateTime] | None = None
        self.__offset_date_time_pattern_parser: _FixedFormatInfoPatternParser[OffsetDateTime] | None = None
        # TODO: self.__offset_date_pattern_parser: _FixedFormatInfoPatternParser[OffsetDate] | None = None
        self.__offset_time_pattern_parser: _FixedFormatInfoPatternParser[OffsetTime] | None = None
        self.__zoned_date_time_pattern_parser: _FixedFormatInfoPatternParser[ZonedDateTime] | None = None
        self.__annual_date_pattern_parser: _FixedFormatInfoPatternParser[AnnualDate] | None = None
        self.__year_month_pattern_parser: _FixedFormatInfoPatternParser[YearMonth] | None = None

    def __ensure_months_initialized(self) -> None:
        if self.__long_month_names is not None:
            return

        with self.__FIELD_LOCK:
            if self.__long_month_names is not None:
                return  # type: ignore[unreachable]
            # Turn month names into 1-based read-only lists
            self.__long_month_names = self.__convert_month_array(self.date_time_format.month_names)
            self.__short_month_names = self.__convert_month_array(self.date_time_format.abbreviated_month_names)
            self.__long_month_genitive_names = self.__convert_genitive_month_array(
                self.__long_month_names, self.date_time_format.month_genitive_names, self.__LONG_INVARIANT_MONTH_NAMES
            )
            self.__short_month_genitive_names = self.__convert_genitive_month_array(
                self.__short_month_names,
                self.date_time_format.abbreviated_month_genitive_names,
                self.__SHORT_INVARIANT_MONTH_NAMES,
            )

    @staticmethod
    def __convert_month_array(month_names: Sequence[str]) -> list[str]:
        """The BCL returns arrays of month names starting at 0; we want a read-only list starting at 1 (with 0 as an
        empty string)."""
        return ["", *month_names]

    def __ensure_days_initialized(self) -> None:
        if self.__long_day_names is not None:
            return

        with self.__FIELD_LOCK:
            if self.__long_day_names is not None:
                return  # type: ignore[unreachable]
            self.__long_day_names = self.__convert_day_array(self.date_time_format.day_names)
            self.__short_day_names = self.__convert_day_array(self.date_time_format.abbreviated_day_names)

    @staticmethod
    def __convert_day_array(day_names: list[str]) -> list[str]:
        """The BCL returns arrays of week names starting at 0 as Sunday; we want a read-only list starting at 1 (with 0
        as an empty string) and with 7 as Sunday."""
        # TODO: The desired string array is what ICU (and PyICU) gives us.
        #  If we refactor out the BCL stuff at some point, this sort of thing won't be necessary.
        return ["", *day_names[1:], day_names[0]]

    @classmethod
    def __convert_genitive_month_array(
        cls, non_genitive_names: list[str], bcl_names: Sequence[str], invariant_names: Sequence[str]
    ) -> list[str]:
        """Checks whether any of the genitive names differ from the non-genitive names, and returns either a reference
        to the non-genitive names or a converted list as per ConvertMonthArray."""
        # In Noda Time, this method works around two Mono bugs; One where genitive month names are
        # identical to invariant month names, and another where abbreviated month names are strings
        # containing integers.
        #
        # I don't anticipate that we will have those issues in Pyoda Time, but there is a test which
        # mimics the mono behaviour and I want the Python implementation to not differ from the mother
        # project too much at this stage. We may remove these workarounds at a later date.

        # Workaround for Mono 3.0.6 returning numeric strings for genitive month names.
        if bcl_names[0].isdigit():
            return non_genitive_names

        # Workaround for Mono using invariant genitive month names for non-invariant cultures.
        for i in range(len(bcl_names)):
            if bcl_names[i] != non_genitive_names[i] != invariant_names[i]:
                return cls.__convert_month_array(bcl_names)

        return non_genitive_names

    @property
    def culture_info(self) -> CultureInfo:
        """Gets the culture info associated with this format provider."""
        return self.__culture_info

    # TODO: public CompareInfo CompareInfo => CultureInfo.CompareInfo;

    # TODO:
    #  internal FixedFormatInfoPatternParser<Duration> DurationPatternParser

    @property
    def _duration_pattern_parser(self) -> _FixedFormatInfoPatternParser[Duration]:
        if self.__duration_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__duration_pattern_parser is None:
                    from ..text._duration_pattern_parser import _DurationPatternParser
                    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser

                    self.__duration_pattern_parser = _FixedFormatInfoPatternParser(_DurationPatternParser(), self)
        return self.__duration_pattern_parser

    @property
    def _offset_pattern_parser(self) -> _FixedFormatInfoPatternParser[Offset]:
        if self.__offset_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__offset_pattern_parser is None:
                    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
                    from ..text._offset_pattern_parser import _OffsetPatternParser

                    self.__offset_pattern_parser = _FixedFormatInfoPatternParser(_OffsetPatternParser(), self)
        return self.__offset_pattern_parser

    @property
    def _instant_pattern_parser(self) -> _FixedFormatInfoPatternParser[Instant]:
        if self.__instant_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__instant_pattern_parser is None:
                    from pyoda_time.text import InstantPattern, LocalDatePattern
                    from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
                    from pyoda_time.text._instant_pattern_parser import _InstantPatternParser

                    self.__instant_pattern_parser = _FixedFormatInfoPatternParser(
                        _InstantPatternParser._ctor(
                            InstantPattern._DEFAULT_TEMPLATE_VALUE, LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX
                        ),
                        self,
                    )
        return self.__instant_pattern_parser

    @property
    def _local_time_pattern_parser(self) -> _FixedFormatInfoPatternParser[LocalTime]:
        if self.__local_time_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__local_time_pattern_parser is None:
                    from pyoda_time._local_time import LocalTime
                    from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
                    from pyoda_time.text._local_time_pattern_parser import _LocalTimePatternParser

                    self.__local_time_pattern_parser = _FixedFormatInfoPatternParser(
                        _LocalTimePatternParser._ctor(LocalTime.midnight), self
                    )

        return self.__local_time_pattern_parser

    @property
    def _local_date_pattern_parser(self) -> _FixedFormatInfoPatternParser[LocalDate]:
        if self.__local_date_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__local_date_pattern_parser is None:
                    from pyoda_time.text import LocalDatePattern
                    from pyoda_time.text._local_date_pattern_parser import _LocalDatePatternParser

                    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser

                    self.__local_date_pattern_parser = _FixedFormatInfoPatternParser(
                        _LocalDatePatternParser._ctor(
                            LocalDatePattern._DEFAULT_TEMPLATE_VALUE, LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX
                        ),
                        self,
                    )
        return self.__local_date_pattern_parser

    @property
    def _local_date_time_pattern_parser(self) -> _FixedFormatInfoPatternParser[LocalDateTime]:
        if self.__local_date_time_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__local_date_time_pattern_parser is None:
                    from pyoda_time.text import LocalDatePattern, LocalDateTimePattern
                    from pyoda_time.text._local_date_time_pattern_parser import _LocalDateTimePatternParser

                    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser

                    self.__local_date_time_pattern_parser = _FixedFormatInfoPatternParser(
                        _LocalDateTimePatternParser._ctor(
                            LocalDateTimePattern._DEFAULT_TEMPLATE_VALUE, LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX
                        ),
                        self,
                    )
        return self.__local_date_time_pattern_parser

    # TODO:
    #  internal FixedFormatInfoPatternParser<OffsetDateTime> OffsetDateTimePatternParser
    #  internal FixedFormatInfoPatternParser<OffsetDate> OffsetDatePatternParser
    #  internal FixedFormatInfoPatternParser<OffsetTime> OffsetTimePatternParser
    #  internal FixedFormatInfoPatternParser<ZonedDateTime> ZonedDateTimePatternParser
    #  internal FixedFormatInfoPatternParser<YearMonth> YearMonthPatternParser

    @property
    def _annual_date_pattern_parser(self) -> _FixedFormatInfoPatternParser[AnnualDate]:
        if self.__annual_date_pattern_parser is None:
            with self.__FIELD_LOCK:
                if self.__annual_date_pattern_parser is None:
                    from pyoda_time.text import AnnualDatePattern
                    from pyoda_time.text._annual_date_pattern_parser import _AnnualDatePatternParser

                    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser

                    self.__annual_date_pattern_parser = _FixedFormatInfoPatternParser(
                        _AnnualDatePatternParser._ctor(AnnualDatePattern._DEFAULT_TEMPLATE_VALUE),
                        self,
                    )
        return self.__annual_date_pattern_parser

    @property
    def long_month_names(self) -> Sequence[str]:
        """Returns a read-only list of the names of the months for the default calendar for this culture.

        See the usage guide for caveats around the use of these names for other calendars. Element 0 of the list is
        null, to allow a more natural mapping from (say) 1 to the string "January".
        """
        self.__ensure_months_initialized()
        return cast(list[str], self.__long_month_names)

    @property
    def short_month_names(self) -> Sequence[str]:
        """Returns a read-only list of the abbreviated names of the months for the default calendar for this culture.

        See the usage guide for caveats around the use of these names for other calendars. Element 0 of the list is
        null, to allow a more natural mapping from (say) 1 to the string "Jan".
        """
        self.__ensure_months_initialized()
        return cast(list[str], self.__short_month_names)

    @property
    def long_month_genitive_names(self) -> Sequence[str]:
        """Returns a read-only list of the names of the months for the default calendar for this culture.

        See the usage guide for caveats around the use of these names for other calendars.
        Element 0 of the list is null, to allow a more natural mapping from (say) 1 to the string "January".
        The genitive form is used for month text where the day of month also appears in the pattern.
        If the culture does not use genitive month names, this property will return the same reference as
        ``long_month_names``.
        """
        self.__ensure_months_initialized()
        return cast(list[str], self.__long_month_genitive_names)

    @property
    def short_month_genitive_names(self) -> Sequence[str]:
        """Returns a read-only list of the abbreviated names of the months for the default calendar for this culture.

        See the usage guide for caveats around the use of these names for other calendars.
        Element 0 of the list is null, to allow a more natural mapping from (say) 1 to the string "Jan".
        The genitive form is used for month text where the day also appears in the pattern.
        If the culture does not use genitive month names, this property will return the same reference as
        ``short_month_names``.
        """
        self.__ensure_months_initialized()
        return cast(list[str], self.__short_month_genitive_names)

    @property
    def long_day_names(self) -> Sequence[str]:
        """Returns a read-only list of the names of the days of the week for the default calendar for this culture.

        See the usage guide for caveats around the use of these names for other calendars.
        Element 0 of the list is null, and the other elements correspond with the index values returned from
        ``LocalDateTime.DayOfWeek`` and similar properties.
        """
        self.__ensure_days_initialized()
        # Cast required as mypy thinks this might be None.
        return cast(list[str], self.__long_day_names)

    @property
    def short_day_names(self) -> Sequence[str]:
        """Returns a read-only list of the abbreviated names of the days of the week for the default calendar for this
        culture.

        See the usage guide for caveats around the use of these names for other calendars.
        Element 0 of the list is null, and the other elements correspond with the index values returned from
        ``LocalDateTime.day_of_week`` and similar properties.
        """
        self.__ensure_days_initialized()
        return self.__short_day_names

    @property
    def date_time_format(self) -> DateTimeFormatInfo:
        """Gets the BCL date time format associated with this formatting information.

        This is usually the ``DateTimeFormatInfo`` from ``culture_info``,
        but in some cases they're different: if a DateTimeFormatInfo is provided with no
        CultureInfo, that's used for format strings but the invariant culture is used for
        text comparisons and culture lookups for non-BCL formats (such as Offset) and for error messages.
        """
        return self.__date_time_format

    @property
    def time_separator(self) -> str:
        """Gets the time separator."""
        return self.__date_time_format.time_separator

    @property
    def date_separator(self) -> str:
        """Gets the date separator."""
        return self.__date_time_format.date_separator

    @property
    def am_designator(self) -> str:
        """Gets the AM designator."""
        return self.date_time_format.am_designator

    @property
    def pm_designator(self) -> str:
        """Gets the PM designator."""
        return self.date_time_format.pm_designator

    def get_era_names(self, era: Era) -> list[str]:
        """Returns the names for the given era in this culture.

        :param era: The era to find the names of.
        :return: A read-only list of names for the given era, or an empty list if the era is not known in this culture.
        """
        _Preconditions._check_not_null(era, "era")
        return self.__get_era_description(era)._all_names

    def get_era_primary_name(self, era: Era) -> str:
        """Returns the primary name for the given era in this culture.

        :param era: The era to find the primary name of.
        :return: The primary name for the given era, or an empty string if the era name is not known.
        """
        _Preconditions._check_not_null(era, "era")
        return self.__get_era_description(era)._primary_name

    def __get_era_description(self, era: Era) -> _EraDescription:
        with self.__FIELD_LOCK:
            if (description := self.__era_descriptions.get(era)) is None:
                description = self.__era_descriptions[era] = _EraDescription._for_era(era, self.culture_info)
            return description

    @property
    def offset_pattern_long(self) -> str:
        """Gets the ``Offset`` 'l' pattern."""
        return cast(str, _PatternResources._resource_manager.get_string("OffsetPatternLong", self.culture_info))

    @property
    def offset_pattern_medium(self) -> str:
        """Gets the ``Offset`` 'm' pattern."""
        return cast(str, _PatternResources._resource_manager.get_string("OffsetPatternMedium", self.culture_info))

    @property
    def offset_pattern_short(self) -> str:
        """Gets the ``Offset`` 's' pattern."""
        return cast(str, _PatternResources._resource_manager.get_string("OffsetPatternShort", self.culture_info))

    @property
    def offset_pattern_long_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'L' pattern."""
        return cast(
            str, _PatternResources._resource_manager.get_string("OffsetPatternLongNoPunctuation", self.culture_info)
        )

    @property
    def offset_pattern_medium_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'M' pattern."""
        return cast(
            str, _PatternResources._resource_manager.get_string("OffsetPatternMediumNoPunctuation", self.culture_info)
        )

    @property
    def offset_pattern_short_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'S' pattern."""
        return cast(
            str, _PatternResources._resource_manager.get_string("OffsetPatternShortNoPunctuation", self.culture_info)
        )

    @classmethod
    def _clear_cache(cls) -> None:
        """Clears the cache.

        Only used for test purposes.
        """
        cls.__CACHE.clear()

    @classmethod
    def _get_format_info(cls, culture_info: CultureInfo) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` for the given ``CultureInfo``."""
        _Preconditions._check_not_null(culture_info, "culture_info")
        if culture_info == CultureInfo.invariant_culture:
            return _PyodaFormatInfo.invariant_info
        if not culture_info.is_read_only:
            return _PyodaFormatInfo(culture_info)
        return cls.__CACHE.get_or_add(culture_info)

    @classmethod
    def get_instance(cls, provider: IFormatProvider | None) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` for the given ``IFormatProvider``.

        If the
        /// format provider is null then the format object for the current thread is returned. If it's
        /// a CultureInfo, that's used for everything. If it's a DateTimeFormatInfo, that's used for
        /// format strings, day names etc but the invariant culture is used for text comparisons and
        /// resource lookups. Otherwise, ``ValueError`` is thrown.
        """
        if provider is None:
            return cls._get_format_info(cls.current_info.culture_info)
        if isinstance(provider, CultureInfo):
            return cls._get_format_info(provider)
        if isinstance(provider, DateTimeFormatInfo):
            return _PyodaFormatInfo(CultureInfo.invariant_culture, provider)
        raise ValueError(f"Cannot use provider of type {type(provider).__name__} in Pyoda Time")

    def __str__(self) -> str:
        """Returns a string that represents this instance."""
        return f"PyodaFormatInfo[{self.__culture_info.name}]"


class _EraDescription:
    """The description for an era: the primary name and all possible names."""

    def __init__(self, primary_name: str, all_names: list[str]) -> None:
        self._primary_name = primary_name
        self._all_names = all_names

    @classmethod
    def _for_era(cls, era: Era, culture_info: CultureInfo) -> _EraDescription:
        pipe_delimited = _PatternResources._resource_manager.get_string(era._resource_identifier, culture_info)
        all_names: list[str] = []
        primary_name: str = ""

        if pipe_delimited:
            # If the BCL has provided an era name other than the one we'd consider
            # to be the primary one, make *that* the primary one for formatting.
            era_name_from_culture = cls.__get_era_name_from_bcl(era, culture_info)
            if era_name_from_culture and not pipe_delimited.startswith(era_name_from_culture + "|"):
                pipe_delimited = f"{era_name_from_culture}|{pipe_delimited}"
            all_names = pipe_delimited.split("|")
            primary_name = all_names[0]
            # Order by length, descending to avoid early out
            # (e.g. parsing BCE as BC and then having a spare E)
            all_names = sorted(all_names, key=lambda x: len(x), reverse=True)

        return _EraDescription(primary_name, all_names)

    @classmethod
    def __get_era_name_from_bcl(cls, era: Era, culture: CultureInfo) -> str | None:
        from pyoda_time._compatibility._gregorian_calendar import GregorianCalendar
        from pyoda_time._compatibility._hijri_calendar import HijriCalendar
        from pyoda_time._compatibility._persian_calendar import PersianCalendar
        from pyoda_time._compatibility._um_al_qura_calendar import UmAlQuraCalendar

        calendar = culture.date_time_format.calendar

        get_era_from_calendar: bool = (
            (era == Era.common and isinstance(calendar, GregorianCalendar))
            or (era == Era.anno_persico and isinstance(calendar, PersianCalendar))
            or (era == Era.anno_hegirae and isinstance(calendar, HijriCalendar | UmAlQuraCalendar))
        )

        if get_era_from_calendar:
            return culture.date_time_format.get_era_name(1)
        return None
