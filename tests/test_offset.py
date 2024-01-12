# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from datetime import timedelta
from typing import Final

import pytest

from pyoda_time import (
    Offset,
    PyodaConstants,
)
from tests import helpers

THREE_HOURS: Final[Offset] = helpers.create_positive_offset(3, 0, 0)
NEGATIVE_THREE_HOURS: Final[Offset] = helpers.create_negative_offset(3, 0, 0)
NEGATIVE_TWELVE_HOURS: Final[Offset] = helpers.create_negative_offset(12, 0, 0)


class TestOffset:
    def test_max(self) -> None:
        x = Offset.from_seconds(100)
        y = Offset.from_seconds(200)
        assert Offset.max(x, y) == y
        assert Offset.max(y, x) == y
        assert Offset.max(x, Offset.min_value) == x
        assert Offset.max(Offset.min_value, x) == x
        assert Offset.max(Offset.max_value, x) == Offset.max_value
        assert Offset.max(x, Offset.max_value) == Offset.max_value

    def test_min(self) -> None:
        x = Offset.from_seconds(100)
        y = Offset.from_seconds(200)
        assert Offset.min(x, y) == x
        assert Offset.min(y, x) == x
        assert Offset.min(x, Offset.min_value) == Offset.min_value
        assert Offset.min(Offset.min_value, x) == Offset.min_value
        assert Offset.min(Offset.max_value, x) == x
        assert Offset.min(x, Offset.max_value) == x

    def test_to_timedelta(self) -> None:
        td: timedelta = Offset.from_seconds(1234).to_timedelta()
        assert td == timedelta(seconds=1234)

    @pytest.mark.parametrize("hours", (-24, 24))
    def test_from_timedelta_out_of_range(self, hours: int) -> None:
        td: timedelta = timedelta(hours=hours)
        with pytest.raises(ValueError):
            Offset.from_timedelta(td)

    def test_from_timedelta_truncation(self) -> None:
        td: timedelta = timedelta(milliseconds=1000 + 200)
        assert Offset.from_timedelta(td) == Offset.from_seconds(1)

    def test_from_timedelta_simple(self) -> None:
        td: timedelta = timedelta(hours=2)
        assert Offset.from_timedelta(td) == Offset.from_hours(2)

    def test_default_constructor(self) -> None:
        actual = Offset()
        assert actual == Offset.zero

    # TODO: def test_xml_serialization(self):

    # TODO: def test_xml_serialization_invalid(self):


class TestOffsetConstruction:
    def test_zero(self) -> None:
        test = Offset.zero
        assert test.milliseconds == 0

    def test_from_seconds_valid(self) -> None:
        test = Offset.from_seconds(12345)
        assert test.seconds == 12345

    def test_from_seconds_invalid(self) -> None:
        seconds = 18 * PyodaConstants.SECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_seconds(seconds)
        with pytest.raises(ValueError):
            Offset.from_seconds(-seconds)

    def test_from_milliseconds_valid(self) -> None:
        value = Offset.from_milliseconds(-15 * PyodaConstants.MILLISECONDS_PER_MINUTE)
        assert value.seconds == -15 * PyodaConstants.SECONDS_PER_MINUTE
        assert value.milliseconds == -15 * PyodaConstants.MILLISECONDS_PER_MINUTE

    def test_from_milliseconds_invalid(self) -> None:
        millis = 18 * PyodaConstants.MILLISECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_milliseconds(millis)
        with pytest.raises(ValueError):
            Offset.from_milliseconds(-millis)

    def test_from_ticks_valid(self) -> None:
        value = Offset.from_ticks(-15 * PyodaConstants.TICKS_PER_MINUTE)
        assert value.seconds == -15 * PyodaConstants.SECONDS_PER_MINUTE
        assert value.ticks == -15 * PyodaConstants.TICKS_PER_MINUTE

    def test_from_ticks_invalid(self) -> None:
        ticks = 18 * PyodaConstants.TICKS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_ticks(ticks)
        with pytest.raises(ValueError):
            Offset.from_ticks(-ticks)

    def test_from_nanoseconds_valid(self) -> None:
        value = Offset.from_nanoseconds(-15 * PyodaConstants.NANOSECONDS_PER_MINUTE)
        assert value.seconds == -15 * PyodaConstants.SECONDS_PER_MINUTE
        assert value.nanoseconds == -15 * PyodaConstants.NANOSECONDS_PER_MINUTE

    def test_from_nanoseconds_invalid(self) -> None:
        nanos = 18 * PyodaConstants.NANOSECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_nanoseconds(nanos)
        with pytest.raises(ValueError):
            Offset.from_nanoseconds(-nanos)

    def test_from_hours_valid(self) -> None:
        value = Offset.from_hours(-15)
        assert value.seconds == -15 * PyodaConstants.SECONDS_PER_HOUR

    def test_from_hours_invalid(self) -> None:
        with pytest.raises(ValueError):
            Offset.from_hours(19)
        with pytest.raises(ValueError):
            Offset.from_hours(-19)

    def test_from_hours_and_minutes_valid(self) -> None:
        value = Offset.from_hours_and_minutes(5, 30)
        assert value.seconds == 5 * PyodaConstants.SECONDS_PER_HOUR + 30 * PyodaConstants.SECONDS_PER_MINUTE


class TestOffsetOperators:
    def test_iequatable_icomparable_tests(self) -> None:
        value = Offset.from_seconds(12345)
        equal_value = Offset.from_seconds(12345)
        greater_value = Offset.from_seconds(54321)
        helpers.test_equals(value, equal_value, greater_value)
        helpers.test_compare_to(value, equal_value, greater_value)
        helpers.test_operator_comparison_equality(value, equal_value, greater_value)

    def test_unary_plus_operator(self) -> None:
        assert +Offset.zero == Offset.zero, "+0"
        assert +Offset.from_seconds(1) == Offset.from_seconds(1), "+ 1"
        assert +Offset.from_seconds(-7) == Offset.from_seconds(-7), "+ (-7)"

    def test_negate_operator(self) -> None:
        assert -Offset.zero == Offset.zero, "-0"
        assert -Offset.from_seconds(1) == Offset.from_seconds(-1), "-1"
        assert -Offset.from_seconds(-7) == Offset.from_seconds(7), "- (-7)"

    def test_negate_method(self) -> None:
        assert Offset.negate(Offset.zero) == Offset.zero, "-0"
        assert Offset.negate(Offset.from_seconds(1)) == Offset.from_seconds(-1), "-1"
        assert Offset.negate(Offset.from_seconds(-7)) == Offset.from_seconds(7), "- (-7)"

    # region operator +

    def test_operator_plus_zero_is_neutral_element(self) -> None:
        assert (Offset.zero + Offset.zero).seconds == 0, "0 + 0"
        assert THREE_HOURS + Offset.zero == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS + 0"
        assert Offset.zero + THREE_HOURS == helpers.create_positive_offset(3, 0, 0), "0 + THREE_HOURS"

    def test_operator_plus_non_zero(self) -> None:
        assert THREE_HOURS + THREE_HOURS == helpers.create_positive_offset(6, 0, 0), "THREE_HOURS + THREE_HOURS"
        assert THREE_HOURS + NEGATIVE_THREE_HOURS == Offset.zero, "THREE_HOURS + (-THREE_HOURS)"
        assert NEGATIVE_TWELVE_HOURS + THREE_HOURS == helpers.create_negative_offset(
            9, 0, 0
        ), "-TWELVE_HOURS + THREE_HOURS"

    # Static method equivalents

    def test_method_add_zero_is_neutral_element(self) -> None:
        assert Offset.add(Offset.zero, Offset.zero).milliseconds == 0, "0 + 0"
        assert Offset.add(THREE_HOURS, Offset.zero) == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS + 0"
        assert Offset.add(Offset.zero, THREE_HOURS) == helpers.create_positive_offset(3, 0, 0), "0 + THREE_HOURS"

    def test_method_add_non_zero(self) -> None:
        assert Offset.add(THREE_HOURS, THREE_HOURS) == helpers.create_positive_offset(
            6, 0, 0
        ), "THREE_HOURS + THREE_HOURS"
        assert Offset.add(THREE_HOURS, NEGATIVE_THREE_HOURS) == Offset.zero, "THREE_HOURS + (-THREE_HOURS)"
        assert Offset.add(NEGATIVE_TWELVE_HOURS, THREE_HOURS) == helpers.create_negative_offset(
            9, 0, 0
        ), "-TWELVE_HOURS + THREE_HOURS"

    # Instance method equivalents

    def test_method_plus_zero_is_neutral_element(self) -> None:
        assert Offset.zero.plus(Offset.zero).milliseconds == 0, "0 + 0"
        assert THREE_HOURS.plus(Offset.zero) == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS + 0"
        assert Offset.zero.plus(THREE_HOURS) == helpers.create_positive_offset(3, 0, 0), "0 + THREE_HOURS"

    def test_method_plus_non_zero(self) -> None:
        assert THREE_HOURS.plus(THREE_HOURS) == helpers.create_positive_offset(6, 0, 0), "THREE_HOURS + THREE_HOURS"
        assert THREE_HOURS.plus(NEGATIVE_THREE_HOURS) == Offset.zero, "THREE_HOURS + (-THREE_HOURS)"
        assert NEGATIVE_TWELVE_HOURS.plus(THREE_HOURS) == helpers.create_negative_offset(
            9, 0, 0
        ), "-TWELVE_HOURS + THREE_HOURS"

    # endregion

    # region operator -

    def test_operator_minus_zero_is_neutral_element(self) -> None:
        assert Offset.zero - Offset.zero == Offset.zero, "0 - 0"
        assert THREE_HOURS - Offset.zero == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS - 0"
        assert Offset.zero - THREE_HOURS == helpers.create_negative_offset(3, 0, 0), "0 - THREE_HOURS"

    def test_operator_minus_non_zero(self) -> None:
        assert THREE_HOURS - THREE_HOURS == Offset.zero, "THREE_HOURS - THREE_HOURS"
        assert THREE_HOURS - NEGATIVE_THREE_HOURS == helpers.create_positive_offset(
            6, 0, 0
        ), "THREE_HOURS - (-THREE_HOURS)"
        assert NEGATIVE_TWELVE_HOURS - THREE_HOURS == helpers.create_negative_offset(
            15, 0, 0
        ), "-TWELVE_HOURS - THREE_HOURS"

    # Static method equivalents

    def test_subtract_zero_is_neutral_element(self) -> None:
        assert Offset.subtract(Offset.zero, Offset.zero) == Offset.zero, "0 - 0"
        assert Offset.subtract(THREE_HOURS, Offset.zero) == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS - 0"
        assert Offset.subtract(Offset.zero, THREE_HOURS) == helpers.create_negative_offset(3, 0, 0), "0 - THREE_HOURS"

    def test_subtract_non_zero(self) -> None:
        assert Offset.subtract(THREE_HOURS, THREE_HOURS) == Offset.zero, "THREE_HOURS - THREE_HOURS"
        assert Offset.subtract(THREE_HOURS, NEGATIVE_THREE_HOURS) == helpers.create_positive_offset(
            6, 0, 0
        ), "THREE_HOURS - (-THREE_HOURS)"
        assert Offset.subtract(NEGATIVE_TWELVE_HOURS, THREE_HOURS) == helpers.create_negative_offset(
            15, 0, 0
        ), "-TWELVE_HOURS - THREE_HOURS"

    # Instance method equivalents

    def test_minus_zero_is_neutral_element(self) -> None:
        assert Offset.zero.minus(Offset.zero) == Offset.zero, "0 - 0"
        assert THREE_HOURS.minus(Offset.zero) == helpers.create_positive_offset(3, 0, 0), "THREE_HOURS - 0"
        assert Offset.zero.minus(THREE_HOURS) == helpers.create_negative_offset(3, 0, 0), "0 - THREE_HOURS"

    def test_minus_non_zero(self) -> None:
        assert THREE_HOURS.minus(THREE_HOURS) == Offset.zero, "THREE_HOURS - THREE_HOURS"
        assert THREE_HOURS.minus(NEGATIVE_THREE_HOURS) == helpers.create_positive_offset(
            6, 0, 0
        ), "THREE_HOURS - (-THREE_HOURS)"
        assert NEGATIVE_TWELVE_HOURS.minus(THREE_HOURS) == helpers.create_negative_offset(
            15, 0, 0
        ), "-TWELVE_HOURS - THREE_HOURS"

    # endregion
