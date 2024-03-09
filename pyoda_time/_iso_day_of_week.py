# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from enum import IntEnum

__all__ = ["IsoDayOfWeek"]


class IsoDayOfWeek(IntEnum):
    """Equates the days of the week with their numerical value according to ISO-8601."""

    NONE = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
