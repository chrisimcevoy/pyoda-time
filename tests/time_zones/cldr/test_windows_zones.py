# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io
from typing import Final

from pyoda_time.time_zones.cldr import MapZone, WindowsZones
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter

MAP_ZONE_1: Final[MapZone] = MapZone("windowsId1", "territory1", ("id1.1", "id1.2", "id1.3"))
MAP_ZONE_2: Final[MapZone] = MapZone("windowsId2", MapZone.PRIMARY_TERRITORY, ("primaryId2",))
MAP_ZONE_3: Final[MapZone] = MapZone("windowsId3", MapZone.PRIMARY_TERRITORY, ("primaryId3",))


class TestWindowsZones:
    def test_properties(self) -> None:
        zones = WindowsZones._ctor("version", "tzdb_version", "windowsVersion", (MAP_ZONE_1, MAP_ZONE_2, MAP_ZONE_3))
        assert zones.version == "version"
        assert zones.tzdb_version == "tzdb_version"
        assert zones.windows_version == "windowsVersion"
        assert zones.primary_mapping["windowsId2"] == "primaryId2"
        assert zones.primary_mapping["windowsId3"] == "primaryId3"
        assert zones.map_zones == (MAP_ZONE_1, MAP_ZONE_2, MAP_ZONE_3)

    def test_read_write(self) -> None:
        zones = WindowsZones._ctor("version", "tzdb_version", "windowsVersion", (MAP_ZONE_1, MAP_ZONE_2, MAP_ZONE_3))

        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        zones._write(writer)
        stream.seek(0)

        reader = _DateTimeZoneReader._ctor(stream, None)
        zones_2 = WindowsZones._read(reader)

        assert zones_2.version == "version"
        assert zones_2.tzdb_version == "tzdb_version"
        assert zones_2.windows_version == "windowsVersion"
        assert zones_2.primary_mapping["windowsId2"] == "primaryId2"
        assert zones_2.primary_mapping["windowsId3"] == "primaryId3"
        assert zones_2.map_zones == (MAP_ZONE_1, MAP_ZONE_2, MAP_ZONE_3)
