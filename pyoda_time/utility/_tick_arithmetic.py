# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from ._csharp_compatibility import _CsharpConstants, _towards_zero_division


class _TickArithmetic:
    """Common operations on ticks."""

    @staticmethod
    def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
        """Cautiously converts a number of ticks (which can have any value) into a number of days and a tick within that
        day."""

        from pyoda_time import PyodaConstants

        if ticks >= 0:
            days = int((ticks >> 14) / 52734375)
            tick_of_day = ticks - days * PyodaConstants.TICKS_PER_DAY
        else:
            days = _towards_zero_division(ticks + 1, PyodaConstants.TICKS_PER_DAY) - 1
            tick_of_day = ticks - (days + 1) * PyodaConstants.TICKS_PER_DAY + PyodaConstants.TICKS_PER_DAY

        return days, tick_of_day

    @staticmethod
    def days_and_tick_of_day_to_ticks(days: int, tick_of_day: int) -> int:
        """Cautiously computes a number of ticks from day/tick-of-day value.

        This may overflow, but will only do so if it has to.
        """
        from .. import PyodaConstants

        # TODO: Get a better handle on what this is doing with regard to long overflow
        if days >= _towards_zero_division(_CsharpConstants.LONG_MIN_VALUE, PyodaConstants.TICKS_PER_DAY):
            return days * PyodaConstants.TICKS_PER_DAY + tick_of_day
        return (days + 1) * PyodaConstants.TICKS_PER_DAY + tick_of_day - PyodaConstants.TICKS_PER_DAY

    @staticmethod
    def bounded_days_and_tick_of_day_to_ticks(days: int, tick_of_day: int) -> int:
        """Computes a number of ticks from a day/tick-of-day value which is trusted not to overflow, even when computed
        in the simplest way.

        Only call this method from places where there are suitable constraints on the input.
        """

        from pyoda_time import PyodaConstants

        return days * PyodaConstants.TICKS_PER_DAY + tick_of_day
