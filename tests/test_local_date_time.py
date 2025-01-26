# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from pyoda_time import (
    CalendarSystem,
    DateAdjusters,
    DateTimeZone,
    DateTimeZoneProviders,
    LocalDate,
    LocalDateTime,
    PyodaConstants,
    TimeAdjusters,
)

PACIFIC: DateTimeZone = DateTimeZoneProviders.tzdb["America/Los_Angeles"]


class TestLocalDateTime:
    def test_to_naive_datetime(self) -> None:
        """Equivalent to ``LocalDateTime.ToDateTimeUnspecified()`` in Noda Time."""
        ldt = LocalDateTime(2011, 3, 5, 1, 0, 0)
        expected = datetime(2011, 3, 5, 1, 0, 0)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    def test_to_naive_datetime_julian_calendar(self) -> None:
        ldt = LocalDateTime(2011, 3, 5, 1, 0, 0, calendar=CalendarSystem.julian)
        expected = datetime(2011, 3, 18, 1, 0, 0)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    @pytest.mark.parametrize("year", (100, 1900, 2900))
    def test_to_naive_datetime_truncates_towards_start_of_time(self, year: int) -> None:
        ldt = LocalDateTime(year, 1, 1, 13, 15, 55).plus_nanoseconds(PyodaConstants.NANOSECONDS_PER_SECOND - 1)
        expected = datetime(year, 1, 1, 13, 15, 55) + timedelta(microseconds=PyodaConstants.MICROSECONDS_PER_SECOND - 1)
        actual = ldt.to_naive_datetime()
        assert actual == expected
        assert actual.tzinfo is None

    def test_to_naive_datetime_out_of_range(self) -> None:
        ldt = LocalDate(datetime.min.year, datetime.min.month, datetime.min.day).plus_days(-1).at_midnight()
        with pytest.raises(RuntimeError) as e:
            ldt.to_naive_datetime()
        assert str(e.value) == "LocalDateTime out of range of datetime"

    def test_from_naive_datetime(self) -> None:
        expected = LocalDateTime(2011, 8, 18, 20, 53)
        actual = LocalDateTime.from_naive_datetime(datetime(2011, 8, 18, 20, 53))
        assert actual == expected

    def test_from_naive_datetime_with_calendar(self) -> None:
        # Julian calendar is 13 days behind Gregorian calendar in the 21st century
        expected = LocalDateTime(2011, 8, 5, 20, 53, calendar=CalendarSystem.julian)
        actual = LocalDateTime.from_naive_datetime(datetime(2011, 8, 18, 20, 53), CalendarSystem.julian)
        assert actual == expected

    @pytest.mark.parametrize("tzinfo", (UTC, ZoneInfo("UTC"), ZoneInfo("Europe/London")))
    def test_from_naive_datetime_raises_for_aware_datetime(self, tzinfo: timezone | ZoneInfo) -> None:
        """This test doesn't exist in Noda Time, becase in C# DateTime does not have a tzinfo equivalent."""
        dt = datetime(2024, 6, 4, 23, 5, tzinfo=tzinfo)
        with pytest.raises(ValueError) as e:
            LocalDateTime.from_naive_datetime(dt)
        assert str(e.value) == "Invalid datetime.tzinfo for LocalDateTime.from_datetime_utc"
        assert e.value.__notes__ == ["Parameter name: datetime"]

    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to January 1st 1970, midnight, UTC, ISO calendar."""
        actual = LocalDateTime()
        assert actual == LocalDateTime(1, 1, 1, 0, 0)


class TestLocalDateTimePseudomutators:
    def test_with_time_adjuster(self) -> None:
        start = LocalDateTime(2014, 6, 27, 12, 15, 8).plus_nanoseconds(123456789)
        expected = LocalDateTime(2014, 6, 27, 12, 15, 8)
        assert start.with_time_adjuster(TimeAdjusters.truncate_to_second) == expected

    def test_with_date_adjuster(self) -> None:
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789)
        expected = LocalDateTime(2014, 6, 30, 12, 5, 8).plus_nanoseconds(123456789)
        assert start.with_date_adjuster(DateAdjusters.end_of_month) == expected
