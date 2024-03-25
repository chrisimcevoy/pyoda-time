# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class UmAlQuraCalendar(Calendar):
    """
    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   1900/04/30  2077/05/13
        UmAlQura    1318/01/01  1500/12/30
        ==========  ==========  ==========
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.UMALQURA
