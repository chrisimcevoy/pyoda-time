# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import cast

import pytest

from pyoda_time import LocalDate, Offset
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text import (
    InvalidPatternError,
    ParseResult,
    UnparsableValueError,
)
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._offset_pattern_parser import _OffsetPatternParser
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_cursor import _TextCursor
from pyoda_time.text._value_cursor import _ValueCursor
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder


class SampleBucket(_ParseBucket[LocalDate]):
    def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[LocalDate]:
        raise NotImplementedError


class TestSteppedPatternBuilder:
    SIMPLE_OFFSET_PATTERN: _IPartialPattern[Offset] = cast(
        _IPartialPattern[Offset], _OffsetPatternParser().parse_pattern("HH:mm", _PyodaFormatInfo.invariant_info)
    )

    def test_parse_partial_valid_in_middle(self) -> None:
        value = _ValueCursor("x17:30y")
        value.move_next()
        value.move_next()
        # Start already looking at the value to parse
        assert value.current == "1"
        result = self.SIMPLE_OFFSET_PATTERN.parse_partial(value)
        assert result.value == Offset.from_hours_and_minutes(17, 30)
        # Finish just after the value
        assert value.current == "y"

    def test_parse_partial_valid_at_end(self) -> None:
        value = _ValueCursor("x17:30")
        value.move_next()
        value.move_next()
        result = self.SIMPLE_OFFSET_PATTERN.parse_partial(value)
        assert result.value == Offset.from_hours_and_minutes(17, 30)
        # Finish just after the value, which in this case is at the end.
        assert value.current == _TextCursor._NUL

    def test_parse_partial_invalid(self) -> None:
        value = _ValueCursor("x17:y")
        value.move_next()
        value.move_next()
        result = self.SIMPLE_OFFSET_PATTERN.parse_partial(value)
        with pytest.raises(UnparsableValueError) as e:
            result.get_value_or_throw()
        assert (
            str(e.value) == 'The value string does not match the required number from the format string "mm". '
            "Value being parsed: 'x17:^y'. (^ indicates error position.)"
        )

    def test_format_only_parsing_fails(self) -> None:
        def format_action(date: LocalDate, sb: StringBuilder) -> None:
            sb.append("Formatted")

        builder = _SteppedPatternBuilder[LocalDate, SampleBucket](_PyodaFormatInfo.invariant_info, SampleBucket)
        builder._add_format_action(format_action)
        builder._set_format_only()
        pattern = builder._build(LocalDate.min_iso_value)

        value = _ValueCursor("xyz")
        result = pattern.parse_partial(value)
        assert result == ParseResult._format_only_pattern
        result = pattern.parse("xyz")
        assert result == ParseResult._format_only_pattern

    def test_append_format(self) -> None:
        builder = StringBuilder("x")
        offset = Offset.from_hours_and_minutes(17, 30)
        self.SIMPLE_OFFSET_PATTERN.append_format(offset, builder)
        assert builder.to_string() == "x17:30"

    @pytest.mark.parametrize(
        "text,valid",
        [("aBaB", True), ("aBAB", False), ("<aBaB", False), ("aBaB>", False)],
        ids=[
            "Valid",
            "Case-sensitive",
            "< is reserved",
            "> is reserved",
        ],
    )
    def test_unhandled_literal(self, text: str, valid: bool) -> None:
        def handler(_: _PatternCursor, __: _SteppedPatternBuilder[LocalDate, SampleBucket]) -> None:
            return None

        handlers = {
            "a": handler,
            "B": handler,
        }
        builder = _SteppedPatternBuilder[LocalDate, SampleBucket](
            _PyodaFormatInfo.invariant_info,
            SampleBucket,
        )
        if valid:
            builder._parse_custom_pattern(text, handlers)
        else:
            with pytest.raises(InvalidPatternError) as e:
                builder._parse_custom_pattern(text, handlers)
            assert str(e.value).startswith("The character ")
            assert str(e.value).endswith(
                "is not a format specifier for this pattern type, and should "
                "be quoted to act as a literal. Note that each type of pattern "
                "has its own set of valid format specifiers."
            )
