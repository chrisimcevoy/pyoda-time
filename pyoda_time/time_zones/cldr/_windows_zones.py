# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import types
from typing import TYPE_CHECKING, final

from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

from ._map_zone import MapZone

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ..io._i_date_time_zone_reader import _IDateTimeZoneReader
    from ..io._i_date_time_zone_writer import _IDateTimeZoneWriter


@final
@_sealed
@_private
class WindowsZones:
    """Representation of the ``<windowsZones>`` element of CLDR supplemental data.

    See the CLDR design proposal for more details of the structure of the file from which data is taken.
    http://cldr.unicode.org/development/development-process/design-proposals/extended-windows-olson-zid-mapping
    """

    __version: str
    __tzdb_version: str
    __windows_version: str
    __map_zones: Sequence[MapZone]
    __primary_mapping: types.MappingProxyType[str, str]

    @property
    def version(self) -> str:
        """Gets the version of the Windows zones mapping data read from the original file.

        As with other IDs, this should largely be treated as an opaque string, but the current method for generating
        this from the mapping file extracts a number from an element such as <c>&lt;version number="$Revision: 7825
        $"/&gt;</c>. This is a Subversion revision number, but that association should only be used for diagnostic
        curiosity, and never assumed in code.

        :return: The version of the Windows zones mapping data read from the original file.
        """
        return self.__version

    @property
    def tzdb_version(self) -> str:
        """Gets the TZDB version this Windows zone mapping data was created from.

        The CLDR mapping file usually lags behind the TZDB file somewhat - partly because the
        mappings themselves don't always change when the time zone data does. For example, it's entirely
        reasonable for a ``TzdbDateTimeZoneSource`` with a ``tzdb_version`` of
        "2013b" to be supply a ``WindowsZones`` object with a ``tzdb_version`` of "2012f".

        :return: The TZDB version this Windows zone mapping data was created from.
        """
        return self.__tzdb_version

    @property
    def windows_version(self) -> str:
        r"""Gets the Windows time zone database version this Windows zone mapping data was created from.

        At the time of this writing, this is populated (by CLDR) from the registry key
        HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones\TzVersion, so "7dc0101" for example.

        :return: The Windows time zone database version this Windows zone mapping data was created from.
        """
        return self.__windows_version

    @property
    def map_zones(self) -> Sequence[MapZone]:
        """Gets an immutable collection of mappings from Windows system time zones to TZDB time zones.

        Each mapping consists of a single Windows time zone ID and a single territory to potentially multiple TZDB IDs
        that are broadly equivalent to that Windows zone/territory pair.

        Mappings for a single Windows system time zone can appear multiple times in this list, in different territories.
        For example, "Central Standard Time" maps to different TZDB zones in different countries (the US, Canada,
        Mexico) and even within a single territory there can be multiple zones. Every Windows system time zone covered
        within this collection has a "primary" entry with a territory code of "001" (which is the value of
        ``MapZone.PRIMARY_TERRITORY``) and a single corresponding TZDB zone.

        This collection is not guaranteed to cover every Windows time zone. Some zones may be unmappable (such as
        "Mid-Atlantic Standard Time") and there can be a delay between a new Windows time zone being introduced and it
        appearing in CLDR, ready to be used by Noda Time. (There's also bound to be a delay between it appearing in
        CLDR and being used in your production system.) In practice however, you're unlikely to wish to use a time zone
        which isn't covered here.

        :return: An immutable collection of mappings from Windows system time zones to TZDB time zones.
        """
        return self.__map_zones

    @property
    def primary_mapping(self) -> types.MappingProxyType[str, str]:
        """Gets an immutable dictionary of primary mappings, from Windows system time zone ID to TZDB zone ID. This
        corresponds to the "001" territory which is present for every zone within the mapping file.

        Each value in the dictionary is a canonical ID in CLDR, but it may not be canonical
        in TZDB. For example, the ID corresponding to "India Standard Time" is "Asia/Calcutta", which
        is canonical in CLDR but is an alias in TZDB for "Asia/Kolkata". To obtain a canonical TZDB
        ID, use ``TzdbDateTimeZoneSource.canonical_id_map``.

        :return: An immutable dictionary of primary mappings, from Windows system time zone ID to TZDB zone ID.
        """
        return self.__primary_mapping

    @classmethod
    def _ctor(cls, version: str, tzdb_version: str, windows_version: str, map_zones: Sequence[MapZone]) -> WindowsZones:
        return cls.__ctor(
            version=_Preconditions._check_not_null(version, "version"),
            tzdb_version=_Preconditions._check_not_null(tzdb_version, "tzdb_version"),
            windows_version=_Preconditions._check_not_null(windows_version, "windows_version"),
            map_zones=tuple(_Preconditions._check_not_null(map_zones, "map_zones")),
        )

    @classmethod
    def __ctor(
        cls, version: str, tzdb_version: str, windows_version: str, map_zones: Sequence[MapZone]
    ) -> WindowsZones:
        self = super().__new__(cls)
        self.__version = version
        self.__tzdb_version = tzdb_version
        self.__windows_version = windows_version
        self.__map_zones = map_zones
        self.__primary_mapping = types.MappingProxyType(
            {z.windows_id: z.tzdb_ids[0] for z in map_zones if z.territory == MapZone.PRIMARY_TERRITORY}
        )
        return self

    @classmethod
    def _read(cls, reader: _IDateTimeZoneReader) -> WindowsZones:
        version: str = reader.read_string()
        tzdb_version: str = reader.read_string()
        windows_version: str = reader.read_string()
        count: int = reader.read_count()
        map_zones = tuple(MapZone._read(reader) for _ in range(count))
        return WindowsZones.__ctor(version, tzdb_version, windows_version, map_zones)

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        writer.write_string(self.version)
        writer.write_string(self.tzdb_version)
        writer.write_string(self.windows_version)
        writer.write_count(len(self.map_zones))
        for map_zone in self.map_zones:
            map_zone._write(writer)
