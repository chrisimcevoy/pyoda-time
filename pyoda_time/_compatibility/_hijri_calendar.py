# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class HijriCalendar(Calendar):
    """Rules for the Hijri calendar:
    - The Hijri calendar is a strictly Lunar calendar.
    - Days begin at sunset.
    - Islamic Year 1 (Muharram 1, 1 A.H.) is equivalent to absolute date
      227015 (Friday, July 16, 622 C.E. - Julian).
    - Leap Years occur in the 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, &amp; 29th
      years of a 30-year cycle.  Year = leap iff ((11y+14) mod 30 &lt; 11).
    - There are 12 months which contain alternately 30 and 29 days.
    - The 12th month, Dhu al-Hijjah, contains 30 days instead of 29 days
      in a leap year.
    - Common years have 354 days.  Leap years have 355 days.
    - There are 10,631 days in a 30-year cycle.
    - The Islamic months are:
        1.  Muharram       (30 days)
        2.  Safar          (29 days)
        3.  Rabi I         (30 days)
        4.  Rabi II        (29 days)
        5.  Jumada I       (30 days)
        6.  Jumada II      (29 days)
        7.  Rajab          (30 days)
        8.  Sha'ban        (29 days)
        9.  Ramadan        (30 days)
        10. Shawwal        (29 days)
        11. Dhu al-Qada    (30 days)
        12. Dhu al-Hijjah  (29 days) {30}

    NOTE:
    The calculation of the HijriCalendar is based on the absolute date.  And the
    absolute date means the number of days from January 1st, 1 A.D.
    Therefore, we do not support the days before the January 1st, 1 A.D.

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   0622/07/18   9999/12/31
        Hijri       0001/01/01   9666/04/03
        ==========  ==========  ==========
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.HIJRI
