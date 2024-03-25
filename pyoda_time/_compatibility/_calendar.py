# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
from abc import ABC

from pyoda_time._compatibility._calendar_id import _CalendarId


class Calendar(ABC):  # TODO: ICloneable
    """A bare-bones equivalent to the ``System.Globalization.Calendar`` abstract class in .NET."""

    def __init__(self) -> None:
        self.__is_read_only: bool = False

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.UNINITIALIZED_VALUE

    @property
    def is_read_only(self) -> bool:
        """Gets a value indicating whether this ``Calendar`` is read-only."""
        return self.__is_read_only

    @staticmethod
    def read_only(calendar: Calendar) -> Calendar:
        """Returns a read-only version of the specified ``Calendar``."""
        if calendar is None:
            raise ValueError("Calendar must not be None.")
        if calendar.is_read_only:
            return calendar
        calendar_1: Calendar = copy.copy(calendar)
        calendar_1._set_read_only_state(True)
        return calendar_1

    def _set_read_only_state(self, read_only: bool) -> None:
        self.__is_read_only = read_only
