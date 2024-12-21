# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from pyoda_time.text import ParseResult
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.utility._csharp_compatibility import _towards_zero_division

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyoda_time._compatibility._string_builder import StringBuilder
    from pyoda_time.text._parse_bucket import _ParseBucket
    from pyoda_time.text._value_cursor import _ValueCursor
    from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
    from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder

T = TypeVar("T")


class _TimePatternHelper:
    """Common methods used when parsing dates.

    These are used from LocalDateTimePatternParser, OffsetPatternParser and LocalTimePatternParser.
    """

    @classmethod
    def _create_period_handler(
        cls, max_count: int, getter: Callable[[T], int], setter: Callable[[_ParseBucket[T], int], None]
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        def period_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            # Note: Deliberately *not* using the decimal separator of the culture - see issue 21.

            # If the next part of the pattern is an F, then this decimal separator is effectively optional.
            # At parse time, we need to check whether we've matched the decimal separator.
            # If we have, match the fractional seconds part as normal.
            # Otherwise, we continue on to the next parsing token.
            # At format time, we should always append the decimal separator, and then append using PadRightTruncate.

            if pattern.peek_next() == "F":
                pattern.move_next()
                count: int = pattern.get_repeat_count(max_count)
                builder._add_field(_PatternFields.FRACTIONAL_SECONDS, pattern.current)

                def parse_action(value_cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                    # If the next token isn't the decimal separator, we
                    # assume it's part of the next token in the pattern
                    if not value_cursor._match("."):
                        return None

                    # If there *was* a decimal separator, we should definitely have a number.
                    # Last argument is 1 because we need at least one digit after the decimal separator
                    success, fractional_seconds = value_cursor._parse_fraction(count, max_count, 1)
                    if not success:
                        return ParseResult._mismatched_number(value_cursor, "F" * count)
                    # No need to validate the value - we've got one to three digits, so the range 0-999 is guaranteed.
                    setter(bucket, fractional_seconds)
                    return None

                builder._add_parse_action(parse_action)

                def format_action(local_time: T, sb: StringBuilder) -> None:
                    sb.append(".")

                builder._add_format_action(format_action)

                builder._add_format_fraction_truncate(count, max_count, getter)
            else:
                builder._add_literal(expected_char=".", failure_selector=ParseResult._mismatched_character)

        return period_handler

    @classmethod
    def _create_comma_dot_handler(
        cls,
        max_count: int,
        getter: Callable[[T], int],
        setter: Callable[[_ParseBucket[T], int], None],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        """Creates a character handler for a dot (period) or comma, which have the same meaning.

        Formatting always uses a dot, but parsing will allow a comma instead, to conform with ISO-8601. This is *not*
        culture sensitive.
        """

        # Note: Deliberately *not* using the decimal separator of the culture - see issue 21.

        # If the next part of the pattern is an F, then this decimal separator is effectively optional.
        # At parse time, we need to check whether we've matched the decimal separator. If we have, match the fractional
        # seconds part as normal. Otherwise, we continue on to the next parsing token.
        # At format time, we should always append the decimal separator, and then append using PadRightTruncate.

        def comma_dot_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            if pattern.peek_next() == "F":
                pattern.move_next()
                count: int = pattern.get_repeat_count(max_count)
                builder._add_field(_PatternFields.FRACTIONAL_SECONDS, pattern.current)

                def parse_action(value_cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                    # If the next token isn't a dot or comma, we assume
                    # it's part of the next token in the pattern
                    if not value_cursor._match(".") and not value_cursor._match(","):
                        return None

                    # If there *was* a decimal separator, we should definitely have a number.
                    # Last argument is 1 because we need at least one digit to be present after a decimal separator
                    success, fractional_seconds = value_cursor._parse_fraction(count, max_count, 1)
                    if not success:
                        return ParseResult._mismatched_number(value_cursor, "F" * count)
                    # No need to validate the value.
                    # We've got an appropriate number of digits, so the range is guaranteed.
                    setter(bucket, fractional_seconds)
                    return None

                builder._add_parse_action(parse_action)

                def format_action(local_time: T, sb: StringBuilder) -> None:
                    sb.append(".")

                builder._add_format_action(format_action)

                builder._add_format_fraction_truncate(count, max_count, getter)
            else:

                def parse_action(value_cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                    if value_cursor._match(".") or value_cursor._match(","):
                        return None
                    return ParseResult._mismatched_character(value_cursor, ";")

                builder._add_parse_action(parse_action)

                def format_action(local_time: T, sb: StringBuilder) -> None:
                    sb.append(".")

                builder._add_format_action(format_action)

        return comma_dot_handler

    @classmethod
    def _create_fraction_handler(
        cls,
        max_count: int,
        getter: Callable[[T], int],
        setter: Callable[[_ParseBucket[T], int], None],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        """Creates a character handler to handle the "fraction of a second" specifier (f or F)."""

        def fraction_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            pattern_character = pattern.current
            count = pattern.get_repeat_count(max_count)
            builder._add_field(_PatternFields.FRACTIONAL_SECONDS, pattern.current)

            def parse_action(value_cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                # If the pattern is 'f', we need exactly "count" digits. Otherwise ('F') we need
                # "up to count" digits.
                success, fractional_seconds = value_cursor._parse_fraction(
                    count, max_count, count if pattern_character == "f" else 0
                )
                if not success:
                    return ParseResult._mismatched_number(value_cursor, pattern_character * count)
                # No need to validate the value - we've got an appropriate number of digits, so the range is guaranteed.
                setter(bucket, fractional_seconds)
                return None

            builder._add_parse_action(parse_action)

            if pattern_character == "f":
                builder._add_format_fraction(count, max_count, getter)
            else:
                builder._add_format_fraction_truncate(count, max_count, getter)

        return fraction_handler

    @classmethod
    def _create_am_pm_handler(
        cls,
        hour_of_day_getter: Callable[[T], int],
        am_pm_setter: Callable[[_ParseBucket[T], int], None],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        def am_pm_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            count = pattern.get_repeat_count(2)
            builder._add_field(_PatternFields.AM_PM, pattern.current)

            am_designator: str = builder._format_info.am_designator
            pm_designator: str = builder._format_info.pm_designator

            # If we don't have an AM or PM designator, we're nearly done. Set the AM/PM designator
            # to the special value of 2, meaning "take it from the template".
            if not am_designator and not pm_designator:

                def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                    am_pm_setter(bucket, 2)
                    return None

                builder._add_parse_action(parse_action)
                return

            # Odd scenario (but present in af-ZA for .NET 2) - exactly one of the AM/PM designator is valid.
            # Delegate to a separate method to keep this clearer...
            if not am_designator or not pm_designator:
                specified_designator_value: int = 1 if len(am_designator) == 0 else 0
                specified_designator: str = pm_designator if specified_designator_value == 1 else am_designator
                cls.__handle_half_am_pm_designator(
                    count, specified_designator, specified_designator_value, hour_of_day_getter, am_pm_setter, builder
                )
                return

            # TODO: Noda Time uses CompareInfo here...

            # Single character designator
            if count == 1:
                # It's not entirely clear whether this is the right thing to do... there's no nice
                # way of providing a single-character case-insensitive match.
                am_first: str = am_designator[0]
                pm_first: str = pm_designator[0]

                def single_character_parse_action(
                    cursor: _ValueCursor, bucket: _ParseBucket[T]
                ) -> ParseResult[T] | None:
                    if cursor._match_case_insensitive(am_first, True):
                        am_pm_setter(bucket, 0)
                        return None
                    if cursor._match_case_insensitive(pm_first, True):
                        am_pm_setter(bucket, 1)
                        return None
                    return ParseResult._missing_am_pm_designator(cursor)

                builder._add_parse_action(single_character_parse_action)

                def single_character_format_action(value: T, sb: StringBuilder) -> None:
                    sb.append(pm_designator[0] if hour_of_day_getter(value) > 11 else am_designator[0])

                builder._add_format_action(single_character_format_action)
                return

            # Full designator
            def full_designator_parse_action(cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                # Could use the "match longest" approach, but with only two it feels a bit silly to build a list...
                pm_longer_than_am: bool = len(pm_designator) > len(am_designator)
                longer_designator: str = pm_designator if pm_longer_than_am else am_designator
                shorter_designator: str = am_designator if pm_longer_than_am else pm_designator
                longer_value: int = 1 if pm_longer_than_am else 0
                if cursor._match_case_insensitive(longer_designator, True):
                    am_pm_setter(bucket, longer_value)
                    return None
                if cursor._match_case_insensitive(shorter_designator, True):
                    am_pm_setter(bucket, 1 - longer_value)
                    return None
                return ParseResult._missing_am_pm_designator(cursor)

            builder._add_parse_action(full_designator_parse_action)

            def full_designator_format_action(value: T, sb: StringBuilder) -> None:
                sb.append(pm_designator if hour_of_day_getter(value) > 11 else am_designator)

            builder._add_format_action(full_designator_format_action)

        return am_pm_handler

    @classmethod
    def __handle_half_am_pm_designator(
        cls,
        count: int,
        specified_designator: str,
        specified_designator_value: int,
        hour_of_day_getter: Callable[[T], int],
        am_pm_setter: Callable[[_ParseBucket[T], int], None],
        builder: _SteppedPatternBuilder[T],
    ) -> None:
        if count == 1:
            specified_designator = specified_designator[0]

        def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
            value: int = (
                specified_designator_value
                if cursor._match_case_insensitive(specified_designator, True)
                else 1 - specified_designator_value
            )
            am_pm_setter(bucket, value)
            return None

        def format_action(value: T, sb: StringBuilder) -> None:
            # Only append anything if it's the non-empty designator.
            if _towards_zero_division(hour_of_day_getter(value), 12) == specified_designator_value:
                sb.append(specified_designator)

        builder._add_parse_action(parse_action)
        builder._add_format_action(format_action)
