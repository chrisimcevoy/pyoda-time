# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from .. import IsoDayOfWeek as _IsoDayOfWeek
    from . import CalendarWeekRule, IWeekYearRule


class _WeekYearRulesMeta(type):
    @property
    def iso(cls) -> IWeekYearRule:
        from .. import IsoDayOfWeek
        from ._simple_week_year_rule import _SimpleWeekYearRule

        return _SimpleWeekYearRule(4, IsoDayOfWeek.MONDAY, False)


class WeekYearRules(metaclass=_WeekYearRulesMeta):
    """Factory methods to construct week-year rules supported by Noda Time."""

    @staticmethod
    def for_min_days_in_first_week(
        min_days_in_first_week: int, first_day_of_week: _IsoDayOfWeek | None = None
    ) -> IWeekYearRule:
        from ._simple_week_year_rule import _SimpleWeekYearRule

        if first_day_of_week is None:
            from .. import IsoDayOfWeek

            first_day_of_week = IsoDayOfWeek.MONDAY
        return _SimpleWeekYearRule(min_days_in_first_week, first_day_of_week, False)

    @staticmethod
    def from_calendar_week_rule(
        # TODO: We are using IsoDayOfWeek here, whereas Noda Time uses System.DayOfWeek from the bcl.
        #   I *think* it should be ok given that the argument in Noda Time is converted to IsoDayOfWeek.
        calendar_week_rule: CalendarWeekRule,
        first_day_of_week: _IsoDayOfWeek,
    ) -> IWeekYearRule:
        from . import CalendarWeekRule
        from ._simple_week_year_rule import _SimpleWeekYearRule

        min_days_in_first_week: int
        match calendar_week_rule:
            case CalendarWeekRule.FIRST_DAY:
                min_days_in_first_week = 1
            case CalendarWeekRule.FIRST_FOUR_DAY_WEEK:
                min_days_in_first_week = 4
            case CalendarWeekRule.FIRST_FULL_WEEK:
                min_days_in_first_week = 7
            case _:
                raise ValueError(f"Unsupported CalendarWeekRule: {calendar_week_rule}")
        return _SimpleWeekYearRule(min_days_in_first_week, first_day_of_week, True)
