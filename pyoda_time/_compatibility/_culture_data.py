# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
import typing
from enum import IntEnum
from typing import Iterable

import icu

from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_data import _CalendarData
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._culture_types import CultureTypes
from pyoda_time._compatibility._globalization_mode import _GlobalizationMode
from pyoda_time._compatibility._gregorian_calendar import GregorianCalendar
from pyoda_time._compatibility._string_builder import StringBuilder

if typing.TYPE_CHECKING:
    from pyoda_time._compatibility._culture_info import CultureInfo
    from pyoda_time._compatibility._number_format_info import NumberFormatInfo


class _CultureDataMeta(type):
    """Metaclass for CultureData static properties."""

    @property
    def invariant(self) -> _CultureData:
        """Equivalent to CultureData.Invariant in .NET.

        The invariant culture independent of any particular real-world locale.

        Whereas in .NET it is a set of hard-coded definitions within the CultureData
        class itself, here we are creating a PyICU.Locale with an empty name.

        PyICU accepts this name and gives us back a Locale with default (i.e. invariant)
        defaults.

        Whether the values which that Locale gives us are the same as those of the invariant culture
        in .NET remains to be seen, but so far it does...
        """
        return _CultureData("C")


class _CultureData(metaclass=_CultureDataMeta):
    """A bare-bones port of the ``System.Globalization.CultureData`` internal class in .NET.

    In .NET this is a partial class with four source files.

    * CultureData.cs
    * CultureData.Icu.cs
    * CultureData.Nls.cs
    * CultureData.Unix.cs

    In .NET, culture (locale) data is typically gleaned from ICU (International Components for Unicode).

    https://unicode-org.github.io/icu-docs/

    .NET interacts with ICU's C/C++ API via a dotnet runtime interop layer within System.Globalization.Native:

    https://github.com/dotnet/runtime/blob/cc89d7db095028948afde863114b3ca04147477d/src/native/libs/System.Globalization.Native/pal_locale.c

    In .NET Framework, CultureData is an internal C# abstraction over those interop layer calls to ICU's C++ API.

    This Python implementation relies on the PyICU library, which is python bindings for ICU's C++ API,
    to emulate the functionality of ``CultureData`` in .NET.

    Unlike the .NET CultureData, there is no support for NLS, which is Microsoft's own localisation information.

    (That is unlikely to change; As of dotnet 5, the globalization mode defaults to ICU over NLS.)
    """

    __LOCALE_NAME_MAX_LENGTH: typing.Final[int] = 85

    def __init__(self, name: str = "") -> None:
        name = name.strip()

        if name in ("", "C", "c"):
            # Using this as roughly equivalent to the "Invariant" CultureInfo name
            icu_compatible_name = ""
        else:
            # ICU uses underscores (en_US), whereas dotnet typically uses hyphens (en-US),
            # although internally dotnet allows for locale names to be formatted either way.
            # Let's be kind to folks coming to the library who are familiar with .NET.
            icu_compatible_name = name.replace("-", "_")

            if not self.__is_valid_culture_name(icu_compatible_name):
                raise ValueError(f"{name} is not a valid culture name.")

            # According to the BCP47 standard, this should be case-insensitive.
            # So "en_US", "EN_us" and "EN_US" should all result in the same Locale object.
            available_locales: Iterable[str] = (k.lower() for k in icu.Locale.getAvailableLocales().keys())
            if icu_compatible_name.lower() not in available_locales:
                # PyICU doesn't do this validation for us.
                # If we don't do this check ourselves, it will
                # happily just return a locale with our name
                # with the default values for locale data.
                raise ValueError(f"Unknown locale: {name}")

        self.__raw_name: str = name
        self.__sName, self.__bNeutral = self.__normalize_culture_name(self.__raw_name)
        self.__sRealName = self.__sWindowsName = self.__sName
        self.__locale: icu.Locale = icu.Locale(icu_compatible_name)

        self.__calendars: dict[int, _CalendarData] = {}
        self.__sAM1159: str | None = None  # (user can override) AM designator
        self.__sPM1159: str | None = None  # // (user can override) PM designator
        self.__sTimeSeparator: str | None = None

    # TODO: IcuGetLocaleInfo overrides should be fun, if we need them...
    def __icu_get_locale_info(self, type_: LocaleStringData, ui_culture_name: str | None = None) -> str:
        assert not _GlobalizationMode._invariant
        assert not _GlobalizationMode._use_nls
        assert self.__sWindowsName is not None

        match type_:
            case LocaleStringData.NegativeInfinitySymbol:
                # Noped out of this for now, until its needed
                raise NotImplementedError
        from pyoda_time._compatibility._interop import _Interop

        return _Interop._Globalization._get_locale_info_string(self.__sWindowsName, type_) or ""

    @classmethod
    def _get_cultures(cls, types: CultureTypes) -> typing.Sequence[CultureInfo]:
        # TODO: ArgumentOutOfRange validation?

        # TODO: WindowsOnlyCulture check

        # TODO: GlobalizationMode.Invariant check

        # TODO: GlobalizationMode.UseNls check

        return cls.__icu_enum_cultures(types)

    @property
    def _culture_name(self) -> str:
        """The real name used to construct the locale (ie: de-DE_phoneb)."""
        return self.__raw_name

    @property
    def name(self) -> str:
        """Locale name (ie: de-DE, NO sort information)"""
        return self.__sName  # Wrapped in str() for mypy reasons

    @property
    def _am_designator(self) -> str:
        if self.__sAM1159 is None:
            self.__sAM1159 = self.__get_locale_info_core_user_override(LocaleStringData.AMDesignator)
        return self.__sAM1159

    @property
    def _pm_designator(self) -> str:
        if self.__sPM1159 is None:
            self.__sPM1159 = self.__get_locale_info_core_user_override(LocaleStringData.PMDesignator)
        return self.__sPM1159

    def _day_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return typing.cast(list[str], self._get_calendar(calendar_id)._saDayNames)

    def _abbreviated_day_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        return typing.cast(list[str], self._get_calendar(calendar_id)._saAbbrevDayNames)

    def _month_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return typing.cast(list[str], self._get_calendar(calendar_id)._saMonthNames)

    def _genitive_month_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        return typing.cast(list[str], self._get_calendar(calendar_id)._saMonthGenitiveNames)

    def _abbreviated_month_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        return typing.cast(list[str], self._get_calendar(calendar_id)._saAbbrevMonthNames)

    def _abbreviated_genitive_month_names(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        return typing.cast(list[str], self._get_calendar(calendar_id)._saAbbrevMonthGenitiveNames)

    def _short_dates(self, calendar_id: _CalendarId) -> typing.Sequence[str]:
        """(user can override default only) short date format."""
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return typing.cast(list[str], self._get_calendar(calendar_id)._saShortDates)

    def _get_calendar(self, calendar_id: _CalendarId) -> _CalendarData:
        if _GlobalizationMode._invariant:
            return _CalendarData._invariant

        assert 0 < calendar_id.value < _CalendarId.LAST_CALENDAR.value, "Expect calendarId to be in a valid range"

        # arrays are 0 based, calendarIds are 1 based
        calendar_index = calendar_id.value - 1

        if not (calendar := self.__calendars.get(calendar_index)):
            # TODO: A literal port would be:
            #  calendar = _CalendarData(self.__sWindowsName, calendar_id, self.__bUseOverrides)
            calendar = _CalendarData(self.name, calendar_id, False)
        return calendar

    @property
    def _is_invariant_culture(self) -> bool:
        return not self.name  # string.IsNullOrEmpty(this.Name)

    @property
    def _default_calendar(self) -> Calendar:
        """Port of the internal ``CultureData.DefaultCalendar`` property.

        This returns an instance of the default ``System.Globalization.Calendar`` for the locale.
        """

        if _GlobalizationMode._invariant:
            return GregorianCalendar()

        # TODO: .NET calls into ICU to get the supported calendars and the default/preferred one.
        #  https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L109-L140
        #  That part of the ICU API is not exposed by PyICU...
        #  So we have to get a bit creative here to map it to a .NET style calendar ID.

        calendar: icu.Calendar = icu.Calendar.createInstance(self.__locale)
        icu_calendar_name: str = calendar.getType()
        calendar_id: _CalendarId = _CalendarId.from_icu_calendar_name(icu_calendar_name)
        from ._culture_info import CultureInfo

        return CultureInfo._get_calendar_instance(calendar_id)

    def _era_names(self, calendar_id: _CalendarId) -> list[str]:
        return self._get_calendar(calendar_id)._saEraNames

    @property
    def _time_separator(self) -> str:
        """Port of the internal ``CultureData.TimeSeparator`` property.

        As in .NET, the time separator is determined by parsing the locale's long time format.
        """
        if self.__sTimeSeparator is None and not _GlobalizationMode._invariant:
            # TODO: Check/test this is actually the case
            #  As in .NET, fr-CA is special cased to force the colon separator.
            #  The pattern there is "HH 'h' mm 'min' ss 's'", from which the
            #  separator cannot be derived.
            if self.name == "fr-CA":
                self._sTimeSeparator = ":"
            else:
                long_time_format = self.__icu_get_time_format_string()
                if not long_time_format or not long_time_format.strip():
                    raise NotImplementedError("longTimeFormat = LongTimes[0];")
                self._sTimeSeparator = self.__get_time_separator(long_time_format)

        return self._sTimeSeparator

    def __icu_get_time_format_string(self, short_format: bool = False) -> str:
        style = icu.DateFormat.kShort if short_format else icu.DateFormat.kLong
        return str(icu.SimpleDateFormat(style=style, locale=self.__locale).toPattern())

    @classmethod
    def __get_time_separator(cls, pattern: str) -> str:
        """Port of the private static ``GetTimeSeparator`` method.

        This is used to derive the locale's time separator (e.g. ':' in '12:39:00') from the locale's long time pattern.
        """
        return cls.__get_separator(pattern, "Hhms")

    @classmethod
    def __get_date_separator(cls, pattern: str) -> str:
        """Port of the private static ``GetDateSeparator`` method.

        This is used to derive the locale's date separator (e.g. '/' in '9/1/03') from the locale's short date format.
        """
        return cls.__get_separator(pattern, "dyM")

    @classmethod
    def __get_separator(cls, pattern: str, time_parts: str) -> str:
        """Finds the separator between time_parts in the given pattern.

        This is used to derive the locale's date or time separator from its date/time patterns.
        """
        index = cls.__index_of_time_part(pattern, 0, time_parts)
        if index != -1:
            # Found a time part, find out when it changes
            c_time_part = pattern[index]

            index += 1

            while index < len(pattern) and pattern[index] == c_time_part:
                index += 1

            separator_start = index

            # Now we need to find the end of the separator
            if separator_start < len(pattern):
                separator_end = cls.__index_of_time_part(pattern, separator_start, time_parts)
                if separator_end != -1:
                    return cls.__unescape_nls_string(pattern, separator_start, separator_end - 1)

        return ""

    @classmethod
    def __index_of_time_part(cls, pattern: str, start_index: int, time_parts: str) -> int:
        """Return the index of the time part in the given pattern.

        Python implementation of ``CultureData.IndexOfTimePart()``.
        """
        # TODO: can this be replaced with str.index() in Python?
        assert start_index >= 0, "start_index cannot be negative"
        assert not any(char in time_parts for char in "'\\"), "time_parts cannot include quote characters"
        in_quote = False
        i = start_index
        while i < len(pattern):
            char = pattern[i]
            if not in_quote and char in time_parts:
                return i
            if char == "\\":
                if i + 1 < len(pattern):
                    i += 1
                    if pattern[i] not in ["'", "\\"]:
                        i -= 1  # backup since we will move over this next
            elif char == "'":
                in_quote = not in_quote
            i += 1
        return -1

    def _date_separator(self, calendar_id: _CalendarId) -> str:
        """Date separator (derived from short date format)."""
        if _GlobalizationMode._invariant:
            return "/"

        if calendar_id == _CalendarId.JAPAN:  # TODO: && !LocalAppContextSwitches.EnforceLegacyJapaneseDateParsing)
            # The date separator is derived from the default short date pattern. So far this pattern is using
            # '/' as date separator when using the Japanese calendar which make the formatting and parsing work fine.
            # changing the default pattern is likely will happen in the near future which can easily break formatting
            # and parsing.
            # We are forcing here the date separator to '/' to ensure the parsing is not going to break when changing
            # the default short date pattern. The application still can override this in the code by
            # DateTimeFormatInfo.DateSeparator.
            return "/"

        return self.__get_date_separator(self._short_dates(calendar_id)[0])

    @classmethod
    def __unescape_nls_string(cls, s: str, start: int, end: int) -> str:
        """Used to unescape NLS strings in .NET Framework.

        Probably not needed here, but for the sake of completeness...
        """
        # TODO: Do we actually need this method if we don't support NLS?
        assert s is not None
        assert start >= 0
        assert end >= 0
        result = None

        i = start
        while i < len(s) and i <= end:
            char = s[i]
            if char == "'":
                if result is None:
                    result = StringBuilder(s[start:i])
            elif char == "\\":
                if result is None:
                    result = StringBuilder(s[start:i])
                i += 1
                if i < len(s):
                    if result is not None:
                        result.append(s[i])
            else:
                if result is not None:
                    result.append(char)
            i += 1

        if result is None:
            return s[start : end + 1]
        else:
            return result.to_string()

    def _get_nfi_values(self, nfi: NumberFormatInfo) -> None:
        """Populate the provided ``NumberFormatInfo`` with locale-specific values from ICU."""
        # TODO: This is a bare-bones port; just as much as we needed at the time and no more.
        number_format: icu.DecimalFormatSymbols = icu.DecimalFormatSymbols(self.__locale)
        nfi.positive_sign = number_format.getSymbol(icu.DecimalFormatSymbols.kPlusSignSymbol)

    def __get_locale_info_core_user_override(self, type_: LocaleStringData) -> str:
        # Omitting a couple of things which aren't relevant to this port:
        # - Check for invariant globalization mode which is never reached
        # - Check for use of NLS (as opposed to ICU) data
        return self.__icu_get_locale_info(type_)

    @classmethod
    def __icu_enum_cultures(cls, types: CultureTypes) -> typing.Sequence[CultureInfo]:
        from ._culture_info import CultureInfo

        if not (types & (CultureTypes.NEUTRAL_CULTURES | CultureTypes.SPECIFIC_CULTURES)):
            return []

        enum_neutrals = bool(types & CultureTypes.NEUTRAL_CULTURES)
        enum_specifics = bool(types & CultureTypes.SPECIFIC_CULTURES)

        culture_info_list: list[CultureInfo] = []

        for k, v in icu.Locale.getAvailableLocales().items():
            ci: CultureInfo = CultureInfo(k)
            if (enum_neutrals and ci.is_neutral_culture) or (enum_specifics and not ci.is_neutral_culture):
                culture_info_list.append(ci)

        return culture_info_list

    @staticmethod
    def __is_valid_culture_name(subject: str) -> tuple[bool, int, int]:
        """Port of the private static ``CultueData.IsValidCultureName()`` method in .NET.

        In .NET this method is 'a fast approximate implementation based on the BCP47 spec'.

        https://en.wikipedia.org/wiki/IETF_language_tag

        When it returns False, the input is definitely wrong. However, it may return True in some
        cases where the name contains characters which aren't strictly allowed by the spec.

        It accommodates the input length of zero for invariant culture purposes.
        """

        index_of_underscore = -1
        index_of_extensions = -1
        if len(subject) == 0:
            return True, index_of_underscore, index_of_extensions
        if len(subject) == 1 or len(subject) > 85:
            return False, index_of_underscore, index_of_extensions

        flag = False
        for index, ch in enumerate(subject):
            if not ("A" <= ch <= "Z" or "a" <= ch <= "z" or ch in "0123456789" or ch in ["-", "_"]):
                return False, index_of_underscore, index_of_extensions

            if ch in ["-", "_"]:
                if index == 0 or index == len(subject) - 1 or subject[index - 1] in ["_", "-"]:
                    return False, index_of_underscore, index_of_extensions
                if ch == "_":
                    if flag:
                        return False, index_of_underscore, index_of_extensions
                    flag = True
                    index_of_underscore = index
                elif ch == "-" and index_of_extensions < 0 and index < len(subject) - 2:
                    if subject[index + 1] in ["t", "u"]:
                        if subject[index + 2] == "-" and (
                            subject[index + 1] == "t"
                            or index >= len(subject) - 6
                            or subject[index + 3 : index + 6] != "co-"
                        ):
                            index_of_extensions = index
        return True, index_of_underscore, index_of_extensions

    def __deepcopy__(self, memo: dict[int, typing.Any]) -> _CultureData:
        """Implementation to support CultureInfo.clone(), so we can copy.deepcopy(some_culture_info)

        icu.Locale is not pickleable, so we need to handle it manually.
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if not isinstance(v, icu.Locale):
                setattr(result, k, copy.deepcopy(v, memo))
        result.__locale = icu.Locale(self.__locale.getName())
        return result

    @property
    def _two_letter_iso_country_name(self) -> str:
        """ISO 3166 Country Name."""
        return str(self.__locale.getCountry())

    @property
    def _three_letter_iso_country_name(self) -> str:
        """3 letter ISO 3166 country code."""
        return str(self.__locale.getISO3Country())

    @property
    def _text_info_name(self) -> str:
        return self._culture_name

    @property
    def _is_neutral_culture(self) -> bool:
        return len(self._two_letter_iso_country_name) == 0

    @classmethod
    def __normalize_culture_name(cls, name: str) -> tuple[str, bool]:
        """Normalize the culture name.

        Returns a 2-tuple of the normalized name, and a bool indicating whether the culture is neutral.
        """
        if len(name) > cls.__LOCALE_NAME_MAX_LENGTH:
            raise ValueError(f"Invalid id for 'name': {name}")

        is_neutral_name = True
        normalized_name = []
        changed = False
        i = 0

        # Process characters before '-' or '_'
        while i < len(name) and name[i] not in ["-", "_"]:
            if name[i].isupper():
                normalized_name.append(name[i].lower())
                changed = True
            else:
                normalized_name.append(name[i])
            i += 1

        if i < len(name):
            # If we encounter '-' or '_', it's not a neutral culture name
            is_neutral_name = False

        # Process characters after '-' or '_'
        while i < len(name):
            if name[i].islower():
                normalized_name.append(name[i].upper())
                changed = True
            else:
                normalized_name.append(name[i])
            i += 1

        if changed:
            return "".join(normalized_name), is_neutral_name
        return name, is_neutral_name


class LocaleStringData(IntEnum):
    # localized name of locale, eg "German (Germany)" in UI language (corresponds to LOCALE_SLOCALIZEDDISPLAYNAME)
    LocalizedDisplayName = (0x00000002,)
    # Display name (language + country usually) in English, eg "German (Germany)"
    # (corresponds to LOCALE_SENGLISHDISPLAYNAME)
    EnglishDisplayName = (0x00000072,)
    # Display name in native locale language, eg "Deutsch (Deutschland) (corresponds to LOCALE_SNATIVEDISPLAYNAME)
    NativeDisplayName = (0x00000073,)
    # Language Display Name for a language, eg "German" in UI language (corresponds to LOCALE_SLOCALIZEDLANGUAGENAME)
    LocalizedLanguageName = (0x0000006F,)
    # English name of language, eg "German" (corresponds to LOCALE_SENGLISHLANGUAGENAME)
    EnglishLanguageName = (0x00001001,)
    # native name of language, eg "Deutsch" (corresponds to LOCALE_SNATIVELANGUAGENAME)
    NativeLanguageName = (0x00000004,)
    # localized name of country, eg "Germany" in UI language (corresponds to LOCALE_SLOCALIZEDCOUNTRYNAME)
    LocalizedCountryName = (0x00000006,)
    # English name of country, eg "Germany" (corresponds to LOCALE_SENGLISHCOUNTRYNAME)
    EnglishCountryName = (0x00001002,)
    # native name of country, eg "Deutschland" (corresponds to LOCALE_SNATIVECOUNTRYNAME)
    NativeCountryName = (0x00000008,)
    # abbreviated language name (corresponds to LOCALE_SABBREVLANGNAME)
    AbbreviatedWindowsLanguageName = (0x00000003,)
    # list item separator (corresponds to LOCALE_SLIST)
    ListSeparator = (0x0000000C,)
    # decimal separator (corresponds to LOCALE_SDECIMAL)
    DecimalSeparator = (0x0000000E,)
    # thousand separator (corresponds to LOCALE_STHOUSAND)
    ThousandSeparator = (0x0000000F,)
    # native digits for 0-9, eg "0123456789" (corresponds to LOCALE_SNATIVEDIGITS)
    Digits = (0x00000013,)
    # local monetary symbol (corresponds to LOCALE_SCURRENCY)
    MonetarySymbol = (0x00000014,)
    # English currency name (corresponds to LOCALE_SENGCURRNAME)
    CurrencyEnglishName = (0x00001007,)
    # Native currency name (corresponds to LOCALE_SNATIVECURRNAME)
    CurrencyNativeName = (0x00001008,)
    # uintl monetary symbol (corresponds to LOCALE_SINTLSYMBOL)
    Iso4217MonetarySymbol = (0x00000015,)
    # monetary decimal separator (corresponds to LOCALE_SMONDECIMALSEP)
    MonetaryDecimalSeparator = (0x00000016,)
    # monetary thousand separator (corresponds to LOCALE_SMONTHOUSANDSEP)
    MonetaryThousandSeparator = (0x00000017,)
    # AM designator (corresponds to LOCALE_S1159)
    AMDesignator = (0x00000028,)
    # PM designator (corresponds to LOCALE_S2359)
    PMDesignator = (0x00000029,)
    # positive sign (corresponds to LOCALE_SPOSITIVESIGN)
    PositiveSign = (0x00000050,)
    # negative sign (corresponds to LOCALE_SNEGATIVESIGN)
    NegativeSign = (0x00000051,)
    # ISO abbreviated language name (corresponds to LOCALE_SISO639LANGNAME)
    Iso639LanguageTwoLetterName = (0x00000059,)
    # ISO abbreviated country name (corresponds to LOCALE_SISO639LANGNAME2)
    Iso639LanguageThreeLetterName = (0x00000067,)
    # ISO abbreviated language name (corresponds to LOCALE_SISO639LANGNAME)
    Iso639LanguageName = (0x00000059,)
    # ISO abbreviated country name (corresponds to LOCALE_SISO3166CTRYNAME)
    Iso3166CountryName = (0x0000005A,)
    # 3 letter ISO country code (corresponds to LOCALE_SISO3166CTRYNAME2)
    Iso3166CountryName2 = (0x00000068,)  # 3 character ISO country name
    # Not a Number (corresponds to LOCALE_SNAN)
    NaNSymbol = (0x00000069,)
    # + Infinity (corresponds to LOCALE_SPOSINFINITY)
    PositiveInfinitySymbol = (0x0000006A,)
    # - Infinity (corresponds to LOCALE_SNEGINFINITY)
    NegativeInfinitySymbol = (0x0000006B,)
    # Fallback name for resources (corresponds to LOCALE_SPARENT)
    ParentName = (0x0000006D,)
    # Fallback name for within the console (corresponds to LOCALE_SCONSOLEFALLBACKNAME)
    ConsoleFallbackName = (0x0000006E,)
    # Returns the percent symbol (corresponds to LOCALE_SPERCENT)
    PercentSymbol = (0x00000076,)
    # Returns the permille (U+2030) symbol (corresponds to LOCALE_SPERMILLE)
    PerMilleSymbol = 0x00000077
