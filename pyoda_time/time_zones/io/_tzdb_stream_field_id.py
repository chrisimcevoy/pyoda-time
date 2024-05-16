# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from enum import IntEnum


class _TzdbStreamFieldId(IntEnum):
    """Enumeration of the fields which can occur in a TZDB stream file.

    This enables the file to be self-describing to a reasonable extent.
    """

    STRING_POOL = 0
    """String pool.

    Format is: number of strings (WriteCount) followed by that many string values.
    The indexes into the resultant list are used for other strings in the file, in some fields.
    """

    TIME_ZONE = 1
    """Repeated field of time zones.

    Format is: zone ID, then zone as written by ``_DateTimeZoneWriter``.
    """

    TZDB_VERSION = 2
    """Single field giving the version of the TZDB source data.

    A string value which does *not* use the string pool.
    """

    TZDB_ID_MAP = 3
    """Single field giving the mapping of ID to canonical ID, as written by ``_DateTimeZoneWriter.write_dictionary``."""

    CLDR_SUPPLEMENTAL_WINDOWS_ZONES = 4
    """Single field containing mapping data as written by ``_WindowsZones.write``."""

    WINDOWS_ADDITIONAL_STANDARD_NAME_TO_ID_MAPPING = 5
    """Single field giving the mapping of Windows StandardName to TZDB canonical ID, for time zones where
    TimeZoneInfo.Id != TimeZoneInfo.StandardName, as written by ``_DateTimeZoneWriter.write_dictionary``."""

    ZONE_LOCATIONS = 6
    """Single field providing all zone locations.

    The format is simply a count, and then that many copies of ``_TzdbZoneLocation`` data.
    """

    ZONE_1970_LOCATIONS = 7
    """Single field providing all "zone 1970" locations.

    The format is simply a count, and then that many copies of ``_TzdbZone1970Location`` data.
    """
