# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

import pytest

from pyoda_time.time_zones import TzdbZoneLocation
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility import InvalidPyodaDataError


class TestTzdbZoneLocation:
    def test_valid(self) -> None:
        location = TzdbZoneLocation(
            latitude_seconds=60 * 3600 + 15 * 60 + 5,
            longitude_seconds=100 * 3600 + 30 * 60 + 10,
            country_name="Country name",
            country_code="CO",
            zone_id="Etc/MadeUpZone",
            comment="Comment",
        )
        assert location.latitude == pytest.approx(60.25 + 5.0 / 3600, abs=0.000001)
        assert location.longitude == pytest.approx(100.5 + 10.0 / 3600, abs=0.000001)
        assert location.country_name == "Country name"
        assert location.country_code == "CO"
        assert location.zone_id == "Etc/MadeUpZone"
        assert location.comment == "Comment"

    def test_latitude_range(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZoneLocation(90 * 3600 + 1, 0, "Name", "CO", "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZoneLocation(-90 * 3600 - 1, 0, "Name", "CO", "Zone", "")
        # We'll assume these are built correctly: we're just checking the constructor doesn't throw.
        TzdbZoneLocation(90 * 3600, 0, "Name", "CO", "Zone", "")
        TzdbZoneLocation(-90 * 3600, 0, "Name", "CO", "Zone", "")

    def test_longitude_range(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZoneLocation(0, 180 * 3600 + 1, "Name", "CO", "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZoneLocation(0, -180 * 3600 - 1, "Name", "CO", "Zone", "")
        # We'll assume these are built correctly: we're just checking the constructor doesn't throw.
        TzdbZoneLocation(0, 180 * 3600, "Name", "CO", "Zone", "")
        TzdbZoneLocation(0, -180 * 3600, "Name", "CO", "Zone", "")

    def test_constructor_invalid_arguments(self) -> None:
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZoneLocation(0, 0, None, "CO", "Zone", "")  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZoneLocation(0, 0, "Name", None, "Zone", "")  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZoneLocation(0, 0, "Name", "CO", None, "")  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZoneLocation(0, 0, "Name", "CO", "Zone", None)  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZoneLocation(0, 0, "", "CO", "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZoneLocation(0, 0, "Name", "Long code", "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZoneLocation(0, 0, "Name", "S", "Zone", "")

    def test_serialization(self) -> None:
        location = TzdbZoneLocation(
            60 * 3600 + 15 * 60 + 5,
            100 * 3600 + 30 * 60 + 10,
            "Country name",
            "CO",
            "Etc/MadeUpZone",
            "Comment",
        )

        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        location._write(writer)
        stream.seek(0)

        reader = _DateTimeZoneReader._ctor(stream, None)
        location_2 = TzdbZoneLocation._read(reader)

        assert location_2.latitude == pytest.approx(60.25 + 5.0 / 3600, abs=0.000001)
        assert location_2.longitude == pytest.approx(100.5 + 10.0 / 3600, abs=0.000001)
        assert location_2.country_name == "Country name"
        assert location_2.country_code == "CO"
        assert location_2.zone_id == "Etc/MadeUpZone"
        assert location_2.comment == "Comment"

    def test_read_invalid(self) -> None:
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        # This is invalid
        writer.write_signed_count(90 * 3600 + 1)
        writer.write_signed_count(0)
        writer.write_string("name")
        writer.write_string("co")
        writer.write_string("Europe/Somewhere")
        writer.write_string("")
        stream.seek(0)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            TzdbZoneLocation._read(reader)
