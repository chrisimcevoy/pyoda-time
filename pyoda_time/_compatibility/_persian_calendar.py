# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId


class PersianCalendar(Calendar):
    """Modern Persian calendar is a solar observation based calendar. Each new year begins on the day when the vernal
    equinox occurs before noon. The epoch is the date of the vernal equinox prior to the epoch of the Islamic calendar
    (March 19, 622 Julian or March 22, 622 Gregorian) There is no Persian year 0. Ordinary years have 365 days. Leap
    years have 366 days with the last month (Esfand) gaining the extra day.

    Calendar support range:
        ==========  ==========  ==========
        Calendar    Minimum     Maximum
        ==========  ==========  ==========
        Gregorian   0622/03/22   9999/12/31
        Persian     0001/01/01   9378/10/13
        ==========  ==========  ==========
    """

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.PERSIAN

    @property
    def _base_calendar_id(self) -> _CalendarId:
        return _CalendarId.GREGORIAN
