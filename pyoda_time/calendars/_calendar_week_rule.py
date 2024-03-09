# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import enum


class CalendarWeekRule(enum.IntEnum):
    """Analogous to the ``CalendarWeekRule`` enum found in the .NET framework."""

    # TODO: Move this to _compatibility?

    FIRST_DAY = 0
    FIRST_FULL_WEEK = 1
    FIRST_FOUR_DAY_WEEK = 2
