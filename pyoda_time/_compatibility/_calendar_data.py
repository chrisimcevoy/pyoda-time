# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Sequence, cast, final

from icu import DateFormat, DateFormatSymbols, DateTimePatternGenerator, Locale

from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._globalization_mode import _GlobalizationMode
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.utility import _sealed


class _CalendarDataType(IntEnum):
    UNINITIALIZED = 0
    NATIVE_NAME = 1
    MONTH_DAY = 2
    SHORT_DATES = 3
    LONG_DATES = 4
    YEAR_MONTHS = 5
    DAY_NAMES = 6
    ABBREV_DAY_NAMES = 7
    MONTH_NAMES = 8
    ABBREV_MONTH_NAMES = 9
    SUPER_SHORT_DAY_NAMES = 10
    MONTH_GENITIVE_NAMES = 11
    ABBREV_MONTH_GENITIVE_NAMES = 12
    ERA_NAMES = 13
    ABBREV_ERA_NAMES = 14


@dataclass
class _IcuEnumCalendarsData:
    results: list[str] = field(default_factory=list)
    disallow_duplicates: bool = False


class _CalendarDataMeta(type):
    @property
    def _invariant(self) -> _CalendarData:
        raise NotImplementedError


@_sealed
@final
class _CalendarData(metaclass=_CalendarDataMeta):
    def __init__(self, locale_name: str, calendar_id: _CalendarId, bUseUserOverrides: bool) -> None:
        self._bUseUserOverrides = bUseUserOverrides

        # In C# these private fields are all defined outside of the constructor.
        # But this is Python, so...
        self._sNativeName: str | None = None
        self._saShortDates: Sequence[str] | None = None
        self._saYearMonths: Sequence[str] | None = None
        self._saLongDates: Sequence[str] | None = None
        self._sMonthDay: str | None = None
        self._saEraNames: list[str] = []
        self._saAbbrevEraNames: Sequence[str] | None = None
        self._saAbbrevEnglishEraNames: Sequence[str] | None = None
        self._saDayNames: Sequence[str] | None = None
        self._saAbbrevDayNames: Sequence[str] | None = None
        self._saSuperShortDayNames: Sequence[str] | None = None
        self._saMonthNames: Sequence[str] | None = None
        self._saAbbrevMonthNames: Sequence[str] | None = None
        self._saMonthGenitiveNames: Sequence[str] | None = None
        self._saAbbrevMonthGenitiveNames: Sequence[str] | None = None
        self._saLeapYearMonthNames: Sequence[str] | None = None
        self._iTwoDigitYearMax: int = 2029
        self.__iCurrentEra: int = 0
        self._iCurrentEra: int = 0

        if not self.__load_calendar_data_from_system_core(locale_name, calendar_id):
            raise NotImplementedError()

        self.__initialize_era_names(locale_name, calendar_id)

        # TODO: There is a whole lot left to implement here

    def __icu_load_calendar_data_from_system(self, locale_name: str, calendar_id: _CalendarId) -> bool:
        # TODO: This needs a bunch more work, and is very different to .NET

        assert not _GlobalizationMode._use_nls

        locale: Locale = Locale(locale_name)
        datetime_pattern_generator: DateTimePatternGenerator = DateTimePatternGenerator.createInstance(locale)
        date_format_symbols: DateFormatSymbols = DateFormatSymbols(locale)

        self._sNativeName = calendar_id.to_icu_calendar_name()
        self._sMonthDay = datetime_pattern_generator.getBestPattern("MMMMd")

        if self._sMonthDay:
            self._sMonthDay = self.__normalize_date_pattern(self._sMonthDay)

        # .NET builds up a string array of three short date patterns:
        #
        # - ICU's "kShort" pattern
        # - ICU's "kMedium" pattern
        # - A specific skeleton ("yMd"), which closely matches what is used on Windows.
        #
        # Source at:
        # https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L494-L499
        #
        # See also (specifically, how it disallows duplicates):
        # https://source.dot.net/#System.Private.CoreLib/src/libraries/System.Private.CoreLib/src/System/Globalization/CalendarData.Icu.cs,99c4abaab8c2bae5,references
        patterns = []
        for pattern in [
            DateFormat.createDateInstance(DateFormat.kShort, locale).toPattern(),
            DateFormat.createDateInstance(DateFormat.kMedium, locale).toPattern(),
            datetime_pattern_generator.getBestPattern("yMd"),
        ]:
            if pattern not in patterns:
                patterns.append(pattern)
        self._saShortDates = patterns

        # The first item in the collection which getWeekdays() returns is an empty string.
        # Interestingly, .NET removes that empty string.
        # Even more interestingly, NodaFormatInfo adds it back in, and moves the days around.
        self._saDayNames = [name for name in date_format_symbols.getWeekdays() if name]
        assert len(self._saDayNames) == 7

        abbrev_day_names_result, self._saAbbrevDayNames = self._enum_calendar_info(
            locale_name,
            calendar_id,
            _CalendarDataType.ABBREV_DAY_NAMES,
        )

        month_names_result, self._saMonthNames, leap_hebrew_month_name = self.__enum_month_names(
            locale_name, calendar_id, _CalendarDataType.MONTH_NAMES
        )
        if leap_hebrew_month_name:
            assert self._saMonthNames

            # In Hebrew calendar, get the leap month name Adar II and override the non-leap month 7
            assert calendar_id == _CalendarId.HEBREW and len(self._saMonthNames) == 13
            self._saLeapYearMonthNames = list(self._saMonthNames)
            self._saLeapYearMonthNames[6] = leap_hebrew_month_name

            # The returned data from ICU has 6th month name as 'Adar I' and 7th month name as 'Adar'
            # We need to adjust that in the list used with non-leap year to have 6th month as 'Adar'
            # and 7th month as 'Adar II'
            # note that when formatting non-leap year dates, 7th month shouldn't get used at all.
            self._saMonthNames[5] = self._saMonthNames[6]
            self._saMonthNames[6] = leap_hebrew_month_name

        abbreviated_month_names_result, self._saAbbrevMonthNames, _ = self.__enum_month_names(
            locale_name, calendar_id, _CalendarDataType.ABBREV_MONTH_NAMES
        )

        month_genitive_names_result, self._saMonthGenitiveNames, _ = self.__enum_month_names(
            locale_name, calendar_id, _CalendarDataType.MONTH_GENITIVE_NAMES
        )

        abbrev_month_genitive_names_result, self._saAbbrevMonthGenitiveNames, _ = self.__enum_month_names(
            locale_name, calendar_id, _CalendarDataType.ABBREV_MONTH_GENITIVE_NAMES
        )

        # The cast here is because icu has no return type annotation for getEras()
        self._saEraNames = cast(list[str], date_format_symbols.getEras())

        # .NET expects that only the Japanese calendars have more than 1 era.
        # So for other calendars, only return the latest era.
        if (
            calendar_id != _CalendarId.JAPAN
            and calendar_id != _CalendarId.JAPANESELUNISOLAR
            and len(self._saEraNames) > 0
        ):
            # TODO: Do the same thing for short era names when/if that is implemented
            latest_era_name = self._saEraNames[-1]
            self._saEraNames = [latest_era_name]

        return all(
            (
                # TODO: Add other bools here
                abbrev_day_names_result,
                month_names_result,
                abbreviated_month_names_result,
                month_genitive_names_result,
                abbrev_month_genitive_names_result,
            )
        )

    def __load_calendar_data_from_system_core(self, locale_name: str, calendar_id: _CalendarId) -> bool:
        return self.__icu_load_calendar_data_from_system(locale_name, calendar_id)

    def __initialize_era_names(self, locale_name: str, calendar_id: _CalendarId) -> None:
        def are_era_names_empty() -> bool:
            return not self._saEraNames or not self._saEraNames[0]

        # Note that the saEraNames only include "A.D."
        # We don't have localized names for other calendars available from windows
        match calendar_id:
            # For Localized Gregorian we really expect the data from the OS.
            case _CalendarId.GREGORIAN:
                # Fallback for CoreCLR < Win7 or culture.dll missing
                if are_era_names_empty():
                    self._saEraNames = ["A.D."]
            # The rest of the calendars have constant data, so we'll just use that
            case _CalendarId.GREGORIAN_US, _CalendarId.JULIAN:
                self._saEraNames = ["A.D."]
            case _CalendarId.HEBREW:
                self._saEraNames = ["C.E."]
            case _CalendarId.HIJRI, _CalendarId.UMALQURA:
                if locale_name == "dv-MV":
                    # Special case for Divehi
                    self._saEraNames = ["\u0780\u07a8\u0796\u07b0\u0783\u07a9"]
                else:
                    self._saEraNames = ["\u0628\u0639\u062f \u0627\u0644\u0647\u062c\u0631\u0629"]
            case _CalendarId.GREGORIAN_ARABIC, _CalendarId.GREGORIAN_XLIT_ENGLISH, _CalendarId.GREGORIAN_XLIT_FRENCH:
                # These are all the same:
                self._saEraNames = ["\u0645"]
            case _CalendarId.GREGORIAN_ME_FRENCH:
                self._saEraNames = ["ap. J.-C."]
            case _CalendarId.TAIWAN:
                if self.__system_supports_taiwanese_calendar():
                    self._saEraNames = ["\u4e2d\u83ef\u6c11\u570b"]
                else:
                    self._saEraNames = [""]
            case _CalendarId.KOREA:
                self._saEraNames = ["\ub2e8\uae30"]
            case _CalendarId.THAI:
                self._saEraNames = ["\u0e1e\u002e\u0e28\u002e"]
            case _CalendarId.JAPAN, _CalendarId.JAPANESELUNISOLAR:
                from pyoda_time._compatibility._japanese_calendar import JapaneseCalendar

                self._saEraNames = JapaneseCalendar._era_names()
            case _CalendarId.PERSIAN:
                if are_era_names_empty():
                    self._saEraNames = ["\u0647\u002e\u0634"]
            case _:
                # Most calendars are just "A.D."
                self._saEraNames = self.__class__._invariant._saEraNames

    @classmethod
    def __normalize_date_pattern(cls, date_pattern: str) -> str:
        """The ICU date format characters are not exactly the same as the .NET date format characters.

        NormalizeDatePattern will take in an ICU date pattern and return the equivalent .NET date pattern.

        see Date Field Symbol Table in
        http://userguide.icu-project.org/formatparse/datetime
        and https://msdn.microsoft.com/en-us/library/8kb3ddd4(v=vs.110).aspx
        """

        destination = StringBuilder()

        index = 0

        while index < len(date_pattern):
            match date_pattern[index]:
                case "'":
                    # single quotes escape characters, like 'de' in es-SP
                    # so read verbatim until the next single quote
                    destination.append(date_pattern[index])
                    index += 1
                    while index < len(date_pattern):
                        current = date_pattern[index]
                        destination.append(current)
                        index += 1
                        if current == "'":
                            break
                case "E", "e", "c":
                    # 'E' in ICU is the day of the week, which maps to 3 or 4 'd's in .NET
                    # 'e' in ICU is the local day of the week, which has no representation in .NET, but
                    # maps closest to 3 or 4 'd's in .NET
                    # 'c' in ICU is the stand-alone day of the week, which has no representation in .NET, but
                    # maps closest to 3 or 4 'd's in .NET
                    index = cls.__normalize_day_of_week(date_pattern, destination, index)
                case "L", "M":
                    # 'L' in ICU is the stand-alone name of the month,
                    # which maps closest to 'M' in .NET since it doesn't support stand-alone month names in patterns
                    # 'M' in both ICU and .NET is the month,
                    # but ICU supports 5 'M's, which is the super short month name
                    occurrences, index = cls.__count_occurrences(date_pattern, date_pattern[index], index)
                    if occurrences > 4:
                        # 5 'L's or 'M's in ICU is the super short name, which maps closest to MMM in .NET
                        occurrences = 3
                    destination.append("M" * occurrences)
                case "G":
                    # 'G' in ICU is the era, which maps to 'g' in .NET
                    _, index = cls.__count_occurrences(date_pattern, date_pattern[index], index)
                    # it doesn't matter how many 'G's, since .NET only supports 'g' or 'gg', and they
                    # have the same meaning
                    destination.append("g")
                case "y":
                    # a single 'y' in ICU is the year with no padding or trimming.
                    # a single 'y' in .NET is the year with 1 or 2 digits
                    # so convert any single 'y' to 'yyyy'
                    occurrences, index = cls.__count_occurrences(date_pattern, "y", index)
                    if occurrences == 1:
                        occurrences = 4
                    destination.append("y" * occurrences)
                case _:
                    unsupported_date_field_symbols = "YuUrQqwWDFg"
                    assert date_pattern[index] not in unsupported_date_field_symbols
                    destination.append(date_pattern[index])
                    index += 1

        return destination.to_string()

    @classmethod
    def __normalize_day_of_week(cls, date_pattern: str, destination: StringBuilder, index: int) -> int:
        day_char = date_pattern[index]
        occurrences, index = cls.__count_occurrences(date_pattern, day_char, index)
        occurrences = max(occurrences, 3)
        if occurrences > 4:
            # 5 and 6 E/e/c characters in ICU is the super short names, which maps closest to ddd in .NET
            occurrences = 3

        destination.append("d" * occurrences)

        return index

    @classmethod
    def __count_occurrences(cls, date_pattern: str, value: str, index: int) -> tuple[int, int]:
        start_index = index
        while index < len(date_pattern) and date_pattern[index] == value:
            index += 1

        return index - start_index, index

    @classmethod
    def __enum_month_names(
        cls,
        locale_name: str,
        calendar_id: _CalendarId,
        data_type: _CalendarDataType,
    ) -> tuple[bool, list[str] | None, str | None]:
        """Return a 3-tuple containing.

        * True if the operation was successful, False otherwise
        * A list of month names if the operation was successful, otherwise None
        * A string representing the leap Hebrew month if successful, otherwise None
        """
        month_names: list[str] | None = None
        leap_hebrew_month_name: str | None = None

        callback_context = _IcuEnumCalendarsData()

        result: bool = cls.__enum_calendar_info(locale_name, calendar_id, data_type, callback_context)

        if result:
            # the month-name arrays are expected to have 13 elements.  If ICU only returns 12, add an
            # extra empty string to fill the array.
            if len(callback_context.results) == 12:
                callback_context.results.append("")

            if len(callback_context.results) > 13:
                assert calendar_id == _CalendarId.HEBREW and len(callback_context.results) == 14

                if calendar_id == _CalendarId.HEBREW:
                    leap_hebrew_month_name = callback_context.results[13]
                callback_context.results.pop(13)
            month_names = callback_context.results

        return result, month_names, leap_hebrew_month_name

    @classmethod
    def _enum_calendar_info(
        cls, locale_name: str, calendar_id: _CalendarId, data_type: _CalendarDataType
    ) -> tuple[bool, list[str]]:
        callback_context = _IcuEnumCalendarsData()
        result = cls.__enum_calendar_info(locale_name, calendar_id, data_type, callback_context)
        return result, callback_context.results

    @classmethod
    def __enum_calendar_info(
        cls,
        locale_name: str,
        calendar_id: _CalendarId,
        data_type: _CalendarDataType,
        callback_context: _IcuEnumCalendarsData,
    ) -> bool:
        from pyoda_time._compatibility._interop import _Interop

        return _Interop._Globalization._enum_calendar_info(
            cls.__enum_calendar_info_callback, locale_name, calendar_id, data_type, callback_context
        )

    @classmethod
    def __enum_calendar_info_callback(cls, calendar_string: str, context: _IcuEnumCalendarsData) -> None:
        if context.disallow_duplicates:
            if calendar_string in context.results:
                return
        context.results.append(calendar_string)

    @classmethod
    def __system_supports_taiwanese_calendar(cls) -> bool:
        if _GlobalizationMode._use_nls:
            raise NotImplementedError
        return cls.__icu_system_supports_taiwanese_calendar()

    @staticmethod
    def __icu_system_supports_taiwanese_calendar() -> bool:
        assert not _GlobalizationMode._use_nls
        return True
