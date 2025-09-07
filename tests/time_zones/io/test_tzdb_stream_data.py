# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io
from typing import TYPE_CHECKING

import pytest

from pyoda_time.time_zones.cldr import WindowsZones
from pyoda_time.time_zones.io._tzdb_stream_data import _TzdbStreamData
from pyoda_time.time_zones.io._tzdb_stream_field import _TzdbStreamField
from pyoda_time.time_zones.io._tzdb_stream_field_id import _TzdbStreamFieldId
from pyoda_time.utility import InvalidPyodaDataError

if TYPE_CHECKING:
    from collections.abc import Callable


class TestTzdbStreamData:
    def test_minimal(self) -> None:
        data = _TzdbStreamData(self.__create_minimal_builder())
        assert data.tzdb_version

    def test_missing_string_pool(self) -> None:
        builder = self.__create_minimal_builder()
        builder._string_pool = None
        with pytest.raises(InvalidPyodaDataError):
            _TzdbStreamData(builder)

    def test_missing_tzdb_alias_map(self) -> None:
        builder = self.__create_minimal_builder()
        builder._tzdb_id_map = None
        with pytest.raises(InvalidPyodaDataError):
            _TzdbStreamData(builder)

    def test_missing_tzdb_version(self) -> None:
        builder = self.__create_minimal_builder()
        builder._tzdb_version = None
        with pytest.raises(InvalidPyodaDataError):
            _TzdbStreamData(builder)

    def test_missing_windows_mapping(self) -> None:
        builder = self.__create_minimal_builder()
        builder._windows_mapping = None
        with pytest.raises(InvalidPyodaDataError):
            _TzdbStreamData(builder)

    def test_invalid_version(self) -> None:
        # It's hard to create a stream that's valid apart from the version, so we'll just
        # give one with an invalid version and check that it looks like the right message.
        stream = io.BytesIO(bytes([0, 0, 0, 1]))
        with pytest.raises(InvalidPyodaDataError) as e:
            _TzdbStreamData._from_stream(stream)
        assert "version" in str(e.value)

    @pytest.mark.parametrize(
        "field_id,handler_method_name",
        [
            (_TzdbStreamFieldId.TIME_ZONE, "_handle_zone_field"),
            (_TzdbStreamFieldId.ZONE_1970_LOCATIONS, "_handle_zone_1970_locations_field"),
            (_TzdbStreamFieldId.ZONE_LOCATIONS, "_handle_zone_locations_field"),
        ],
    )
    def test_missing_string_pool_2(self, field_id: _TzdbStreamFieldId, handler_method_name: str) -> None:
        field = _TzdbStreamField._ctor(field_id, bytearray([0]))
        builder = _TzdbStreamData._Builder()
        method: Callable[[_TzdbStreamField], None] = getattr(builder, handler_method_name)

        with pytest.raises(InvalidPyodaDataError):
            method(field)

    @pytest.mark.parametrize(
        "field_id,handler_method_name",
        [
            (_TzdbStreamFieldId.STRING_POOL, "_handle_string_pool_field"),
            (_TzdbStreamFieldId.TZDB_ID_MAP, "_handle_tzdb_id_map_field"),
            (_TzdbStreamFieldId.TZDB_VERSION, "_handle_tzdb_version_field"),
            (_TzdbStreamFieldId.ZONE_1970_LOCATIONS, "_handle_zone_1970_locations_field"),
            (_TzdbStreamFieldId.ZONE_LOCATIONS, "_handle_zone_locations_field"),
        ],
    )
    def test_duplicate_field(self, field_id: _TzdbStreamFieldId, handler_method_name: str) -> None:
        field = _TzdbStreamField._ctor(field_id, bytearray([0]))
        builder = _TzdbStreamData._Builder()
        # Provide an empty string pool if we're not checking for a duplicate string pool
        if field_id != _TzdbStreamFieldId.STRING_POOL:
            builder._string_pool = []
        method: Callable[[_TzdbStreamField], None] = getattr(builder, handler_method_name)

        # First call should be okay
        method(field)

        # Second call should throw
        with pytest.raises(InvalidPyodaDataError):
            method(field)

    def test_duplicate_time_zone_field(self) -> None:
        # This isn't really a valid field, but we don't parse the data yet anyway - it's
        # enough to give the ID.
        zone_field = _TzdbStreamField._ctor(_TzdbStreamFieldId.STRING_POOL, bytearray(1))

        builder = _TzdbStreamData._Builder()
        builder._string_pool = ["zone1"]
        builder._handle_zone_field(zone_field)
        with pytest.raises(InvalidPyodaDataError):
            builder._handle_zone_field(zone_field)

    @staticmethod
    def __create_minimal_builder() -> _TzdbStreamData._Builder:
        return _TzdbStreamData._Builder(
            string_pool=[],
            tzdb_id_map={},
            tzdb_version="tzdb-version",
            windows_mapping=WindowsZones._ctor(
                version="cldr-version", tzdb_version="tzdb-version", windows_version="windows-version", map_zones=[]
            ),
        )
