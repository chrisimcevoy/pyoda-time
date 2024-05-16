# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

from pyoda_time.time_zones.cldr import MapZone
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter

from ... import helpers


class TestMapZone:
    def test_equality(self) -> None:
        zone_1 = MapZone("windowsId", "territory", ("id1", "id2", "id3"))
        zone_2 = MapZone("windowsId", "territory", ("id1", "id2", "id3"))
        zone_3 = MapZone("otherWindowsId", "territory", ("id1", "id2", "id3"))
        zone_4 = MapZone("windowsId", "otherTerritory", ("id1", "id2", "id3"))
        zone_5 = MapZone("windowsId", "territory", ("id1", "id2"))
        zone_6 = MapZone("windowsId", "territory", ("id1", "id2", "id4"))
        helpers.test_equals_class(zone_1, zone_2, zone_3)
        helpers.test_equals_class(zone_1, zone_2, zone_4)
        helpers.test_equals_class(zone_1, zone_2, zone_5)
        helpers.test_equals_class(zone_1, zone_2, zone_6)

    def test_to_string(self) -> None:
        zone = MapZone("windowsId", "territory", ("id1", "id2", "id3"))
        expected = "Windows ID: windowsId; Territory: territory; TzdbIds: id1 id2 id3"
        assert str(zone) == expected

    def test_read_write(self) -> None:
        zone = MapZone("windowsId", "territory", ("id1", "id2", "id3"))
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        zone._write(writer)
        stream.seek(0)

        reader = _DateTimeZoneReader._ctor(stream, None)
        zone_2 = MapZone._read(reader)
        assert zone == zone_2
