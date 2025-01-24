# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

import pytest

from pyoda_time import CalendarSystem, DateInterval, Instant, LocalDate
from pyoda_time.text import LocalDatePattern


class TestDateInterval:
    JULIAN_CALENDAR: Final[CalendarSystem] = CalendarSystem.julian

    def test_construction_different_calendars(self) -> None:
        start: LocalDate = LocalDate(1600, 1, 1)
        end: LocalDate = LocalDate(1800, 1, 1, self.JULIAN_CALENDAR)
        with pytest.raises(ValueError):  # TODO: ArgumentException
            DateInterval(start, end)

    def test_construction_end_before_start(self) -> None:
        start: LocalDate = LocalDate(1600, 1, 1)
        end: LocalDate = LocalDate(1500, 1, 1)
        with pytest.raises(ValueError):  # TODO: ArgumentException
            DateInterval(start, end)

    def test_equal_start_and_end(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        # In Noda Time this is wrapped in `Assert.DoesNotThrow()`
        DateInterval(start, start)

    def test_construction_properties(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval = DateInterval(start, end)
        assert interval.start == start
        assert interval.end == end

    def test_equals_same_instance(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval = DateInterval(start, end)

        # In Noda Time, this looks a wee bit different owing to the differing types of equality check in C#
        # (Object.Equals(), IEquatable.Equals())
        assert interval == interval  # noqa: PLR0124
        assert hash(interval) == hash(interval)
        assert not (interval != interval)  # noqa: PLR0124
        assert interval is interval  # noqa: PLR0124

    def test_equals_equal_values(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval1 = DateInterval(start, end)
        interval2 = DateInterval(start, end)

        assert interval1.equals(interval2)
        assert hash(interval1) == hash(interval2)
        assert interval1 == interval2
        assert not (interval1 != interval2)

    def test_equals_different_calendars(self) -> None:
        start1: LocalDate = LocalDate(2000, 1, 1)
        end1: LocalDate = LocalDate(2001, 6, 19)
        # This is a really, really similar calendar to ISO, but we do distinguish.
        start2: LocalDate = start1.with_calendar(CalendarSystem.gregorian)
        end2: LocalDate = end1.with_calendar(CalendarSystem.gregorian)
        interval1 = DateInterval(start1, end1)
        interval2 = DateInterval(start2, end2)

        assert not interval1.equals(interval2)
        assert hash(interval1) != hash(interval2)
        assert not (interval1 == interval2)
        assert interval1 != interval2

    def test_equals_different_start(self) -> None:
        start1: LocalDate = LocalDate(2000, 1, 1)
        start2: LocalDate = LocalDate(2001, 1, 2)
        end = LocalDate(2001, 6, 19)
        interval1 = DateInterval(start1, end)
        interval2 = DateInterval(start2, end)

        assert not interval1.equals(interval2)
        assert hash(interval1) != hash(interval2)
        assert not (interval1 == interval2)
        assert interval1 != interval2

    def test_equals_different_end(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end1 = LocalDate(2001, 6, 19)
        end2 = LocalDate(2001, 6, 20)
        interval1 = DateInterval(start, end1)
        interval2 = DateInterval(start, end2)

        assert not interval1.equals(interval2)
        assert hash(interval1) != hash(interval2)
        assert not (interval1 == interval2)
        assert interval1 != interval2

    def test_equals_different_to_null(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval = DateInterval(start, end)

        assert not interval.equals(None)  # type: ignore[arg-type]

    def test_equals_different_to_other_type(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval = DateInterval(start, end)

        assert not interval.equals(Instant.from_unix_time_ticks(0))  # type: ignore[arg-type]

    def test_string_representation(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2001, 6, 19)
        interval = DateInterval(start, end)

        assert str(interval) == "[2000-01-01, 2001-06-19]"

    def test_length(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2000, 2, 10)
        interval = DateInterval(start, end)

        assert len(interval) == 41

    def test_calendar(self) -> None:
        calendar = CalendarSystem.julian
        start: LocalDate = LocalDate(2000, 1, 1, calendar)
        end: LocalDate = LocalDate(2000, 2, 10, calendar)
        interval = DateInterval(start, end)
        assert interval.calendar == calendar

    @pytest.mark.parametrize(
        ("candidate_text", "expected"),
        [
            pytest.param("1999-12-31", False, id="Before start"),
            pytest.param("2000-01-01", True, id="On start"),
            pytest.param("2005-06-06", True, id="In middle"),
            pytest.param("2014-06-30", True, id="On end"),
            pytest.param("2014-07-01", False, id="After end"),
        ],
    )
    def test_contains(self, candidate_text: str, expected: bool) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2014, 6, 30)
        candidate = LocalDatePattern.iso.parse(candidate_text).value
        interval = DateInterval(start, end)
        assert interval.contains(candidate) is expected
        # Different to Noda Time:
        assert (candidate in interval) is expected

    def test_contains_different_calendar(self) -> None:
        start: LocalDate = LocalDate(2000, 1, 1)
        end: LocalDate = LocalDate(2014, 6, 30)
        interval = DateInterval(start, end)
        candidate = LocalDate(2000, 1, 1, self.JULIAN_CALENDAR)
        with pytest.raises(ValueError):
            interval.contains(candidate)
        # Different to Noda Time:
        with pytest.raises(ValueError):
            candidate in interval

    # TODO: def test_deconstruction(self) -> None:

    def test_contains_null_interval_throws(self) -> None:
        start: LocalDate = LocalDate(2017, 11, 6)
        end: LocalDate = LocalDate(2017, 11, 10)
        value = DateInterval(start, end)

        with pytest.raises(TypeError):  # ArgumentNullException in Noda Time
            value.contains(None)  # type: ignore[call-overload]

    def test_contains_interval_within_another_calendar_throws(self) -> None:
        value = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.gregorian),
            LocalDate(2017, 11, 10, CalendarSystem.gregorian),
        )

        other = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.coptic),
            LocalDate(2017, 11, 10, CalendarSystem.coptic),
        )

        with pytest.raises(ValueError):
            value.contains(other)
        # Different to Noda Time:
        with pytest.raises(ValueError):
            other in value

    @pytest.mark.parametrize(
        ("first_interval", "second_interval", "expected_result"),
        [
            ("2014-03-07,2014-03-07", "2014-03-07,2014-03-07", True),
            ("2014-03-07,2014-03-10", "2015-01-01,2015-04-01", False),
            ("2015-01-01,2015-04-01", "2014-03-07,2014-03-10", False),
            ("2014-03-07,2014-03-31", "2014-03-07,2014-03-15", True),
            ("2014-03-07,2014-03-31", "2014-03-10,2014-03-31", True),
            ("2014-03-07,2014-03-31", "2014-03-10,2014-03-15", True),
            ("2014-03-07,2014-03-31", "2014-03-05,2014-03-09", False),
            ("2014-03-07,2014-03-31", "2014-03-20,2014-04-07", False),
            ("2014-11-01,2014-11-30", "2014-01-01,2014-12-31", False),
        ],
    )
    def test_contains_interval_overload(self, first_interval: str, second_interval: str, expected_result: bool) -> None:
        value = self.__parse_interval(first_interval)
        other = self.__parse_interval(second_interval)
        assert value.contains(other) is expected_result
        # Different to Noda Time:
        assert (other in value) is expected_result

    def test_intersection_null_interval_throws(self) -> None:
        value = DateInterval(LocalDate._ctor(days_since_epoch=100), LocalDate._ctor(days_since_epoch=200))
        with pytest.raises(TypeError):  # ArgumentNullException in Noda Time
            value.intersection(None)  # type: ignore[arg-type]
        # Different to Noda Time:
        with pytest.raises(TypeError):
            None & value  # type: ignore[operator]

    def test_intersection_interval_in_different_calendar_throws(self) -> None:
        value = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.gregorian),
            LocalDate(2017, 11, 10, CalendarSystem.gregorian),
        )
        other = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.coptic),
            LocalDate(2017, 11, 10, CalendarSystem.coptic),
        )
        with pytest.raises(ValueError):  # ArgumentException in Noda Time
            value.intersection(other)
        # Different to Noda Time:
        with pytest.raises(ValueError):
            value & other

    @pytest.mark.parametrize(
        ("first_interval", "second_interval", "expected_interval"),
        [
            ("2014-03-07,2014-03-07", "2014-03-07,2014-03-07", "2014-03-07,2014-03-07"),
            ("2014-03-07,2014-03-10", "2015-01-01,2015-04-01", None),
            ("2015-01-01,2015-04-01", "2014-03-07,2014-03-10", None),
            ("2014-03-07,2014-03-31", "2014-03-07,2014-03-15", "2014-03-07,2014-03-15"),
            ("2014-03-07,2014-03-31", "2014-03-10,2014-03-31", "2014-03-10,2014-03-31"),
            ("2014-03-07,2014-03-31", "2014-03-10,2014-03-15", "2014-03-10,2014-03-15"),
            ("2014-03-07,2014-03-31", "2014-03-05,2014-03-09", "2014-03-07,2014-03-09"),
            ("2014-03-07,2014-03-31", "2014-03-20,2014-04-07", "2014-03-20,2014-03-31"),
            ("2014-11-01,2014-11-30", "2014-01-01,2014-12-31", "2014-11-01,2014-11-30"),
        ],
    )
    def test_intersection(self, first_interval: str, second_interval: str, expected_interval: str | None) -> None:
        value = self.__parse_interval(first_interval)
        other = self.__parse_interval(second_interval)
        expected_result = self.__parse_interval_or_none(expected_interval)
        assert value.intersection(other) == expected_result
        # Different to Noda Time:
        assert (value & other) == expected_result

    def test_union_null_interval_throws(self) -> None:
        value = DateInterval(LocalDate._ctor(days_since_epoch=100), LocalDate._ctor(days_since_epoch=200))
        with pytest.raises(TypeError):
            value.union(None)  # type: ignore[arg-type]
        # Different to Noda Time:
        with pytest.raises(TypeError):
            value | None  # type: ignore[operator]

    def test_union_different_calendar_throws(self) -> None:
        value = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.gregorian),
            LocalDate(2017, 11, 10, CalendarSystem.gregorian),
        )
        other = DateInterval(
            LocalDate(2017, 11, 6, CalendarSystem.coptic),
            LocalDate(2017, 11, 10, CalendarSystem.coptic),
        )

        with pytest.raises(ValueError):  # ArgumentException in Noda Time
            value.union(other)
        # Different to Noda Time:
        with pytest.raises(ValueError):
            other | value

    @pytest.mark.parametrize(
        ("first", "second", "expected"),
        [
            pytest.param("2014-03-07,2014-03-20", "2015-03-07,2015-03-20", None, id="Disjointed intervals"),
            pytest.param(
                "2014-03-07,2014-03-20", "2014-03-21,2014-03-30", "2014-03-07,2014-03-30", id="Abutting intervals"
            ),
            pytest.param(
                "2014-03-07,2014-03-20", "2014-03-07,2014-03-20", "2014-03-07,2014-03-20", id="Equal intervals"
            ),
            pytest.param(
                "2014-03-07,2014-03-20", "2014-03-15,2014-03-23", "2014-03-07,2014-03-23", id="Overlapping intervals"
            ),
            pytest.param(
                "2014-03-07,2014-03-20",
                "2014-03-10,2014-03-15",
                "2014-03-07,2014-03-20",
                id="Interval completely contained in another",
            ),
        ],
    )
    def test_union(self, first: str, second: str, expected: str | None) -> None:
        first_interval = self.__parse_interval(first)
        second_interval = self.__parse_interval(second)
        expected_result = self.__parse_interval_or_none(expected)

        assert first_interval.union(second_interval) == expected_result
        assert second_interval.union(first_interval) == expected_result
        # Different to Noda Time:
        assert (first_interval | second_interval) == expected_result
        assert (second_interval | first_interval) == expected_result

    @pytest.mark.parametrize(
        ("interval_text", "expected_date_texts"),
        [
            pytest.param("2018-05-04,2018-05-06", ["2018-05-04", "2018-05-05", "2018-05-06"], id="Multi-day"),
            pytest.param("2018-05-04,2018-05-04", ["2018-05-04"], id="Single date"),
            pytest.param("9999-12-29,9999-12-31", ["9999-12-29", "9999-12-30", "9999-12-31"], id="Max dates"),
        ],
    )
    def test_iteration(self, interval_text: str, expected_date_texts: list[str]) -> None:
        interval = self.__parse_interval(interval_text)
        expected = [LocalDatePattern.iso.parse(x).value for x in expected_date_texts]
        actual = list(interval)
        assert actual == expected

    def __parse_interval_or_none(self, textual_interval: str | None) -> DateInterval | None:
        if textual_interval is None:
            return None
        return self.__parse_interval(textual_interval)

    def __parse_interval(self, textual_interval: str) -> DateInterval:
        parts = textual_interval.split(",")
        start = LocalDatePattern.iso.parse(parts[0]).value
        end = LocalDatePattern.iso.parse(parts[1]).value
        return DateInterval(start, end)
