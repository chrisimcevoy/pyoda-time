# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import itertools
from pathlib import Path

import pytest

from pyoda_time import DateTimeZone, DateTimeZoneProviders, Instant, LocalDateTime, PyodaConstants, ZonedDateTime
from pyoda_time.time_zones import TzdbZone1970Location, TzdbZoneLocation
from pyoda_time.time_zones._tzdb_date_time_zone_source import TzdbDateTimeZoneSource
from pyoda_time.time_zones.cldr import MapZone, WindowsZones
from pyoda_time.time_zones.io._tzdb_stream_data import _TzdbStreamData
from pyoda_time.time_zones.io._tzdb_stream_field import _TzdbStreamField
from pyoda_time.time_zones.io._tzdb_stream_field_id import _TzdbStreamFieldId
from pyoda_time.utility import InvalidPyodaDataError


class TestTzdbDateTimeZoneSource:
    def test_can_load_noda_time_resource_from_one_point_one_release(self) -> None:
        path = Path(__file__).parent.parent / "test_data" / "Tzdb2013bFromNodaTime1.1.nzd"
        assert path.exists()
        assert path.is_file()
        with open(path, mode="rb") as stream:
            source = TzdbDateTimeZoneSource.from_stream(stream)
        assert source.version_id == "TZDB: 2013b (mapping: 8274)"

        utc = Instant.from_utc(2007, 8, 24, 9, 30, 0)

        # Test a regular zone with rules.
        london = source.for_id("Europe/London")
        in_london = ZonedDateTime(instant=utc, zone=london)
        expected_local = LocalDateTime(2007, 8, 24, 10, 30)
        assert in_london.local_date_time == expected_local

        # Test a fixed-offset zone.
        utc_fixed = source.for_id("Etc/UTC")
        in_utc_fixed = ZonedDateTime(instant=utc, zone=utc_fixed)
        expected_local = LocalDateTime(2007, 8, 24, 9, 30)
        assert in_utc_fixed.local_date_time == expected_local

        # Test an alias
        jersey = source.for_id("Japan")  # Asia/Tokyo
        in_jersey = ZonedDateTime(instant=utc, zone=jersey)
        expected_local = LocalDateTime(2007, 8, 24, 18, 30)
        assert in_jersey.local_date_time == expected_local

        # Test ZoneLocations
        assert source.zone_locations
        france = next(s for s in source.zone_locations if s.country_name == "France")
        # Tolerance of about 2 seconds
        assert france.latitude == pytest.approx(48.86666, abs=0.00055)
        assert france.longitude == pytest.approx(2.3333, abs=0.00055)
        assert france.zone_id == "Europe/Paris"
        assert france.country_code == "FR"
        assert france.comment == ""

    def test_for_id_all_ids(self) -> None:
        """Simply tests that every ID in the built-in database can be fetched.

        This is also
        helpful for diagnostic debugging when we want to check that some potential
        invariant holds for all time zones...
        """
        source: TzdbDateTimeZoneSource = TzdbDateTimeZoneSource.default

        for id_ in source.get_ids():
            assert source.for_id(id_) is not None

    def test_for_id_null(self) -> None:
        with pytest.raises(TypeError):
            TzdbDateTimeZoneSource.default.for_id(None)  # type: ignore

    def test_for_id_unknown(self) -> None:
        with pytest.raises(ValueError) as e:
            TzdbDateTimeZoneSource.default.for_id("unknown")
        assert str(e.value) == "Time zone with ID unknown not found in source 2023c (mapping: $Revision$)"

    def test_utc_equals_builtin(self) -> None:
        zone = TzdbDateTimeZoneSource.default.for_id("UTC")
        assert zone == DateTimeZone.utc

    def test_aliases(self) -> None:
        aliases = TzdbDateTimeZoneSource.default.aliases
        assert aliases["Europe/London"] == [
            "Europe/Belfast",
            "Europe/Guernsey",
            "Europe/Isle_of_Man",
            "Europe/Jersey",
            "GB",
            "GB-Eire",
        ]
        assert aliases["Europe/London"] == sorted(aliases["Europe/London"])
        assert len(aliases["Europe/Jersey"]) == 0

    def test_canonical_id_map_contents(self) -> None:
        map_ = TzdbDateTimeZoneSource.default.canonical_id_map
        assert map_["Europe/Jersey"] == "Europe/London"
        assert map_["Europe/London"] == "Europe/London"

    def test_canonical_id_map_is_read_only(self) -> None:
        source: TzdbDateTimeZoneSource = TzdbDateTimeZoneSource.default
        map_ = source.canonical_id_map
        with pytest.raises(TypeError) as e:
            map_["Foo"] = "Bar"  # type: ignore
        assert str(e.value) == "'mappingproxy' object does not support item assignment"

    def test_zone_locations_contains_france(self) -> None:
        # Sample zone location checks to ensure we've serialized and deserialized correctly
        # Input line: FR	+4852+00220	Europe/Paris
        zone_locations = TzdbDateTimeZoneSource.default.zone_locations
        assert zone_locations
        france = next(g for g in zone_locations if g.country_name == "France")
        # Tolerance of about 2 seconds
        assert france.latitude == pytest.approx(48.86666, abs=0.00055)
        assert france.longitude == pytest.approx(2.3333, abs=0.00055)
        assert france.zone_id == "Europe/Paris"
        assert france.country_code == "FR"
        assert france.comment == ""

    def test_zone_1970_locations_contains_britain(self) -> None:
        # Sample zone location checks to ensure we've serialized and deserialized correctly
        # Input line: GB,GG,IM,JE	+513030-0000731	Europe/London
        zone_locations = TzdbDateTimeZoneSource.default.zone_1970_locations
        assert zone_locations
        britain = next(g for g in zone_locations if g.zone_id == "Europe/London")
        # Tolerance of about 2 seconds
        assert britain.latitude == pytest.approx(51.5083, abs=0.00055)
        assert britain.longitude == pytest.approx(-0.1253, abs=0.00055)
        assert britain.zone_id == "Europe/London"
        assert list(britain.countries) == [
            TzdbZone1970Location.Country("Britain (UK)", "GB"),
            TzdbZone1970Location.Country("Guernsey", "GG"),
            TzdbZone1970Location.Country("Isle of Man", "IM"),
            TzdbZone1970Location.Country("Jersey", "JE"),
        ]
        assert britain.comment == ""

    def test_zone_locations_contains_resolute(self) -> None:
        # Input line: CA	+744144-0944945	America/Resolute	Central - NU (Resolute)
        # (Note: prior to 2016b, this was "Central Time - Resolute, Nunavut".)
        # (Note: prior to 2014f, this was "Central Standard Time - Resolute, Nunavut".)
        zone_locations = TzdbDateTimeZoneSource.default.zone_locations
        assert zone_locations
        resolute = next(g for g in zone_locations if g.zone_id == "America/Resolute")
        # Tolerance of about 2 seconds
        assert resolute.latitude == pytest.approx(74.69555, abs=0.00055)
        assert resolute.longitude == pytest.approx(-94.82916, abs=0.00055)
        assert resolute.country_name == "Canada"
        assert resolute.country_code == "CA"
        assert resolute.comment == "Central - NU (Resolute)"

    def test_tzdb_version(self) -> None:
        source = TzdbDateTimeZoneSource.default
        assert source.tzdb_version.startswith("20")

    def test_fixed_date_time_zone_name(self) -> None:
        zulu = DateTimeZoneProviders.tzdb["Etc/Zulu"]
        assert zulu.get_zone_interval(PyodaConstants.UNIX_EPOCH).name == "UTC"

    def test_version_id(self) -> None:
        source = TzdbDateTimeZoneSource.default
        assert source.version_id.startswith(f"TZDB: {source.tzdb_version}")

    def test_validate_default(self) -> None:
        TzdbDateTimeZoneSource.default.validate()

    # TODO: Skipping over these tests for now as they depend on BCL stuff like TimeZoneInfo
    #  GuessZoneIdByTransitionsUncached
    #  LocalZoneIsNull
    #  MapTimeZoneInfoId

    def test_canonical_id_map_value_is_not_a_key(self) -> None:
        builder = self.__create_sample_builder()
        assert builder._tzdb_id_map is not None  # just to satisfy mypy
        builder._tzdb_id_map["zone3"] = "missing-zone"
        self.__assert_invalid(builder)

    def test_canonical_id_map_value_is_not_canonical(self) -> None:
        builder = self.__create_sample_builder()
        assert builder._tzdb_id_map is not None  # just to satisfy mypy
        builder._tzdb_id_map["zone4"] = "zone3"  # zone3 is an alias for zone1
        self.__assert_invalid(builder)

    def test_windows_mapping_without_primary_territory(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version", "tzdb-version", "windows-version", [MapZone("windows-id", "nonprimary", ["zone1", "zone2"])]
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_primary_territory_not_in_non_primary(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id", "UK", ["zone2"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_uses_missing_id(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id", MapZone.PRIMARY_TERRITORY, ["zone4"]),
                MapZone("windows-id", "UK", ["zone4"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_contains_duplicate_tzdb_ids_same_territory(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id", "UK", ["zone1"]),
                MapZone("windows-id", "CA", ["zone2", "zone2"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_contains_duplicate_tzdb_ids_same_windows_id_different_territory(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id", "UK", ["zone1"]),
                MapZone("windows-id", "CA", ["zone1"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_contains_duplicate_tzdb_ids_different_territories(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id1", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id1", "CA", ["zone1"]),
                MapZone("windows-id2", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id2", "UK", ["zone1"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_contains_windows_id_with_no_primary_territory(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id1", "CA", ["zone1"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_windows_mapping_contains_windows_id_with_duplicate_territories(self) -> None:
        builder = self.__create_sample_builder()
        builder._windows_mapping = WindowsZones._ctor(
            "cldr-version",
            "tzdb-version",
            "windows-version",
            [
                MapZone("windows-id1", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                MapZone("windows-id1", "CA", ["zone2"]),
                MapZone("windows-id1", "CA", ["zone3"]),
            ],
        )
        self.__assert_invalid(builder)

    def test_zone_locations_contains_missing_id(self) -> None:
        builder = self.__create_sample_builder()
        builder._zone_locations = [
            TzdbZoneLocation(0, 0, "country", "xx", "zone4", "comment"),
        ]
        self.__assert_invalid(builder)

    def test_zone_1970_locations_contains_missing_id(self) -> None:
        builder = self.__create_sample_builder()
        builder._zone_1970_locations = [
            TzdbZone1970Location(0, 0, [TzdbZone1970Location.Country("Country", "xx")], "zone4", "comment"),
        ]
        self.__assert_invalid(builder)

    def __create_sample_builder(self) -> _TzdbStreamData._Builder:
        """Creates a sample builder with two canonical zones (zone1 and zone2), and a link from zone3 to zone1.

        There's a single Windows mapping territory, but no zone locations.
        """
        builder = _TzdbStreamData._Builder(
            string_pool=[],
            tzdb_id_map={"zone3": "zone1"},
            tzdb_version="tzdb-version",
            windows_mapping=WindowsZones._ctor(
                "cldr-version",
                "tzdb-version",
                "windows-version",
                [
                    MapZone("windows-id", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                    MapZone("windows-id", "UK", ["zone1"]),
                ],
            ),
        )
        self.__populate_zone_fields(builder, "zone1", "zone2")
        return builder

    def __populate_zone_fields(self, builder: _TzdbStreamData._Builder, *zone_ids: str) -> None:
        for zone_id in zone_ids:
            builder._zone_fields[zone_id] = _TzdbStreamField._ctor(_TzdbStreamFieldId.TIME_ZONE, bytes([0]))

    def __assert_invalid(self, builder: _TzdbStreamData._Builder) -> None:
        stream_data = _TzdbStreamData(builder)
        source = TzdbDateTimeZoneSource._ctor(stream_data)
        with pytest.raises(InvalidPyodaDataError):
            source.validate()

    def test_windows_to_tzdb_ids(self) -> None:
        source = self.__create_complex_mapping_source()
        actual = source.windows_to_tzdb_ids
        expected = {
            "win1": "zone1",
            "win2": "zone2",
            "win3": "zone3",
            "win4": "zone4",
        }
        assert actual == expected

    def test_tzdb_to_windows_ids(self) -> None:
        source = self.__create_complex_mapping_source()
        actual = source.tzdb_to_windows_ids
        expected = {
            "zone1": "win1",
            "link1": "win1",
            "zone2": "win2",
            "link2": "win2",
            # No explicit zone3 mapping; link3a and link3b map to win3 and win4 respectively;
            # link3a "wins" as it's earlier lexicographically.
            "zone3": "win3",
            "link3a": "win3",
            # Explicit mapping to win4 from link3b.
            # This is unusual, but we handle it
            "link3b": "win4",
            # link3c isn't mentioned at all, so we use the canonical ID
            "link3c": "win3",
            "zone4": "win4",
            "zone5": "win4",
            # zone6 isn't mapped at all
        }
        assert actual == expected

    def test_tzdb_to_windows_id_documentation_examples(self) -> None:
        source: TzdbDateTimeZoneSource = TzdbDateTimeZoneSource.default
        kolkata = "Asia/Kolkata"
        calcutta = "Asia/Calcutta"
        india_standard_time = "India Standard Time"

        asmara = "Africa/Asmara"
        east_africa_standard_time = "E. Africa Standard Time"
        nairobi = "Africa/Nairobi"

        # Validate the claims about the source data
        assert source.canonical_id_map[calcutta] == kolkata
        assert kolkata not in itertools.chain(mz.tzdb_ids for mz in source.windows_mapping.map_zones)

        assert source.canonical_id_map[asmara] == nairobi
        assert asmara not in itertools.chain(mz.tzdb_ids for mz in source.windows_mapping.map_zones)

        # And the mappings
        mapping = source.tzdb_to_windows_ids
        assert mapping[kolkata] == india_standard_time
        assert mapping[asmara] == east_africa_standard_time

    def test_utc_mappings(self) -> None:
        """Asserts that [Jon's] commentary is correct in https://github.com/nodatime/nodatime/pull/1393"""
        source: TzdbDateTimeZoneSource = TzdbDateTimeZoneSource.default
        # Note: was Etc/GMT before CLDR v39.
        assert source.windows_to_tzdb_ids["UTC"] == "Etc/UTC"

        assert source.tzdb_to_windows_ids["Etc/UTC"] == "UTC"
        # We follow the link
        assert source.tzdb_to_windows_ids["Etc/GMT+0"] == "UTC"

    def test_windows_to_tzdb_id_documentation_examples(self) -> None:
        source: TzdbDateTimeZoneSource = TzdbDateTimeZoneSource.default
        kolkata = "Asia/Kolkata"
        calcutta = "Asia/Calcutta"
        india_standard_time = "India Standard Time"

        # Validate the claims about the source data
        assert source.canonical_id_map[calcutta] == kolkata
        assert kolkata not in itertools.chain(mz.tzdb_ids for mz in source.windows_mapping.map_zones)

        # And the mapping
        mapping = source.windows_to_tzdb_ids
        assert mapping[india_standard_time] == kolkata

    def __create_complex_mapping_source(self) -> TzdbDateTimeZoneSource:
        """Creates a time zone source with everything required to test the maps between Windows and TZDB IDs.

        Details (not in XML) in the source...
        """
        # Canonical IDs: zone1, zone2, zone3, zone4, zone5, zone6
        # Aliases, linked to the obvious corresponding IDs: link1, link2, link3a, link3b, link3c
        # Windows mappings:
        # win1: zone1 (primary, UK)
        # win2: link2 (primary, UK)
        # win3: link3a (primary, UK)
        # win4: zone4 (primary, UK), zone5 (FR), link3b (CA)
        builder = _TzdbStreamData._Builder(
            string_pool=[],
            tzdb_id_map={
                "link1": "zone1",
                "link2": "zone2",
                "link3a": "zone3",
                "link3b": "zone3",
                "link3c": "zone3",
            },
            tzdb_version="tzdb-version",
            windows_mapping=WindowsZones._ctor(
                "cldr-version",
                "tzdb-version",
                "windows-version",
                [
                    MapZone("win1", MapZone.PRIMARY_TERRITORY, ["zone1"]),
                    MapZone("win1", "UK", ["zone1"]),
                    MapZone("win2", MapZone.PRIMARY_TERRITORY, ["link2"]),
                    MapZone("win2", "UK", ["link2"]),
                    MapZone("win3", MapZone.PRIMARY_TERRITORY, ["link3a"]),
                    MapZone("win3", "UK", ["link3a"]),
                    MapZone("win4", MapZone.PRIMARY_TERRITORY, ["zone4"]),
                    MapZone("win4", "UK", ["zone4"]),
                    MapZone("win4", "FR", ["zone5"]),
                    MapZone("win4", "CA", ["link3b"]),
                ],
            ),
        )
        self.__populate_zone_fields(builder, "zone1", "zone2", "zone3", "zone4", "zone5", "zone6")
        source = TzdbDateTimeZoneSource._ctor(_TzdbStreamData(builder))
        source.validate()
        return source
