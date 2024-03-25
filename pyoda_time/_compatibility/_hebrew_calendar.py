# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class HebrewCalendar(Calendar):
    """Rules for the Hebrew calendar:
    - The Hebrew calendar is both a Lunar (months) and Solar (years)
      calendar, but allows for a week of seven days.
    - Days begin at sunset.
    - Leap Years occur in the 3, 6, 8, 11, 14, 17, &amp; 19th years of a
      19-year cycle.  Year = leap iff ((7y+1) mod 19 &lt; 7).
    - There are 12 months in a common year and 13 months in a leap year.
    - In a common year, the 6th month, Adar, has 29 days.  In a leap
      year, the 6th month, Adar I, has 30 days and the leap month,
      Adar II, has 29 days.
    - Common years have 353-355 days.  Leap years have 383-385 days.
    - The Hebrew new year (Rosh HaShanah) begins on the 1st of Tishri,
      the 7th month in the list below.
    - The new year may not begin on Sunday, Wednesday, or Friday.
    - If the new year would fall on a Tuesday and the conjunction of
      the following year were at midday or later, the new year is
      delayed until Thursday.
    - If the new year would fall on a Monday after a leap year, the
      new year is delayed until Tuesday.
    - The length of the 8th and 9th months vary from year to year,
      depending on the overall length of the year.
    - The length of a year is determined by the dates of the new
      years (Tishri 1) preceding and following the year in question.
    - The 2th month is long (30 days) if the year has 355 or 385 days.
    - The 3th month is short (29 days) if the year has 353 or 383 days.
    - The Hebrew months are:
      1.  Tishri        (30 days)
      2.  Heshvan       (29 or 30 days)
      3.  Kislev        (29 or 30 days)
      4.  Teveth        (29 days)
      5.  Shevat        (30 days)
      6.  Adar I        (30 days)
      7.  Adar {II}     (29 days, this only exists if that year is a leap year)
      8.  Nisan         (30 days)
      9.  Iyyar         (29 days)
      10. Sivan         (30 days)
      11. Tammuz        (29 days)
      12. Av            (30 days)
      13. Elul          (29 days)

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   1583/01/01  2239/09/29
        Hebrew      5343/04/07  5999/13/29
        ==========  ==========  ==========

    Includes CHebrew implementation;i.e All the code necessary for converting
    Gregorian to Hebrew Lunar from 1583 to 2239.
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.HEBREW
