# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from collections.abc import Sequence
from typing import Final, final

from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class MapZone:
    """Represents a single ``<mapZone>`` element in the CLDR Windows zone mapping file.

    Equality is defined in a component-wise fashion. When comparing two values for equality, the ``tzdb_ids`` properties
    must return the same IDs in the same order for the values to be considered equal.
    """

    PRIMARY_TERRITORY: Final[str] = "001"
    """Identifier used for the primary territory of each Windows time zone.

    A zone mapping with this territory will always have a single entry. The value of this constant is "001".
    """

    FIXED_OFFSET_TERRITORY: Final[str] = "ZZ"
    """Identifier used for the "fixed offset" territory.

    A zone mapping with this territory will always have a single entry. The value of this constant is "ZZ".
    """

    @property
    def windows_id(self) -> str:
        """Gets the Windows system time zone identifier for this mapping, such as "Central Standard Time".

        Most Windows system time zone identifiers use the name for the "standard" part of the zone as the overall
        identifier. Don't be fooled: just because a time zone includes "standard" in its identifier doesn't mean that it
        doesn't observe daylight saving time.

        :return: The Windows system time zone identifier for this mapping, such as "Central Standard Time".
        """
        return self.__windows_id

    @property
    def territory(self) -> str:
        """Gets the territory code for this mapping.

        This is typically either "001" to indicate that it's the primary territory for this ID, or "ZZ" to indicate a
        fixed-offset ID, or a different two-character capitalized code which indicates the geographical territory.

        :return: The territory code for this mapping.
        """
        return self.__territory

    @property
    def tzdb_ids(self) -> Sequence[str]:
        """Gets a read-only non-empty collection of TZDB zone identifiers for this mapping, such as "America/Chicago"
        and "America/Matamoros" (both of which are TZDB zones associated with the "Central Standard Time" Windows system
        time zone).

        For the primary and fixed-offset territory IDs ("001" and "ZZ") this always contains exactly one time zone ID.
        The IDs returned are not necessarily canonical in TZDB.

        :return: A read-only non-empty collection of TZDB zone identifiers for this mapping.
        """
        return self.__tzdb_ids

    def __init__(self, windows_id: str, territory: str, tzdb_ids: Sequence[str]) -> None:
        """Creates a new mapping entry.

        This constructor is only public for the sake of testability.

        :param windows_id: Windows system time zone identifier. Must not be null.
        :param territory: Territory code. Must not be null.
        :param tzdb_ids: List of territory codes. Must not be null, and must not contain null values.
        """
        self.__windows_id: str = _Preconditions._check_not_null(windows_id, "windows_id")
        self.__territory: str = _Preconditions._check_not_null(territory, "territory")
        self.__tzdb_ids: Sequence[str] = _Preconditions._check_not_null(tuple(tzdb_ids), "tzdb_ids")

    @classmethod
    def __ctor(cls, windows_id: str, territory: str, tzdb_ids: Sequence[str]) -> MapZone:
        """Private constructor to avoid unnecessary list copying (and validation) when deserializing."""
        self = super().__new__(cls)
        self.__windows_id = windows_id
        self.__territory = territory
        self.__tzdb_ids = tzdb_ids
        return self

    @classmethod
    def _read(cls, reader: _IDateTimeZoneReader) -> MapZone:
        """Reads a mapping from a reader."""
        windows_id: str = reader.read_string()
        territory: str = reader.read_string()
        count: int = reader.read_count()
        tzdb_ids: Sequence[str] = tuple(reader.read_string() for _ in range(count))
        return cls.__ctor(windows_id, territory, tzdb_ids)

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        """Writes this mapping to a writer."""
        writer.write_string(self.windows_id)
        writer.write_string(self.territory)
        writer.write_count(len(self.tzdb_ids))
        for tzdb_id in self.tzdb_ids:
            writer.write_string(tzdb_id)

    def equals(self, other: MapZone) -> bool:
        """Compares two ``MapZone`` values for equality.

        :param other: The value to compare this map zone with.
        :return: True if the given value is another map zone equal to this one; false otherwise.
        """
        return self == other

    def __eq__(self, other: object) -> bool:
        """Compares two ``MapZone`` values for equality.

        See the type documentation for a description of equality semantics.

        :param other: The value to compare this map zone with.
        :return: True if the given value is another map zone equal to this one; false otherwise.
        """
        if not isinstance(other, MapZone):
            return NotImplemented
        return (
            self.windows_id == other.windows_id
            and self.territory == other.territory
            and self.tzdb_ids == other.tzdb_ids
        )

    def __hash__(self) -> int:
        """Returns a hash code for this map zone.

        See the type documentation for a description of equality semantics.

        :return: A hash code for this map zone.
        """
        return _hash_code_helper(
            self.windows_id,
            self.territory,
            *self.tzdb_ids,
        )

    def __repr__(self) -> str:
        """Returns a ``str`` that represents this instance.

        :return: The value of the current instance, for diagnostic purposes.
        """
        return f"Windows ID: {self.windows_id}; Territory: {self.territory}; TzdbIds: {' '.join(self.tzdb_ids)}"
