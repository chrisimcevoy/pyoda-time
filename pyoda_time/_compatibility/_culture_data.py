# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
import typing
from typing import Iterable

import icu

from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._gregorian_calendar import GregorianCalendar
from pyoda_time._compatibility._string_builder import StringBuilder

if typing.TYPE_CHECKING:
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

            available_locales: Iterable[str] = icu.Locale.getAvailableLocales().keys()

            # TODO: Should this be case-insensitive?
            #  My gut says no, because we don't own the data.
            #  Better to be strict at first then more lenient
            #  later than the other way around.
            if icu_compatible_name not in available_locales:
                # PyICU doesn't do this validation for us.
                # If we don't do this check ourselves, it will
                # happily just return a locale with our name
                # with the default values for locale data.
                raise ValueError(f"Unknown locale: {name}")

        self.__raw_name: str = name
        self.__locale: icu.Locale = icu.Locale(icu_compatible_name)

    @property
    def _culture_name(self) -> str:
        """The real name used to construct the locale (ie: de-DE_phoneb)."""
        return self.__raw_name

    @property
    def name(self) -> str:
        """Locale name (ie: de-DE, NO sort information)"""
        return str(self.__locale.getName())  # Wrapped in str() for mypy reasons

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

    @property
    def _default_calendar(self) -> Calendar:
        """Port of the internal ``CultureData.DefaultCalendar`` property.

        This returns an instance of the default ``System.Globalization.Calendar`` for the locale.
        """
        # TODO: Only the invariant culture is supported.
        if True:  # if (GlobalizationMode.Invariant) {...}
            return GregorianCalendar()

    @property
    def _time_separator(self) -> str:
        """Port of the internal ``CultureData.TimeSeparator`` property.

        As in .NET, the time separator is determined by parsing the locale's long time format.
        """
        # TODO: Check/test this is actually the case
        #  As in .NET, fr-CA is special cased to force the colon separator.
        #  The pattern there is "HH 'h' mm 'min' ss 's'", from which the
        #  separator cannot be derived.
        if self.name == "fr-CA":
            return ":"

        long_time_format: str = icu.SimpleDateFormat(style=icu.DateFormat.kLong, locale=self.__locale).toPattern()

        return self.__get_time_separator(long_time_format)

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

    def __deepcopy__(self, memo: dict) -> _CultureData:
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

    def _get_nfi_values(self, nfi: NumberFormatInfo) -> None:
        """Populate the provided ``NumberFormatInfo`` with locale-specific values from ICU."""
        # TODO: This is a bare-bones port; just as much as we needed at the time and no more.
        number_format: icu.DecimalFormatSymbols = icu.DecimalFormatSymbols(self.__locale)
        nfi.positive_sign = number_format.getSymbol(icu.DecimalFormatSymbols.kPlusSignSymbol)

    @property
    def _is_invariant_culture(self) -> bool:
        return not self.name  # string.IsNullOrEmpty(this.Name)
