# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._gregorian_calendar_types import GregorianCalendarTypes


class GregorianCalendar(Calendar):
    """Represents the Gregorian calendar."""

    _MIN_YEAR: Final[int] = 1
    _MAX_YEAR: Final[int] = 9999

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId(self._type.value)

    def __init__(self, type_: GregorianCalendarTypes = GregorianCalendarTypes.Localized) -> None:
        super().__init__()
        self._type = type_
