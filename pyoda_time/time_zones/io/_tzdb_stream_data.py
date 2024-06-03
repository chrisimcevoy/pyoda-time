# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import struct
import types
from typing import Any, BinaryIO, Callable, Final, Sequence, TypeVar, final

from pyoda_time._date_time_zone import DateTimeZone
from pyoda_time.time_zones import TzdbZoneLocation
from pyoda_time.time_zones._cached_date_time_zone import _CachedDateTimeZone
from pyoda_time.time_zones._fixed_date_time_zone import _FixedDateTimeZone
from pyoda_time.time_zones._precalculated_date_time_zone import _PrecalculatedDateTimeZone
from pyoda_time.time_zones._tzdb_zone_1970_location import TzdbZone1970Location
from pyoda_time.time_zones.cldr import WindowsZones
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.time_zones.io._tzdb_stream_field import _TzdbStreamField
from pyoda_time.time_zones.io._tzdb_stream_field_id import _TzdbStreamFieldId
from pyoda_time.utility import InvalidPyodaDataError
from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._preconditions import _Preconditions

T = TypeVar("T")


@final
@_sealed
class _TzdbStreamData:
    """Provides the raw data exposed by ``TzdbDateTimeZoneSource``."""

    class _Builder:
        """Mutable builder class used during parsing."""

        def __init__(
            self,
            string_pool: Sequence[str] | None = None,
            tzdb_version: str | None = None,
            tzdb_id_map: dict[str, str] | None = None,
            windows_mapping: WindowsZones | None = None,
        ) -> None:
            self._string_pool: Sequence[str] | None = string_pool
            self._tzdb_version: str | None = tzdb_version
            self._tzdb_id_map: dict[str, str] | None = tzdb_id_map
            self._zone_locations: Sequence[TzdbZoneLocation] | None = None
            self._zone_1970_locations: Sequence[TzdbZone1970Location] | None = None
            self._windows_mapping: WindowsZones | None = windows_mapping
            self._zone_fields: dict[str, _TzdbStreamField] = {}

        def _handle_string_pool_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._string_pool)
            with field._create_stream() as stream:
                reader = _DateTimeZoneReader._ctor(stream, None)
                count: int = reader.read_count()
                string_pool_array = tuple(reader.read_string() for _ in range(count))
                self._string_pool = string_pool_array

        def _handle_zone_field(self, field: _TzdbStreamField) -> None:
            self.__check_string_pool_presence(field)
            # Just read the ID from the zone - we don't parse the data yet.
            # (We could, but we might as well be lazy.)
            with field._create_stream() as stream:
                reader = _DateTimeZoneReader._ctor(stream, self._string_pool)
                id_: str = reader.read_string()
                if id_ in self._zone_fields:
                    raise InvalidPyodaDataError(f"Multiple definitions for zone {id_}")
                self._zone_fields[id_] = field

        def _handle_tzdb_version_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._tzdb_version)
            self._tzdb_version = field._extract_single_value(lambda reader: reader.read_string(), None)

        def _handle_tzdb_id_map_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._tzdb_id_map)
            self._tzdb_id_map = field._extract_single_value(lambda reader: reader.read_dictionary(), self._string_pool)

        def _handle_supplemental_windows_zones_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._windows_mapping)
            self._windows_mapping = field._extract_single_value(WindowsZones._read, self._string_pool)

        def _handle_zone_locations_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._zone_locations)
            self.__check_string_pool_presence(field)
            with field._create_stream() as stream:
                reader = _DateTimeZoneReader._ctor(stream, self._string_pool)
                count = reader.read_count()
                array = tuple(TzdbZoneLocation._read(reader) for _ in range(count))
                self._zone_locations = array

        def _handle_zone_1970_locations_field(self, field: _TzdbStreamField) -> None:
            self.__check_single_field(field, self._zone_1970_locations)
            self.__check_string_pool_presence(field)
            with field._create_stream() as stream:
                reader = _DateTimeZoneReader._ctor(stream, self._string_pool)
                count = reader.read_count()
                array = tuple(TzdbZone1970Location._read(reader) for _ in range(count))
                self._zone_1970_locations = array

        @staticmethod
        def __check_single_field(field: _TzdbStreamField, expected_null_field: Any) -> None:
            if expected_null_field is not None:
                raise InvalidPyodaDataError(f"Multiple fields of ID {field.id}")

        def __check_string_pool_presence(self, field: _TzdbStreamField) -> None:
            if self._string_pool is None:
                raise InvalidPyodaDataError(f"String pool must be present before field {field.id}")

    __FIELD_HANDLERS: Final[dict[_TzdbStreamFieldId, Callable[[_Builder, _TzdbStreamField], None]]] = {
        _TzdbStreamFieldId.STRING_POOL: lambda builder, field: builder._handle_string_pool_field(field),
        _TzdbStreamFieldId.TIME_ZONE: lambda builder, field: builder._handle_zone_field(field),
        _TzdbStreamFieldId.TZDB_ID_MAP: lambda builder, field: builder._handle_tzdb_id_map_field(field),
        _TzdbStreamFieldId.TZDB_VERSION: lambda builder, field: builder._handle_tzdb_version_field(field),
        _TzdbStreamFieldId.CLDR_SUPPLEMENTAL_WINDOWS_ZONES: lambda builder,
        field: builder._handle_supplemental_windows_zones_field(field),
        _TzdbStreamFieldId.ZONE_LOCATIONS: lambda builder, field: builder._handle_zone_locations_field(field),
        _TzdbStreamFieldId.ZONE_1970_LOCATIONS: lambda builder, field: builder._handle_zone_1970_locations_field(field),
    }

    __ACCEPTED_VERSION: Final[int] = 0

    @property
    def tzdb_version(self) -> str:
        """Returns the TZDB version string."""
        return self.__tzdb_version

    @property
    def tzdb_id_map(self) -> types.MappingProxyType[str, str]:
        """Returns the TZDB ID dictionary (alias to canonical ID)."""
        return self.__tzdb_id_map

    @property
    def windows_mapping(self) -> WindowsZones:
        """Returns the Windows mapping dictionary.

        (As the type is immutable, it can be exposed directly to callers.)
        """
        return self.__windows_mapping

    @property
    def zone_locations(self) -> Sequence[TzdbZoneLocation] | None:
        """Returns the zone locations for the source, or null if no location data is available."""
        return self.__zone_locations

    @property
    def zone_1970_locations(self) -> Sequence[TzdbZone1970Location] | None:
        """Returns the "zone 1970" locations for the source, or null if no such location data is available."""
        return self.__zone_1970_locations

    def __init__(self, builder: _Builder) -> None:
        self.__string_pool: Sequence[str] = self._check_not_null(builder._string_pool, "string pool")
        mutable_id_map = self._check_not_null(builder._tzdb_id_map, "TZDB alias map")
        self.__tzdb_version = self._check_not_null(builder._tzdb_version, "TZDB version")
        self.__windows_mapping = self._check_not_null(builder._windows_mapping, "CLDR Supplemental Windows Zones")
        self.__zone_fields = builder._zone_fields
        self.__zone_locations = builder._zone_locations
        self.__zone_1970_locations = builder._zone_1970_locations

        # Add in the canonical IDs as mappings to themselves
        for zone_id in self.__zone_fields:
            mutable_id_map[zone_id] = zone_id
        self.__tzdb_id_map: types.MappingProxyType[str, str] = types.MappingProxyType(mutable_id_map)

    def create_zone(self, id_: str, canonical_id: str) -> DateTimeZone:
        """Creates the ``DateTimeZone`` for the given canonical ID, which will definitely be one of the values of the
        TzdbAliases dictionary.

        :param id_: ID for the returned zone, which may be an alias.
        :param canonical_id: Canonical ID for zone data
        :return: The created ``DateTimeZone`` for the given ID.
        """
        _Preconditions._check_not_null(id_, "id_")
        _Preconditions._check_not_null(canonical_id, "canonical_id")
        with self.__zone_fields[canonical_id]._create_stream() as stream:
            reader = _DateTimeZoneReader._ctor(stream, self.__string_pool)
            # Skip over the ID before the zone data itself
            reader.read_string()
            type_ = _DateTimeZoneWriter._DateTimeZoneType(reader.read_byte())
            match type_:
                case _DateTimeZoneWriter._DateTimeZoneType.FIXED:
                    return _FixedDateTimeZone.read(reader, id_)
                case _DateTimeZoneWriter._DateTimeZoneType.PRECALCULATED:
                    return _CachedDateTimeZone._for_zone(_PrecalculatedDateTimeZone._read(reader, id_))
                case _:
                    raise InvalidPyodaDataError(f"Unknown time zone type {type_.name}")

    @staticmethod
    def _check_not_null(input_: T | None, name: str) -> T:
        if input_ is None:
            raise InvalidPyodaDataError(f"Incomplete TZDB data. Missing field: {name}")
        return input_

    @classmethod
    def _from_stream(cls, stream: BinaryIO) -> _TzdbStreamData:
        _Preconditions._check_not_null(stream, "stream")

        version = struct.unpack("i", stream.read(4))[0]
        if version != cls.__ACCEPTED_VERSION:
            raise InvalidPyodaDataError(f"Unable to read stream with version {version}")

        builder = cls._Builder()
        for field in _TzdbStreamField._read_fields(stream):
            handler = cls.__FIELD_HANDLERS.get(field.id)
            if handler:
                handler(builder, field)

        return cls(builder)
