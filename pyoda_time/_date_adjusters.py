# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from . import LocalDate


class DateAdjusters:
    # TODO: In Noda Time, these are properties which return functions. Any reason not to just use staticmethod?

    @staticmethod
    def end_of_month(date: LocalDate) -> LocalDate:
        """A date adjuster to move to the last day of the current month."""
        from . import LocalDate

        return LocalDate(
            year=date.year,
            month=date.month,
            day=date.calendar.get_days_in_month(date.year, date.month),
            calendar=date.calendar,
        )
