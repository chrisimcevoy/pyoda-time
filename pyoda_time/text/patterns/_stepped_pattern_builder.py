# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Final,
    Generic,
    Mapping,
    Protocol,
    Sequence,
    TypeVar,
    final,
    overload,
    runtime_checkable,
)

from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._value_cursor import _ValueCursor

from ..._compatibility._string_builder import StringBuilder
from ..._local_date import LocalDate
from ..._local_date_time import LocalDateTime
from ..._local_time import LocalTime
from ...globalization._pyoda_format_info import _PyodaFormatInfo
from ...utility._csharp_compatibility import _sealed
from ...utility._preconditions import _Preconditions
from .._format_helper import _FormatHelper
from .._i_partial_pattern import _IPartialPattern
from .._invalid_pattern_exception import InvalidPatternError
from .._local_time_pattern import LocalTimePattern
from .._parse_result import ParseResult
from .._text_error_messages import _TextErrorMessages
from ._pattern_cursor import _PatternCursor
from ._pattern_fields import _PatternFields

if TYPE_CHECKING:
    from .._local_date_pattern_parser import _LocalDatePatternParser
    from .._local_time_pattern_parser import _LocalTimePatternParser

# TODO: In Noda Time, SteppedPatternBuilder has two generic type parameters:
#  `SteppedPatternBuilder<TResult, TBucket> where TBucket : ParseBucket<TResult>`
#  This seems to be impossible to replicate with TypeVar.
#  If you do this:
#  `TBucket = TypeVar(TResult, bound=_ParseBucket)`
#  Then mypy complains that _ParseBucket is missing a type parameter, because it
#  is itself a generic class.
#  If you then do this:
#  `TBucket = TypeVar(TResult, bound=_ParseBucket[TBucket])`
#  Mypy complains that TResult is unbound, because in the context that TBucket is
#  declared it really is unbound. Also, PyCharm gives a warning that TypeVar
#  constraints may not have generic type parameters.
#  I tried a bunch of different stuff to make it work, to no avail.
#  In the end I decided to omit the TBucket type parameter from SteppedPatternBuilder
#  altogether.
#  This is fine for SteppedPatternBuilder, but it does mean that occasionally discrete
#  inheritors (e.g. OffsetPatternParser) will have e.g. `_ParseBucket[Offset]` type
#  annotations where Noda Time has `_OffsetParseBucket` types.
#  This means that occasionally we have to convince mypy to accept that the actual type
#  of those parameters is `_OffsetParseBucket` inside function bodies, to be able to
#  set the required attributes which don't exist on the `ParseBucket` base class.
#  Bit of a pain, but overall preferable to having any more `# type: ignore` than
#  we have to.
#  Maybe there is a refactor to be had here which is more sympathetic to Python's
#  static typing limitations...?

TResult = TypeVar("TResult")
TEmbedded = TypeVar("TEmbedded")


@_sealed
@final
class _SteppedPatternBuilder(Generic[TResult]):
    """Builder for a pattern which implements parsing and formatting as a sequence of steps applied in turn."""

    @property
    def _format_info(self) -> _PyodaFormatInfo:
        return self.__format_info

    @property
    def _used_fields(self) -> _PatternFields:
        return self.__used_fields

    def __init__(self, format_info: _PyodaFormatInfo, bucket_provider: Callable[[], _ParseBucket[TResult]]) -> None:
        self.__format_info: Final[_PyodaFormatInfo] = format_info
        self.__format_actions: Final[list[Callable[[TResult, StringBuilder], None]]] = []
        self.__parse_actions: Final[
            list[Callable[[_ValueCursor, _ParseBucket[TResult]], ParseResult[TResult] | None]]
        ] = []
        self.__bucket_provider: Final[Callable[[], _ParseBucket[TResult]]] = bucket_provider
        self.__used_fields: _PatternFields = _PatternFields.NONE
        self.__format_only: bool = False

    def _create_sample_bucket(self) -> _ParseBucket[TResult]:
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
        character_handlers: Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[TResult]], None]],
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
                    raise InvalidPatternError(_TextErrorMessages.UNQUOTED_LITERAL, current)

                self._add_literal(
                    expected_char=pattern_cursor.current, failure_selector=ParseResult._mismatched_character
                )

    def _validate_used_fields(self) -> None:
        """Validates the combination of fields used."""

        # We assume invalid combinations are global across all parsers. The way that
        # the patterns are parsed ensures we never end up with any invalid individual fields
        # (e.g. time fields within a date pattern).

        if (self.__used_fields & (_PatternFields.ERA | _PatternFields.YEAR_OF_ERA)) == _PatternFields.ERA:
            raise InvalidPatternError(_TextErrorMessages.ERA_WITHOUT_YEAR_OF_ERA)
        calendar_and_era: Final[_PatternFields] = _PatternFields.ERA | _PatternFields.CALENDAR
        if (self.__used_fields & calendar_and_era) == calendar_and_era:
            raise InvalidPatternError(_TextErrorMessages.CALENDAR_AND_ERA)

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
            raise InvalidPatternError(_TextErrorMessages.DATE_FIELD_AND_EMBEDDED_DATE)
        # Ditto for time
        if self.__used_fields.has_any(_PatternFields.EMBEDDED_TIME) and self._used_fields.has_any(
            _PatternFields.ALL_TIME_FIELDS & ~_PatternFields.EMBEDDED_TIME
        ):
            raise InvalidPatternError(_TextErrorMessages.TIME_FIELD_AND_EMBEDDED_TIME)

        delegates: list[Callable[[TResult, StringBuilder], None]] = []

        for format_action in self.__format_actions:
            # In Noda Time, this section of code checks whether the .Target of the formatAction delegate
            # implements this interface. A close approximation in Python is to check the __self__ attribute
            # of a bound method (if it exists) is an instance of a runtime-checkable Protocol.
            if hasattr(format_action, "__self__") and isinstance(
                format_action.__self__, self._IPostPatternParseFormatAction
            ):
                delegates.append(format_action.__self__.build_format_action(self.__used_fields))
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
            raise InvalidPatternError(_TextErrorMessages.REPEATED_FIELD_IN_PATTERN, character_in_pattern)
        self.__used_fields = new_used_fields

    def _add_parse_action(
        self, parse_action: Callable[[_ValueCursor, _ParseBucket[TResult]], ParseResult[TResult] | None]
    ) -> None:
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
        value_setter: Callable[[_ParseBucket[TResult], int], None],
        type_: type[TResult],
    ) -> None:
        def parse_value_action(cursor: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
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

    @overload
    def _add_literal(self, *, expected_text: str, failure: Callable[[_ValueCursor], ParseResult[TResult]]) -> None: ...

    @overload
    def _add_literal(
        self, *, expected_char: str, failure_selector: Callable[[_ValueCursor, str], ParseResult[TResult]]
    ) -> None: ...

    def _add_literal(
        self,
        *,
        expected_text: str | None = None,
        failure: Callable[[_ValueCursor], ParseResult[TResult]] | None = None,
        expected_char: str | None = None,
        failure_selector: Callable[[_ValueCursor, str], ParseResult[TResult]] | None = None,
    ) -> None:
        """Adds text which must be matched exactly when parsing, and appended directly when formatting."""

        # Overload 1
        if expected_text is not None and failure is not None:

            def overload_1_parse_action(
                cursor: _ValueCursor, bucket: _ParseBucket[TResult]
            ) -> ParseResult[TResult] | None:
                if cursor._match(expected_text):
                    return None
                return failure(cursor)

            def overload_1_format_action(value: TResult, builder: StringBuilder) -> None:
                builder.append(expected_text)

            self._add_parse_action(overload_1_parse_action)
            self._add_format_action(overload_1_format_action)
            return

        # Overload 2
        if expected_char is not None and failure_selector is not None:

            def overload_2_parse_action(
                cursor: _ValueCursor, bucket: _ParseBucket[TResult]
            ) -> ParseResult[TResult] | None:
                if cursor._match(expected_char):
                    return None
                return failure_selector(cursor, expected_char)

            def overload_2_format_action(value: TResult, builder: StringBuilder) -> None:
                builder.append(expected_char)

            self._add_parse_action(overload_2_parse_action)
            self._add_format_action(overload_2_format_action)
            return

        raise RuntimeError("_SteppedPatternBuilder._add_literal called with incorrect arguments")

    def _add_parse_longest_text_action(
        self,
        field: str,
        setter: Callable[[_ParseBucket[TResult], int], None],
        # TODO: compare_info: CompareInfo,
        text_values_1: Sequence[str],
        text_values_2: Sequence[str] | None = None,
    ) -> None:
        """Adds parse actions for up to two list of strings, such as non-genitive and genitive month names.

        The parsing is performed case-insensitively. All candidates are tested, and only the longest match is used.
        """

        def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
            best_index = -1
            longest_match = 0
            best_index, longest_match = self.__find_longest_match(cursor, text_values_1, best_index, longest_match)
            if text_values_2:
                best_index, longest_match = self.__find_longest_match(cursor, text_values_2, best_index, longest_match)
            if best_index != -1:
                setter(bucket, best_index)
                cursor.move(cursor.index + longest_match)
                return None
            return ParseResult._mismatched_text(cursor, field)

        self._add_parse_action(parse_action)

    @staticmethod
    def __find_longest_match(
        cursor: _ValueCursor, values: Sequence[str], best_index: int, longest_match: int
    ) -> tuple[int, int]:
        """Find the longest match from a given set of candidate strings, updating the index/length of the best value
        accordingly."""
        for i, candidate in enumerate(values):
            if candidate is None or len(candidate) <= longest_match:
                continue
            if cursor._match_case_insensitive(candidate, False):
                best_index = i
                longest_match = len(candidate)
        return best_index, longest_match

    @classmethod
    def _handle_quote(cls, pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult]) -> None:
        quoted: str = pattern.get_quoted_string(pattern.current)
        builder._add_literal(expected_text=quoted, failure=ParseResult[TResult]._quoted_string_mismatch)

    @classmethod
    def _handle_backslash(cls, pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult]) -> None:
        if not pattern.move_next():
            raise InvalidPatternError(_TextErrorMessages.ESCAPE_AT_END_OF_STRING)

        builder._add_literal(
            expected_char=pattern.current, failure_selector=ParseResult[TResult]._escaped_character_missmatch
        )

    @classmethod
    def _handle_percent(cls, pattern: _PatternCursor, _builder: _SteppedPatternBuilder[TResult]) -> None:
        """Handle a leading "%" which acts as a pseudo-escape - it's mostly used to allow format strings such as '%H'
        to mean 'use a custom format string consisting of H instead of a standard pattern H'."""
        if pattern.has_more_characters:
            if pattern.peek_next() != "%":
                # Handle the next character as normal
                return
            raise InvalidPatternError(_TextErrorMessages.PERCENT_DOUBLED)
        raise InvalidPatternError(_TextErrorMessages.PERCENT_AT_END_OF_STRING)

    @classmethod
    def _handle_padded_field(
        cls,
        max_count: int,
        field: _PatternFields,
        min_value: int,
        max_value: int,
        getter: Callable[[TResult], int],
        setter: Callable[[_ParseBucket[TResult], int], None],
        type_: type[TResult],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[TResult]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[TResult]) -> None:
            count = pattern.get_repeat_count(max_count)
            builder._add_field(field, pattern.current)
            builder._add_parse_value_action(count, max_count, pattern.current, min_value, max_value, setter, type_)
            builder.add_format_left_pad(
                count, getter, assume_non_negative=(min_value >= 0), assume_fits_in_count=(count == max_count)
            )

        return handler

    def add_required_sign(
        self,
        sign_setter: Callable[[_ParseBucket[TResult], bool], None],
        non_negative_predicate: Callable[[TResult], bool],
    ) -> None:
        """Adds parse and format actions for a mandatory positive/negative sign."""

        def parse_action(string: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
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
        self,
        sign_setter: Callable[[_ParseBucket[TResult], bool], None],
        non_negative_predicate: Callable[[TResult], bool],
    ) -> None:
        """Adds parse and format actions for an "negative only" sign."""

        def parse_action(string: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
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
                _FormatHelper._format_2_digits_non_negative(selector(value), sb)
        elif count == 4 and assume_fits_in_count:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                _FormatHelper._format_4_digits_value_fits(selector(value), sb)
        elif assume_non_negative:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                _FormatHelper._left_pad_non_negative(selector(value), count, sb)
        else:

            def format_action(value: TResult, sb: StringBuilder) -> None:
                _FormatHelper._left_pad(selector(value), count, sb)

        self._add_format_action(format_action)

    def _add_format_fraction(self, width: int, scale: int, selector: Callable[[TResult], int]) -> None:
        def format_action(value: TResult, sb: StringBuilder) -> None:
            _FormatHelper._append_fraction(selector(value), width, scale, sb)

        self._add_format_action(format_action)

    def _add_format_fraction_truncate(self, width: int, scale: int, selector: Callable[[TResult], int]) -> None:
        def format_action(value: TResult, sb: StringBuilder) -> None:
            _FormatHelper._append_fraction_truncate(selector(value), width, scale, sb)

        self._add_format_action(format_action)

    def _add_embedded_local_partial(
        self,
        pattern: _PatternCursor,
        date_bucket_extractor: Callable[[_ParseBucket[TResult]], _LocalDatePatternParser._LocalDateParseBucket],
        time_bucket_extractor: Callable[[_ParseBucket[TResult]], _LocalTimePatternParser._LocalTimeParseBucket],
        date_extractor: Callable[[TResult], LocalDate],
        time_extractor: Callable[[TResult], LocalTime],
        # null if date/time embedded patterns are invalid
        date_time_extractor: Callable[[TResult], LocalDateTime] | None,
        type_: type[TResult],
    ) -> None:
        """Handles date, time and date/time embedded patterns."""
        # This will be d (date-only), t (time-only), or < (date and time)
        # If it's anything else, we'll see the problem when we try to get the pattern.
        pattern_type: str = pattern.peek_next()
        if pattern_type == "d" or pattern_type == "t":
            pattern.move_next()

        embedded_pattern_text = pattern.get_embedded_pattern()

        match pattern_type:
            case "<":
                sample_bucket = self._create_sample_bucket()
                two_digit_year_max = date_bucket_extractor(sample_bucket)._two_digit_year_max
                template_time = time_bucket_extractor(sample_bucket)._template_value
                template_date = date_bucket_extractor(sample_bucket)._template_value
                if date_time_extractor is None:
                    raise InvalidPatternError(_TextErrorMessages.INVALID_EMBEDDED_PATTERN_TYPE)
                self._add_field(_PatternFields.EMBEDDED_DATE, "l")
                self._add_field(_PatternFields.EMBEDDED_TIME, "l")

                def parse_action(bucket: _ParseBucket[TResult], value: LocalDateTime) -> None:
                    date_bucket = date_bucket_extractor(bucket)
                    time_bucket = time_bucket_extractor(bucket)
                    date_bucket._calendar = value.calendar
                    date_bucket._year = value.year
                    date_bucket._month_of_year_numeric = value.month
                    date_bucket._day_of_month = value.day
                    time_bucket._hours_24 = value.hour
                    time_bucket._minutes = value.minute
                    time_bucket._seconds = value.second
                    time_bucket._fractional_seconds = value.nanosecond_of_second

                from .._local_date_time_pattern import LocalDateTimePattern

                self._add_embedded_pattern(
                    LocalDateTimePattern._create(
                        embedded_pattern_text,
                        self.__format_info,
                        template_date + template_time,
                        two_digit_year_max,
                    )._underlying_pattern,
                    parse_action,
                    date_time_extractor,
                    type_,
                )
            case "d":
                self.__add_embedded_date_pattern(
                    "l", embedded_pattern_text, date_bucket_extractor, date_extractor, type_
                )
            case "t":
                self.__add_embedded_time_pattern(
                    "l", embedded_pattern_text, time_bucket_extractor, time_extractor, type_
                )
            case _:
                raise RuntimeError("Bug in Pyoda Time: embedded pattern type wasn't date, time, or date+time")

    def __add_embedded_date_pattern(
        self,
        character_in_pattern: str,
        embedded_pattern_text: str,
        date_bucket_extractor: Callable[[_ParseBucket[TResult]], _LocalDatePatternParser._LocalDateParseBucket],
        date_extractor: Callable[[TResult], LocalDate],
        eventual_result_type: type[TResult],
    ) -> None:
        template_value = date_bucket_extractor(self._create_sample_bucket())._template_value
        self._add_field(_PatternFields.EMBEDDED_DATE, character_in_pattern)

        def parse_action(bucket: _ParseBucket[TResult], value: LocalDate) -> None:
            date_bucket = date_bucket_extractor(bucket)
            date_bucket._calendar = value.calendar
            date_bucket._year = value.year
            date_bucket._month_of_year_numeric = value.month
            date_bucket._day_of_month = value.day

        from .._local_date_pattern import LocalDatePattern

        self._add_embedded_pattern(
            LocalDatePattern._create(
                embedded_pattern_text, self.__format_info, template_value, LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX
            )._underlying_pattern,
            parse_action,
            date_extractor,
            eventual_result_type,
        )

    def __add_embedded_time_pattern(
        self,
        character_in_pattern: str,
        embedded_pattern_text: str,
        time_bucket_extractor: Callable[[_ParseBucket[TResult]], _LocalTimePatternParser._LocalTimeParseBucket],
        time_extractor: Callable[[TResult], LocalTime],
        eventual_result_type: type[TResult],
    ) -> None:
        template_time = time_bucket_extractor(self._create_sample_bucket())._template_value
        self._add_field(_PatternFields.EMBEDDED_TIME, character_in_pattern)

        def parse_action(bucket: _ParseBucket[TResult], value: LocalTime) -> None:
            time_bucket = time_bucket_extractor(bucket)
            time_bucket._hours_24 = value.hour
            time_bucket._minutes = value.minute
            time_bucket._seconds = value.second
            time_bucket._fractional_seconds = value.nanosecond_of_second

        self._add_embedded_pattern(
            LocalTimePattern._create(embedded_pattern_text, self.__format_info, template_time)._underlying_pattern,
            parse_action,
            time_extractor,
            eventual_result_type,
        )

    def _add_embedded_pattern(
        self,
        embedded_pattern: _IPartialPattern[TEmbedded],
        parse_action: Callable[[_ParseBucket[TResult], TEmbedded], None],
        value_extractor: Callable[[TResult], TEmbedded],
        type_: type[TResult],
    ) -> None:
        """Adds parsing/formatting of an embedded pattern, e.g. an offset within a ZonedDateTime/OffsetDateTime."""

        def parse_action_to_add(value: _ValueCursor, bucket: _ParseBucket[TResult]) -> ParseResult[TResult] | None:
            result = embedded_pattern.parse_partial(value)
            if not result.success:
                return result.convert_error(type_)
            parse_action(bucket, result.value)
            return None

        def format_action_to_add(value: TResult, sb: StringBuilder) -> None:
            embedded_pattern.append_format(value_extractor(value), sb)

        self._add_parse_action(parse_action_to_add)
        self._add_format_action(format_action_to_add)

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
            parse_actions: list[Callable[[_ValueCursor, _ParseBucket[TResult]], ParseResult[TResult] | None]] | None,
            bucket_provider: Callable[[], _ParseBucket[TResult]],
            used_fields: _PatternFields,
            sample: TResult,
        ) -> None:
            self.__format_actions: Final[Callable[[TResult, StringBuilder], None]] = format_actions
            # This will be null if the pattern is only capable of formatting.
            self.__parse_actions: Final[
                list[Callable[[_ValueCursor, _ParseBucket[TResult]], ParseResult[TResult] | None]] | None
            ] = parse_actions
            self.__bucket_provider: Final[Callable[[], _ParseBucket[TResult]]] = bucket_provider
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
                # TODO: The type:ignore here is because text is str, not str|None.
                #  This faithfully recreates a quirk in the Noda Time implementation
                #  where the type is string in a non-nullable context, but the code
                #  checks whether text is null anyway. Can this be safely removed?
                return ParseResult[TResult]._argument_null("text")  # type: ignore[unreachable]
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
