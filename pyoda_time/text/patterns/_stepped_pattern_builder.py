# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import (
    Callable,
    Final,
    Generic,
    Mapping,
    Protocol,
    TypeVar,
    final,
    runtime_checkable,
)

from ..._compatibility._string_builder import StringBuilder
from ...globalization import _PyodaFormatInfo
from ...utility import _Preconditions, _sealed
from .. import InvalidPatternError, ParseResult, _ParseBucket, _ValueCursor
from .._format_helper import FormatHelper
from .._i_partial_pattern import _IPartialPattern
from .._text_error_messages import TextErrorMessages
from . import _PatternCursor, _PatternFields

TResult = TypeVar("TResult")
TBucket = TypeVar("TBucket", bound="_ParseBucket")


@_sealed
@final
class _SteppedPatternBuilder(Generic[TResult, TBucket]):
    """Builder for a pattern which implements parsing and formatting as a sequence of steps applied in turn."""

    @property
    def _format_info(self) -> _PyodaFormatInfo:
        return self.__format_info

    @property
    def _used_fields(self) -> _PatternFields:
        return self.__used_fields

    def __init__(self, format_info: _PyodaFormatInfo, bucket_provider: Callable[[], TBucket]) -> None:
        self.__format_info: Final[_PyodaFormatInfo] = format_info
        self.__format_actions: Final[list[Callable[[TResult, StringBuilder], None]]] = []
        self.__parse_actions: Final[list[Callable[[_ValueCursor, TBucket], ParseResult[TResult] | None]]] = []
        self.__bucket_provider: Final[Callable[[], TBucket]] = bucket_provider
        self.__used_fields: _PatternFields = _PatternFields.NONE
        self.__format_only: bool = False

    def _create_sample_bucket(self) -> TBucket:
        """Calls the bucket provider and returns a sample bucket.

        This means that any values normally propagated via the bucket can also be used when building the pattern.
        """
        return self.__bucket_provider()

    def _set_format_only(self) -> None:
        """Sets this pattern to only be capable of formatting; any attempt to parse using the built pattern will fail
        immediately."""
        self.__format_only = True

    def _parse_custom_pattern(
        self,
        pattern_text: str,
        character_handlers: Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[TResult, TBucket]], None]],
    ) -> None:
        """Performs common parsing operations: start with a parse action to move the
        value cursor onto the first character, then call a character handler for each
        character in the pattern to build up the steps. If any handler fails,
        that failure is returned - otherwise the return value is null.
        """
        pattern_cursor = _PatternCursor(pattern_text)

        while pattern_cursor.move_next():
            if handler := character_handlers.get(pattern_cursor.current):
                handler(pattern_cursor, self)
            else:
                current = pattern_cursor.current
                if (
                    (ord("A") <= ord(current) <= ord("Z"))
                    or (ord("a") <= ord(current) <= ord("z"))
                    or current == _PatternCursor._EMBEDDED_PATTERN_START
                    or current == _PatternCursor._EMBEDDED_PATTERN_END
                ):
                    raise InvalidPatternError(TextErrorMessages.UNQUOTED_LITERAL, current)

                def failure(cursor: _ValueCursor) -> ParseResult[TResult]:
                    return ParseResult._mismatched_character(cursor, current)

                self._add_literal(current, failure)

    def _validate_used_fields(self) -> None:
        """Validates the combination of fields used."""

        # We assume invalid combinations are global across all parsers. The way that
        # the patterns are parsed ensures we never end up with any invalid individual fields
        # (e.g. time fields within a date pattern).

        if (self.__used_fields & (_PatternFields.ERA | _PatternFields.YEAR_OF_ERA)) == _PatternFields.ERA:
            raise InvalidPatternError(TextErrorMessages.ERA_WITHOUT_YEAR_OF_ERA)
        calendar_and_era: Final[_PatternFields] = _PatternFields.ERA | _PatternFields.CALENDAR
        if (self.__used_fields & calendar_and_era) == calendar_and_era:
            raise InvalidPatternError(TextErrorMessages.CALENDAR_AND_ERA)

    def _build(self, sample: TResult) -> _IPartialPattern[TResult]:
        """Returns a built pattern.

        This is mostly to keep the API for the builder separate from that of the pattern, and for thread safety
        (publishing a new object, thus leading to a memory barrier). Note that this builder *must not* be used after the
        result has been built.
        """
        # If we've got an embedded date and any *other* date fields, throw.
        if self.__used_fields.has_any(_PatternFields.EMBEDDED_DATE) and self._used_fields.has_any(
            _PatternFields.ALL_DATE_FIELDS & ~_PatternFields.EMBEDDED_DATE
        ):
            raise InvalidPatternError(TextErrorMessages.DATE_FIELD_AND_EMBEDDED_DATE)
        # Ditto for time
        if self.__used_fields.has_any(_PatternFields.EMBEDDED_TIME) and self._used_fields.has_any(
            _PatternFields.ALL_TIME_FIELDS & ~_PatternFields.EMBEDDED_TIME
        ):
            raise InvalidPatternError(TextErrorMessages.TIME_FIELD_AND_EMBEDDED_TIME)

        delegates = []

        for format_action in self.__format_actions:
            # TODO: Figure out how to port multicast delegate
            # TODO: Consider using hasattr() instead of isinstance().
            #  The python docs say isinstance() is markedly slower with runtime_checkable Protocols.
            if isinstance(format_action, self._IPostPatternParseFormatAction):
                delegates.append(format_action.build_format_action(self.__used_fields))
            else:
                delegates.append(format_action)

        def multicast_delegate(result: TResult, sb: StringBuilder) -> None:
            for d in delegates:
                d(result, sb)

        return self.__SteppedPattern(
            format_actions=multicast_delegate,
            parse_actions=None if self.__format_only else self.__parse_actions,
            bucket_provider=self.__bucket_provider,
            used_fields=self.__used_fields,
            sample=sample,
        )

    def _add_field(self, field: _PatternFields, character_in_pattern: str) -> None:
        """Registers that a pattern field has been used in this pattern, and throws a suitable error result if it's
        already been used."""
        new_used_fields = self.__used_fields | field
        if new_used_fields == self.__used_fields:
            raise InvalidPatternError(TextErrorMessages.REPEATED_FIELD_IN_PATTERN, character_in_pattern)
        self.__used_fields = new_used_fields

    def _add_parse_action(self, parse_action: Callable[[_ValueCursor, TBucket], ParseResult[TResult] | None]) -> None:
        self.__parse_actions.append(parse_action)

    def _add_format_action(self, format_action: Callable[[TResult, StringBuilder], None]) -> None:
        self.__format_actions.append(format_action)

    def _add_parse_value_action(
        self,
        minimum_digits: int,
        maximum_digits: int,
        pattern_char: str,
        minimum_value: int,
        maximum_value: int,
        value_setter: Callable[[TBucket, int], None],
        type_: type[TResult],
    ) -> None:
        def parse_value_action(cursor: _ValueCursor, bucket: TBucket) -> ParseResult[TResult] | None:
            starting_index = cursor.index
            negative = cursor._match("-")
            if negative and minimum_value >= 0:
                cursor.move(starting_index)
                return ParseResult[TResult]._unexpected_negative(cursor)
            success, value = cursor._parse_digits(minimum_digits, maximum_digits)
            if not success:
                cursor.move(starting_index)
                return ParseResult._mismatched_number(cursor, pattern_char * minimum_digits)
            if negative:
                value = -value
            if value < minimum_value or value > maximum_value:
                cursor.move(starting_index)
                return ParseResult[TResult]._field_value_out_of_range(cursor, value, pattern_char, type_)

            value_setter(bucket, value)
            return None

        self._add_parse_action(parse_value_action)

    def _add_literal(self, expected_text: str, failure: Callable[[_ValueCursor], ParseResult[TResult]], /) -> None:
        """Adds text which must be matched exactly when parsing, and appended directly when formatting."""

        def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
            if cursor._match(expected_text):
                return None
            return failure(cursor)

        def format_action(value: TResult, builder: StringBuilder) -> None:
            builder.append(expected_text)

        self._add_parse_action(parse_action)
        self._add_format_action(format_action)
        return

    @classmethod
    def _handle_quote(cls, pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult, TBucket]) -> None:
        quoted: str = pattern.get_quoted_string(pattern.current)
        builder._add_literal(quoted, ParseResult[TResult]._quoted_string_mismatch)

    @classmethod
    def _handle_backslash(cls, pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult, TBucket]) -> None:
        if not pattern.move_next():
            raise InvalidPatternError(TextErrorMessages.ESCAPE_AT_END_OF_STRING)

        current = pattern.current

        def failure(cursor: _ValueCursor) -> ParseResult[TResult]:
            return ParseResult[TResult]._escaped_character_missmatch(cursor, current)

        builder._add_literal(pattern.current, failure)

    @classmethod
    def _handle_percent(cls, pattern: _PatternCursor, _builder: _SteppedPatternBuilder[TResult, TBucket]) -> None:
        """Handle a leading "%" which acts as a pseudo-escape - it's mostly used to allow format strings such as '%H'
        to mean 'use a custom format string consisting of H instead of a standard pattern H'."""
        if pattern.has_more_characters:
            if pattern.peek_next() != "%":
                # Handle the next character as normal
                return
            raise InvalidPatternError(TextErrorMessages.PERCENT_DOUBLED)
        raise InvalidPatternError(TextErrorMessages.PERCENT_AT_END_OF_STRING)

    @classmethod
    def _handle_padded_field(
        cls,
        max_count: int,
        field: _PatternFields,
        min_value: int,
        max_value: int,
        getter: Callable[[TResult], int],
        setter: Callable[[TBucket, int], None],
        type_: type[TResult],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[TResult, TBucket]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult, TBucket]) -> None:
            count = pattern.get_repeat_count(max_count)
            builder._add_field(field, pattern.current)
            builder._add_parse_value_action(count, max_count, pattern.current, min_value, max_value, setter, type_)
            builder.add_format_left_pad(
                count, getter, assume_non_negative=(min_value >= 0), assume_fits_in_count=(count == max_count)
            )

        return handler

    def add_required_sign(
        self, sign_setter: Callable[[TBucket, bool], None], non_negative_predicate: Callable[[TResult], bool]
    ) -> None:
        """Adds parse and format actions for a mandatory positive/negative sign."""

        def parse_action(string: _ValueCursor, bucket: TBucket) -> ParseResult[TResult] | None:
            if string._match("-"):
                sign_setter(bucket, False)
                return None

            if string._match("+"):
                sign_setter(bucket, True)
                return None

            return ParseResult[TResult]._missing_sign(string)

        def format_action(value: TResult, sb: StringBuilder) -> None:
            sb.append("+" if non_negative_predicate(value) else "-")

        self._add_parse_action(parse_action)
        self._add_format_action(format_action)

    def add_negative_only_sign(
        self, sign_setter: Callable[[TBucket, bool], None], non_negative_predicate: Callable[[TResult], bool]
    ) -> None:
        """Adds parse and format actions for an "negative only" sign."""

        def parse_action(string: _ValueCursor, bucket: TBucket) -> ParseResult[TResult] | None:
            if string._match("-"):
                sign_setter(bucket, False)
                return None

            if string._match("+"):
                return ParseResult[TResult]._positive_sign_invalid(string)

            sign_setter(bucket, True)
            return None

        def format_action(value: TResult, sb: StringBuilder) -> None:
            if not non_negative_predicate(value):
                sb.append("-")

        self._add_parse_action(parse_action)
        self._add_format_action(format_action)

    def add_format_left_pad(
        self, count: int, selector: Callable[[TResult], int], assume_non_negative: bool, assume_fits_in_count: bool
    ) -> None:
        """Adds an action to pad a selected value to a given minimum length.

        :param count: The minimum length to pad to
        :param selector: The selector function to apply to obtain a value to format
        :param assume_non_negative: Whether it is safe to assume the value will be non-negative
        :param assume_fits_in_count: Whether it is safe to assume the value will not exceed the specified length
        """
        if count == 2 and assume_non_negative and assume_fits_in_count:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                FormatHelper.format_2_digits_non_negative(selector(value), sb)
        elif count == 4 and assume_fits_in_count:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                FormatHelper.format_4_digits_value_fits(selector(value), sb)
        elif assume_non_negative:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                FormatHelper.left_pad_non_negative(selector(value), count, sb)
        else:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                FormatHelper.left_pad(selector(value), count, sb)

        self._add_format_action(format_action)

    @runtime_checkable
    class _IPostPatternParseFormatAction(Protocol):
        """Hack to handle genitive month names.

        We only know what we need to do *after* we've parsed the whole pattern.
        """

        def build_format_action(self, final_fields: _PatternFields) -> Callable[[TResult, StringBuilder], None]: ...

    class __SteppedPattern(_IPartialPattern[TResult]):
        def __init__(
            self,
            format_actions: Callable[[TResult, StringBuilder], None],
            parse_actions: list[Callable[[_ValueCursor, TBucket], ParseResult[TResult] | None]] | None,
            bucket_provider: Callable[[], TBucket],
            used_fields: _PatternFields,
            sample: TResult,
        ) -> None:
            self.__format_actions: Final[Callable[[TResult, StringBuilder], None]] = format_actions
            # This will be null if the pattern is only capable of formatting.
            self.__parse_actions: Final[list[Callable[[_ValueCursor, TBucket], ParseResult[TResult] | None]] | None] = (
                parse_actions
            )
            self.__bucket_provider: Final[Callable[[], TBucket]] = bucket_provider
            self.__used_fields: Final[_PatternFields] = used_fields

            # Format the sample value to work out the expected length, so we
            # can use that when creating a StringBuilder. This will definitely not always
            # be appropriate, but it's a start.
            builder = StringBuilder()
            format_actions(sample, builder)
            self.__expected_length: Final[int] = builder.length

        def parse(self, text: str) -> ParseResult[TResult]:
            if self.__parse_actions is None:
                return ParseResult[TResult]._format_only_pattern
            if text is None:
                return ParseResult[TResult]._argument_null("text")
            if len(text) == 0:
                return ParseResult[TResult]._value_string_empty()

            value_cursor = _ValueCursor(text)
            # Prime the pump... the value cursor ends up *before* the first character, but
            # our steps always assume it's *on* the right character.
            value_cursor.move_next()
            result = self.parse_partial(value_cursor)
            if not result.success:
                return result
            # Check that we've used up all the text
            if value_cursor.current != _ValueCursor._NUL:
                return ParseResult[TResult]._extra_value_characters(value_cursor, value_cursor.remainder)
            return result

        def format(self, value: TResult) -> str:
            builder = StringBuilder(capacity=self.__expected_length)
            # This will call all the actions in the multicast delegate.
            self.__format_actions(value, builder)
            return builder.to_string()

        def parse_partial(self, cursor: _ValueCursor) -> ParseResult[TResult]:
            # At the moment we shouldn't get a partial parse for a format-only pattern, but
            # let's guard against it for the future.
            if self.__parse_actions is None:
                return ParseResult[TResult]._format_only_pattern

            bucket = self.__bucket_provider()

            for action in self.__parse_actions:
                failure: ParseResult[TResult] | None = action(cursor, bucket)
                if failure is not None:
                    return failure

            return bucket.calculate_value(self.__used_fields, cursor.value)

        def append_format(self, value: TResult, builder: StringBuilder) -> StringBuilder:
            _Preconditions._check_not_null(builder, "builder")
            self.__format_actions(value, builder)
            return builder
