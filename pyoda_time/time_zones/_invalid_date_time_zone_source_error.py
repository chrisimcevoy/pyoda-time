# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.


class InvalidDateTimeZoneSourceError(Exception):
    """Exception thrown to indicate that a time zone source has violated the contract of ``IDateTimeZoneSource``.

    This exception is primarily intended to be thrown from ``DateTimeZoneCache``, and only in the face of a buggy
    source; user code should not usually need to be aware of this or catch it.
    """
