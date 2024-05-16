# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Protocol

from pyoda_time._instant import Instant
from pyoda_time._offset import Offset


class _IDateTimeZoneReader(Protocol):
    """Interface for reading time-related data from a binary stream."""

    @property
    def has_more_data(self) -> bool:
        """Returns whether or not there is more data in this stream.

        :return: Whether or not there is more data in the stream.
        """
        ...

    def read_count(self) -> int:
        """Reads a non-negative integer from the stream, which must have been written by a call to
        ``_IDateTimeZoneWriter.write_count``.

        :return: The integer read from the stream.
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_signed_count(self) -> int:
        """Reads a non-negative integer from the stream, which must have been written by a call to
        ``_IDateTimeZoneWriter.write_signed_count``.

        :return: The integer read from the stream
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_string(self) -> str:
        """Reads a string from the stream.

        :return: The string read from the stream; will not be null
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_byte(self) -> int:
        """Reads a signed 8 bit integer value from the stream and returns it as an int.

        :return: The 8 bit int value.
        :raises InvalidPyodaDataError: The data in the stream has been exhausted.
        """
        ...

    def read_milliseconds(self) -> int:
        """Reads a number of milliseconds from the stream.

        :return: The number of milliseconds read from the stream
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_offset(self) -> Offset:
        """Reads an offset from the stream.

        :return: The offset read from the stream
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_zone_interval_transition(self, previous: Instant | None) -> Instant:
        """Reads an instant representing a zone interval transition from the stream.

        :param previous: The previous transition written (usually for a given timezone), or None if there is no previous
            transition.
        :return: The instant read from the stream
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...

    def read_dictionary(self) -> dict[str, str]:
        """Reads a string-to-string dictionary from the stream.

        :return: The dictionary read from the stream
        :raises InvalidPyodaDataError: The data was invalid.
        """
        ...
