# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
from enum import IntEnum
from threading import Lock
from typing import TYPE_CHECKING, Any, Final, cast, overload

import icu

from pyoda_time._compatibility._calendar_data import _CalendarData
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._culture_types import CultureTypes
from pyoda_time._compatibility._globalization_mode import _GlobalizationMode
from pyoda_time._compatibility._gregorian_calendar import GregorianCalendar
from pyoda_time._compatibility._icu_locale_data import _IcuLocaleData, _IcuLocaleDataParts
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.utility._csharp_compatibility import _as_span, _private

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyoda_time._compatibility._calendar import Calendar
    from pyoda_time._compatibility._culture_info import CultureInfo
    from pyoda_time._compatibility._number_format_info import NumberFormatInfo


class _CultureDataMeta(type):
    """Metaclass for CultureData static properties."""

    _s_Invariant: _CultureData | None = None
    __lock = Lock()

    @property
    def _invariant(self) -> _CultureData:
        if self._s_Invariant is None:
            with self.__lock:
                if self._s_Invariant is None:
                    self._s_Invariant = _CultureData._create_culture_with_invariant_data()
        return self._s_Invariant

    @classmethod
    def _create_culture_with_invariant_data(cls) -> _CultureData:
        invariant: _CultureData = _CultureData._ctor()

        # Basics
        # Note that we override the resources since this IS NOT supposed to change (by definition)
        invariant._bUseOverrides = False
        invariant._bUseOverridesUserSetting = False
        invariant._sRealName = ""  # Name you passed in (ie: en-US, en, or de-DE_phoneb)
        invariant._sWindowsName = (
            ""  # Name OS thinks the object is (ie: de-DE_phoneb, or en-US (even if en was passed in))
        )

        # Identity
        invariant._sName = ""  # locale name (ie: en-us)
        invariant._sParent = ""  # Parent name (which may be a custom locale/culture)
        invariant._bNeutral = False  # Flags for the culture (ie: neutral or not right now)
        invariant._sEnglishDisplayName = "Invariant Language (Invariant Country)"  # English pretty name for this locale
        invariant._sNativeDisplayName = "Invariant Language (Invariant Country)"  # Native pretty name for this locale
        invariant._sSpecificCulture = ""  # The culture name to be used in CultureInfo.CreateSpecificCulture()

        # Language
        invariant._sISO639Language = "iv"  # ISO 639 Language Name
        invariant._sISO639Language2 = "ivl"  # 3 char ISO 639 lang name 2
        invariant._sEnglishLanguage = "Invariant Language"  # English name for this language
        invariant._sNativeLanguage = "Invariant Language"  # Native name of this language
        invariant._sAbbrevLang = "IVL"  # abbreviated language name (Windows Language Name)
        invariant._sConsoleFallbackName = ""  # The culture name for the console fallback UI culture
        invariant._iInputLanguageHandle = 0x07F  # input language handle

        # Region
        invariant._sRegionName = "IV"  # (RegionInfo)
        invariant._sEnglishCountry = "Invariant Country"  # english country name (RegionInfo)
        invariant._sNativeCountry = "Invariant Country"  # native country name (Windows Only)
        invariant._sISO3166CountryName = "IV"  # (RegionInfo), ie: US
        invariant._sISO3166CountryName2 = "ivc"  # 3 char ISO 3166 country name 2 2(RegionInfo)
        invariant._iGeoId = 244  # GeoId (Windows Only)

        # Numbers
        invariant._sPositiveSign = "+"  # positive sign
        invariant._sNegativeSign = "-"  # negative sign
        invariant._iDigits = 2  # number of fractional digits
        invariant._iNegativeNumber = 1  # negative number format
        invariant._waGrouping = []  # grouping of digits
        invariant._sDecimalSeparator = "."  # decimal separator
        invariant._sThousandSeparator = ","  # thousands separator
        invariant._sNaN = "NaN"  # Not a Number
        invariant._sPositiveInfinity = "Infinity"  # + Infinity
        invariant._sNegativeInfinity = "-Infinity"  # - Infinity

        # Percent
        invariant._iNegativePercent = 0  # Negative Percent (0-3)
        invariant._iPositivePercent = 0  # Positive Percent (0-11)
        invariant._sPercent = "%"  # Percent (%) symbol
        invariant._sPerMille = "\u2030"  # PerMille symbol

        # Currency
        invariant._sCurrency = "\u00a4"  # local monetary symbol: for international monetary symbol
        invariant._sIntlMonetarySymbol = "XDR"  # international monetary symbol (RegionInfo)
        invariant._sEnglishCurrency = "International Monetary Fund"  # English name for this currency (Windows Only)
        invariant._sNativeCurrency = "International Monetary Fund"  # Native name for this currency (Windows Only)
        invariant._iCurrencyDigits = 2  # local monetary fractional digits
        invariant._iCurrency = 0  # positive currency format
        invariant._iNegativeCurrency = 0  # negative currency format
        invariant._waMonetaryGrouping = []  # monetary grouping of digits
        invariant._sMonetaryDecimal = "."  # monetary decimal separator
        invariant._sMonetaryThousand = ","  # monetary thousands separator

        # Misc
        invariant._iMeasure = 0  # system of measurement 0=metric, 1=US (RegionInfo)
        invariant._sListSeparator = ","  # list separator

        # Time
        invariant._sTimeSeparator = ":"
        invariant._sAM1159 = "AM"  # AM designator
        invariant._sPM2359 = "PM"  # PM designator
        invariant._saLongTimes = ["HH:mm:ss"]  # time format
        invariant._saShortTimes = ["HH:mm", "hh:mm tt", "H:mm", "h:mm tt"]  # short time format
        invariant._saDurationFormats = ["HH:mm:ss"]

        # Calendar specific data
        invariant._iFirstDayOfWeek = 0  # first day of week
        invariant._iFirstWeekOfYear = 0  # first week of year

        # all available calendar type(s).  The first one is the default calendar
        invariant._waCalendars = [_CalendarId.GREGORIAN]

        if not _GlobalizationMode._invariant:
            # Store for specific data about each calendar
            invariant._calendars = [_CalendarData._invariant]

        # Text information
        invariant._iReadingLayout = 0

        # These are .NET Framework only, not coreclr
        from ._culture_info import CultureInfo

        invariant._iLanguage = CultureInfo._LOCALE_INVARIANT  # locale ID (0409) - NO sort information
        invariant._iDefaultAnsiCodePage = 1252  # default ansi code page ID (ACP)
        invariant._iDefaultOemCodePage = 437  # default oem code page ID (OCP or OEM)
        invariant._iDefaultMacCodePage = 10000  # default macintosh code page
        invariant._iDefaultEbcdicCodePage = 37  # default EBCDIC code page

        return invariant


@_private
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

    (That is unlikely to change As of dotnet 5, the globalization mode defaults to ICU over NLS.)
    """

    __ICU_ULOC_KEYWORD_AND_VALUES_CAPACITY: Final[int] = 100  # max size of keyword or value
    __ICU_ULOC_FULLNAME_CAPACITY: Final[int] = 157  # max size of locale name
    __WINDOWS_MAX_COLLATION_NAME_LENGTH: Final[int] = 8  # max collation name length in the culture name
    __LOCALE_NAME_MAX_LENGTH: Final[int] = 85
    __UNDEF: Final[int] = -1

    # Cache of cultures we've already looked up
    __s_cachedCultures: dict[str, _CultureData] | None = None
    __s_lock: Lock = Lock()

    # Override Flag
    # Name you passed in (ie: en-US, en, or de-DE_phoneb). Initialized by helper called during initialization.
    _sRealName: str | None = None
    _sWindowsName: str | None = (
        None  # Name OS thinks the object is (ie: de-DE_phoneb, or en-US (even if en was passed in))
    )

    # Identity
    _sName: str | None = None  # locale name (ie: en-us, NO sort info, but could be neutral)
    _sParent: str | None = None  # Parent name (which may be a custom locale/culture)
    _sEnglishDisplayName: str | None = None  # English pretty name for this locale
    _sNativeDisplayName: str | None = None  # Native pretty name for this locale
    # The culture name to be used in CultureInfo.CreateSpecificCulture(), en-US form if neutral, sort name if sort
    _sSpecificCulture: str | None = None

    # Language
    _sISO639Language: str | None = None  # ISO 639 Language Name
    _sISO639Language2: str | None = None  # ISO 639 Language Name
    _sEnglishLanguage: str | None = None  # English name for this language
    _sNativeLanguage: str | None = None  # Native name of this language
    _sAbbrevLang: str | None = None  # abbreviated language name (Windows Language Name) ex: ENU
    _sConsoleFallbackName: str | None = None  # The culture name for the console fallback UI culture
    _iInputLanguageHandle: int = __UNDEF  # input language handle

    # Region
    _sRegionName: str | None = None  # (RegionInfo)
    _sLocalizedCountry: str | None = None  # localized country name
    _sEnglishCountry: str | None = None  # english country name (RegionInfo)
    _sNativeCountry: str | None = None  # native country name
    _sISO3166CountryName: str | None = None  # ISO 3166 (RegionInfo), ie: US
    _sISO3166CountryName2: str | None = None  # 3 char ISO 3166 country name 2 2(RegionInfo) ex: USA (ISO)
    _iGeoId: int = __UNDEF  # GeoId

    # Numbers
    _sPositiveSign: str | None = None  # (user can override) positive sign
    _sNegativeSign: str | None = None  # (user can override) negative sign
    # (nfi populates these 5, don't have to be = undef)
    _iDigits: int = 0  # (user can override) number of fractional digits
    _iNegativeNumber: int = 0  # (user can override) negative number format
    _waGrouping: list[int] | None = None  # (user can override) grouping of digits
    _sDecimalSeparator: str | None = None  # (user can override) decimal separator
    _sThousandSeparator: str | None = None  # (user can override) thousands separator
    _sNaN: str | None = None  # Not a Number
    _sPositiveInfinity: str | None = None  # + Infinity
    _sNegativeInfinity: str | None = None  # - Infinity

    # Percent
    _iNegativePercent: int = __UNDEF  # Negative Percent (0-3)
    _iPositivePercent: int = __UNDEF  # Positive Percent (0-11)
    _sPercent: str | None = None  # Percent (%) symbol
    _sPerMille: str | None = None  # PerMille symbol

    # Currency
    _sCurrency: str | None = None  # (user can override) local monetary symbol
    _sIntlMonetarySymbol: str | None = None  # international monetary symbol (RegionInfo)
    _sEnglishCurrency: str | None = None  # English name for this currency
    _sNativeCurrency: str | None = None  # Native name for this currency
    # (nfi populates these 4, don't have to be = undef)
    _iCurrencyDigits: int = 0  # (user can override) # local monetary fractional digits
    _iCurrency: int = 0  # (user can override) positive currency format
    _iNegativeCurrency: int = 0  # (user can override) negative currency format
    _waMonetaryGrouping: list[int] | None = None  # (user can override) monetary grouping of digits
    _sMonetaryDecimal: str | None = None  # (user can override) monetary decimal separator
    _sMonetaryThousand: str | None = None  # (user can override) monetary thousands separator

    # Misc
    _iMeasure: int = __UNDEF  # (user can override) system of measurement 0=metric, 1=US (RegionInfo)
    _sListSeparator: str | None = None  # (user can override) list separator

    # Time
    _sAM1159: str | None = None  # (user can override) AM designator
    _sPM2359: str | None = None  # (user can override) PM designator
    _sTimeSeparator: str | None = None
    _saLongTimes: Sequence[str] | None = None  # (user can override) time format
    _saShortTimes: Sequence[str] | None = None  # (user can override) short time format
    _saDurationFormats: list[str] | None = None  # time duration format

    # Calendar specific data
    _iFirstDayOfWeek: int = __UNDEF  # (user can override) first day of week (gregorian really)
    _iFirstWeekOfYear: int = __UNDEF  # (user can override) first week of year (gregorian really)
    _waCalendars: list[_CalendarId] | None = (
        None  # all available calendar type(s).  The first one is the default calendar
    )

    # Store for specific data about each calendar
    _calendars: list[_CalendarData | None] | None = None  # Store for specific calendar data

    # Text information
    _iReadingLayout: int = __UNDEF  # Reading layout data
    # 0 - Left to right (eg en-US)
    # 1 - Right to left (eg arabic locales)
    # 2 - Vertical top to bottom with columns to the left and also left to right (ja-JP locales)
    # 3 - Vertical top to bottom with columns proceeding to the right

    # CoreCLR depends on this even though its not exposed publicly.

    _iDefaultAnsiCodePage: int = __UNDEF  # default ansi code page ID (ACP)
    _iDefaultOemCodePage: int = __UNDEF  # default oem code page ID (OCP or OEM)
    _iDefaultMacCodePage: int = __UNDEF  # default macintosh code page
    _iDefaultEbcdicCodePage: int = __UNDEF  # default EBCDIC code page

    _iLanguage: int = 0  # locale ID (0409) - NO sort information
    _bUseOverrides: bool = False  # use user overrides? this depends on user setting and if is user default locale.
    _bUseOverridesUserSetting: bool = False  # the setting the user requested for.
    _bNeutral: bool = False  # Flags for the culture (ie: neutral or not right now)

    # TODO: Region Names etc.

    @classmethod
    def _ctor(cls) -> _CultureData:
        """Implementation of the default, internal constructor.

        Returns an instance with the default (class level) attributes. These are "initialised" later with instance
        attributes.
        """
        return super().__new__(cls)

    @classmethod
    def _get_culture_data(cls, culture_name: str | None, use_user_override: bool) -> _CultureData | None:
        # First do a shortcut for Invariant
        if not culture_name:
            return cls._invariant

        if _GlobalizationMode._predefined_cultures_only:
            if _GlobalizationMode._invariant:  # Some extra checks (NLS etc.) omitted here
                # dotnet returns null here, not convinced that we need the extra complexity
                raise NotImplementedError

        # Try the hash table first
        hash_name = cls._ansi_to_lower(culture_name if use_user_override else culture_name + "*")
        temp_hash_table: dict[str, _CultureData] | None = cls.__s_cachedCultures
        if temp_hash_table is None:
            # No table yet, make a new one
            temp_hash_table = {}
        else:
            with cls.__s_lock:
                ret_val = temp_hash_table.get(hash_name)
            if ret_val is not None:
                return ret_val

        # Not found in the hash table, need to see if we can build one that works for us
        culture = cls.__create_culture_data(culture_name, use_user_override)
        if culture is None:
            return None

        # Found one, add it to the cache
        with cls.__s_lock:
            temp_hash_table[hash_name] = culture

        # Copy the hashtable to the corresponding member variables.  This will potentially overwrite
        # new tables simultaneously created by a new thread, but maximizes thread safety.
        cls.__s_cachedCultures = temp_hash_table

        return culture

    @classmethod
    def _ansi_to_lower(cls, test_string: str) -> str:
        # TODO: This should be TextInfo.ToLowerAsciiInvariant(testString)
        return test_string.lower()

    @classmethod
    def __create_culture_data(cls, culture_name: str, use_user_override: bool) -> _CultureData | None:
        from ._culture_info import CultureInfo

        if _GlobalizationMode._invariant:
            if len(culture_name) > cls.__LOCALE_NAME_MAX_LENGTH or not CultureInfo._verify_culture_name(
                culture_name, False
            ):
                return None
            cd: _CultureData = cls._create_culture_with_invariant_data()
            cd._sName, cd._bNeutral = cls.__normalize_culture_name(culture_name)
            cd._bUseOverridesUserSetting = use_user_override
            cd._sRealName = cd._sName
            cd._sWindowsName = cd._sName
            cd._iLanguage = CultureInfo._LOCALE_CUSTOM_UNSPECIFIED
            return cd

        if (len(culture_name) == 1 and culture_name[0] == "C") or culture_name[0] == "c":
            # Always map the "C" locale to Invariant to avoid mapping it to en_US_POSIX on Linux because POSIX
            # locale collation doesn't support case insensitive comparisons.
            # We do the same mapping on Windows for the sake of consistency.
            return cls._invariant

        culture: _CultureData = _CultureData._ctor()
        culture._sRealName = culture_name
        culture._bUseOverridesUserSetting = use_user_override

        # Ask native code if that one's real, populate _sWindowsName
        if not culture.__init_culture_data_core() and not culture.__init_compatibility_culture_data():
            return None

        # We need _sWindowsName to be initialized to know if we're using overrides.
        culture.__init_user_override(use_user_override)
        return culture

    def __init_user_override(self, use_user_override: bool) -> None:
        # Unix doesn't support user overrides
        pass

    def __init_compatibility_culture_data(self) -> bool:
        # for compatibility handle the deprecated ids: zh-chs, zh-cht

        # In .NET, the null-forgiving operator is used in this assignment.
        assert self._sRealName is not None
        culture_name: str = self._sRealName

        fallback_culture_name: str
        real_culture_name: str
        match self._ansi_to_lower(culture_name):
            case "zh-chs":
                fallback_culture_name = "zh-Hans"
                real_culture_name = "zh-CHS"
            case "zh-cht":
                fallback_culture_name = "zh-Hant"
                real_culture_name = "zh-CHT"
            case _:
                return False

        # fixup our data
        self._sRealName = real_culture_name  # the name that goes back to the user
        self._sParent = fallback_culture_name

        return True

    def __init_culture_data_core(self) -> bool:
        return self.__init_icu_culture_data_core()

    def __init_icu_culture_data_core(self) -> bool:
        """This method uses the sRealName field (which is initialized by the constructor before this is called) to
        initialize the rest of the state of CultureData based on the underlying OS globalization library."""
        from ._culture_info import CultureInfo

        assert self._sRealName is not None
        assert not _GlobalizationMode._invariant

        ICU_COLLATION_KEYWORD: Final[str] = "@collation="
        real_name_buffer = self._sRealName

        # Basic validation
        is_valid_culture_name, index, index_of_extensions = self.__is_valid_culture_name(real_name_buffer)
        if not is_valid_culture_name:
            return False

        # Replace _ (alternate sort) with @collation= for ICU
        if index > 0:
            # TODO: Check this
            # Extract the part of the string after the underscore
            alternate_sort_name = real_name_buffer[index + 1 :]
            # Concatenate the part of the string before the underscore, the ICU collation keyword,
            # and the alternate sort name
            real_name_buffer = real_name_buffer[:index] + ICU_COLLATION_KEYWORD + alternate_sort_name

        # TODO:
        #  if _GlobalizationMode._hybrid:
        #      ...
        #  else:

        # Get the locale name from ICU
        success, self._sWindowsName = self.__get_locale_name(real_name_buffer)
        if not success:
            return False

        assert self._sWindowsName is not None

        self._sRealName, collation_start = self.__normalize_culture_name(
            self._sWindowsName, _as_span(self._sRealName, index_of_extensions) if index_of_extensions > 0 else ""
        )

        self._iLanguage = self._LCID
        if self._iLanguage == 0:
            self._iLanguage = CultureInfo._LOCALE_CUSTOM_UNSPECIFIED

        self._bNeutral = len(self._two_letter_iso_country_name) == 0
        self._sSpecificCulture = (
            _IcuLocaleData._get_specific_culture_name(self._sRealName) if self._bNeutral else self._sRealName
        )

        # Remove the sort from sName unless custom culture
        # To ensure compatibility, it is necessary to allow the creation of
        # cultures like zh_CN (using ICU notation) in the case of _bNeutral.
        self._sName = self._sRealName if collation_start < 0 or self._bNeutral else self._sRealName[0:collation_start]

        return True

    @property
    def _LCID(self) -> int:
        if self._iLanguage == 0 and not _GlobalizationMode._invariant:
            assert self._sRealName is not None
            if _GlobalizationMode._use_nls:
                raise NotImplementedError
            self._iLanguage = self.__icu_locale_name_to_LCID(self._sRealName)
        return self._iLanguage

    @classmethod
    def __icu_locale_name_to_LCID(cls, culture_name: str) -> int:
        assert not _GlobalizationMode._invariant
        assert not _GlobalizationMode._use_nls
        from ._culture_info import CultureInfo

        lcid: int = _IcuLocaleData._get_locale_data_numeric_part(culture_name, _IcuLocaleDataParts.Lcid)
        return CultureInfo._LOCALE_CUSTOM_UNSPECIFIED if lcid == -1 else lcid

    @classmethod
    def __get_locale_name(cls, locale_name: str) -> tuple[bool, str | None]:
        buffer: list[str] = []
        from pyoda_time._compatibility._interop import _Interop

        if not _Interop._Globalization._get_locale_name(locale_name, buffer, cls.__ICU_ULOC_FULLNAME_CAPACITY):
            return False, None
        windows_name = "".join(buffer)
        return True, windows_name

    @overload
    def __icu_get_locale_info(self, type_: LocaleNumberData) -> int: ...

    @overload
    def __icu_get_locale_info(self, type_: LocaleStringData, ui_culture_name: str | None = None) -> str: ...

    def __icu_get_locale_info(
        self, type_: LocaleStringData | LocaleNumberData, ui_culture_name: str | None = None
    ) -> str | int:
        # private int IcuGetLocaleInfo(LocaleNumberData type)
        if isinstance(type_, LocaleNumberData):
            assert not _GlobalizationMode._use_nls
            assert self._sWindowsName is not None

            match type_:
                case LocaleNumberData.CalendarType:
                    # returning 0 will cause the first supported calendar to
                    # be returned, which is the preferred calendar
                    return 0

            raise NotImplementedError
        elif isinstance(type_, LocaleStringData):
            assert not _GlobalizationMode._invariant
            assert not _GlobalizationMode._use_nls
            assert self._sWindowsName is not None

            match type_:
                case LocaleStringData.NegativeInfinitySymbol:
                    # Noped out of this for now, until its needed
                    raise NotImplementedError
            from pyoda_time._compatibility._interop import _Interop

            return _Interop._Globalization._get_locale_info_string(self._sWindowsName, type_) or ""
        raise NotImplementedError

    def __get_time_formats_core(self, short_format: bool) -> Sequence[str]:
        time_format = self.__icu_get_time_format_string(short_format)
        return [time_format]

    @classmethod
    def _get_cultures(cls, types: CultureTypes) -> Sequence[CultureInfo]:
        from ._culture_info import CultureInfo
        # TODO: ArgumentOutOfRange validation?

        # TODO: WindowsOnlyCulture check

        if _GlobalizationMode._invariant:
            return [CultureInfo("")]

        if _GlobalizationMode._use_nls:
            raise NotImplementedError

        return cls.__icu_enum_cultures(types)

    @property
    def _culture_name(self) -> str:
        """The real name used to construct the locale (ie: de-DE_phoneb)."""
        assert self._sRealName is not None
        # since windows doesn't know about zh-CHS and zh-CHT,
        # we leave sRealName == zh-Hanx but we still need to
        # pretend that it was zh-CHX.
        match self._sName:
            case "zh-CHS" | "zh-CHT":
                return self._sName
        return self._sRealName

    @property
    def name(self) -> str:
        """Locale name (ie: de-DE, NO sort information)"""
        return self._sName or ""

    @property
    def _am_designator(self) -> str:
        if self._sAM1159 is None:
            self._sAM1159 = self.__get_locale_info_core_user_override(LocaleStringData.AMDesignator)
        return self._sAM1159

    @property
    def _pm_designator(self) -> str:
        if self._sPM2359 is None:
            self._sPM2359 = self.__get_locale_info_core_user_override(LocaleStringData.PMDesignator)
        return self._sPM2359

    @property
    def _long_times(self) -> Sequence[str]:
        if self._saLongTimes is None and not _GlobalizationMode._invariant:
            assert not _GlobalizationMode._invariant
            long_times = self.__get_time_formats_core(short_format=False)
            if not long_times:
                # TODO: long_times = self._invariant._saLongTimes
                raise NotImplementedError("Requires CultureData.Invariant")
            self._saLongTimes = long_times

        # In .NET, the return statement uses the null-forgiving operator.
        assert self._saLongTimes is not None
        return self._saLongTimes

    @property
    def _short_times(self) -> Sequence[str]:
        if self._saShortTimes is None and not _GlobalizationMode._invariant:
            assert not _GlobalizationMode._invariant
            short_times = self.__get_time_formats_core(short_format=True)
            if not short_times:
                short_times = self.__derive_short_times_from_long()
            self._saShortTimes = short_times

        # In .NET, the return statement uses the null-forgiving operator.
        # This assert could potentially throw at runtime, but it _shouldn't_.
        # And it is probably safer than cast() or a type ignore.
        assert self._saShortTimes is not None
        return self._saShortTimes

    def __derive_short_times_from_long(self) -> Sequence[str]:
        raise NotImplementedError

    def _long_dates(self, calendar_id: _CalendarId) -> Sequence[str]:
        long_dates = self._get_calendar(calendar_id)._saLongDates
        assert long_dates
        return long_dates

    def _day_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return cast(list[str], self._get_calendar(calendar_id)._saDayNames)

    def _abbreviated_day_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        return cast(list[str], self._get_calendar(calendar_id)._saAbbrevDayNames)

    def _month_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return cast(list[str], self._get_calendar(calendar_id)._saMonthNames)

    def _genitive_month_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        return cast(list[str], self._get_calendar(calendar_id)._saMonthGenitiveNames)

    def _abbreviated_month_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        return cast(list[str], self._get_calendar(calendar_id)._saAbbrevMonthNames)

    def _abbreviated_genitive_month_names(self, calendar_id: _CalendarId) -> Sequence[str]:
        return cast(list[str], self._get_calendar(calendar_id)._saAbbrevMonthGenitiveNames)

    def _short_dates(self, calendar_id: _CalendarId) -> Sequence[str]:
        """(user can override default only) short date format."""
        # Cast required as mypy thinks this might be None.
        # Can be refactored out later.
        return cast(list[str], self._get_calendar(calendar_id)._saShortDates)

    def _get_calendar(self, calendar_id: _CalendarId) -> _CalendarData:
        if _GlobalizationMode._invariant:
            return _CalendarData._invariant

        assert (
            0 < calendar_id.value <= _CalendarId.LAST_CALENDAR.value
        ), f"Expect calendarId to be in a valid range, not {calendar_id}"

        # arrays are 0 based, calendarIds are 1 based
        calendar_index = calendar_id.value - 1

        # Have to have calendars
        if self._calendars is None:
            self._calendars = [None for _ in range(_CalendarData._MAX_CALENDARS)]

        if (calendar := self._calendars[calendar_index]) is None:
            assert self._sWindowsName is not None
            calendar = _CalendarData(self._sWindowsName, calendar_id, self._bUseOverrides)
        return calendar

    @property
    def _is_invariant_culture(self) -> bool:
        return not self.name  # string.IsNullOrEmpty(this.Name)

    @property
    def _default_calendar(self) -> Calendar:
        """Port of the internal ``CultureData.DefaultCalendar`` property.

        This returns an instance of the default ``System.Globalization.Calendar`` for the locale.
        """

        from ._culture_info import CultureInfo

        if _GlobalizationMode._invariant:
            return GregorianCalendar()

        # TODO: .NET calls into ICU to get the supported calendars and the default/preferred one.
        #  https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L109-L140
        #  That part of the ICU API is not exposed by PyICU...
        #  So we have to get a bit creative here to map it to a .NET style calendar ID.

        default_cal_id: _CalendarId = _CalendarId(self.__get_locale_info_core(LocaleNumberData.CalendarType))

        if default_cal_id == _CalendarId.UNINITIALIZED_VALUE:
            default_cal_id = self._calendar_ids[0]

        return CultureInfo._get_calendar_instance(default_cal_id)

    @property
    def _calendar_ids(self) -> list[_CalendarId]:
        if self._waCalendars is None and not _GlobalizationMode._invariant:
            # In .NET, the array is initialised with a capacity of 23 (nulls).
            # The interop code then fills up the array with however many calendars
            # ICU knows about for the locale.
            #
            # PyICU only gives us one calendar though, so here we just set the
            # first (and only) item in the list to the uninitialized enum member.
            calendars: list[_CalendarId] = [_CalendarId.UNINITIALIZED_VALUE]
            assert self._sWindowsName is not None

            count: int = _CalendarData._get_calendars_core(self._sWindowsName, self._bUseOverrides, calendars)
            assert len(calendars) == count

            # See if we had a calendar to add.
            if count == 0:
                # Failed for some reason, just grab Gregorian from Invariant
                self._waCalendars = self.__class__._invariant._waCalendars
            else:
                # The OS may not return calendar 4 for zh-TW, but we've always allowed it.
                # TODO: Is this hack necessary long-term?
                # TODO: Is this hack necessary for Python because PyICU only gives us one calendar anyway?
                if self._sWindowsName == "zh-TW":
                    raise NotImplementedError

                # It worked, remember the list
                self._waCalendars = calendars

        # In .NET, they use the null-forgiving operator on the return statement.
        # This _shouldn't_ ever throw at runtime, but if it does then at least
        # it will be safer than a `typing.cast()` or a `# type: ignore`.
        assert self._waCalendars is not None
        assert len(self._waCalendars) > 0
        assert _CalendarId.UNINITIALIZED_VALUE not in self._waCalendars

        return self._waCalendars

    def _era_names(self, calendar_id: _CalendarId) -> list[str]:
        return self._get_calendar(calendar_id)._saEraNames

    @property
    def _time_separator(self) -> str | None:
        """Time separator (derived from time format)"""
        if self._sTimeSeparator is None and not _GlobalizationMode._invariant:
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
        assert not _GlobalizationMode._use_nls
        assert self._sWindowsName is not None

        # TODO: Move this logic to Interop.Globalization method e.g.
        #  from pyoda_time._compatibility._interop import _Interop
        #  _Interop._Globalization._get_locale_time_format(
        #      self._sWindowsName, short_format, buffer, self.__ICU_ULOC_KEYWORD_AND_VALUES_CAPACITY
        #  )

        style = icu.DateFormat.kShort if short_format else icu.DateFormat.kLong
        pattern = icu.DateFormat.createTimeInstance(style, icu.Locale(self._sWindowsName)).toPattern()

        # Replace non-breaking and narrow non-breaking spaces
        pattern = pattern.replace("\u00a0", " ").replace("\u202f", " ").strip()

        return self.__convert_icu_time_format_string(pattern).strip()

    @staticmethod
    def __convert_icu_time_format_string(icu_format_string: str) -> str:
        result = []
        am_pm_added = False
        i = 0

        while i < len(icu_format_string):
            current = icu_format_string[i]

            if current == "'":  # Literal text markers
                result.append(icu_format_string[i])
                i += 1
                while i < len(icu_format_string):
                    current = icu_format_string[i]
                    result.append(current)
                    if current == "'":
                        break
                    i += 1

            elif current in ":.Hhms \u00a0\u202f":  # Time format characters and spaces
                result.append(current)

            elif current == "a":  # AM/PM marker
                if not am_pm_added:
                    am_pm_added = True
                    result.extend(["t", "t"])
            i += 1

        return "".join(result)

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
            elif result is not None:
                result.append(char)
            i += 1

        if result is None:
            return s[start : end + 1]
        else:
            return result.to_string()

    def _get_nfi_values(self, nfi: NumberFormatInfo) -> None:
        """Populate the provided ``NumberFormatInfo`` with locale-specific values from ICU."""
        # TODO: This is a bare-bones port; just as much as we needed at the time and no more.
        number_format: icu.DecimalFormatSymbols = icu.DecimalFormatSymbols(icu.Locale(self._sWindowsName))
        nfi.positive_sign = number_format.getSymbol(icu.DecimalFormatSymbols.kPlusSignSymbol)

    @overload
    def __get_locale_info_core(self, type_: LocaleNumberData) -> int: ...

    @overload
    def __get_locale_info_core(self, type_: LocaleStringData, ui_culture_name: str | None = None) -> str: ...

    def __get_locale_info_core(
        self, type_: LocaleNumberData | LocaleStringData, ui_culture_name: str | None = None
    ) -> int | str:
        if _GlobalizationMode._invariant:
            return 0

        if _GlobalizationMode._use_nls:
            raise NotImplementedError
        if isinstance(type_, LocaleStringData):
            return self.__icu_get_locale_info(type_)
        return self.__icu_get_locale_info(type_)

    def __get_locale_info_core_user_override(self, type_: LocaleStringData) -> str:
        # Omitting a couple of things which aren't relevant to this port:
        # - Check for invariant globalization mode which is never reached
        # - Check for use of NLS (as opposed to ICU) data
        return self.__icu_get_locale_info(type_)

    @classmethod
    def __icu_enum_cultures(cls, types: CultureTypes) -> Sequence[CultureInfo]:
        from ._culture_info import CultureInfo

        assert not _GlobalizationMode._invariant
        assert not _GlobalizationMode._use_nls

        if not (types & (CultureTypes.NEUTRAL_CULTURES | CultureTypes.SPECIFIC_CULTURES)):
            return []

        enum_neutrals = bool(types & CultureTypes.NEUTRAL_CULTURES)
        enum_specifics = bool(types & CultureTypes.SPECIFIC_CULTURES)

        culture_info_list: list[CultureInfo] = []
        # TODO: Move the appropriate functionality to Interop.Globalization.GetLocales()
        #  Should be similar to GlobalizationNative_GetLocales:
        #  https://github.com/dotnet/runtime/blob/d88c7ba88627b4b68ad523ba27cb354809eb7e67/src/native/libs/System.Globalization.Native/pal_locale.c#L149-L194
        for icu_locale_name in icu.Locale.getAvailableLocales().keys():
            dotnet_compatible_locale_name = icu_locale_name.replace("_", "-")
            ci: CultureInfo = CultureInfo.get_culture_info(dotnet_compatible_locale_name)
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
                        # Check for -u-co- which is not considered an extension for this purpose
                        is_u_co = (
                            subject[index + 1] == "u"
                            and index < len(subject) - 5
                            and subject[index + 2 : index + 6] == "-co-"
                        )

                        # If it's not -u-co-, then we can mark it as an extension
                        if not is_u_co:
                            index_of_extensions = index

        return True, index_of_underscore, index_of_extensions

    def __deepcopy__(self, memo: dict[int, Any]) -> _CultureData:
        """Implements copy functionality.

        In C# this class has no public constructor, so in Python we mimic that by monkeypatching __init__ and __new__ to
        raise an Exception.

        To get around that when copying such objects, we have to manage the instance creation on behalf of the copy
        module.
        """
        # Create a new instance of the class
        new_obj = super().__new__(self.__class__)
        memo[id(self)] = new_obj

        # Copy the attributes to the new instance.
        for k, v in self.__dict__.items():
            setattr(new_obj, k, copy.deepcopy(v, memo))

        return new_obj

    @property
    def _two_letter_iso_country_name(self) -> str:
        """ISO 3166 Country Name."""
        if self._sISO3166CountryName is None:
            self._sISO3166CountryName = self.__get_locale_info_core(LocaleStringData.Iso3166CountryName)
        return self._sISO3166CountryName

    @property
    def _three_letter_iso_country_name(self) -> str:
        """3 letter ISO 3166 country code."""
        if self._sISO3166CountryName2 is None:
            self._sISO3166CountryName2 = self.__get_locale_info_core(LocaleStringData.Iso3166CountryName2)
        return self._sISO3166CountryName2

    @property
    def _text_info_name(self) -> str:
        return self._culture_name

    @property
    def _is_neutral_culture(self) -> bool:
        return self._bNeutral

    @classmethod
    @overload
    def __normalize_culture_name(cls, name: str) -> tuple[str, bool]: ...

    @classmethod
    @overload
    def __normalize_culture_name(cls, name: str, extension: str) -> tuple[str, int]: ...

    @classmethod
    def __normalize_culture_name(cls, name: str, extension: str | None = None) -> tuple[str, int] | tuple[str, bool]:
        """Normalize the culture name.

        If just name is provided:
        Returns a 2-tuple of the normalized name, and a bool indicating whether the culture is neutral.

        If name and extension is provided:
        Returns a 2-tuple of the normalized name, and an integer representing the start index of the collation.
        """
        if extension is None:
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

        # both name and extension has been provided

        collation_start = -1
        changed = False
        buffer: list[str] = []

        i = 0
        while i < len(name) and len(buffer) < cls.__ICU_ULOC_FULLNAME_CAPACITY:
            c = name[i]
            if c == "-" and i < len(name) - 1 and name[i + 1] == "-":
                # Handling the special ICU transformation for certain names
                changed = True
                buffer.append("-")
                i += 1  # Skipping the next dash
            elif c == "@":
                changed = True
                if extension:
                    buffer.extend(extension)

                collation_index = name.find("collation=", i + 1)
                if collation_index > 0:
                    collation_index += len("collation=")
                    end_of_collation = name.find(";", collation_index)
                    if end_of_collation < 0:
                        end_of_collation = len(name)

                    length = min(cls.__WINDOWS_MAX_COLLATION_NAME_LENGTH, end_of_collation - collation_index)
                    if len(buffer) + length + 1 <= len(name):
                        collation_start = len(buffer)
                        buffer.append("_")
                        buffer.extend(name[collation_index : collation_index + length])

                # Once '@' is encountered and processed, break from the loop
                break
            else:
                buffer.append(c)
            i += 1

        return "".join(buffer) if changed else name, collation_start

    def _month_day(self, calendar_id: _CalendarId) -> str:
        month_day = self._get_calendar(calendar_id)._sMonthDay
        assert month_day is not None
        return month_day


class LocaleStringData(IntEnum):
    # localized name of locale, eg "German (Germany)" in UI language (corresponds to LOCALE_SLOCALIZEDDISPLAYNAME)
    LocalizedDisplayName = 0x00000002
    # Display name (language + country usually) in English, eg "German (Germany)"
    # (corresponds to LOCALE_SENGLISHDISPLAYNAME)
    EnglishDisplayName = 0x00000072
    # Display name in native locale language, eg "Deutsch (Deutschland) (corresponds to LOCALE_SNATIVEDISPLAYNAME)
    NativeDisplayName = 0x00000073
    # Language Display Name for a language, eg "German" in UI language (corresponds to LOCALE_SLOCALIZEDLANGUAGENAME)
    LocalizedLanguageName = 0x0000006F
    # English name of language, eg "German" (corresponds to LOCALE_SENGLISHLANGUAGENAME)
    EnglishLanguageName = 0x00001001
    # native name of language, eg "Deutsch" (corresponds to LOCALE_SNATIVELANGUAGENAME)
    NativeLanguageName = 0x00000004
    # localized name of country, eg "Germany" in UI language (corresponds to LOCALE_SLOCALIZEDCOUNTRYNAME)
    LocalizedCountryName = 0x00000006
    # English name of country, eg "Germany" (corresponds to LOCALE_SENGLISHCOUNTRYNAME)
    EnglishCountryName = 0x00001002
    # native name of country, eg "Deutschland" (corresponds to LOCALE_SNATIVECOUNTRYNAME)
    NativeCountryName = 0x00000008
    # abbreviated language name (corresponds to LOCALE_SABBREVLANGNAME)
    AbbreviatedWindowsLanguageName = 0x00000003
    # list item separator (corresponds to LOCALE_SLIST)
    ListSeparator = 0x0000000C
    # decimal separator (corresponds to LOCALE_SDECIMAL)
    DecimalSeparator = 0x0000000E
    # thousand separator (corresponds to LOCALE_STHOUSAND)
    ThousandSeparator = 0x0000000F
    # native digits for 0-9, eg "0123456789" (corresponds to LOCALE_SNATIVEDIGITS)
    Digits = 0x00000013
    # local monetary symbol (corresponds to LOCALE_SCURRENCY)
    MonetarySymbol = 0x00000014
    # English currency name (corresponds to LOCALE_SENGCURRNAME)
    CurrencyEnglishName = 0x00001007
    # Native currency name (corresponds to LOCALE_SNATIVECURRNAME)
    CurrencyNativeName = 0x00001008
    # uintl monetary symbol (corresponds to LOCALE_SINTLSYMBOL)
    Iso4217MonetarySymbol = 0x00000015
    # monetary decimal separator (corresponds to LOCALE_SMONDECIMALSEP)
    MonetaryDecimalSeparator = 0x00000016
    # monetary thousand separator (corresponds to LOCALE_SMONTHOUSANDSEP)
    MonetaryThousandSeparator = 0x00000017
    # AM designator (corresponds to LOCALE_S1159)
    AMDesignator = 0x00000028
    # PM designator (corresponds to LOCALE_S2359)
    PMDesignator = 0x00000029
    # positive sign (corresponds to LOCALE_SPOSITIVESIGN)
    PositiveSign = 0x00000050
    # negative sign (corresponds to LOCALE_SNEGATIVESIGN)
    NegativeSign = 0x00000051
    # ISO abbreviated language name (corresponds to LOCALE_SISO639LANGNAME)
    Iso639LanguageTwoLetterName = 0x00000059
    # ISO abbreviated country name (corresponds to LOCALE_SISO639LANGNAME2)
    Iso639LanguageThreeLetterName = 0x00000067
    # ISO abbreviated language name (corresponds to LOCALE_SISO639LANGNAME)
    Iso639LanguageName = 0x00000059
    # ISO abbreviated country name (corresponds to LOCALE_SISO3166CTRYNAME)
    Iso3166CountryName = 0x0000005A
    # 3 letter ISO country code (corresponds to LOCALE_SISO3166CTRYNAME2)
    Iso3166CountryName2 = 0x00000068  # 3 character ISO country name
    # Not a Number (corresponds to LOCALE_SNAN)
    NaNSymbol = 0x00000069
    # + Infinity (corresponds to LOCALE_SPOSINFINITY)
    PositiveInfinitySymbol = 0x0000006A
    # - Infinity (corresponds to LOCALE_SNEGINFINITY)
    NegativeInfinitySymbol = 0x0000006B
    # Fallback name for resources (corresponds to LOCALE_SPARENT)
    ParentName = 0x0000006D
    # Fallback name for within the console (corresponds to LOCALE_SCONSOLEFALLBACKNAME)
    ConsoleFallbackName = 0x0000006E
    # Returns the percent symbol (corresponds to LOCALE_SPERCENT)
    PercentSymbol = 0x00000076
    # Returns the permille (U+2030) symbol (corresponds to LOCALE_SPERMILLE)
    PerMilleSymbol = 0x00000077


class LocaleNumberData(IntEnum):
    # language id (corresponds to LOCALE_ILANGUAGE)
    LanguageId = 0x00000001
    # geographical location id, (corresponds to LOCALE_IGEOID)
    GeoId = 0x0000005B
    # 0 = context, 1 = none, 2 = national (corresponds to LOCALE_IDIGITSUBSTITUTION)
    DigitSubstitution = 0x00001014
    # 0 = metric, 1 = US (corresponds to LOCALE_IMEASURE)
    MeasurementSystem = 0x0000000D
    # number of fractional digits (corresponds to LOCALE_IDIGITS)
    FractionalDigitsCount = 0x00000011
    # negative number mode (corresponds to LOCALE_INEGNUMBER)
    NegativeNumberFormat = 0x00001010
    # # local monetary digits (corresponds to LOCALE_ICURRDIGITS)
    MonetaryFractionalDigitsCount = 0x00000019
    # positive currency mode (corresponds to LOCALE_ICURRENCY)
    PositiveMonetaryNumberFormat = 0x0000001B
    # negative currency mode (corresponds to LOCALE_INEGCURR)
    NegativeMonetaryNumberFormat = 0x0000001C
    # type of calendar specifier (corresponds to LOCALE_ICALENDARTYPE)
    CalendarType = 0x00001009
    # first day of week specifier (corresponds to LOCALE_IFIRSTDAYOFWEEK)
    FirstDayOfWeek = 0x0000100C
    # first week of year specifier (corresponds to LOCALE_IFIRSTWEEKOFYEAR)
    FirstWeekOfYear = 0x0000100D
    #
    # Returns one of the following 4 reading layout values:
    #  0 - Left to right (eg en-US)
    #  1 - Right to left (eg arabic locales)
    #  2 - Vertical top to bottom with columns to the left and also left to right (ja-JP locales)
    #  3 - Vertical top to bottom with columns proceeding to the right
    # (corresponds to LOCALE_IREADINGLAYOUT)
    #
    ReadingLayout = 0x00000070
    # Returns 0-11 for the negative percent format (corresponds to LOCALE_INEGATIVEPERCENT)
    NegativePercentFormat = 0x00000074
    # Returns 0-3 for the positive percent format (corresponds to LOCALE_IPOSITIVEPERCENT)
    PositivePercentFormat = 0x00000075
    # default ansi code page (corresponds to LOCALE_IDEFAULTCODEPAGE)
    OemCodePage = 0x0000000B
    # default ansi code page (corresponds to LOCALE_IDEFAULTANSICODEPAGE)
    AnsiCodePage = 0x00001004
    # default mac code page (corresponds to LOCALE_IDEFAULTMACCODEPAGE)
    MacCodePage = 0x00001011
    # default ebcdic code page (corresponds to LOCALE_IDEFAULTEBCDICCODEPAGE)
    EbcdicCodePage = 0x00001012
