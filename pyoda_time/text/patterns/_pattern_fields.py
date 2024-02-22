# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from enum import Flag


class _PatternFields(Flag):
    """Enum representing the fields available within patterns.

    This single enum is shared by all parser types for simplicity, although most fields aren't used by most parsers.
    Pattern fields don't necessarily have corresponding duration or date/time fields, due to concepts such as "sign".
    """

    NONE = 0
    SIGN = 1 << 0
    HOURS_12 = 1 << 1
    HOURS_24 = 1 << 2
    MINUTES = 1 << 3
    SECONDS = 1 << 4
    FRACTIONAL_SECONDS = 1 << 5
    AM_PM = 1 << 6
    YEAR = 1 << 7
    YEAR_TWO_DIGITS = 1 << 8  # Actually year of *era* as two digits...
    YEAR_OF_ERA = 1 << 9
    MONTH_OF_YEAR_NUMERIC = 1 << 10
    MONTH_OF_YEAR_TEXT = 1 << 11
    DAY_OF_MONTH = 1 << 12
    DAY_OF_WEEK = 1 << 13
    ERA = 1 << 14
    CALENDAR = 1 << 15
    ZONE = 1 << 16
    ZONE_ABBREVIATION = 1 << 17
    EMBEDDED_OFFSET = 1 << 18
    # D, H, M, or S in a DurationPattern.
    TOTAL_DURATION = 1 << 19
    # No other date fields permitted; use calendar/year/month/day from bucket
    EMBEDDED_DATE = 1 << 20
    # No other time fields permitted; user hours24/minutes/seconds/fractional seconds from bucket
    EMBEDDED_TIME = 1 << 21

    ALL_TIME_FIELDS = HOURS_12 | HOURS_24 | MINUTES | SECONDS | FRACTIONAL_SECONDS | AM_PM | EMBEDDED_TIME
    ALL_DATE_FIELDS = (
        YEAR
        | YEAR_TWO_DIGITS
        | YEAR_OF_ERA
        | MONTH_OF_YEAR_NUMERIC
        | MONTH_OF_YEAR_TEXT
        | DAY_OF_MONTH
        | DAY_OF_WEEK
        | ERA
        | CALENDAR
        | EMBEDDED_DATE
    )

    # In Noda Time, the following methods are implemented as extension methods
    # on a ``PatternFieldsExtensions`` class.

    def has_any(self, target: _PatternFields) -> bool:
        """Returns true if the given set of fields contains any of the target fields."""
        return (self & target) != _PatternFields.NONE

    def has_all(self, target: _PatternFields) -> bool:
        """Returns true if the given set of fields contains all of the target fields."""
        return (self & target) == target
