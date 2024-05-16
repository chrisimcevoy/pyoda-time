# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Protocol

from pyoda_time._instant import Instant
from pyoda_time._offset import Offset


class _IDateTimeZoneWriter(Protocol):
    """Interface for writing time-related data to a binary stream."""

    def write_count(self, count: int) -> None:
        """Writes a non-negative integer to the stream.

        This is optimized towards cases where most values will be small.

        :param count: The integer to write to the stream.
        :raises ValueError: ``count`` is negative.
        """
        ...

    def write_signed_count(self, count: int) -> None:
        """Writes a possibly-negative integer to the stream.

        This is optimized for values of small magnitudes.

        :param count: The integer to write to the stream.
        """
        ...

    def write_string(self, value: str) -> None:
        """Writes a string to the stream.

        Callers can reasonably expect that these values will be pooled in some fashion, so should not apply their own
        pooling.

        :param value: The string to write to the stream.
        """
        ...

    def write_milliseconds(self, millis: int) -> None:
        """Writes a number of milliseconds to the stream.

        The number of milliseconds must be in the range (-1 day, +1 day).

        :param millis: The number of milliseconds to write to the stream.
        :raises ValueError: ``millis`` is out of range.
        """
        ...

    def write_offset(self, offset: Offset) -> None:
        """Writes an offset to the stream.

        :param offset: The offset to write to the stream.
        """
        ...

    def write_zone_interval_transition(self, previous: Instant | None, value: Instant) -> None:
        """Writes an instant representing a zone interval transition to the stream.

        This method takes a previously-written transition. Depending on the implementation, this value may be required
        by the reader in order to reconstruct the next transition, so it should be deterministic for any given value.

        :param previous: The previous transition written (usually for a given timezone), or None if there is no previous
            transition.
        :param value: The transition to write to the stream.
        """
        ...

    def write_dictionary(self, dictionary: dict[str, str]) -> None:
        """Writes a string-to-string dictionary to the stream.

        :param dictionary: The dictionary to write to the stream.
        """
        ...

    def write_byte(self, value: int) -> None:
        """Writes the given 8-bit integer value to the stream.

        :param value: The value to write.
        """
        ...
