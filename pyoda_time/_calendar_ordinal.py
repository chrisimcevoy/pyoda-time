# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from enum import IntEnum


class _CalendarOrdinal(IntEnum):
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
