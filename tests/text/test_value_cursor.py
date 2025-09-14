# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time.text import UnparsableValueError
from pyoda_time.text._text_cursor import _TextCursor
from pyoda_time.text._value_cursor import _ValueCursor
from pyoda_time.utility._csharp_compatibility import _CsharpConstants

from .text_cursor_test_base import TextCursorTestBase


class TestValueCursor(TextCursorTestBase):
    def _make_cursor(self, value: str) -> _TextCursor:
        return _ValueCursor(value)

    def test_match_char(self) -> None:
        value = _ValueCursor("abc")
        assert value.move_next()
        assert value._match("a")
        assert value._match("b")
        assert value._match("c")
        assert not value.move_next()

    def test_match_string_not_matched(self) -> None:
        value = _ValueCursor("xabcdef")
        assert value.move_next()
        assert not value._match("abc")
        self._validate_current_character(value, 0, "x")

    def test_match_string_over_long_string_to_match(self) -> None:
        value = _ValueCursor("x")
        assert value.move_next()
        assert not value._match("long string")
        self._validate_current_character(value, 0, "x")

    def test_match_case_insensitive_match_and_move(self) -> None:
        value = _ValueCursor("abcd")
        assert value.move_next()
        assert value._match_case_insensitive("AbC", True)
        self._validate_current_character(value, 3, "d")

    def test_match_case_insensitive_match_without_moving(self) -> None:
        value = _ValueCursor("abcd")
        assert value.move_next()
        assert value._match_case_insensitive("AbC", False)
        self._validate_current_character(value, 0, "a")

    def test_match_case_insensitive_string_not_matched(self) -> None:
        value = _ValueCursor("xabcdef")
        assert value.move_next()
        assert not value._match_case_insensitive("abc", True)
        self._validate_current_character(value, 0, "x")

    def test_match_case_insensitive_string_over_long_string_to_match(self) -> None:
        value = _ValueCursor("x")
        assert value.move_next()
        assert not value._match_case_insensitive("long string", True)
        self._validate_current_character(value, 0, "x")

    def test_match_string_partial(self) -> None:
        value = _ValueCursor("abcdef")
        assert value.move_next()
        assert value._match("abc")
        self._validate_current_character(value, 3, "d")

    def test_parse_digits_too_few_digits(self) -> None:
        value = _ValueCursor("a12b")
        assert value.move_next()
        self._validate_current_character(value, 0, "a")
        assert value.move_next()
        success, _result = value._parse_digits(3, 3)
        assert not success
        self._validate_current_character(value, 1, "1")

    def test_parse_digits_no_number(self) -> None:
        value = _ValueCursor("abc")
        assert value.move_next()
        success, _ = value._parse_digits(1, 2)
        assert not success
        self._validate_current_character(value, 0, "a")

    def test_parse_digits_maximum(self) -> None:
        value = _ValueCursor("12")
        assert value.move_next()
        success, actual = value._parse_digits(1, 2)
        assert success
        assert actual == 12
        self._validate_end_of_string(value)

    def test_parse_digits_maximum_more_digits(self) -> None:
        value = _ValueCursor("1234")
        assert value.move_next()
        success, actual = value._parse_digits(1, 2)
        assert success
        assert actual == 12
        self._validate_current_character(value, 2, "3")

    def test_parse_digits_minimum(self) -> None:
        value = _ValueCursor("1")
        value.move_next()
        success, actual = value._parse_digits(1, 2)
        assert success
        assert actual == 1
        self._validate_end_of_string(value)

    def test_parse_digits_minimum_non_digits(self) -> None:
        value = _ValueCursor("1abc")
        value.move_next()
        success, actual = value._parse_digits(1, 2)
        assert success
        assert actual == 1
        self._validate_current_character(value, 1, "a")

    @pytest.mark.xfail(reason="Unlike in Noda Time, this works...")
    def test_parse_digits_non_ascii_never_matches(self) -> None:
        # Arabic-Indic digits 0 and 1. See
        # https://www.unicode.org/charts/PDF/U0600.pdf
        value = _ValueCursor("\u0660\u0661")
        value.move_next()
        success, actual = value._parse_digits(1, 2)
        assert not success
        assert actual == 1
        self._validate_current_character(value, 1, "a")

    # TODO: There are a bunch of ParseInt64Digits() tests here (as distinct from ParseDigits() tests).
    #  But in Pyoda Time, we only have parse_digits(), because there is only int.
    #  I've omitted most of those as they basically port to duplicate tests.

    def test_parse_int64_digits_large_number(self) -> None:
        value = _ValueCursor("9999999999999")
        assert value.move_next()
        success, actual = value._parse_digits(1, 13)
        assert success
        assert actual == 9999999999999

    def test_parse_fraction_non_ascii_never_matches(self) -> None:
        # Arabic-Indic digits 0 and 1. See
        # https://www.unicode.org/charts/PDF/U0600.pdf
        value = _ValueCursor("\u0660\u0661")
        value.move_next()
        success, _actual = value._parse_fraction(2, 2, 2)
        assert not success

    def test_parse_int64_simple(self) -> None:
        value = _ValueCursor("56x")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is None
        assert int64 == 56

    def test_parse_int64_negative(self) -> None:
        value = _ValueCursor("-56x")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is None
        assert int64 == -56

    def test_parse_int64_non_number(self) -> None:
        value = _ValueCursor("xyz")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 0

    def test_parse_int64_double_negative_sign(self) -> None:
        value = _ValueCursor("--10xyz")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 0

    def test_parse_int64_negative_then_non_digit(self) -> None:
        value = _ValueCursor("-x")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 0

    def test_parse_int64_number_out_of_range_low_leading_digits(self) -> None:
        value = _ValueCursor("1000000000000000000000000")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 1000000000000000000

    def test_parse_int64_number_out_of_range_high_leading_digits(self) -> None:
        value = _ValueCursor("999999999999999999999999")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 999999999999999999

    def test_parse_int64_number_out_of_range_max_value_leading_digits(self) -> None:
        value = _ValueCursor("9223372036854775808")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 922337203685477580

    def test_parse_int64_number_out_of_range_min_value_leading_digits(self) -> None:
        value = _ValueCursor("-9223372036854775809")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is not None
        # Cursor has not moved
        assert value.index == 0
        assert int64 == 922337203685477580

    def test_parse_int64_max_value(self) -> None:
        value = _ValueCursor("9223372036854775807")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        assert parse_result is None
        assert int64 == _CsharpConstants.LONG_MAX_VALUE

    def test_parse_int64_min_value(self) -> None:
        value = _ValueCursor("-9223372036854775808")
        assert value.move_next()
        parse_result, int64 = value._parse_int64()
        if parse_result:
            raise parse_result.exception
        assert parse_result is None
        assert int64 == _CsharpConstants.LONG_MIN_VALUE

    def test_compare_ordinal_exact_match_to_end_of_value(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("abc") == 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_exact_match_value_continues(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("ab") == 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_value_is_earlier(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("mm") < 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_value_is_later(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("aa") > 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_long_match_equal_to_end(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("abcd") < 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_long_match_value_is_earlier(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("cccc") < 0
        assert value.index == 1  # Cursor hasn't moved

    def test_compare_ordinal_long_match_value_is_later(self) -> None:
        value = _ValueCursor("xabc")
        value.move(1)
        assert value._compare_ordinal("aaaa") > 0
        assert value.index == 1  # Cursor hasn't moved

    def test_parse_int64_too_many_digits(self) -> None:
        # We can cope as far as 9223372036854775807, but the trailing 1 causes a failure.
        value = _ValueCursor("92233720368547758071")
        value.move(0)
        parse_result, _int64 = value._parse_int64()
        assert parse_result is not None  # for mypy purposes
        assert not parse_result.success
        assert isinstance(parse_result.exception, UnparsableValueError)
        assert value.index == 0  # Cursor hasn't moved
