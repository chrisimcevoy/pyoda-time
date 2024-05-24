# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import Duration, Instant, Offset, PyodaConstants
from pyoda_time._local_instant import _LocalInstant
from pyoda_time.text._instant_pattern_parser import _InstantPatternParser

from . import helpers


class TestLocalInstant:
    def test_equality(self) -> None:
        equal = _LocalInstant._ctor(days=1, nano_of_day=100)
        different_1 = _LocalInstant._ctor(days=1, nano_of_day=200)
        different_2 = _LocalInstant._ctor(days=2, nano_of_day=100)

        helpers.test_equals_struct(equal, equal, different_1)
        helpers.test_operator_equality(equal, equal, different_1)

        helpers.test_equals_struct(equal, equal, different_2)
        helpers.test_operator_equality(equal, equal, different_2)

    def test_minus_offset_zero_is_neutral_element(self) -> None:
        sample_instant = Instant._ctor(days=1, nano_of_day=23456)
        sample_local_instant = _LocalInstant._ctor(days=1, nano_of_day=23456)
        assert sample_local_instant.minus(Offset.zero) == sample_instant
        assert sample_local_instant._minus_zero_offset() == sample_instant

    @pytest.mark.parametrize(
        "day,nano_of_day,expected_text",
        [
            (0, 0, "1970-01-01T00:00:00 LOC"),
            (0, 1, "1970-01-01T00:00:00.000000001 LOC"),
            (0, 1000, "1970-01-01T00:00:00.000001 LOC"),
            (0, 1000000, "1970-01-01T00:00:00.001 LOC"),
            (-1, PyodaConstants.NANOSECONDS_PER_DAY - 1, "1969-12-31T23:59:59.999999999 LOC"),
        ],
    )
    def test_to_string_valid(self, day: int, nano_of_day: int, expected_text: str) -> None:
        assert str(_LocalInstant._ctor(days=day, nano_of_day=nano_of_day)) == expected_text

    def test_to_string_extremes(self) -> None:
        assert str(_LocalInstant.before_min_value()) == _InstantPatternParser._BEFORE_MIN_VALUE_TEXT
        assert str(_LocalInstant.after_max_value()) == _InstantPatternParser._AFTER_MAX_VALUE_TEXT

    def test_safe_minus_normal_time(self) -> None:
        start = _LocalInstant._ctor(days=0, nano_of_day=0)
        end = start._safe_minus(Offset.from_hours(1))
        assert end._time_since_epoch == Duration.from_hours(-1)

    @pytest.mark.parametrize(
        "initial_offset,offset_to_subtract,final_offset",
        [
            (None, 0, None),
            (None, 1, None),
            (None, -1, None),
            (1, 1, 0),
            (1, 2, None),
            (2, 1, 1),
        ],
    )
    def test_safe_minus_near_start_of_time(
        self, initial_offset: int | None, offset_to_subtract: int, final_offset: int | None
    ) -> None:
        # A null offset indicates "BeforeMinValue". Otherwise, MinValue.Plus(offset)
        start = (
            _LocalInstant.before_min_value()
            if initial_offset is None
            else Instant.min_value._plus(Offset.from_hours(initial_offset))
        )
        expected = (
            Instant._before_min_value()
            if final_offset is None
            else Instant.min_value + Duration.from_hours(final_offset)
        )
        actual = start._safe_minus(Offset.from_hours(offset_to_subtract))
        assert actual == expected

    @pytest.mark.parametrize(
        "initial_offset,offset_to_subtract,final_offset",
        [
            (None, 0, None),
            (None, 1, None),
            (None, -1, None),
            (-1, -1, 0),
            (-1, -2, None),
            (-2, -1, -1),
        ],
    )
    def test_safe_minus_near_end_of_time(
        self, initial_offset: int | None, offset_to_subtract: int, final_offset: int | None
    ) -> None:
        # A null offset indicates "AfterMaxValue". Otherwise, MaxValue.Plus(offset)
        start = (
            _LocalInstant.after_max_value()
            if initial_offset is None
            else Instant.max_value._plus(Offset.from_hours(initial_offset))
        )
        expected = (
            Instant._after_max_value()
            if final_offset is None
            else Instant.max_value + Duration.from_hours(final_offset)
        )
        actual = start._safe_minus(Offset.from_hours(offset_to_subtract))
        assert actual == expected
