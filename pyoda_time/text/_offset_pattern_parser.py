# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from pyoda_time._offset import Offset
from pyoda_time._pyoda_constants import PyodaConstants
from pyoda_time.text import InvalidPatternError, ParseResult
from pyoda_time.text._composite_pattern_builder import CompositePatternBuilder
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from pyoda_time._compatibility._string_builder import StringBuilder
    from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
    from pyoda_time.text._i_pattern import IPattern
    from pyoda_time.text._value_cursor import _ValueCursor
    from pyoda_time.text.patterns._pattern_cursor import _PatternCursor


@_sealed
@final
class _OffsetParseBucket(_ParseBucket[Offset]):
    """Provides a container for the interim parsed pieces of an ``Offset`` value."""

    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0, is_negative: bool = False) -> None:
        # The hours in the range [0, 23].
        self._hours = hours
        # The minutes in the range [0, 59].
        self._minutes = minutes
        # The seconds in the range [0, 59].
        self._seconds = seconds
        # ``True`` if this instance is negative; otherwise, ``False``.
        self._is_negative = is_negative

    def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[Offset]:
        """Calculates the value from the parsed pieces."""
        seconds: int = (
            self._hours * PyodaConstants.SECONDS_PER_HOUR
            + self._minutes * PyodaConstants.SECONDS_PER_MINUTE
            + self._seconds
        )
        if self._is_negative:
            seconds = -seconds
        return ParseResult[Offset].for_value(Offset.from_seconds(seconds))


@_sealed
@final
class _OffsetPatternParser(_IPatternParser[Offset]):
    @staticmethod
    def __get_positive_hours(offset: Offset) -> int:
        return _towards_zero_division(abs(offset.milliseconds), PyodaConstants.MILLISECONDS_PER_HOUR)

    @staticmethod
    def __H_setter(bucket: _ParseBucket[Offset], value: int) -> None:
        assert isinstance(bucket, _OffsetParseBucket)
        bucket._hours = value

    @staticmethod
    def __get_positive_minutes(offset: Offset) -> int:
        return _towards_zero_division(
            _csharp_modulo(abs(offset.milliseconds), PyodaConstants.MILLISECONDS_PER_HOUR),
            PyodaConstants.MILLISECONDS_PER_MINUTE,
        )

    @staticmethod
    def __m_setter(bucket: _ParseBucket[Offset], value: int) -> None:
        assert isinstance(bucket, _OffsetParseBucket)
        bucket._minutes = value

    @staticmethod
    def __get_positive_seconds(offset: Offset) -> int:
        return _towards_zero_division(
            _csharp_modulo(abs(offset.milliseconds), PyodaConstants.MILLISECONDS_PER_MINUTE),
            PyodaConstants.MILLISECONDS_PER_SECOND,
        )

    @staticmethod
    def __s_setter(bucket: _ParseBucket[Offset], value: int) -> None:
        assert isinstance(bucket, _OffsetParseBucket)
        bucket._seconds = value

    @staticmethod
    def __handle_colon(_: _PatternCursor, builder: _SteppedPatternBuilder[Offset]) -> None:
        builder._add_literal(
            expected_text=builder._format_info.time_separator, failure=ParseResult[Offset]._time_separator_mismatch
        )

    @staticmethod
    def __handle_h(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Offset]) -> None:
        raise InvalidPatternError(_TextErrorMessages.HOUR12_PATTERN_NOT_SUPPORTED, Offset.__name__)

    @staticmethod
    def __handle_Z(_: _PatternCursor, __: _SteppedPatternBuilder[Offset]) -> None:
        raise InvalidPatternError(_TextErrorMessages.ZPREFIX_NOT_AT_START_OF_PATTERN)

    @staticmethod
    def __handle_plus(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Offset]) -> None:
        def sign_setter(bucket: _ParseBucket[Offset], positive: bool) -> None:
            assert isinstance(bucket, _OffsetParseBucket)
            bucket._is_negative = not positive

        def non_negative_predicate(offset: Offset) -> bool:
            return offset.milliseconds >= 0

        builder._add_field(_PatternFields.SIGN, pattern.current)
        builder.add_required_sign(sign_setter, non_negative_predicate)

    @staticmethod
    def __handle_minus(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Offset]) -> None:
        def sign_setter(bucket: _ParseBucket[Offset], positive: bool) -> None:
            assert isinstance(bucket, _OffsetParseBucket)
            bucket._is_negative = not positive

        def non_negative_predicate(offset: Offset) -> bool:
            return offset.milliseconds >= 0

        builder._add_field(_PatternFields.SIGN, pattern.current)
        builder.add_negative_only_sign(sign_setter, non_negative_predicate)

    __PATTERN_CHARACTER_HANDLERS: Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[Offset]], None]] = {
        "%": _SteppedPatternBuilder[Offset]._handle_percent,
        "'": _SteppedPatternBuilder[Offset]._handle_quote,
        '"': _SteppedPatternBuilder[Offset]._handle_quote,
        "\\": _SteppedPatternBuilder[Offset]._handle_backslash,
        ":": __handle_colon,
        "h": __handle_h,
        "H": _SteppedPatternBuilder[Offset]._handle_padded_field(
            2, _PatternFields.HOURS_24, 0, 23, __get_positive_hours, __H_setter, Offset
        ),
        "m": _SteppedPatternBuilder[Offset]._handle_padded_field(
            2, _PatternFields.MINUTES, 0, 59, __get_positive_minutes, __m_setter, Offset
        ),
        "s": _SteppedPatternBuilder[Offset]._handle_padded_field(
            2, _PatternFields.SECONDS, 0, 59, __get_positive_seconds, __s_setter, Offset
        ),
        "+": __handle_plus,
        "-": __handle_minus,
        "Z": __handle_Z,
    }

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[Offset]:
        return self.__parse_partial_pattern(pattern, format_info)

    def __parse_partial_pattern(self, pattern_text: str, format_info: _PyodaFormatInfo) -> _IPartialPattern[Offset]:
        # Nullity check is performed in OffsetPattern.
        if len(pattern_text) == 0:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)

        if len(pattern_text) == 1:
            match pattern_text[0]:
                case "g":
                    return CompositePatternBuilder(
                        patterns=[
                            self.__parse_partial_pattern(format_info.offset_pattern_long, format_info),
                            self.__parse_partial_pattern(format_info.offset_pattern_medium, format_info),
                            self.__parse_partial_pattern(format_info.offset_pattern_short, format_info),
                        ],
                        format_predicates=[
                            lambda offset: True,
                            self.__has_zero_seconds,
                            self.__has_zero_seconds_and_minutes,
                        ],
                    )._build_as_partial()
                case "G":
                    return self.__ZPrefixPattern(self.__parse_partial_pattern("g", format_info))
                case "i":
                    return CompositePatternBuilder(
                        patterns=[
                            self.__parse_partial_pattern(format_info.offset_pattern_long_no_punctuation, format_info),
                            self.__parse_partial_pattern(format_info.offset_pattern_medium_no_punctuation, format_info),
                            self.__parse_partial_pattern(format_info.offset_pattern_short_no_punctuation, format_info),
                        ],
                        format_predicates=[
                            lambda offset: True,
                            self.__has_zero_seconds,
                            self.__has_zero_seconds_and_minutes,
                        ],
                    )._build_as_partial()
                case "I":
                    return self.__ZPrefixPattern(self.__parse_partial_pattern("i", format_info))
                case "l":
                    pattern_text = format_info.offset_pattern_long
                case "m":
                    pattern_text = format_info.offset_pattern_medium
                case "s":
                    pattern_text = format_info.offset_pattern_short
                case "L":
                    pattern_text = format_info.offset_pattern_long_no_punctuation
                case "M":
                    pattern_text = format_info.offset_pattern_medium_no_punctuation
                case "S":
                    pattern_text = format_info.offset_pattern_short_no_punctuation
                case _:
                    raise InvalidPatternError(_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern_text, Offset.__name__)

        # This is the only way we'd normally end up in custom parsing land for Z on its own.
        if pattern_text == "%Z":
            raise InvalidPatternError(_TextErrorMessages.EMPTY_ZPREFIXED_OFFSET_PATTERN)

        # Handle Z-prefix by stripping it, parsing the rest as a normal pattern, then building a special pattern
        # which decides whether or not to delegate.
        # Note that patternText is guaranteed not to be empty due to the check at the start.
        # (And assuming we don't add any standard => custom pattern expansions that result in an empty pattern.)
        z_prefix: bool = pattern_text[0] == "Z"

        pattern_builder = _SteppedPatternBuilder[Offset](format_info, _OffsetParseBucket)
        pattern_builder._parse_custom_pattern(
            pattern_text[1:] if z_prefix else pattern_text, self.__PATTERN_CHARACTER_HANDLERS
        )
        # No need to validate field combinations here, but we do need to do something a bit special
        # for Z-handling.
        pattern: _IPartialPattern[Offset] = pattern_builder._build(Offset.from_hours_and_minutes(5, 30))
        return self.__ZPrefixPattern(pattern) if z_prefix else pattern

    @staticmethod
    def __has_zero_seconds(offset: Offset) -> bool:
        """Returns true if the offset is representable just in hours and minutes (no seconds)."""
        return _csharp_modulo(offset.seconds, PyodaConstants.SECONDS_PER_MINUTE) == 0

    @staticmethod
    def __has_zero_seconds_and_minutes(offset: Offset) -> bool:
        """Returns true if the offset is representable just in hours (no minutes or seconds)."""
        return _csharp_modulo(offset.seconds, PyodaConstants.SECONDS_PER_HOUR) == 0

    class __ZPrefixPattern(_IPartialPattern[Offset]):
        """Pattern which optionally delegates to another, but both parses and formats Offset.Zero as "Z"."""

        def __init__(self, full_pattern: _IPartialPattern[Offset]) -> None:
            self.__full_pattern: Final[_IPartialPattern[Offset]] = full_pattern

        def parse(self, text: str) -> ParseResult[Offset]:
            if text == "Z":
                return ParseResult[Offset].for_value(Offset.zero)
            return self.__full_pattern.parse(text)

        def format(self, value: Offset) -> str:
            if value == Offset.zero:
                return "Z"
            return self.__full_pattern.format(value)

        def parse_partial(self, cursor: _ValueCursor) -> ParseResult[Offset]:
            if cursor.current == "Z":
                cursor.move_next()
                return ParseResult[Offset].for_value(Offset.zero)
            return self.__full_pattern.parse_partial(cursor)

        def append_format(self, value: Offset, builder: StringBuilder) -> StringBuilder:
            _Preconditions._check_not_null(builder, "builder")
            if value == Offset.zero:
                return builder.append("Z")
            return self.__full_pattern.append_format(value, builder)
