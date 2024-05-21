# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.text._format_helper import _FormatHelper
from pyoda_time.utility._csharp_compatibility import _CsharpConstants


class TestFormatHelper:
    @pytest.mark.parametrize(
        "value,length,expected",
        [
            (123, 1, "123"),
            (123, 3, "123"),
            (123, 4, "0123"),
            (123, 5, "00123"),
            (123, 6, "000123"),
            (123, 7, "0000123"),
            (123, 15, "000000000000123"),
            (-123, 1, "-123"),
            (-123, 3, "-123"),
            (-123, 4, "-0123"),
            (-123, 5, "-00123"),
            (-123, 6, "-000123"),
            (-123, 7, "-0000123"),
            (-123, 15, "-000000000000123"),
            (_CsharpConstants.INT_MIN_VALUE, 15, "-000002147483648"),
            (_CsharpConstants.INT_MIN_VALUE, 10, "-2147483648"),
            (_CsharpConstants.INT_MIN_VALUE, 3, "-2147483648"),
        ],
    )
    def test_left_pad(self, value: int, length: int, expected: str) -> None:
        builder = StringBuilder()
        _FormatHelper._left_pad(value, length, builder)
        assert builder.to_string() == expected

    @pytest.mark.parametrize(
        "value,length,expected",
        [
            (123, 1, "123"),
            (123, 3, "123"),
            (123, 4, "0123"),
            (123, 5, "00123"),
            (123, 6, "000123"),
            (123, 7, "0000123"),
            (123, 15, "000000000000123"),
        ],
    )
    def test_left_pad_non_negative_int_64(self, value: int, length: int, expected: str) -> None:
        builder = StringBuilder()
        _FormatHelper._left_pad_non_negative(value, length, builder)
        assert builder.to_string() == expected

    @pytest.mark.parametrize(
        "value,length,scale,expected",
        [
            (1, 3, 3, "001"),
            (1200, 4, 5, "0120"),
            (1, 2, 3, "00"),
        ],
    )
    def test_append_fraction(self, value: int, length: int, scale: int, expected: str) -> None:
        builder = StringBuilder()
        _FormatHelper._append_fraction(value, length, scale, builder)
        assert builder.to_string() == expected

    @pytest.mark.parametrize(
        "initial,value,length,scale,expected",
        [
            ("x", 1, 3, 3, "x001"),
            ("x", 1200, 4, 5, "x012"),
            ("x", 1, 2, 3, "x"),
            ("1.", 1, 2, 3, "1"),
        ],
    )
    def test_append_fraction_truncate(self, initial: str, value: int, length: int, scale: int, expected: str) -> None:
        builder = StringBuilder(initial)
        _FormatHelper._append_fraction_truncate(value, length, scale, builder)
        assert builder.to_string() == expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            (0, "x0"),
            (-1230, "x-1230"),
            (1230, "x1230"),
            (_CsharpConstants.LONG_MIN_VALUE, "x-9223372036854775808"),
        ],
    )
    def test_format_invariant(self, value: int, expected: str) -> None:
        builder = StringBuilder("x")
        _FormatHelper._format_invariant(value, builder)
        assert builder.to_string() == expected
