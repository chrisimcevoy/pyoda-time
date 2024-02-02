# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations as _annotations

__all__: list[str] = [
    "CalendarWeekRule",
    "Era",
    "HebrewMonthNumbering",
    "IslamicEpoch",
    "IslamicLeapYearPattern",
    "IWeekYearRule",
    "WeekYearRules",
]

import enum as _enum

from ._badi_year_month_day_calculator import _BadiYearMonthDayCalculator  # noqa: F401
from ._coptic_year_month_day_calculator import _CopticYearMonthDayCalculator  # noqa: F401
from ._era import (
    Era,
    _EraMeta,  # noqa: F401
)
from ._era_calculator import _EraCalculator  # noqa: F401
from ._fixed_month_year_month_day_calculator import _FixedMonthYearMonthDayCalculator  # noqa: F401
from ._g_j_era_calculator import _GJEraCalculator  # noqa: F401
from ._g_j_year_month_day_calculator import _GJYearMonthDayCalculator  # noqa: F401
from ._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator  # noqa: F401
from ._hebrew_month_converter import _HebrewMonthConverter  # noqa: F401
from ._hebrew_month_numbering import HebrewMonthNumbering
from ._hebrew_scriptural_calculator import _HebrewScripturalCalculator  # noqa: F401
from ._hebrew_year_month_day_calculator import _HebrewYearMonthDayCalculator  # noqa: F401
from ._i_week_year_rule import IWeekYearRule
from ._islamic_epoch import IslamicEpoch
from ._islamic_leap_year_pattern import IslamicLeapYearPattern
from ._islamic_year_month_day_calculator import _IslamicYearMonthDayCalculator  # noqa: F401
from ._julian_year_month_day_calculator import _JulianYearMonthDayCalculator  # noqa: F401
from ._persian_year_month_day_calculator import _PersianYearMonthDayCalculator  # noqa: F401
from ._regular_year_month_day_calculator import _RegularYearMonthDayCalculator  # noqa: F401
from ._simple_week_year_rule import _SimpleWeekYearRule  # noqa: F401
from ._single_era_calculator import _SingleEraCalculator  # noqa: F401
from ._um_al_qura_year_month_day_calculator import _UmAlQuraYearMonthDayCalculator  # noqa: F401
from ._week_year_rules import WeekYearRules
from ._year_month_day_calculator import _YearMonthDayCalculator  # noqa: F401
from ._year_start_cache_entry import _YearStartCacheEntry  # noqa: F401


class CalendarWeekRule(_enum.IntEnum):
    FIRST_DAY = 0
    FIRST_FULL_WEEK = 1
    FIRST_FOUR_DAY_WEEK = 2
