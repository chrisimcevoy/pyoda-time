# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Callable

import icu

from pyoda_time._compatibility._calendar_data import _CalendarDataType, _IcuEnumCalendarsData
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._culture_data import LocaleStringData


def fixup_locale_name(locale_name: str) -> str:
    """Replaces underscores (which ICU uses in locale names) with hyphens (which dotnet uses in culture names).

    https://github.com/dotnet/runtime/blob/d1747a74705a49700d7c568fdb568704c2bbad58/src/native/libs/System.Globalization.Native/pal_locale.c#L114
    """
    return locale_name.replace("_", "-")


def get_locale_name(locale_name: str, canonicalize: bool) -> str:
    """
    https://github.com/dotnet/runtime/blob/d1747a74705a49700d7c568fdb568704c2bbad58/src/native/libs/System.Globalization.Native/pal_locale.c#L199
    """

    # TODO: This is simplified

    locale = icu.Locale(locale_name)

    if canonicalize:
        locale.canonicalize()

    locale_name = locale.getName()

    return fixup_locale_name(locale_name)


class _Interop:
    class _Globalization:
        @classmethod
        def _get_calendars(cls, locale_name: str, calendars: list[_CalendarId], calendars_capacity: int) -> int:
            """In .NET, this method calls into runtime native code.

            This Python method approximates that native code which interfaces with ICU.

            https://github.com/dotnet/runtime/blob/22d12888e1c327e9edad74a090b265c11f48cd12/src/native/libs/System.Globalization.Native/pal_calendarData.c#L115
            """
            locale = icu.Locale(locale_name)
            calendar = icu.Calendar.createInstance(locale)
            calendars[0] = _CalendarId.from_icu_calendar_name(calendar.getType())
            return 1

        @classmethod
        def _get_locale_name(cls, locale_name: str, value: list[str], value_length: int) -> bool:
            """In .NET, this method calls into runtime native code.

            This Python method approximates that native code which interfaces with ICU.

            https://github.com/dotnet/runtime/blob/d1747a74705a49700d7c568fdb568704c2bbad58/src/native/libs/System.Globalization.Native/pal_locale.c#L199
            """
            # TODO: This is simplified
            locale_name = get_locale_name(locale_name, True)
            value.extend(locale_name)
            return True

        @classmethod
        def _get_locale_info_string(cls, locale_name: str, locale_string_data: LocaleStringData) -> str:
            """Roughly equivalent to:

            https://github.com/dotnet/runtime/blob/a027afb198c787fbfbca0b1d272ce41d9ab7d27a/src/native/libs/System.Globalization.Native/pal_localeStringData.c#L214
            """
            locale = icu.Locale(locale_name)

            match locale_string_data:
                case LocaleStringData.AMDesignator:
                    return cls.__get_locale_info_am_pm(locale, False)
                case LocaleStringData.PMDesignator:
                    return cls.__get_locale_info_am_pm(locale, True)
                case LocaleStringData.Iso3166CountryName:
                    return cls.__get_locale_iso3166_country_name(locale)
                case LocaleStringData.Iso3166CountryName2:
                    return cls.__get_locale_iso3166_country_code(locale)
                case _:
                    raise NotImplementedError(locale_string_data)

        @classmethod
        def __get_locale_iso3166_country_name(cls, locale: icu.Locale) -> str:
            """PyICU equivalent to GetLocaleIso3166CountryName:

            https://github.com/dotnet/runtime/blob/256191f27a95d2ea8d2e9785817a7d1ae50e8505/src/native/libs/System.Globalization.Native/pal_localeStringData.c#L126
            """
            return str(locale.getCountry())

        @classmethod
        def __get_locale_iso3166_country_code(cls, locale: icu.Locale) -> str:
            """PyICU equivalent to GetLocaleIso3166CountryCode:

            https://github.com/dotnet/runtime/blob/256191f27a95d2ea8d2e9785817a7d1ae50e8505/src/native/libs/System.Globalization.Native/pal_localeStringData.c#L150
            """
            return str(locale.getISO3Country())

        @classmethod
        def __get_locale_info_am_pm(cls, locale: icu.Locale, pm: bool) -> str:
            """Roughly equivalent to (but nothing like):

            https://github.com/dotnet/runtime/blob/a027afb198c787fbfbca0b1d272ce41d9ab7d27a/src/native/libs/System.Globalization.Native/pal_localeStringData.c#L65
            """
            date_format: icu.SimpleDateFormat = icu.SimpleDateFormat("a", locale)
            date_format_symbols: icu.DateFormatSymbols = date_format.getDateFormatSymbols()
            return str(date_format_symbols.getAmPmStrings()[int(pm)])

        @classmethod
        def _enum_calendar_info(
            cls,
            callback: Callable[[str, _IcuEnumCalendarsData], None],
            locale_name: str,
            calendar_id: _CalendarId,
            calendar_data_type: _CalendarDataType,
            context: _IcuEnumCalendarsData,
        ) -> bool:
            return cls.__enum_calendar_info(
                callback,
                locale_name,
                calendar_id,
                calendar_data_type,
                context,
            )

        @classmethod
        def __enum_calendar_info(
            cls,
            callback: Callable[[str, _IcuEnumCalendarsData], None],
            locale_name: str,
            calendar_id: _CalendarId,
            calendar_data_type: _CalendarDataType,
            context: _IcuEnumCalendarsData,
        ) -> bool:
            """In .NET this function calls into native code.

            Specifically, it calls `GlobalizationNative_EnumCalendarInfo` which interacts with ICU.

            https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L479

            In Python, this function mimics the behavior of that native code.
            """
            match calendar_data_type:
                case _CalendarDataType.SHORT_DATES:
                    ret = cls.__invoke_callback_for_date_pattern(
                        locale_name,
                        icu.DateFormat.kShort,
                        callback,
                        context,
                    ) and cls.__invoke_callback_for_date_pattern(
                        locale_name,
                        icu.DateFormat.kMedium,
                        callback,
                        context,
                    )
                    # TODO: Bit hacky, but required because PyICU has a different API to ICU.
                    callback(
                        icu.DateTimePatternGenerator.createInstance(icu.Locale(locale_name)).getBestPattern("yMd"),
                        context,
                    )
                    return ret
                case _CalendarDataType.LONG_DATES:
                    # LongDates map to kFull and kLong in ICU.
                    return cls.__invoke_callback_for_date_pattern(
                        locale_name,
                        icu.DateFormat.kFull,
                        callback,
                        context,
                    ) and cls.__invoke_callback_for_date_pattern(
                        locale_name,
                        icu.DateFormat.kLong,
                        callback,
                        context,
                    )
                case _CalendarDataType.ABBREV_DAY_NAMES:
                    return cls.__enum_symbols(
                        locale_name,
                        calendar_id,
                        calendar_data_type,
                        1,
                        callback,
                        context,
                    )
                case _CalendarDataType.MONTH_NAMES:
                    return cls.__enum_symbols(
                        locale_name,
                        calendar_id,
                        calendar_data_type,
                        0,
                        callback,
                        context,
                    )
                case _CalendarDataType.ABBREV_MONTH_NAMES:
                    return cls.__enum_symbols(
                        locale_name,
                        calendar_id,
                        calendar_data_type,
                        0,
                        callback,
                        context,
                    )
                case _CalendarDataType.MONTH_GENITIVE_NAMES:
                    return cls.__enum_symbols(
                        locale_name,
                        calendar_id,
                        calendar_data_type,
                        0,
                        callback,
                        context,
                    )
                case _CalendarDataType.ABBREV_MONTH_GENITIVE_NAMES:
                    return cls.__enum_symbols(
                        locale_name,
                        calendar_id,
                        calendar_data_type,
                        0,
                        callback,
                        context,
                    )
                case _:
                    raise NotImplementedError

        @classmethod
        def __enum_symbols(
            cls,
            locale_name: str,
            calendar_id: _CalendarId,
            type_: _CalendarDataType,
            start_index: int,
            callback: Callable[[str, _IcuEnumCalendarsData], None],
            context: _IcuEnumCalendarsData,
        ) -> bool:
            # .NET's native code calls ICU's C API here.
            #
            # https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L295
            #
            # This Python code attempts to mimic that, using PyICU.
            #
            # More context on ICU's C API, e.g. udat_open(), udat_setCalendar() and friends:
            # https://unicode-org.github.io/icu-docs/apidoc/dev/icu4c/udat_8h.html#a27dd4504fd957101d616aaeaf9e8ec9c

            locale = icu.Locale(locale_name)
            # To the best of my knowledge, ICU defaults to Gregorian calendar for most locales.
            # So we need to explicitly tell it which calendar to use.
            locale.setKeywordValue("calendar", calendar_id.to_icu_calendar_name())
            calendar = icu.Calendar.createInstance(locale)

            date_format: icu.SimpleDateFormat = icu.SimpleDateFormat("", locale)
            date_format.setCalendar(calendar)
            date_format_symbols: icu.DateFormatSymbols = date_format.getDateFormatSymbols()

            # In native .NET code, they have to make separate calls in C to first count the number
            # of symbols for the given symbol type (udat_countSymbols), and a call per symbol to
            # get the value (udat_getSymbols). PyICU usage looks a little different. We have to
            # translate those C calls to udat_getSymbols(), where a UDateFormatSymbolType argument
            # is passed, into PyICU calls.

            symbols: list[str]

            match type_:
                case _CalendarDataType.ABBREV_DAY_NAMES:
                    symbols = date_format_symbols.getShortWeekdays()
                case _CalendarDataType.MONTH_NAMES:
                    symbols = date_format_symbols.getMonths(
                        icu.DateFormatSymbols.STANDALONE, icu.DateFormatSymbols.WIDE
                    )
                case _CalendarDataType.ABBREV_MONTH_NAMES:
                    # We could use .getShortMonths() here, but in the interest of consistency/explicitness...
                    symbols = date_format_symbols.getMonths(
                        icu.DateFormatSymbols.STANDALONE, icu.DateFormatSymbols.ABBREVIATED
                    )
                case _CalendarDataType.MONTH_GENITIVE_NAMES:
                    symbols = date_format_symbols.getMonths(icu.DateFormatSymbols.FORMAT, icu.DateFormatSymbols.WIDE)
                case _CalendarDataType.ABBREV_MONTH_GENITIVE_NAMES:
                    symbols = date_format_symbols.getMonths(
                        icu.DateFormatSymbols.FORMAT, icu.DateFormatSymbols.ABBREVIATED
                    )

                case _:
                    raise NotImplementedError

            for symbol in symbols[start_index:]:
                callback(symbol, context)

            return True

        @classmethod
        def __invoke_callback_for_date_pattern(
            cls,
            locale_name: str,
            pattern: int,
            callback: Callable[[str, _IcuEnumCalendarsData], None],
            context: _IcuEnumCalendarsData,
        ) -> bool:
            """Roughly equivalent to:
            https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L255
            """
            locale = icu.Locale(locale_name)
            best_pattern = icu.DateFormat.createDateInstance(pattern, locale).toPattern()
            callback(best_pattern, context)
            return True
