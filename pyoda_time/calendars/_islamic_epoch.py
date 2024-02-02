# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import enum as _enum


class IslamicEpoch(_enum.IntEnum):
    """The epoch to use when constructing an Islamic calendar.

    The Islamic, or Hijri, calendar can either be constructed starting on July 15th 622CE (in the Julian calendar) or on
    the following day. The former is the "astronomical" or "Thursday" epoch; the latter is the "civil" or "Friday"
    epoch.
    """

    # Epoch beginning on July 15th 622CE (Julian), which is July 18th 622 CE in the Gregorian calendar.
    # This is the epoch used by the BCL HijriCalendar.
    ASTRONOMICAL = 1
    # Epoch beginning on July 16th 622CE (Julian), which is July 19th 622 CE in the Gregorian calendar.
    CIVIL = 2
