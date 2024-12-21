# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import types
from importlib import resources
from typing import TYPE_CHECKING, BinaryIO, _ProtocolMeta, cast, final

from pyoda_time.time_zones import IDateTimeZoneSource, TzdbZone1970Location, TzdbZoneLocation
from pyoda_time.time_zones.cldr import MapZone, WindowsZones
from pyoda_time.time_zones.io._tzdb_stream_data import _TzdbStreamData
from pyoda_time.utility import InvalidPyodaDataError
from pyoda_time.utility._csharp_compatibility import _private, _sealed, _to_lookup
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from pyoda_time._date_time_zone import DateTimeZone


class __TzdbDateTimeZoneSourceMeta(_ProtocolMeta):
    _default: TzdbDateTimeZoneSource

    @property
    def default(self) -> TzdbDateTimeZoneSource:
        if getattr(self, "_default", None) is None:
            path = resources.files(__name__) / "Tzdb.nzd"
            with cast(BinaryIO, path.open("rb")) as stream:
                self._default = TzdbDateTimeZoneSource._ctor(_TzdbStreamData._from_stream(stream))
        return self._default


@final
@_sealed
@_private
class TzdbDateTimeZoneSource(IDateTimeZoneSource, metaclass=__TzdbDateTimeZoneSourceMeta):
    """Provides an implementation of ``IDateTimeZoneSource`` that loads data originating from the
    `tz database <https://www.iana.org/time-zones>`_ (also known as the IANA Time Zone database, or zoneinfo
    or Olson database).

    All calls to ``for_id`` for fixed-offset IDs advertised by the source (i.e. "UTC" and "UTC+/-Offset")
    will return zones equal to those returned by ``DateTimeZone.for_offset``.
    """

    __source: _TzdbStreamData
    __aliases: Mapping[str, Sequence[str]]
    __version: str
    __tzdb_to_windows_id: Mapping[str, str] | None
    __windows_to_tzdb_id: Mapping[str, str] | None
    __guesses: dict[str, str | None]

    @property
    def aliases(self) -> Mapping[str, Sequence[str]]:
        """Gets a lookup from canonical time zone ID (e.g. "Europe/London") to a group of aliases for that time zone
        (e.g. {"Europe/Belfast", "Europe/Guernsey", "Europe/Jersey", "Europe/Isle_of_Man", "GB", "GB-Eire"}).

        The group of values for a key never contains the canonical ID, only aliases. Any time zone ID which is itself an
        alias or has no aliases linking to it will not be present in the lookup. The aliases within a group are returned
        in alphabetical (ordinal) order.

        :return: A lookup from canonical ID to the aliases of that ID.
        """
        return self.__aliases

    @property
    def canonical_id_map(self) -> Mapping[str, str]:
        """Returns a read-only map from time zone ID to the canonical ID. For example, the key "Europe/Jersey" would be
        associated with the value "Europe/London".

        This map contains an entry for every ID returned by ``get_ids``, where canonical IDs map to themselves.

        The returned map is read-only.

        :return: A map from time zone ID to the canonical ID.
        """
        return self.__source.tzdb_id_map

    @property
    def zone_locations(self) -> Sequence[TzdbZoneLocation] | None:
        """Gets a read-only list of zone locations known to this source, or null if the original source data does not
        include zone locations.

        Every zone location's time zone ID is guaranteed to be valid within this source (assuming the source has been
        validated).

        :return: A read-only list of zone locations known to this source.
        """
        return self.__source.zone_locations

    @property
    def zone_1970_locations(self) -> Sequence[TzdbZone1970Location] | None:
        """Gets a read-only list of "zone 1970" locations known to this source, or None if the original source data does
        not include zone locations.

        This location data differs from ``zone_locations`` in two important respects:

        * Where multiple similar zones exist but only differ in transitions before 1970, this location data chooses one
          zone to be the canonical "post 1970" zone.
        * This location data can represent multiple ISO-3166 country codes in a single entry. For example,
          the entry corresponding to "Europe/London" includes country codes GB, GG, JE and IM (Britain,
          Guernsey, Jersey and the Isle of Man, respectively).

        Every zone location's time zone ID is guaranteed to be valid within this source (assuming the source has been
        validated).

        :return: A read-only list of zone locations known to this source.
        """
        return self.__source.zone_1970_locations

    @property
    def version_id(self) -> str:
        """This source returns a string such as "TZDB: 2013b (mapping: 8274)" corresponding to the versions of the tz
        database and the CLDR Windows zones mapping file.

        Note that there is no need to parse this string to extract any of the above information, as it is available
        directly from the ``tzdb_version`` and ``WindowsZones.version`` properties.
        """
        return f"TZDB: {self.__version}"

    @classmethod
    def from_stream(cls, stream: BinaryIO) -> TzdbDateTimeZoneSource:
        """Creates an instance from a stream in the custom Noda Time format. The stream must be readable.

        The stream is not closed by this method, but will be read from without rewinding. A successful call will read
        the stream to the end.

        See the user guide for instructions on how to generate an updated time zone database file from a copy of the
        (textual) tz database.

        :param stream: The stream containing time zone data
        :return: A ``_TzdbDateTimeZoneSource`` providing information from the given stream.
        :raises InvalidPyodaDataError: The stream contains invalid time zone data, or data which cannot be read by this
            version of Pyoda Time.
        """
        _Preconditions._check_not_null(stream, "stream")
        return cls._ctor(_TzdbStreamData._from_stream(stream))

    @classmethod
    def _ctor(cls, source: _TzdbStreamData) -> TzdbDateTimeZoneSource:
        self = super().__new__(cls)
        self.__source = _Preconditions._check_not_null(source, "source")
        self.__aliases = _to_lookup(dict(sorted({k: v for k, v in self.canonical_id_map.items() if k != v}.items())))
        self.__version = f"{source.tzdb_version} (mapping: {source.windows_mapping.version})"
        self.__tzdb_to_windows_id = None
        self.__windows_to_tzdb_id = None
        self.__guesses = {}
        return self

    def __build_tzdb_to_windows_id_map(self) -> Mapping[str, str]:
        """Builds the dictionary returned by ``tzdb_to_windows_ids``; this is called lazily.

        This method assumes the source is valid, for uniqueness purposes etc.
        """
        mutable: dict[str, str] = {}
        # First map everything from the WindowsZones.
        for zone in (zone for zone in self.windows_mapping.map_zones if zone.territory != MapZone.PRIMARY_TERRITORY):
            for tzdb_id in zone.tzdb_ids:
                mutable[tzdb_id] = zone.windows_id

        aliases = {k: v for k, v in self.canonical_id_map.items() if k != v}

        # TODO: can we iterate over aliases once?

        # Now map any missing canonical IDs based on aliases
        for k, v in sorted(aliases.items()):
            if v not in mutable and (windows_id := mutable.get(k)):
                mutable[v] = windows_id

        # Finally map any missing aliases based on canonical IDs
        for k, v in aliases.items():
            if k not in mutable and (windows_id := mutable.get(v)):
                mutable[k] = windows_id

        return types.MappingProxyType(mutable)

    def __build_windows_to_tzdb_id_map(self) -> Mapping[str, str]:
        """Builds the dictionary returned by ``windows_to_tzdb_ids``; this is called lazily."""
        return types.MappingProxyType(
            {k: self.canonical_id_map[v] for k, v in self.windows_mapping.primary_mapping.items()}
        )

    def for_id(self, id_: str) -> DateTimeZone:
        # TODO: inheritdoc?
        if not (canonical_id := self.canonical_id_map.get(_Preconditions._check_not_null(id_, "id_"))):
            raise ValueError(f"Time zone with ID {id_} not found in source {self.__version}")
        return self.__source.create_zone(id_, canonical_id)

    def get_ids(self) -> Iterable[str]:
        return self.canonical_id_map.keys()

    def get_system_default_id(self) -> str | None:
        raise NotImplementedError

    @property
    def tzdb_version(self) -> str:
        """Gets just the TZDB version (e.g. "2013a") of the source data.

        :return: The TZDB version (e.g. "2013a") of the source data.
        """
        return self.__source.tzdb_version

    @property
    def windows_mapping(self) -> WindowsZones:
        """Gets the Windows time zone mapping information provided in the CLDR supplemental "windowsZones.xml" file.

        :return: The Windows time zone mapping information provided in the CLDR supplemental "windowsZones.xml" file.
        """
        return self.__source.windows_mapping

    @property
    def tzdb_to_windows_ids(self) -> Mapping[str, str]:
        """Returns a dictionary mapping TZDB IDs to Windows IDs.

        Where a TZDB alias isn't present directly in the Windows mapping, but its canonical ID is, the dictionary will
        contain an entry for the alias as well. For example, the TZDB ID "Africa/Asmara" is an alias for
        "Africa/Nairobi", which has a Windows ID of "E. Africa Standard Time". "Africa/Asmara" doesn't appear in the
        Windows mapping directly, but it will still be present in the returned dictionary.

        Where a TZDB canonical ID isn't present in the Windows mapping, but an alias is, the dictionary will contain an
        entry for the canonical ID as well. For example, the Windows mapping uses the TZDB ID "Asia/Calcutta" for "India
        Standard Time". This is an alias for "Asia/Kolkata" in TZDB, so the returned dictionary will have an entry
        mapping "Asia/Kolkata" to "Asia/Calcutta". If multiple aliases for the same canonical ID have entries in the
        Windows mapping with different Windows IDs, the alias that is earliest in lexicographical ordering determines
        the value for the entry.

        If a canonical ID is not present in the mapping, nor any of its aliases, it will not be present in the returned
        dictionary.
        """
        if self.__tzdb_to_windows_id is None:
            self.__tzdb_to_windows_id = self.__build_tzdb_to_windows_id_map()
        return self.__tzdb_to_windows_id

    @property
    def windows_to_tzdb_ids(self) -> Mapping[str, str]:
        """Returns a dictionary mapping Windows IDs to canonical TZDB IDs, using the primary mapping in each
        ``MapZone``.

        Sometimes the Windows mapping contains values which are not canonical TZDB IDs. Every value in the returned
        dictionary is a canonical ID. For example, the Windows mapping contains as "Asia/Calcutta" for the Windows ID
        "India Standard Time", but "Asia/Calcutta" is an alias for "Asia/Kolkata". The entry for "India Standard Time"
        in the returned dictionary therefore has "Asia/Kolkata" as the value.

        :return:
        """
        if self.__windows_to_tzdb_id is None:
            self.__windows_to_tzdb_id = self.__build_windows_to_tzdb_id_map()
        return self.__windows_to_tzdb_id

    def validate(self) -> None:
        """Validates that the data within this source is consistent with itself.

        Source data is not validated automatically when it's loaded, but any source loaded from data produced by
        ``NodaTime.TzdbCompiler`` (including the data shipped with Noda Time) will already have been validated via
        this method when it was originally produced. This method should only normally be called explicitly if you have
        data from a source you're unsure of.

        :raises InvalidPyodaDataError: The source data is invalid. The source may not function correctly.
        """
        # Check that each entry has a canonical value. (Every mapping x to y
        # should be such that y maps to itself.)
        for key, value in self.canonical_id_map.items():
            if (canonical := self.canonical_id_map.get(value)) is None:
                raise InvalidPyodaDataError(f"Mapping for entry {key} ({value}) is missing")
            if value != canonical:
                raise InvalidPyodaDataError(
                    f"Mapping for entry {key} ({value}) is not canonical ({value} maps to {canonical})"
                )

        # Check that every Windows mapping has a primary territory
        for map_zone in self.windows_mapping.map_zones:
            # Simplest way of checking is to find the primary mapping...
            if map_zone.windows_id not in self.__source.windows_mapping.primary_mapping:
                raise InvalidPyodaDataError(
                    f"Windows mapping for standard ID {map_zone.windows_id} has no primary territory"
                )

        # Check Windows mappings:
        # - Each MapZone uses TZDB IDs that are known to this source,
        # - Each TZDB ID only occurs once except for the primary territory
        # - Every ID has a primary territory
        # - Within each ID, the territories are unique
        # - Each primary territory TZDB ID occurs as a non-primary territory
        mapped_tzdb_ids = set()
        for map_zone in self.windows_mapping.map_zones:
            for id_ in map_zone.tzdb_ids:
                if id_ not in self.canonical_id_map:
                    raise InvalidPyodaDataError(f"Windows mapping uses TZDB ID {id_} which is missing")
                # The primary territory ID is also present as a non-primary territory,
                # so don't include it in duplicate detection. Everything else should be unique.
                if map_zone.territory != MapZone.PRIMARY_TERRITORY:
                    if id_ in mapped_tzdb_ids:
                        raise InvalidPyodaDataError(f"Windows mapping has multiple entries for TZDB ID {id_}")
                    mapped_tzdb_ids.add(id_)

        territories_by_windows_id = _to_lookup({mz: mz.windows_id for mz in self.windows_mapping.map_zones})
        for key, zones in territories_by_windows_id.items():
            if len({zone.territory for zone in zones}) != len(zones):
                raise InvalidPyodaDataError(f"Windows mapping has duplicate territories entries for Windows ID {key}")
            try:
                primary = next(zone for zone in zones if zone.territory == MapZone.PRIMARY_TERRITORY)
            except StopIteration:
                raise InvalidPyodaDataError(f"Windows mapping has no primary territory entry for Windows ID {key}")
            if len(primary.tzdb_ids) != 1:
                raise InvalidPyodaDataError(
                    f"Expected one tzdb id for primary zone {primary}, got {len(primary.tzdb_ids)}"
                )
            primary_tzdb = primary.tzdb_ids[0]
            if not any(z for z in zones if z.territory != MapZone.PRIMARY_TERRITORY and primary_tzdb in z.tzdb_ids):
                raise InvalidPyodaDataError(
                    f"Windows mapping primary territory entry for Windows ID {key} "
                    f"has TZDB ID {primary_tzdb} which does not occur in a non-primary territory"
                )

        # Check that each zone location has a valid zone ID
        if self.zone_locations:
            for tzdb_zone_location in self.zone_locations:
                if tzdb_zone_location.zone_id not in self.canonical_id_map:
                    raise InvalidPyodaDataError(
                        f"Zone location {tzdb_zone_location.country_name} uses zone ID {tzdb_zone_location.zone_id} "
                        f"which is missing"
                    )
        if self.zone_1970_locations:
            for tzdb_1970_zone_location in self.zone_1970_locations:
                if tzdb_1970_zone_location.zone_id not in self.canonical_id_map:
                    raise InvalidPyodaDataError(
                        f"Zone 1970 location {tzdb_1970_zone_location.countries[0].name} "
                        f"uses zone ID {tzdb_1970_zone_location.zone_id} which is missing"
                    )
