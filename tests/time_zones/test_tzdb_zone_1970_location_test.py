# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

import pytest

from pyoda_time.time_zones import TzdbZone1970Location
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility import InvalidPyodaDataError

from .. import helpers

SAMPLE_COUNTRY = TzdbZone1970Location.Country("Country name", "CO")


class TestTzdbZone1970Location:
    def test_valid(self) -> None:
        location = TzdbZone1970Location(
            60 * 3600 + 15 * 60 + 5, 100 * 3600 + 30 * 60 + 10, [SAMPLE_COUNTRY], "Etc/MadeUpZone", "Comment"
        )
        assert location.latitude == pytest.approx(60.25 + 5.0 / 3600, abs=0.000001)
        assert location.longitude == pytest.approx(100.5 + 10.0 / 3600, abs=0.000001)
        assert location.countries[0].name == "Country name"
        assert location.countries[0].code == "CO"
        assert location.zone_id == "Etc/MadeUpZone"
        assert location.comment == "Comment"

    def test_country_to_string(self) -> None:
        assert str(SAMPLE_COUNTRY) == "CO (Country name)"

    def test_serialization(self) -> None:
        location = TzdbZone1970Location(
            60 * 3600 + 15 * 60 + 5, 100 * 3600 + 30 * 60 + 10, (SAMPLE_COUNTRY,), "Etc/MadeUpZone", "Comment"
        )
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        location._write(writer)
        stream.seek(0)
        reloaded = TzdbZone1970Location._read(_DateTimeZoneReader._ctor(stream, None))
        assert reloaded.latitude == location.latitude
        assert reloaded.longitude == location.longitude
        assert reloaded.countries == location.countries
        assert reloaded.zone_id == location.zone_id
        assert reloaded.comment == location.comment

    def test_read_invalid(self) -> None:
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        # Valid latitude/longitude
        writer.write_signed_count(0)
        writer.write_signed_count(0)
        # But no countries
        writer.write_count(0)
        writer.write_string("Europe/Somewhere")
        writer.write_string("")
        stream.seek(0)
        reader = _DateTimeZoneReader._ctor(stream, None)
        with pytest.raises(InvalidPyodaDataError):
            TzdbZone1970Location._read(reader)

    def test_latitude_range(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZone1970Location(90 * 3600 + 1, 0, [SAMPLE_COUNTRY], "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZone1970Location(-90 * 3600 - 1, 0, [SAMPLE_COUNTRY], "Zone", "")
        # We'll assume these are built correctly: we're just checking the constructor doesn't throw.
        TzdbZone1970Location(90 * 3600, 0, [SAMPLE_COUNTRY], "Zone", "")
        TzdbZone1970Location(-90 * 3600, 0, [SAMPLE_COUNTRY], "Zone", "")

    def test_longitude_range(self) -> None:
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZone1970Location(0, 180 * 3600 + 1, [SAMPLE_COUNTRY], "Zone", "")
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            TzdbZone1970Location(0, -180 * 3600 - 1, [SAMPLE_COUNTRY], "Zone", "")
        # We'll assume these are built correctly: we're just checking the constructor doesn't throw.
        TzdbZone1970Location(0, 180 * 3600, [SAMPLE_COUNTRY], "Zone", "")
        TzdbZone1970Location(0, -180 * 3600, [SAMPLE_COUNTRY], "Zone", "")

    def test_constructor_invalid_arguments(self) -> None:
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZone1970Location(0, 0, None, "Zone", "")  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZone1970Location(0, 0, [SAMPLE_COUNTRY, None], "Zone", "")  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZone1970Location(0, 0, [SAMPLE_COUNTRY], "Zone", None)  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZone1970Location(0, 0, [SAMPLE_COUNTRY], None, "")  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZone1970Location(0, 0, [], None, "")  # type: ignore

    def test_country_constructor_invalid_arguments(self) -> None:
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZone1970Location.Country(code=None, name="Name")  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentNullException
            TzdbZone1970Location.Country(code="CO", name=None)  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZone1970Location.Country(code="CO", name="")
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZone1970Location.Country(code="Long code", name="Name")
        with pytest.raises(ValueError):  # TODO: ArgumentException
            TzdbZone1970Location.Country(code="S", name="Name")

    def test_country_equality(self) -> None:
        helpers.test_equals_class(
            TzdbZone1970Location.Country("France", "FR"),
            TzdbZone1970Location.Country("France", "FR"),
            TzdbZone1970Location.Country("Germany", "DE"),
        )
