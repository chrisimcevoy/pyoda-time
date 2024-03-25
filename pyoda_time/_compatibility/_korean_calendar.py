# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class KoreanCalendar(Calendar):
    """Korean calendar is based on the Gregorian calendar.  And the year is an offset to Gregorian calendar. That is,
    Korean year = Gregorian year + 2333.  So 2000/01/01 A.D. is Korean 4333/01/01.

    0001/1/1 A.D. is Korean year 2334.

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   0001/01/01   9999/12/31
        Korean      2334/01/01  12332/12/31
        ==========  ==========  ==========
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.KOREA

    def __init__(self) -> None:
        from ._culture_info import CultureInfo

        try:
            CultureInfo("ko-KR")
        except Exception as e:
            raise TypeError(self.__class__.__name__) from e
