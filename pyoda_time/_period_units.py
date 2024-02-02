# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import enum as _enum

__all__ = ["PeriodUnits"]


class PeriodUnits(_enum.Flag):
    """The units within a ``Period``.

    When a period is created to find the difference between two local values,
    the caller may specify which units are required - for example, you can ask
    for the difference between two dates in "years and weeks".
    Units are always applied largest-first in arithmetic.
    """

    # Note to Noda Time developers: that the values of the single (non-compound)
    # values must match up with the internal indexes used for Period's values array.

    NONE = 0
    YEARS = 1
    MONTHS = 2
    WEEKS = 4
    DAYS = 8
    ALL_DATE_UNITS = YEARS | MONTHS | WEEKS | DAYS
    YEAR_MONTH_DAY = YEARS | MONTHS | DAYS
    HOURS = 16
    MINUTES = 32
    SECONDS = 64
    MILLISECONDS = 128
    TICKS = 256
    NANOSECONDS = 512
    HOUR_MINUTE_SECOND = HOURS | MINUTES | SECONDS
    ALL_TIME_UNITS = HOURS | MINUTES | SECONDS | MILLISECONDS | TICKS | NANOSECONDS
    DATE_AND_TIME = YEARS | MONTHS | DAYS | HOURS | MINUTES | SECONDS | MILLISECONDS | TICKS | NANOSECONDS
    ALL_UNITS = YEARS | MONTHS | WEEKS | DAYS | HOURS | MINUTES | SECONDS | MILLISECONDS | TICKS | NANOSECONDS
