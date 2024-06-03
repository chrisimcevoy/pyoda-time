# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final, Iterable, cast

import pytest
from testing.single_transition_date_time_zone import SingleTransitionDateTimeZone

from pyoda_time import DateTimeZone, Offset, PyodaConstants
from pyoda_time._date_time_zone_providers import DateTimeZoneProviders
from pyoda_time.time_zones import (
    DateTimeZoneCache,
    DateTimeZoneNotFoundError,
    IDateTimeZoneSource,
    InvalidDateTimeZoneSourceError,
)
from pyoda_time.utility._csharp_compatibility import _csharp_modulo


class DummyDateTimeZoneSource(IDateTimeZoneSource):
    """A dummy ``IDateTimeZoneSource`` for testing purposes.

    In Noda Time, this is called ``TestDateTimeZoneSource``, but that would be misleading here due
    to pytest naming conventions.
    """

    def __init__(self, ids: Iterable[str]) -> None:
        self.__ids: Final[Iterable[str]] = ids
        self.__version_id = "test version"
        self.last_requested_id: str | None = None

    @property
    def version_id(self) -> str:
        return self.__version_id

    @version_id.setter
    def version_id(self, value: str) -> None:
        self.__version_id = value

    def get_ids(self) -> Iterable[str]:
        return self.__ids

    def for_id(self, id_: str) -> DateTimeZone:
        self.last_requested_id = id_

        zone: DateTimeZone = SingleTransitionDateTimeZone(
            PyodaConstants.UNIX_EPOCH,
            Offset.zero,
            Offset.from_hours(_csharp_modulo(hash(id_), 18)),
            id_,
        )

        return zone

    def get_system_default_id(self) -> str | None:
        return "map"


class NoneReturningDummyDateTimeZoneSource(DummyDateTimeZoneSource):
    def for_id(self, id_: str) -> DateTimeZone:
        # Still remember what was requested
        _ = super().for_id(id_)
        return cast(DateTimeZone, None)

    def get_system_default_id(self) -> str | None:
        return None


class TestDateTimeZoneCache:
    """Tests for DateTimeZoneCache."""

    def test_construction_none_provider(self) -> None:
        with pytest.raises(TypeError):
            DateTimeZoneCache(None)  # type: ignore

    def test_invalid_source_none_version_id(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        source.version_id = cast(str, None)

        with pytest.raises(InvalidDateTimeZoneSourceError):
            DateTimeZoneCache(source)

    def test_invalid_source_none_id_sequence(self) -> None:
        source = DummyDateTimeZoneSource(None)  # type: ignore
        with pytest.raises(InvalidDateTimeZoneSourceError):
            DateTimeZoneCache(source)

    def test_invalid_source_returns_none_for_advertised_id(self) -> None:
        source = NoneReturningDummyDateTimeZoneSource(("foo", "bar"))
        cache = DateTimeZoneCache(source)
        with pytest.raises(InvalidDateTimeZoneSourceError):
            cache.get_zone_or_none("foo")

    def test_invalid_provider_none_id_within_sequence(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", cast(str, None)))
        with pytest.raises(InvalidDateTimeZoneSourceError):
            DateTimeZoneCache(source)

    def test_caching_for_present_values(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        zone1a = provider["Test1"]
        assert zone1a
        assert source.last_requested_id == "Test1"

        # Hit up the cache (and thus the source) for Test2
        assert provider["Test2"]
        assert source.last_requested_id == "Test2"

        # Ask for Test1 again
        zone1b = provider["Test1"]
        # We won't have consulted the source again
        assert source.last_requested_id == "Test2"

        assert zone1a is zone1b

    def test_source_is_not_asked_for_utc_if_not_advertised(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        zone = provider[DateTimeZone._UTC_ID]
        assert zone
        assert not source.last_requested_id

    def test_source_is_asked_for_utc_if_advertised(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2", "UTC"))
        provider = DateTimeZoneCache(source)
        zone = provider[DateTimeZone._UTC_ID]
        assert zone
        assert source.last_requested_id == "UTC"

    def test_source_is_not_asked_for_unknown_ids(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        with pytest.raises(DateTimeZoneNotFoundError):
            provider["Unknown"]
        assert not source.last_requested_id

    def test_utc_is_returned_in_ids_if_advertised_by_provider(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2", "UTC"))
        provider = DateTimeZoneCache(source)
        assert DateTimeZone._UTC_ID in provider.ids

    def test_utc_is_not_returned_in_ids_if_not_advertised_by_provider(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        assert DateTimeZone._UTC_ID not in provider.ids

    def test_fixed_offset_succeeds_when_not_advertised(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        id_ = "UTC+05:30"
        zone = provider[id_]
        assert zone == DateTimeZone.for_offset(Offset.from_hours_and_minutes(5, 30))
        assert zone.id == id_
        assert not source.last_requested_id

    def test_fixed_offset_consults_source_when_advertised(self) -> None:
        id_ = "UTC+05:30"
        source = DummyDateTimeZoneSource(("Test1", "Test2", id_))
        provider = DateTimeZoneCache(source)
        zone = provider[id_]
        assert zone.id == id_
        assert source.last_requested_id == id_

    def test_fixed_offset_uncached(self) -> None:
        id_ = "UTC+05:26"
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        zone1 = provider[id_]
        zone2 = provider[id_]
        assert zone1 is not zone2
        assert zone1 == zone2

    def test_fixed_offset_zero_returns_utc(self) -> None:
        id_ = "UTC+00:00"
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        provider = DateTimeZoneCache(source)
        zone = provider[id_]
        assert zone == DateTimeZone.utc
        assert not source.last_requested_id

    def test_tzdb_indexer_invalid_fixed_offset(self) -> None:
        with pytest.raises(DateTimeZoneNotFoundError):
            DateTimeZoneProviders.tzdb["UTC+5Months"]

    def test_null_id_rejected(self) -> None:
        provider = DateTimeZoneCache(DummyDateTimeZoneSource(("Test1", "Test2")))
        with pytest.raises(TypeError):
            provider[cast(str, None)]

    def test_empty_id_accepted(self) -> None:
        provider = DateTimeZoneCache(DummyDateTimeZoneSource(("Test1", "Test2")))
        with pytest.raises(DateTimeZoneNotFoundError):
            provider[""]

    def test_version_id_pass_through(self) -> None:
        source = DummyDateTimeZoneSource(("Test1", "Test2"))
        source.version_id = "foo"
        provider = DateTimeZoneCache(source)

        assert provider.version_id == "foo"

    def test_tzdb_iterate_over_ids(self) -> None:
        """Test for issue 7 in [Noda Time] bug tracker."""

        # According to bug, this would go bang
        count = len(tuple(DateTimeZoneProviders.tzdb.ids))

        assert count > 1
        utc_count = len(tuple(x for x in DateTimeZoneProviders.tzdb.ids if x == DateTimeZone._UTC_ID))
        assert utc_count == 1

    def test_tzdb_indexer_utc_id(self) -> None:
        assert DateTimeZoneProviders.tzdb[DateTimeZone._UTC_ID] == DateTimeZone.utc

    def test_tzdb_indexer_america_los_angeles(self) -> None:
        america_los_angeles = "America/Los_Angeles"
        actual = DateTimeZoneProviders.tzdb[america_los_angeles]
        assert isinstance(actual, DateTimeZone)
        assert actual != DateTimeZone.utc
        assert actual.id == america_los_angeles

    def test_tzdb_ids_all(self) -> None:
        actual = tuple(DateTimeZoneProviders.tzdb.ids)
        actual_count = len(actual)
        assert actual_count > 1
        # TODO: We don't really have a succinct way to emulate LINQ `.Single()` in Python...
        #  There is a redundant assert in the Noda Time code here.
        #  Ported as best I can.
        utc_count = len(tuple(x for x in actual if x == DateTimeZone._UTC_ID))
        assert utc_count == 1

    def test_tzdb_indexer_all_ids(self) -> None:
        """Simply tests that every ID in the built-in database can be fetched.

        This is also
        helpful for diagnostic debugging when we want to check that some potential
        invariant holds for all time zones...
        """
        assert all(DateTimeZoneProviders.tzdb.ids)

    def test_get_system_default_source_returns_null_id(self) -> None:
        source = NoneReturningDummyDateTimeZoneSource(("foo", "bar"))
        cache = DateTimeZoneCache(source)
        with pytest.raises(DateTimeZoneNotFoundError):
            cache.get_system_default()
