# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import Duration, Instant, Interval, LocalDateTime, PyodaConstants
from pyoda_time.text import InstantPattern

from . import helpers

SAMPLE_START = PyodaConstants.UNIX_EPOCH.plus_nanoseconds(-30001)
SAMPLE_END = PyodaConstants.UNIX_EPOCH.plus_nanoseconds(40001)


class TestInterval:
    def test_construction_success(self) -> None:
        interval = Interval(SAMPLE_START, SAMPLE_END)
        assert interval.start == SAMPLE_START
        assert interval.end == SAMPLE_END

    def test_construction_equal_start_and_end(self) -> None:
        interval = Interval(SAMPLE_START, SAMPLE_START)
        assert interval.start == SAMPLE_START
        assert interval.end == SAMPLE_START
        assert interval.duration == Duration.zero

    def test_construction_end_before_start(self) -> None:
        with pytest.raises(ValueError):
            Interval(SAMPLE_END, SAMPLE_START)

    def test_equals(self) -> None:
        helpers.test_equals_struct(
            Interval(SAMPLE_START, SAMPLE_END),
            Interval(SAMPLE_START, SAMPLE_END),
            Interval(PyodaConstants.UNIX_EPOCH, SAMPLE_END),
        )
        helpers.test_equals_struct(
            Interval(None, SAMPLE_END),
            Interval(None, SAMPLE_END),
            Interval(PyodaConstants.UNIX_EPOCH, SAMPLE_END),
        )
        helpers.test_equals_struct(
            Interval(SAMPLE_START, None),
            Interval(SAMPLE_START, None),
            Interval(PyodaConstants.UNIX_EPOCH, SAMPLE_END),
        )
        helpers.test_equals_struct(
            Interval(None, None),
            Interval(None, None),
            Interval(PyodaConstants.UNIX_EPOCH, SAMPLE_END),
        )

    def test_operators(self) -> None:
        helpers.test_operator_equality(
            Interval(SAMPLE_START, SAMPLE_END),
            Interval(SAMPLE_START, SAMPLE_END),
            Interval(PyodaConstants.UNIX_EPOCH, SAMPLE_END),
        )

    def test_duration(self) -> None:
        interval = Interval(SAMPLE_START, SAMPLE_END)
        assert interval.duration == Duration.from_nanoseconds(70002)

    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to a zero duration."""
        actual = Interval()
        assert actual.start == PyodaConstants.UNIX_EPOCH
        assert actual.end == PyodaConstants.UNIX_EPOCH
        assert actual.duration == Duration.zero

    def test_to_string_uses_extended_iso_format(self) -> None:
        start = LocalDateTime(2013, 4, 12, 17, 53, 23).plus_nanoseconds(123456789).in_utc().to_instant()
        end = LocalDateTime(2013, 10, 12, 17, 1, 2, 120).in_utc().to_instant()
        value = Interval(start, end)
        assert str(value) == "2013-04-12T17:53:23.123456789Z/2013-10-12T17:01:02.12Z"

    def test_to_string_infinite(self) -> None:
        value = Interval(None, None)
        assert str(value) == "StartOfTime/EndOfTime"

    # TODO: XmlSerialization tests...?

    @pytest.mark.parametrize(
        "candidate_text,expected_result",
        [
            pytest.param("1990-01-01T00:00:00Z", False, id="Before interval"),
            pytest.param("2000-01-01T00:00:00Z", True, id="Start of interval"),
            pytest.param("2010-01-01T00:00:00Z", True, id="Within interval"),
            pytest.param("2020-01-01T00:00:00Z", False, id="End instant of interval"),
            pytest.param("2030-01-01T00:00:00Z", False, id="After interval"),
        ],
    )
    def test_contains(self, candidate_text: str, expected_result: bool) -> None:
        start = Instant.from_utc(2000, 1, 1, 0, 0)
        end = Instant.from_utc(2020, 1, 1, 0, 0)
        interval = Interval(start, end)
        candidate = InstantPattern.extended_iso.parse(candidate_text).value
        assert interval.contains(candidate) is expected_result
        # This usage is specific to Pyoda Time:
        assert (candidate in interval) is expected_result

    def test_contains_infinite(self) -> None:
        interval = Interval(None, None)
        assert interval.contains(Instant.max_value)
        assert interval.contains(Instant.min_value)
        # This usage is specific to Pyoda Time:
        assert Instant.max_value in interval
        assert Instant.min_value in interval

    def test_has_start(self) -> None:
        assert Interval(Instant.min_value, None).has_start
        assert not Interval(None, Instant.min_value).has_start

    def test_has_end(self) -> None:
        assert Interval(None, Instant.max_value).has_end
        assert not Interval(Instant.max_value, None).has_end

    def test_start(self) -> None:
        assert Interval(PyodaConstants.UNIX_EPOCH, None).start == PyodaConstants.UNIX_EPOCH
        no_start = Interval(None, PyodaConstants.UNIX_EPOCH)
        with pytest.raises(RuntimeError):
            _ = no_start.start

    def test_end(self) -> None:
        assert Interval(None, PyodaConstants.UNIX_EPOCH).end == PyodaConstants.UNIX_EPOCH
        no_end = Interval(PyodaConstants.UNIX_EPOCH, None)
        with pytest.raises(RuntimeError):
            _ = no_end.end

    def test_contains_empty_interval(self) -> None:
        instant = PyodaConstants.UNIX_EPOCH
        interval = Interval(instant, instant)
        assert not interval.contains(instant)
        # This usage is specific to Pyoda Time:
        assert instant not in interval

    def test_contains_empty_interval_max_value(self) -> None:
        instant = Instant.max_value
        interval = Interval(instant, instant)
        assert not interval.contains(instant)
        # This usage is specific to Pyoda Time:
        assert instant not in interval

    def test_deconstruction(self) -> None:
        start = Instant()
        end = start.plus_ticks(1_000_000)
        value = Interval(start, end)

        actual_start, actual_end = value

        assert actual_start == start
        assert actual_end == end

    def test_deconstruction_interval_without_start(self) -> None:
        start = None
        end = Instant._ctor(days=1500, nano_of_day=1_000_000)
        value = Interval(start, end)

        actual_start, actual_end = value

        assert actual_start == start
        assert actual_end == end

    def test_deconstruction_interval_without_end(self) -> None:
        start = Instant._ctor(days=1500, nano_of_day=1_000_000)
        end = None
        value = Interval(start, end)

        actual_start, actual_end = value

        assert actual_start == start
        assert actual_end == end
