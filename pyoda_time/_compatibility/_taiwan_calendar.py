# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class TaiwanCalendar(Calendar):
    """Taiwan calendar is based on the Gregorian calendar. And the year is an offset to Gregorian calendar.

    That is:
    Taiwan year = Gregorian year - 1911.  So 1912/01/01 A.D. is Taiwan 1/01/01

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   1912/01/01  9999/12/31
        Taiwan      01/01/01    8088/12/31
        ==========  ==========  ==========
    """

    def __init__(self) -> None:
        from ._culture_info import CultureInfo

        try:
            CultureInfo("zh-TW")
        except Exception as e:
            raise TypeError(self.__class__.__name__) from e

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.TAIWAN
