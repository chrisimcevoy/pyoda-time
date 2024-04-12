# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
from abc import ABC
from typing import Final

from pyoda_time._compatibility._calendar_id import _CalendarId


class Calendar(ABC):  # TODO: ICloneable
    """A bare-bones equivalent to the ``System.Globalization.Calendar`` abstract class in .NET."""

    CURRENT_ERA: Final[int] = 0

    def __init__(self) -> None:
        self.__is_read_only: bool = False
        self.__current_era_value = -1

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.UNINITIALIZED_VALUE

    @property
    def _base_calendar_id(self) -> _CalendarId:
        """Return the Base calendar ID for calendars that didn't have defined data in calendarData."""
        return self._id

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

    @property
    def _current_era_value(self) -> int:
        """This is used to convert CurrentEra(0) to an appropriate era value."""
        if self.__current_era_value == -1:
            assert self._base_calendar_id != _CalendarId.UNINITIALIZED_VALUE
            from pyoda_time._compatibility._calendar_data import _CalendarData

            self.__current_era_value = _CalendarData._get_calendar_current_era(self)
        return self.__current_era_value
