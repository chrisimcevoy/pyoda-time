# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .. import LocalDate
    from .._calendar_system import CalendarSystem
    from .._iso_day_of_week import IsoDayOfWeek


class IWeekYearRule(Protocol):
    def get_local_date(
        self,
        week_year: int,
        week_of_week_year: int,
        day_of_week: IsoDayOfWeek,
        calendar: CalendarSystem | None = None,
    ) -> LocalDate: ...

    def get_week_year(self, date: LocalDate) -> int: ...

    def get_week_of_week_year(self, date: LocalDate) -> int: ...

    def get_weeks_in_week_year(self, week_year: int, calendar: CalendarSystem | None = None) -> int: ...
