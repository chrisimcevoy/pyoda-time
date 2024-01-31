# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
"""https://github.com/nodatime/nodatime/blob/main/src/NodaTime.Test/DurationTest.cs"""
import sys
from datetime import timedelta
from typing import Callable, Final, TypeVar

import pytest

from pyoda_time import Duration, PyodaConstants
from pyoda_time.utility import _CsharpConstants, _towards_zero_division
from tests import helpers

T = TypeVar("T")


class TestDuration:
    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to Duration.Zero."""
        actual = Duration()
        assert Duration.zero == actual

    # TODO: def test_xml_serialization(self) -> None:
    # TODO: def test_xml_serialization_invalid(self) -> None:

    @pytest.mark.parametrize(
        "int64_nanos",
        [
            _CsharpConstants.LONG_MIN_VALUE,
            _CsharpConstants.LONG_MIN_VALUE + 1,
            -PyodaConstants.NANOSECONDS_PER_DAY - 1,
            -PyodaConstants.NANOSECONDS_PER_DAY,
            -PyodaConstants.NANOSECONDS_PER_DAY + 1,
            -1,
            0,
            1,
            PyodaConstants.NANOSECONDS_PER_DAY - 1,
            PyodaConstants.NANOSECONDS_PER_DAY,
            PyodaConstants.NANOSECONDS_PER_DAY + 1,
            _CsharpConstants.LONG_MAX_VALUE - 1,
            _CsharpConstants.LONG_MAX_VALUE,
        ],
    )
    def test_int64_conversions(self, int64_nanos: int) -> None:
        # Note: There is no Duration.ToInt64Nanoseconds() in Pyoda Time.
        nanoseconds = Duration.from_nanoseconds(int64_nanos)
        assert nanoseconds.to_nanoseconds() == int64_nanos

    @pytest.mark.parametrize(
        "int64_nanos",
        [
            _CsharpConstants.LONG_MIN_VALUE,
            _CsharpConstants.LONG_MIN_VALUE + 1,
            -PyodaConstants.NANOSECONDS_PER_DAY - 1,
            -PyodaConstants.NANOSECONDS_PER_DAY,
            -PyodaConstants.NANOSECONDS_PER_DAY + 1,
            -1,
            0,
            1,
            PyodaConstants.NANOSECONDS_PER_DAY - 1,
            PyodaConstants.NANOSECONDS_PER_DAY,
            PyodaConstants.NANOSECONDS_PER_DAY + 1,
            _CsharpConstants.LONG_MAX_VALUE - 1,
            _CsharpConstants.LONG_MAX_VALUE,
        ],
    )
    def test_big_integer_conversions(self, int64_nanos: int) -> None:
        # Note: There is no Duration.ToBigIntegerNanoseconds() in Pyoda Time.
        big_integer_nanos = int64_nanos * 100
        nanoseconds = Duration.from_nanoseconds(big_integer_nanos)
        assert nanoseconds.to_nanoseconds() == big_integer_nanos

    def test_constituent_parts_positive(self) -> None:
        nanos = Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY * 5 + 100)
        assert nanos._floor_days == 5
        assert nanos._nanosecond_of_floor_day == 100

    def test_constituent_parts_negative(self) -> None:
        nanos = Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY * -5 + 100)
        assert nanos._floor_days == -5
        assert nanos._nanosecond_of_floor_day == 100

    def test_constituent_parts_large(self) -> None:
        nanos = Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY * 365000 + 500)
        assert nanos._floor_days == 365000
        assert nanos._nanosecond_of_floor_day == 500

    @pytest.mark.parametrize(
        "left_days,left_nanos,right_days,right_nanos,result_days,result_nanos",
        [
            (1, 100, 2, 200, 3, 300),
            (1, PyodaConstants.NANOSECONDS_PER_DAY - 5, 3, 100, 5, 95),
            (1, 10, -1, PyodaConstants.NANOSECONDS_PER_DAY - 100, 0, PyodaConstants.NANOSECONDS_PER_DAY - 90),
        ],
    )
    def test_addition_subtraction(
        self, left_days: int, left_nanos: int, right_days: int, right_nanos: int, result_days: int, result_nanos: int
    ) -> None:
        left = Duration._ctor(days=left_days, nano_of_day=left_nanos)
        right = Duration._ctor(days=right_days, nano_of_day=right_nanos)
        result = Duration._ctor(days=result_days, nano_of_day=result_nanos)

        assert left + right == result
        assert left.plus(right) == result
        assert Duration.add(left, right) == result

        assert result - right == left
        assert result.minus(right) == left
        assert Duration.subtract(result, right) == left

    def test_equality(self) -> None:
        equal1 = Duration._ctor(days=1, nano_of_day=PyodaConstants.NANOSECONDS_PER_HOUR)
        equal2 = Duration.from_ticks(PyodaConstants.TICKS_PER_HOUR * 25)
        different1 = Duration._ctor(days=1, nano_of_day=200)
        different2 = Duration._ctor(days=2, nano_of_day=PyodaConstants.TICKS_PER_HOUR)

        helpers.test_equals(equal1, equal2, different1)
        helpers.test_operator_equality(equal1, equal2, different1)

        helpers.test_equals(equal1, equal2, different2)
        helpers.test_operator_equality(equal1, equal2, different2)

    def test_comparison(self) -> None:
        equal1 = Duration._ctor(days=1, nano_of_day=PyodaConstants.NANOSECONDS_PER_HOUR)
        equal2 = Duration.from_ticks(PyodaConstants.TICKS_PER_HOUR * 25)
        greater1 = Duration._ctor(days=1, nano_of_day=PyodaConstants.NANOSECONDS_PER_HOUR + 1)
        greater2 = Duration._ctor(days=2, nano_of_day=0)

        helpers.test_compare_to(equal1, equal2, greater1)
        helpers.test_operator_comparison_equality(equal1, equal2, greater1, greater2)

    @pytest.mark.parametrize(
        "start_days,start_nano_of_day,scalar,expected_days,expected_nano_of_day",
        [
            (1, 5, 2, 2, 10),
            (-1, PyodaConstants.NANOSECONDS_PER_DAY - 10, 2, -1, PyodaConstants.NANOSECONDS_PER_DAY - 20),
            (365000, 1, 2, 365000 * 2, 2),
            (1000, 1, 365, 365000, 365),
            (1000, 1, -365, -365001, PyodaConstants.NANOSECONDS_PER_DAY - 365),
            (0, 1, PyodaConstants.NANOSECONDS_PER_DAY, 1, 0),
        ],
        ids=[
            "Small, positive",
            "Small, negative",
            "More than 2^63 nanos before multiplication",
            "More than 2^63 nanos after multiplication",
            "Less than -2^63 nanos after multiplication",
            "Large scalar",
        ],
    )
    def test_multiplication(
        self, start_days: int, start_nano_of_day: int, scalar: int, expected_days: int, expected_nano_of_day: int
    ) -> None:
        start = Duration._ctor(days=start_days, nano_of_day=start_nano_of_day)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert start * scalar == expected

    @pytest.mark.parametrize(
        "start_days,start_nano_of_day,expected_days,expected_nano_of_day",
        [
            (0, 0, 0, 0),
            (1, 0, -1, 0),
            (0, 500, -1, PyodaConstants.NANOSECONDS_PER_DAY - 500),
            (365000, 500, -365001, PyodaConstants.NANOSECONDS_PER_DAY - 500),
        ],
    )
    def test_unary_negation(
        self, start_days: int, start_nano_of_day: int, expected_days: int, expected_nano_of_day: int
    ) -> None:
        start = Duration._ctor(days=start_days, nano_of_day=start_nano_of_day)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert -start == expected
        # Test it the other way round as well
        assert start == -expected

    @pytest.mark.parametrize(
        "start_days,start_nano_of_day,divisor,expected_days,expected_nano_of_day",
        [
            # Test cases around 0
            (-1, PyodaConstants.NANOSECONDS_PER_DAY - 1, PyodaConstants.NANOSECONDS_PER_DAY, 0, 0),
            (0, 0, PyodaConstants.NANOSECONDS_PER_DAY, 0, 0),
            (0, 1, PyodaConstants.NANOSECONDS_PER_DAY, 0, 0),
            # Test cases around dividing -1 day by "nanos per day"
            (
                -2,
                PyodaConstants.NANOSECONDS_PER_DAY - 1,
                PyodaConstants.NANOSECONDS_PER_DAY,
                -1,
                PyodaConstants.NANOSECONDS_PER_DAY - 1,
            ),
            (-1, 0, PyodaConstants.NANOSECONDS_PER_DAY, -1, PyodaConstants.NANOSECONDS_PER_DAY - 1),
            (-1, 1, PyodaConstants.NANOSECONDS_PER_DAY, 0, 0),
            # Test cases around dividing 1 day by "nanos per day"
            (0, PyodaConstants.NANOSECONDS_PER_DAY - 1, PyodaConstants.NANOSECONDS_PER_DAY, 0, 0),
            (1, 0, PyodaConstants.NANOSECONDS_PER_DAY, 0, 1),
            (1, PyodaConstants.NANOSECONDS_PER_DAY - 1, PyodaConstants.NANOSECONDS_PER_DAY, 0, 1),
            (10, 20, 5, 2, 4),
            # Large value, which will use decimal arithmetic
            (365000, 3000, 1000, 365, 3),
        ],
    )
    def test_division(
        self, start_days: int, start_nano_of_day: int, divisor: int, expected_days: int, expected_nano_of_day: int
    ) -> None:
        start = Duration._ctor(days=start_days, nano_of_day=start_nano_of_day)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert start / divisor == expected

    def test_bcl_compatible_ticks_zero(self) -> None:
        assert Duration.from_ticks(0).bcl_compatible_ticks == 0
        assert Duration.from_nanoseconds(99).bcl_compatible_ticks == 0
        assert Duration.from_nanoseconds(-99).bcl_compatible_ticks == 0

    @pytest.mark.parametrize(
        "ticks",
        [
            5,
            PyodaConstants.TICKS_PER_DAY * 2,
            PyodaConstants.TICKS_PER_DAY * 365000,
        ],
    )
    def test_bcl_compatible_ticks_positive(self, ticks: int) -> None:
        assert ticks > 0
        start = Duration.from_ticks(ticks)
        assert start.bcl_compatible_ticks == ticks

        # We truncate towards zero... so subtracting 1 nanosecond should
        # reduce the number of ticks, and adding 99 nanoseconds should not change it
        assert start._minus_small_nanoseconds(1).bcl_compatible_ticks == ticks - 1
        assert start._plus_small_nanoseconds(99).bcl_compatible_ticks == ticks

    @pytest.mark.parametrize(
        "ticks",
        [
            -5,
            -PyodaConstants.TICKS_PER_DAY * 2,
            -PyodaConstants.TICKS_PER_DAY * 365000,
        ],
    )
    def test_bcl_compatible_ticks_negative(self, ticks: int) -> None:
        assert ticks < 0
        start = Duration.from_ticks(ticks)
        assert start.bcl_compatible_ticks == ticks

        # We truncate towards zero... so subtracting 99 nanoseconds should
        # have no effect, and adding 1 should increase the number of ticks
        assert start._minus_small_nanoseconds(99).bcl_compatible_ticks == ticks
        assert start._plus_small_nanoseconds(1).bcl_compatible_ticks == ticks + 1

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_bcl_compatible_ticks_min_value(self) -> None:
        with pytest.raises(OverflowError):
            str(Duration.min_value.bcl_compatible_ticks)

    def test_validation(self) -> None:
        # Different to Noda Time:
        # We use different min/max days in Pyoda Time, with a larger range.
        # The aim is to increase the range sufficiently to accommodate the range of
        # `datetime.timedelta`, which is greater than that of `TimeSpan` in dotnet.
        helpers.assert_valid(Duration.from_days, (1 << 30) - 1)
        helpers.assert_out_of_range(Duration.from_days, 1 << 30)
        helpers.assert_valid(Duration.from_days, -(1 << 30))
        helpers.assert_out_of_range(Duration.from_days, -(1 << 30) - 1)

    @pytest.mark.xfail(reason="Python's dynamic integer size prevents Overflow")
    def test_bcl_compatbile_ticks_overflow(self) -> None:
        max_ticks = Duration.from_ticks(_CsharpConstants.LONG_MAX_VALUE) + Duration.from_ticks(1)
        with pytest.raises(OverflowError):
            str(max_ticks.bcl_compatible_ticks)

    def test_positive_components(self) -> None:
        duration = Duration.from_nanoseconds(1234567890123456)
        assert duration.days == 14
        assert duration.nanosecond_of_day == 24967890123456
        assert duration.hours == 6
        assert duration.minutes == 56
        assert duration.seconds == 7
        assert duration.milliseconds == 890
        assert duration.microseconds == 890123
        assert duration.subsecond_ticks == 8901234
        assert duration.subsecond_nanoseconds == 890123456

    def test_negative_components(self) -> None:
        duration = Duration.from_nanoseconds(-1234567890123456)
        assert duration.days == -14
        assert duration.nanosecond_of_day == -24967890123456
        assert duration.hours == -6
        assert duration.minutes == -56
        assert duration.seconds == -7
        assert duration.milliseconds == -890
        assert duration.microseconds == -890123
        assert duration.subsecond_ticks == -8901234
        assert duration.subsecond_nanoseconds == -890123456

    def test_positive_totals(self) -> None:
        duration = (
            Duration.from_days(4)
            + Duration.from_hours(3)
            + Duration.from_minutes(2)
            + Duration.from_seconds(1)
            + Duration.from_nanoseconds(123456789)
        )
        assert duration.total_days == pytest.approx(4.1264, abs=0.0001)
        assert duration.total_hours == pytest.approx(99.0336, abs=0.0001)
        assert duration.total_minutes == pytest.approx(5942.0187, abs=0.0001)
        assert duration.total_seconds == pytest.approx(356521.123456789, abs=0.000000001)
        assert duration.total_milliseconds == pytest.approx(356521123.456789, abs=0.000001)
        assert duration.total_ticks == pytest.approx(3565211234567.89, abs=0.01)
        assert duration.total_nanoseconds == pytest.approx(356521123456789, abs=1)

    def test_negative_totals(self) -> None:
        duration = (
            Duration.from_days(-4)
            + Duration.from_hours(-3)
            + Duration.from_minutes(-2)
            + Duration.from_seconds(-1)
            + Duration.from_nanoseconds(-123456789)
        )
        assert duration.total_days == pytest.approx(-4.1264, abs=0.0001)
        assert duration.total_hours == pytest.approx(-99.0336, abs=0.0001)
        assert duration.total_minutes == pytest.approx(-5942.0187, abs=0.0001)
        assert duration.total_seconds == pytest.approx(-356521.123456789, abs=0.000000001)
        assert duration.total_milliseconds == pytest.approx(-356521123.456789, abs=0.000001)
        assert duration.total_ticks == pytest.approx(-3565211234567.89, abs=0.01)
        assert duration.total_nanoseconds == pytest.approx(-356521123456789, abs=1)

    def test_max_min_relationship(self) -> None:
        # Max and Min work like they do for other signed types - basically the max value is one less than the absolute
        # of the min value.
        assert -Duration.max_value - Duration.epsilon == Duration.min_value

    def test_max(self) -> None:
        x = Duration.from_nanoseconds(100)
        y = Duration.from_nanoseconds(200)
        assert Duration.max(x, y) == y
        assert Duration.max(y, x) == y
        assert Duration.max(x, Duration.min_value) == x
        assert Duration.max(Duration.min_value, x) == x
        assert Duration.max(Duration.max_value, x) == Duration.max_value
        assert Duration.max(x, Duration.max_value) == Duration.max_value

    def test_min(self) -> None:
        x = Duration.from_nanoseconds(100)
        y = Duration.from_nanoseconds(200)
        assert Duration.min(x, y) == x
        assert Duration.min(y, x) == x
        assert Duration.min(x, Duration.min_value) == Duration.min_value
        assert Duration.min(Duration.min_value, x) == Duration.min_value
        assert Duration.min(Duration.max_value, x) == x
        assert Duration.min(x, Duration.max_value) == x


class TestDurationConstruction:
    """Test cases for factory methods.

    In general, we want to check the limits, very small, very large and medium values, with a mixture of positive and
    negative, "on and off" day boundaries.
    """

    DAY_CASES: Final[list[int]] = [Duration._MIN_DAYS, -3000 * 365, -100, -1, 0, 1, 100, 3000 * 365, Duration._MAX_DAYS]

    HOUR_CASES: Final[list[int]] = [
        Duration._MIN_DAYS * PyodaConstants.HOURS_PER_DAY,
        -3000 * 365 * PyodaConstants.HOURS_PER_DAY,
        -100,
        -48,
        -1,
        0,
        1,
        48,
        100,
        3000 * 365 * PyodaConstants.HOURS_PER_DAY,
        ((Duration._MAX_DAYS + 1) * PyodaConstants.HOURS_PER_DAY) - 1,
    ]

    @staticmethod
    def generate_cases(units_per_day: int) -> list[int]:
        return [
            Duration._MIN_DAYS * units_per_day,
            -3000 * 365 * units_per_day - 1,
            -3000 * 365 * units_per_day,
            _towards_zero_division(-5 * units_per_day, 2),
            -2 * units_per_day - 1,
            0,
            1,
            2 * units_per_day,
            _towards_zero_division(5 * units_per_day, 2),
            3000 * 365 * units_per_day,
            3000 * 365 * units_per_day + 1,
            ((Duration._MAX_DAYS + 1) * units_per_day) - 1,
        ]

    MINUTE_CASES = generate_cases(PyodaConstants.MINUTES_PER_DAY)

    SECOND_CASES = generate_cases(PyodaConstants.SECONDS_PER_DAY)

    MILLISECOND_CASES = generate_cases(PyodaConstants.MILLISECONDS_PER_DAY)

    # Different to Noda Time:
    MICROSECOND_CASES = generate_cases(PyodaConstants.MICROSECONDS_PER_DAY)

    # TODO: Look into this Noda Time comment:
    #  No boundary versions as Int64 doesn't have enough ticks to exceed our limits.
    TICK_CASES = generate_cases(PyodaConstants.TICKS_PER_DAY)[1:-2]

    def test_zero(self) -> None:
        test: Duration = Duration.zero
        assert test.bcl_compatible_ticks == 0
        assert test._nanosecond_of_floor_day == 0
        assert test._floor_days == 0

    @staticmethod
    def __test_factory_method(
        method: Callable[[int], Duration] | Callable[[float], Duration], value: int, nanoseconds_per_unit: int
    ) -> None:
        duration = method(value)
        expected_nanoseconds = value * nanoseconds_per_unit
        assert duration.to_nanoseconds() == expected_nanoseconds

    @pytest.mark.parametrize("days", DAY_CASES)
    def test_from_days_int32(self, days: int) -> None:
        self.__test_factory_method(Duration.from_days, days, PyodaConstants.NANOSECONDS_PER_DAY)

    @pytest.mark.parametrize("hours", HOUR_CASES)
    def test_from_hours_int32(self, hours: int) -> None:
        self.__test_factory_method(Duration.from_hours, hours, PyodaConstants.NANOSECONDS_PER_HOUR)

    @pytest.mark.parametrize("minutes", MINUTE_CASES)
    def test_from_minutes_int64(self, minutes: int) -> None:
        self.__test_factory_method(Duration.from_minutes, minutes, PyodaConstants.NANOSECONDS_PER_MINUTE)

    @pytest.mark.parametrize("seconds", SECOND_CASES)
    def test_from_seconds_int64(self, seconds: int) -> None:
        self.__test_factory_method(Duration.from_seconds, seconds, PyodaConstants.NANOSECONDS_PER_SECOND)

    @pytest.mark.parametrize("milliseconds", MILLISECOND_CASES)
    def test_from_milliseconds_int64(self, milliseconds: int) -> None:
        self.__test_factory_method(Duration.from_milliseconds, milliseconds, PyodaConstants.NANOSECONDS_PER_MILLISECOND)

    @pytest.mark.parametrize("microseconds", MICROSECOND_CASES)
    def test_from_microseconds_int64(self, microseconds: int) -> None:
        self.__test_factory_method(Duration.from_microseconds, microseconds, PyodaConstants.NANOSECONDS_PER_MICROSECOND)

    @pytest.mark.parametrize("ticks", TICK_CASES)
    def test_from_ticks(self, ticks: int) -> None:
        nanoseconds = Duration.from_ticks(ticks)
        assert nanoseconds.to_nanoseconds() == ticks * PyodaConstants.NANOSECONDS_PER_TICK

        # Just another sanity check, although Ticks is covered in more detail later.
        assert nanoseconds.bcl_compatible_ticks == ticks

    @pytest.mark.parametrize(
        "days,expected_days,expected_nano_of_day",
        [
            (1.5, 1, PyodaConstants.NANOSECONDS_PER_DAY / 2),
            (-0.25, -1, 3 * PyodaConstants.NANOSECONDS_PER_DAY / 4),
            (100000.5, 100000, PyodaConstants.NANOSECONDS_PER_DAY / 2),
            (-5000, -5000, 0),
        ],
    )
    def test_from_days_double(self, days: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_days(days)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "hours,expected_days,expected_nano_of_day",
        [
            (36.5, 1, PyodaConstants.NANOSECONDS_PER_DAY / 2 + PyodaConstants.NANOSECONDS_PER_HOUR / 2),
            (-0.25, -1, PyodaConstants.NANOSECONDS_PER_DAY - PyodaConstants.NANOSECONDS_PER_HOUR / 4),
            (24000.5, 1000, PyodaConstants.NANOSECONDS_PER_HOUR / 2),
        ],
    )
    def test_from_hours_double(self, hours: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_hours(hours)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "minutes,expected_days,expected_nano_of_day",
        [
            (
                PyodaConstants.MINUTES_PER_DAY + PyodaConstants.MINUTES_PER_DAY / 2,
                1,
                PyodaConstants.NANOSECONDS_PER_DAY / 2,
            ),
            (1.5, 0, PyodaConstants.NANOSECONDS_PER_SECOND * 90),
            (-PyodaConstants.MINUTES_PER_DAY + 1.5, -1, PyodaConstants.NANOSECONDS_PER_SECOND * 90),
        ],
    )
    def test_from_minutes_double(self, minutes: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_minutes(minutes)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "seconds,expected_days,expected_nano_of_day",
        [
            (
                PyodaConstants.SECONDS_PER_DAY + PyodaConstants.SECONDS_PER_DAY / 2,
                1,
                PyodaConstants.NANOSECONDS_PER_DAY / 2,
            ),
            (1.5, 0, PyodaConstants.NANOSECONDS_PER_MILLISECOND * 1500),
            (-PyodaConstants.SECONDS_PER_DAY + 1.5, -1, PyodaConstants.NANOSECONDS_PER_MILLISECOND * 1500),
        ],
    )
    def test_from_seconds_double(self, seconds: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_seconds(seconds)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "milliseconds,expected_days,expected_nano_of_day",
        [
            (
                PyodaConstants.MILLISECONDS_PER_DAY + PyodaConstants.MILLISECONDS_PER_DAY / 2,
                1,
                PyodaConstants.NANOSECONDS_PER_DAY / 2,
            ),
            (1.5, 0, 1500000),
            (-PyodaConstants.MILLISECONDS_PER_DAY + 1.5, -1, 1500000),
        ],
    )
    def test_from_milliseconds_double(self, milliseconds: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_milliseconds(milliseconds)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "microseconds,expected_days,expected_nano_of_day",
        [
            (
                PyodaConstants.MICROSECONDS_PER_DAY + PyodaConstants.MICROSECONDS_PER_DAY / 2,
                1,
                PyodaConstants.NANOSECONDS_PER_DAY / 2,
            ),
            (1.5, 0, 1500),
            (-PyodaConstants.MICROSECONDS_PER_DAY + 1.5, -1, 1500),
        ],
    )
    def test_from_microseconds_double(self, microseconds: float, expected_days: int, expected_nano_of_day: int) -> None:
        actual = Duration.from_microseconds(microseconds)
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    def test_from_and_to_timedelta(self) -> None:
        """Test conversion to and from ``datetime.timedelta``.

        This is more or less equivalent to the Noda Time test:

        ```
            [Test]
            public void FromAndToTimeSpan() {...}
        ```

        Differences between ``timedelta`` and ``TimeSpan``:

        * ``TimeSpan`` has 100-nanosecond tick precision, whereas ``timedelta`` has microsecond precision.
        * ``timedelta`` can represent a larger range of time than ``TimeSpan``.

        Differences between ``Duration`` implementations in Pyoda Time and Noda Time:

        * Noda Time has a smaller valid range of ``Duration`` than the equivalent class in Pyoda Time.
        * Conversion from e.g ``timedelta.max`` would be impossible with Noda Time's min/max constraints.
        * Pyoda Time's ``Duration`` implementation supports microseconds, Noda Time's does not.
        """

        td = timedelta(hours=3, seconds=2, microseconds=1)
        duration = Duration.from_hours(3) + Duration.from_seconds(2) + Duration.from_microseconds(1)
        assert Duration.from_timedelta(td) == duration
        assert duration.to_timedelta() == td
        assert duration.total_seconds == td.total_seconds()

        max_td_duration = (
            Duration.from_days(timedelta.max.days)
            + Duration.from_seconds(timedelta.max.seconds)
            + Duration.from_microseconds(timedelta.max.microseconds)
        )
        assert Duration.from_timedelta(timedelta.max) == max_td_duration
        assert max_td_duration.to_timedelta() == timedelta.max
        assert (
            max_td_duration.total_microseconds == timedelta.max.total_seconds() * PyodaConstants.MICROSECONDS_PER_SECOND
        )

        min_td_duration = (
            Duration.from_days(timedelta.min.days)
            + Duration.from_seconds(timedelta.min.seconds)
            + Duration.from_microseconds(timedelta.min.microseconds)
        )
        assert Duration.from_timedelta(timedelta.min) == min_td_duration
        assert (
            min_td_duration.total_microseconds == timedelta.min.total_seconds() * PyodaConstants.MICROSECONDS_PER_SECOND
        )
        assert min_td_duration.to_timedelta() == timedelta.min

        # The rest of the test documents how using timedelta.total_seconds() is slightly inaccurate.
        assert timedelta.max.total_seconds() * PyodaConstants.MICROSECONDS_PER_SECOND != (
            timedelta.max.days * PyodaConstants.MICROSECONDS_PER_DAY
            + timedelta.max.seconds * PyodaConstants.MICROSECONDS_PER_SECOND
            + timedelta.max.microseconds
        )
        assert timedelta.min.total_seconds() * PyodaConstants.MICROSECONDS_PER_SECOND != (
            timedelta.min.days * PyodaConstants.MICROSECONDS_PER_DAY
            + timedelta.min.seconds * PyodaConstants.MICROSECONDS_PER_SECOND
            + timedelta.min.microseconds
        )
        assert duration.from_seconds(timedelta.max.total_seconds()) != max_td_duration
        assert duration.from_seconds(timedelta.min.total_seconds()) != min_td_duration

    def test_from_nanoseconds_int64(self) -> None:
        assert Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY - 1) == Duration.one_day - Duration.epsilon
        assert Duration.one_day == Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY)
        assert Duration.one_day + Duration.epsilon == Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY + 1)

        assert -Duration.one_day - Duration.epsilon == Duration.from_nanoseconds(
            -PyodaConstants.NANOSECONDS_PER_DAY - 1
        )
        assert -Duration.one_day == Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY)
        assert -Duration.one_day + Duration.epsilon == Duration.from_nanoseconds(
            -PyodaConstants.NANOSECONDS_PER_DAY + 1
        )

    def test_from_nanoseconds_decimal_limits(self) -> None:
        assert Duration.min_value == Duration._from_nanoseconds(Duration._MIN_DECIMAL_NANOSECONDS)
        assert Duration.max_value == Duration._from_nanoseconds(Duration._MAX_DECIMAL_NANOSECONDS)
        with pytest.raises(ValueError):
            Duration._from_nanoseconds(Duration._MIN_DECIMAL_NANOSECONDS - 1)
        with pytest.raises(ValueError):
            Duration._from_nanoseconds(Duration._MAX_DECIMAL_NANOSECONDS + 1)

    def test_from_nanoseconds_big_integer(self) -> None:
        assert Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY - 1) == Duration.one_day - Duration.epsilon
        assert Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY - 0) == Duration.one_day
        assert Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY + 1) == Duration.one_day + Duration.epsilon

        assert (
            Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY - 1) == -Duration.one_day - Duration.epsilon
        )
        assert Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY - 0) == -Duration.one_day
        assert (
            Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY + 1) == -Duration.one_day + Duration.epsilon
        )

    def test_from_nanoseconds_double(self) -> None:
        assert (
            Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY - 1.0) == Duration.one_day - Duration.epsilon
        )
        assert Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY + 0.0) == Duration.one_day
        assert (
            Duration.from_nanoseconds(PyodaConstants.NANOSECONDS_PER_DAY + 1.0) == Duration.one_day + Duration.epsilon
        )

        assert (
            Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY - 1.0) == -Duration.one_day - Duration.epsilon
        )
        assert Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY + 0.0) == -Duration.one_day
        assert (
            Duration.from_nanoseconds(-PyodaConstants.NANOSECONDS_PER_DAY + 1.0) == -Duration.one_day + Duration.epsilon
        )

        # Checks for values outside the range of long...
        # Find a value which is pretty big, but will definitely still convert back to a positive long.
        large_double_value = (_CsharpConstants.LONG_MAX_VALUE / 16) * 15
        large_int64_value = int(large_double_value)  # This won't be exactly long.MaxValue
        assert Duration.from_nanoseconds(large_double_value + 8.0) == Duration.from_nanoseconds(large_int64_value)

    def test_factory_methods_out_of_range(self) -> None:
        def assert_out_of_range(factory_method: Callable[[T], Duration], *values: T) -> None:
            for value in values:
                with pytest.raises(ValueError):  # TODO ArgumentOutOfRangeException
                    factory_method(value)

        def assert_limits_int32(factory_method: Callable[[int], Duration], all_cases: list[int]) -> None:
            assert_out_of_range(factory_method, all_cases[0] - 1, all_cases[-1] + 1)

        def assert_limits_int64(factory_method: Callable[[int], Duration], all_cases: list[int]) -> None:
            assert_out_of_range(factory_method, all_cases[0] - 1, all_cases[-1] + 1)

        # Each set of cases starts with the minimum and ends with the
        # maximum, so we can test just beyond the limits easily.
        assert_limits_int32(Duration.from_days, self.DAY_CASES)
        assert_limits_int32(Duration.from_hours, self.HOUR_CASES)
        assert_limits_int64(Duration.from_minutes, self.MINUTE_CASES)
        assert_limits_int64(Duration.from_seconds, self.SECOND_CASES)
        assert_limits_int64(Duration.from_milliseconds, self.MILLISECOND_CASES)
        assert_limits_int64(Duration.from_microseconds, self.MICROSECOND_CASES)
        # TODO: Duration.from_ticks(long) doesn't throw in C#, but in Python it probably *should* raise.
        # from_ticks(long) never throws

        big_bad_doubles = [
            float("-inf"),  # double.NegativeInfinity
            # The lowest possible non-infinite float is not `sys.float_info.min`.
            # That merely gives you the "smallest" possible *positive* float.
            # The *lowest* float is actually the negation of the maximum float.
            -sys.float_info.max,  # double.MinValue
            sys.float_info.max,  # double.MaxValue
            float("inf"),  # double.PositiveInfinity
            float("nan"),  # double.NaN
        ]
        assert_out_of_range(Duration.from_days, *big_bad_doubles)
        assert_out_of_range(Duration.from_hours, *big_bad_doubles)
        assert_out_of_range(Duration.from_minutes, *big_bad_doubles)
        assert_out_of_range(Duration.from_seconds, *big_bad_doubles)
        assert_out_of_range(Duration.from_milliseconds, *big_bad_doubles)
        assert_out_of_range(Duration.from_ticks, *big_bad_doubles)
        assert_out_of_range(Duration.from_nanoseconds, *big_bad_doubles)

        # Noda Time has the following comment:
        # No such concept as BigInteger.Min/MaxValue, so use the values we know to be just outside valid bounds.
        assert_out_of_range(Duration.from_nanoseconds, Duration._MIN_NANOSECONDS - 1, Duration._MAX_NANOSECONDS + 1)


class TestDurationOperators:
    THREE_MILLION = Duration.from_nanoseconds(3000000)
    NEGATIVE_FIFTY_MILLION = Duration.from_nanoseconds(-50000000)

    # region operator +

    def test_operator_plus_zero_is_neutral_element(self) -> None:
        assert (Duration.zero + Duration.zero).to_nanoseconds() == 0, "0 + 0"
        assert (Duration.epsilon + Duration.zero).to_nanoseconds() == 1, "1 + 0"
        assert (Duration.zero + Duration.epsilon).to_nanoseconds() == 1, "0 + 1"

    def test_operator_plus_non_zero(self) -> None:
        assert (self.THREE_MILLION + Duration.epsilon).to_nanoseconds() == 3000001, "3,000,000 + 1"
        assert (Duration.epsilon + Duration.from_nanoseconds(-1)).to_nanoseconds() == 0, "1 + (-1)"
        assert (self.NEGATIVE_FIFTY_MILLION + Duration.epsilon).to_nanoseconds() == -49999999, "-50,000,000 + 1"

    def test_operator_plus_method_equivalents(self) -> None:
        x = Duration.from_nanoseconds(100)
        y = Duration.from_nanoseconds(200)
        assert Duration.add(x, y) == x + y
        assert x.plus(y) == x + y

    # endregion

    # region operator -

    def test_operator_minus_zero_is_neutral_element(self) -> None:
        assert (Duration.zero - Duration.zero).to_nanoseconds() == 0, "0 - 0"
        assert (Duration.epsilon - Duration.zero).to_nanoseconds() == 1, "1 - 0"
        assert (Duration.zero - Duration.epsilon).to_nanoseconds() == -1, "0 - 1"

    def test_operator_minus_non_zero(self) -> None:
        negativeEpsilon = Duration.from_nanoseconds(-1)
        assert (self.THREE_MILLION - Duration.epsilon).to_nanoseconds() == 2999999, "3,000,000 - 1"
        assert (Duration.epsilon - negativeEpsilon).to_nanoseconds() == 2, "1 - (-1)"
        assert (self.NEGATIVE_FIFTY_MILLION - Duration.epsilon).to_nanoseconds() == -50000001, "-50,000,000 - 1"

    def test_operator_minus_method_equivalents(self) -> None:
        x = Duration.from_nanoseconds(100)
        y = Duration.from_nanoseconds(200)
        assert Duration.subtract(x, y) == x - y
        assert x.minus(y) == x - y

    # endregion

    # region operator /

    @pytest.mark.parametrize(
        "days,nano_of_day,divisor,expected_days,expected_nano_of_day",
        [
            (1, 0, 2, 0, PyodaConstants.NANOSECONDS_PER_DAY / 2),
            (0, 3000000, 3000, 0, 1000),
            (0, 3000000, 2000000, 0, 1),
            (0, 3000000, -2000000, -1, PyodaConstants.NANOSECONDS_PER_DAY - 1),
        ],
    )
    def test_operator_division_int64(
        self, days: int, nano_of_day: int, divisor: int, expected_days: int, expected_nano_of_day: int
    ) -> None:
        duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        actual = duration / divisor
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "days,nano_of_day,divisor,expected_days,expected_nano_of_day",
        [
            (2, 100, 2.0, 1, 50),
            (2, PyodaConstants.NANOSECONDS_PER_DAY / 2, -0.5, -5, 0),
            (1, 0, 2, 0, PyodaConstants.NANOSECONDS_PER_DAY / 2),
        ],
    )
    def test_operator_division_double(
        self, days: int, nano_of_day: int, divisor: float, expected_days: int, expected_nano_of_day: int
    ) -> None:
        duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        actual = duration / divisor
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nano_of_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "dividend_days,dividend_nano_of_day,divisor_days,divisor_nano_of_day,expected",
        [
            (1, 0, 2, 0, 0.5),
            (1, 0, 0, PyodaConstants.NANOSECONDS_PER_DAY / 2, 2.0),
            (-1, 0, 3, 0, -1 / 3.0),
        ],
    )
    def test_operator_division_duration(
        self,
        dividend_days: int,
        dividend_nano_of_day: int,
        divisor_days: int,
        divisor_nano_of_day: int,
        expected: float,
    ) -> None:
        dividend = Duration._ctor(days=dividend_days, nano_of_day=dividend_nano_of_day)
        divisor = Duration._ctor(days=divisor_days, nano_of_day=divisor_nano_of_day)
        actual = dividend / divisor
        assert actual == expected

    def test_operator_division_by_zero_throws(self) -> None:
        with pytest.raises(ZeroDivisionError):
            str(self.THREE_MILLION / 0.0), "3000000 / 0"
        with pytest.raises(ZeroDivisionError):
            str(self.THREE_MILLION / 0), "3000000 / 0"
        with pytest.raises(ZeroDivisionError):
            str(self.THREE_MILLION / Duration.zero), "3000000 / 0"

    def test_operator_division_method_equivalent(self) -> None:
        assert Duration.divide(self.THREE_MILLION, 2000000) == self.THREE_MILLION / 2000000
        assert Duration.divide(self.THREE_MILLION, 2000000.0) == self.THREE_MILLION / 2000000.0
        assert (
            Duration.divide(self.NEGATIVE_FIFTY_MILLION, self.THREE_MILLION)
            == self.NEGATIVE_FIFTY_MILLION / self.THREE_MILLION
        )

    # endregion

    # region operator *

    @pytest.mark.parametrize(
        "days,nanos,right_operand",
        [
            # "Old" non-zero non-one test cases for posterity's sake.
            (0, 3000, 1000),
            (0, 50000, -1000),
            (0, -50000, 1000),
            (0, -3000, -1000),
            # Zero
            (0, 0, 0),
            (0, 1, 0),
            (0, 3000000, 0),
            (0, -50000000, 0),
            (1, 1, 0),
            (0, 0, 10),
            (0, 0, -10),
            # One
            (0, 3000000, 1),
            (0, 0, 1),
            (0, -5000000, 1),
            # More interesting cases - explore the boundaries of the fast path.
            # This currently assumes that we're optimizing on multiplying "less than 100 days"
            # by less than "about a thousand". There's a comment in the code near that constant
            # to indicate that these tests would need to change if that constant changes.
            (-99, 10000, 800),
            (-101, 10000, 800),
            (-99, 10000, 1234),
            (-101, 10000, 1234),
            (-99, 10000, -800),
            (-101, 10000, -800),
            (-99, 10000, -1234),
            (-101, 10000, -1234),
            (99, 10000, 800),
            (101, 10000, 800),
            (99, 10000, 1234),
            (101, 10000, 1234),
            (99, 10000, -800),
            (101, 10000, -800),
            (99, 10000, -1234),
            (101, 10000, -1234),
        ],
    )
    def test_operator_multiplication_int64(self, days: int, nanos: int, right_operand: int) -> None:
        # Rather than expressing an expected answer, just do a "long-hand" version
        # using ToBigIntegerNanoseconds and FromNanoseconds, trusting those two operations
        # to be correct.
        duration = Duration.from_days(days) + Duration.from_nanoseconds(nanos)
        actual = duration * right_operand

        expected = Duration.from_nanoseconds(duration.to_nanoseconds()) * right_operand
        assert actual == expected

    @pytest.mark.parametrize(
        "days,nanos,right_operand,expected_days,expected_nanos",
        [
            (1, 0, 0.5, 0, PyodaConstants.NANOSECONDS_PER_DAY / 2),
            (1, 200, 2.5, 2, PyodaConstants.NANOSECONDS_PER_DAY / 2 + 500),
            (-2, PyodaConstants.NANOSECONDS_PER_DAY / 2, 2.0, -3, 0),
        ],
    )
    def test_operator_multiplication_double(
        self, days: int, nanos: int, right_operand: int, expected_days: int, expected_nanos: int
    ) -> None:
        start = Duration._ctor(days=days, nano_of_day=nanos)
        actual = start * right_operand
        expected = Duration._ctor(days=expected_days, nano_of_day=expected_nanos)
        assert actual == expected
        actual = right_operand * start
        assert actual == expected

    def test_commutation(self) -> None:
        assert 5 * self.THREE_MILLION == self.THREE_MILLION * 5
        assert 5.5 * self.THREE_MILLION == self.THREE_MILLION * 5.5

    def test_operator_multiplication_method_equivalents(self) -> None:
        assert Duration.from_nanoseconds(-50000) * 1000 == Duration.multiply(Duration.from_nanoseconds(-50000), 1000)
        assert 1000 * Duration.from_nanoseconds(-50000) == Duration.multiply(1000, Duration.from_nanoseconds(-50000))
        assert Duration.from_nanoseconds(-50000) * 1000.0 == Duration.multiply(
            Duration.from_nanoseconds(-50000), 1000.0
        )
        assert 1000.0 * Duration.from_nanoseconds(-50000) == Duration.multiply(
            1000.0, Duration.from_nanoseconds(-50000)
        )

    # endregion

    def test_unary_minus_and_negate(self) -> None:
        start = Duration.from_nanoseconds(5000)
        expected = Duration.from_nanoseconds(-5000)
        assert -start == expected
        assert Duration.negate(start) == expected
