# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import enum


class HebrewMonthNumbering(enum.IntEnum):
    """The month numbering to use for the Hebrew calendar.

    When requesting a Hebrew calendar with ``CalendarSystem.get_hebrew_calendar()``, a month numbering
    system needs to be specified. There are two main ways of numbering the Hebrew months: the civil
    system where month 1 is the start of the new year (Tishri) and scriptural system where month 1 is
    Nisan, according to biblical custom.
    """

    # The numbering system where month 1 is Tishri. This has the advantage of familiarity with other
    # calendars where the first month is 1; it is easier to tell which date comes before which, aside
    # from anything else. It is also the numbering system used by the BCL.
    #
    # The main disadvantage is that due to leap years effectively "splitting" Adar into Adar I
    # and Adar II, the months after that (Nisan, Iyyar and so on) have month numberings which depend
    # on the year.
    CIVIL = 1
    # The numbering system where month 1 is Nisan. This is the numbering system which matches biblical
    # custom (such as Leviticus 23:5). This has the advantage that the split of Adar is at the end of the
    # numbering system, so all other month names are stable.
    #
    # The primary disadvantage of this numbering system is that months 1-6 come after months 7-12 (or 13),
    # which is counter-intuitive.
    SCRIPTURAL = 2
