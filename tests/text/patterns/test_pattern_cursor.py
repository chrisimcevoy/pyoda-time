# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time.text import InvalidPatternError, _TextCursor
from pyoda_time.text.patterns import _PatternCursor

from ..text_cursor_test_base import TextCursorTestBase


class TestPatternCursor(TextCursorTestBase):
    def _make_cursor(self, value: str) -> _TextCursor:
        return _PatternCursor(value)

    @pytest.mark.parametrize(
        "pattern,expected_error_message",
        [
            ("'abc\\", "The format string has an escape character (backslash '\\') at the end of the string."),
            ("'abc", 'The format string is missing the end quote character "\'".'),
        ],
        ids=["Escape at end", "Missing closing quote"],
    )
    def test_get_quoted_string_invalid(self, pattern: str, expected_error_message: str) -> None:
        cursor = _PatternCursor(pattern)
        assert self._get_next_character(cursor) == "'"
        with pytest.raises(InvalidPatternError) as e:
            cursor.get_quoted_string("'")
        assert str(e.value) == expected_error_message

    @pytest.mark.parametrize(
        "pattern,expected",
        [
            ("'abc'", "abc"),
            ("''", ""),
            ("'\"abc\"'", '"abc"'),
            ("'ab\\c'", "abc"),
            ("'ab\\'c'", "ab'c"),
        ],
        ids=["abc", "''", "Double quotes", "Escaped backslash", "Escaped close quote"],
    )
    def test_get_quoted_string_valid(self, pattern: str, expected: str) -> None:
        cursor = _PatternCursor(pattern)
        assert self._get_next_character(cursor) == "'"
        actual = cursor.get_quoted_string("'")
        assert actual == expected
        assert not cursor.move_next()

    def test_get_quoted_string_handles_other_quote(self) -> None:
        cursor = _PatternCursor("[abc]")
        self._get_next_character(cursor)
        actual = cursor.get_quoted_string("]")
        assert actual == "abc"
        assert not cursor.move_next()

    def test_get_quoted_string_not_at_end(self) -> None:
        cursor = _PatternCursor("'abc'more")
        open_quote = self._get_next_character(cursor)
        actual = cursor.get_quoted_string(open_quote)
        assert actual == "abc"
        self._validate_current_character(cursor, 4, "'")
        assert self._get_next_character(cursor) == "m"

    @pytest.mark.parametrize(
        "text,expected_count",
        [
            ("aaa", 3),
            ("a", 1),
            ("aaadaa", 3),
        ],
    )
    def test_get_repeat_count_valid(self, text: str, expected_count: int) -> None:
        cursor = _PatternCursor(text)
        assert cursor.move_next()
        actual = cursor.get_repeat_count(10)
        assert actual == expected_count
        self._validate_current_character(cursor, expected_count - 1, "a")

    def test_get_repeat_count_exceeds_max(self) -> None:
        cursor = _PatternCursor("aaa")
        assert cursor.move_next()
        with pytest.raises(InvalidPatternError) as e:
            cursor.get_repeat_count(2)
        assert (
            str(e.value) == "There were more consecutive copies of the pattern character "
            '"a" than the maximum allowed (2) in the format string.'
        )

    @pytest.mark.parametrize(
        "pattern,expected_embedded",
        [
            ("x<HH:mm>y", "HH:mm"),
            ("x<HH:'T'mm>y", "HH:'T'mm"),
            (r"x<HH:\Tmm>y", r"HH:\Tmm"),
            ("x<a<b>c>y", "a<b>c"),
            ("x<a'<'bc>y", "a'<'bc"),
            ("x<a'>'bc>y", "a'>'bc"),
            (r"x<a\<bc>y", r"a\<bc"),
            (r"x<a\>bc>y", r"a\>bc"),
        ],
        ids=[
            "Simple",
            "Quoting",
            "Escaping",
            "Simple nesting",
            "Quoted start embedded",
            "Quoted end embedded",
            "Escaped start embedded",
            "Escaped end embedded",
        ],
    )
    def test_get_embedded_pattern_valid(self, pattern: str, expected_embedded: str) -> None:
        cursor = _PatternCursor(pattern)
        cursor.move_next()
        embedded: str = cursor.get_embedded_pattern()
        assert embedded == expected_embedded
        self._validate_current_character(cursor, len(expected_embedded) + 2, ">")

    @pytest.mark.parametrize(
        "text,expected_error_message",
        [
            ("x(oops)", "The pattern has an embedded pattern which is missing its opening character ('<')."),
            ("x<oops)", "The pattern has an embedded pattern which is missing its closing character ('>')."),
            (r"x<oops\>", "The pattern has an embedded pattern which is missing its closing character ('>')."),
            ("x<oops'>'", "The pattern has an embedded pattern which is missing its closing character ('>')."),
            ("x<oops<nested>", "The pattern has an embedded pattern which is missing its closing character ('>')."),
        ],
        ids=[
            "Wrong start character",
            "No end",
            "Escaped end",
            "Quoted end",
            "Incomplete after nesting",
        ],
    )
    def test_get_embedded_pattern_invalid(self, text: str, expected_error_message: str) -> None:
        cursor = _PatternCursor(text)
        cursor.move_next()
        with pytest.raises(InvalidPatternError) as e:
            cursor.get_embedded_pattern()
        assert str(e.value) == expected_error_message
