# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import cast

import helpers
import pytest
from time_zones.io.dtz_io_helper import _DtzIoHelper

from pyoda_time import Duration, Instant, IsoDayOfWeek, LocalTime, Offset, PyodaConstants
from pyoda_time.calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from pyoda_time.time_zones._transition import _Transition
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.utility._csharp_compatibility import _CsharpConstants


class TestZoneRecurrence:
    def test_constructor_null_name_exception(self) -> None:
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        with pytest.raises(TypeError):
            _ZoneRecurrence(cast(str, None), Offset.zero, year_offset, 1971, 2009)

    def test_constructor_null_year_offset_exception(self) -> None:
        with pytest.raises(TypeError):
            _ZoneRecurrence("bob", Offset.zero, cast(_ZoneYearOffset, None), 1971, 2009)

    def test_next_before_first_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._next(Instant.min_value, Offset.zero, Offset.zero)
        expected = _Transition._ctor(PyodaConstants.UNIX_EPOCH, Offset.zero)
        assert actual == expected

    def test_next_first_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._next(PyodaConstants.UNIX_EPOCH, Offset.zero, Offset.zero)
        expected = _Transition._ctor(Instant.from_utc(1971, 1, 1, 0, 0), Offset.zero)
        assert actual == expected

    def test_next_twice_first_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._next(PyodaConstants.UNIX_EPOCH, Offset.zero, Offset.zero)
        assert actual is not None
        actual = recurrence._next(actual._instant, Offset.zero, Offset.zero)
        expected = _Transition._ctor(Instant.from_utc(1972, 1, 1, 0, 0), Offset.zero)
        assert actual == expected

    def test_next_beyond_last_year_null(self) -> None:
        after_recurrence_end = Instant.from_utc(1980, 1, 1, 0, 0)
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._next(after_recurrence_end, Offset.zero, Offset.zero)
        assert actual is None

    def test_previous_or_same_after_last_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._previous_or_same(Instant.max_value, Offset.zero, Offset.zero)
        expected = _Transition._ctor(Instant.from_utc(1972, 1, 1, 0, 0), Offset.zero)
        assert actual == expected

    def test_previous_or_same_last_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._previous_or_same(
            Instant.from_utc(1971, 1, 1, 0, 0) - Duration.epsilon, Offset.zero, Offset.zero
        )
        expected = _Transition._ctor(PyodaConstants.UNIX_EPOCH, Offset.zero)
        assert actual == expected

    def test_previous_or_same_twice_last_year(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._previous_or_same(
            Instant.from_utc(1972, 1, 1, 0, 0) - Duration.epsilon, Offset.zero, Offset.zero
        )
        assert actual is not None
        actual = recurrence._previous_or_same(actual._instant - Duration.epsilon, Offset.zero, Offset.zero)
        expected = _Transition._ctor(PyodaConstants.UNIX_EPOCH, Offset.zero)
        assert actual == expected

    def test_previous_or_same_on_first_year_null(self) -> None:
        # Transition is on January 2nd, but we're asking for January 1st.
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 2, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._previous_or_same(PyodaConstants.UNIX_EPOCH, Offset.zero, Offset.zero)
        assert actual is None

    def test_previous_or_same_before_first_year_null(self) -> None:
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        actual = recurrence._previous_or_same(PyodaConstants.UNIX_EPOCH - Duration.epsilon, Offset.zero, Offset.zero)
        assert actual is None

    def test_next_excludes_given_instant(self) -> None:
        january_10th_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 10, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("x", Offset.zero, january_10th_midnight, 2000, 3000)
        transition = Instant.from_utc(2500, 1, 10, 0, 0)
        next_ = recurrence._next(transition, Offset.zero, Offset.zero)
        assert next_ is not None
        assert next_._instant.in_utc().year == 2501

    def test_previous_or_same_includes_given_instant(self) -> None:
        january_10th_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 10, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("x", Offset.zero, january_10th_midnight, 2000, 3000)
        transition = Instant.from_utc(2500, 1, 10, 0, 0)
        previous_or_same = recurrence._previous_or_same(transition, Offset.zero, Offset.zero)
        assert previous_or_same is not None
        assert previous_or_same._instant == transition

    def test_next_or_fail_fail(self) -> None:
        after_recurrence_end = Instant.from_utc(1980, 1, 1, 0, 0)
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        with pytest.raises(RuntimeError):
            recurrence._next_or_fail(after_recurrence_end, Offset.zero, Offset.zero)

    def test_previous_or_same_or_fail_fail(self) -> None:
        before_recurrence_start = Instant.from_utc(1960, 1, 1, 0, 0)
        january_first_midnight = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        recurrence = _ZoneRecurrence("bob", Offset.zero, january_first_midnight, 1970, 1972)
        with pytest.raises(RuntimeError):
            recurrence._previous_or_same_or_fail(before_recurrence_start, Offset.zero, Offset.zero)

    def test_serialization(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        expected = _ZoneRecurrence("bob", Offset.zero, year_offset, 1971, 2009)
        dio.test_zone_recurrence(expected)

    def test_serialization_infinite(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        expected = _ZoneRecurrence(
            "bob", Offset.zero, year_offset, _CsharpConstants.INT_MIN_VALUE, _CsharpConstants.INT_MAX_VALUE
        )
        dio.test_zone_recurrence(expected)

    def test_iequatable_tests(self) -> None:
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )

        value = _ZoneRecurrence("bob", Offset.zero, year_offset, 1971, 2009)
        equal_value = _ZoneRecurrence("bob", Offset.zero, year_offset, 1971, 2009)
        unequal_value = _ZoneRecurrence("foo", Offset.zero, year_offset, 1971, 2009)

        helpers.test_equals_class(value, equal_value, unequal_value)

    def test_december_31st_2400_max_year_utc_transition(self) -> None:
        # Each year, the transition is at the midnight at the *end* of December 31st...
        year_offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 12, 31, 0, True, LocalTime.midnight, True)
        # ... and the recurrence is valid for the whole of time
        recurrence = _ZoneRecurrence(
            "awkward",
            Offset.from_hours(1),
            year_offset,
            _GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR,
            _GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR,
        )

        next_ = recurrence._next(Instant.from_utc(9999, 6, 1, 0, 0), Offset.zero, Offset.zero)
        assert next_ is not None
        assert next_._instant == Instant._after_max_value()

    def test_december_31st_2400_ask_at_nano_before_last_transition(self) -> None:
        # The transition occurs after the end of the maximum
        # Each year, the transition is at the midnight at the *end* of December 31st...
        year_offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 12, 31, 0, True, LocalTime.midnight, True)
        # ... and the recurrence is valid for the whole of time
        recurrence = _ZoneRecurrence("awkward", Offset.from_hours(1), year_offset, 1, 5000)

        # We can find the final transition
        final_transition = Instant.from_utc(5001, 1, 1, 0, 0)
        next_ = recurrence._next(final_transition - Duration.epsilon, Offset.zero, Offset.zero)
        expected = _Transition._ctor(final_transition, Offset.from_hours(1))
        assert next_ == expected

        # But we correctly reject anything after that
        assert recurrence._next(final_transition, Offset.zero, Offset.zero) is None

    def test_with_name(self) -> None:
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        original = _ZoneRecurrence("original", Offset.from_hours(1), year_offset, 1900, 2000)
        renamed = original._with_name("renamed")
        assert renamed.name == "renamed"
        assert renamed.savings == original.savings
        assert renamed.year_offset == original.year_offset
        assert renamed.from_year == original.from_year
        assert renamed.to_year == original.to_year

    def test_for_single_year(self) -> None:
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        original = _ZoneRecurrence("original", Offset.from_hours(1), year_offset, 1900, 2000)
        single_year = original._for_single_year(2017)
        assert single_year.name == original.name
        assert single_year.savings == original.savings
        assert single_year.year_offset == original.year_offset
        assert single_year.from_year == 2017
        assert single_year.to_year == 2017

    def test_zone_recurrence_to_string(self) -> None:
        year_offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        recurrence = _ZoneRecurrence("name", Offset.from_hours(1), year_offset, 1900, 2000)
        assert (
            str(recurrence) == "name +01 ZoneYearOffset["
            "mode:UTC "
            "monthOfYear:10 "
            "dayOfMonth:31 "
            "dayOfWeek:3 "
            "advance:True "
            "timeOfDay:00:00:00 "
            "addDay:False"
            "] [1900-2000]"
        )
