# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from enum import Enum

GREGORIAN_NAME = "gregorian"
JAPANESE_NAME = "japanese"
BUDDHIST_NAME = "buddhist"
HEBREW_NAME = "hebrew"
DANGI_NAME = "dangi"
PERSIAN_NAME = "persian"
ISLAMIC_NAME = "islamic"
ISLAMIC_UMALQURA_NAME = "islamic-umalqura"
ROC_NAME = "roc"


class _CalendarId(Enum):
    """A port of the ``System.Globalization.CalendarId`` internal enum in .NET."""

    UNINITIALIZED_VALUE = 0
    GREGORIAN = 1  # Gregorian (localized) calendar
    GREGORIAN_US = 2  # Gregorian (U.S.) calendar
    JAPAN = 3  # Japanese Emperor Era calendar
    TAIWAN = 4  # Taiwan Era calendar /* SSS_WARNINGS_ON */
    KOREA = 5  # Korean Tangun Era calendar
    HIJRI = 6  # Hijri (Arabic Lunar) calendar
    THAI = 7  # Thai calendar
    HEBREW = 8  # Hebrew (Lunar) calendar
    GREGORIAN_ME_FRENCH = 9  # Gregorian Middle East French calendar
    GREGORIAN_ARABIC = 10  # Gregorian Arabic calendar
    GREGORIAN_XLIT_ENGLISH = 11  # Gregorian Transliterated English calendar
    GREGORIAN_XLIT_FRENCH = 12
    # Note that all calendars after this point are MANAGED ONLY for now.
    JULIAN = 13
    JAPANESELUNISOLAR = 14
    CHINESELUNISOLAR = 15
    SAKA = 16  # reserved to match Office but not implemented in our code
    LUNAR_ETO_CHN = 17  # reserved to match Office but not implemented in our code
    LUNAR_ETO_KOR = 18  # reserved to match Office but not implemented in our code
    LUNAR_ETO_ROKUYOU = 19  # reserved to match Office but not implemented in our code
    KOREANLUNISOLAR = 20
    TAIWANLUNISOLAR = 21
    PERSIAN = 22
    UMALQURA = 23
    # Last calendar ID
    LAST_CALENDAR = 23  # noqa: PIE796

    @classmethod
    def from_icu_calendar_name(cls, icu_calendar_name: str) -> _CalendarId:
        """Gets the associated CalendarId for the ICU calendar name.

        Equivalent to:
        https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L82-L107

        :param icu_calendar_name: The ICU calendar name.
        :return: The associated CalendarId.
        """
        if icu_calendar_name == GREGORIAN_NAME:
            return _CalendarId.GREGORIAN
        elif icu_calendar_name == JAPANESE_NAME:
            return _CalendarId.JAPAN
        elif icu_calendar_name == BUDDHIST_NAME:
            return _CalendarId.THAI
        elif icu_calendar_name == HEBREW_NAME:
            return _CalendarId.HEBREW
        elif icu_calendar_name == DANGI_NAME:
            return _CalendarId.KOREA
        elif icu_calendar_name == PERSIAN_NAME:
            return _CalendarId.PERSIAN
        elif icu_calendar_name == ISLAMIC_NAME:
            return _CalendarId.HIJRI
        elif icu_calendar_name == ISLAMIC_UMALQURA_NAME:
            return _CalendarId.UMALQURA
        elif icu_calendar_name == ROC_NAME:
            return _CalendarId.TAIWAN
        else:
            return _CalendarId.UNINITIALIZED_VALUE

    def to_icu_calendar_name(self) -> str:
        """Gets the associated ICU calendar name for the _CalendarId.

        This is roughly equivalent to:
        https://github.com/dotnet/runtime/blob/b181ed507c07bdcfb84e2a2b4786d3c2c763db8c/src/native/libs/System.Globalization.Native/pal_calendarData.c#L30-L76
        """
        match self:
            case _CalendarId.JAPAN:
                return JAPANESE_NAME
            case _CalendarId.THAI:
                return BUDDHIST_NAME
            case _CalendarId.HEBREW:
                return HEBREW_NAME
            case _CalendarId.KOREA:
                return DANGI_NAME
            case _CalendarId.PERSIAN:
                return PERSIAN_NAME
            case _CalendarId.HIJRI:
                return ISLAMIC_NAME
            case _CalendarId.UMALQURA:
                return ISLAMIC_UMALQURA_NAME
            case _CalendarId.TAIWAN:
                return ROC_NAME
            case _:
                return GREGORIAN_NAME
