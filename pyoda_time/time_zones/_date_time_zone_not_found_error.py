# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import final

from pyoda_time.utility._csharp_compatibility import _sealed


@final
@_sealed
class DateTimeZoneNotFoundError(KeyError):
    """Exception thrown when time zone is requested from an ``IDateTimeZoneProvider`` but the specified ID is invalid
    for that provider."""
