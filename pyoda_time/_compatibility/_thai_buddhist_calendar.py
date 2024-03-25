# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class ThaiBuddhistCalendar(Calendar):
    """ThaiBuddhistCalendar is based on Gregorian calendar. Its year value has an offset to the Gregorain calendar.

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   0001/01/01   9999/12/31
        Thai        0544/01/01  10542/12/31
        ==========  ==========  ==========
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.THAI
