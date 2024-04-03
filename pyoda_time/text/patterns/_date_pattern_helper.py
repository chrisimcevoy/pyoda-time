# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Callable, Sequence, TypeVar, final

from pyoda_time import CalendarSystem
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.calendars import Era
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text import InvalidPatternError, ParseResult
from pyoda_time.text._local_date_pattern_parser import _LocalDatePatternParser
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text._value_cursor import _ValueCursor
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _sealed

T = TypeVar("T")


class _DatePatternHelper:
    """Common methods used when parsing dates.

    These are used from both LocalDateTimePatternParser and LocalDatePatternParser.
    """

    @classmethod
    def _create_year_of_era_handler(
        cls, year_getter: Callable[[T], int], setter: Callable[[_ParseBucket[T], int], None], type_: type[T]
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        def selector(value: T) -> int:
            return _csharp_modulo(_csharp_modulo(year_getter(value), 100) + 100, 100)

        def year_of_era_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            count = pattern.get_repeat_count(4)
            builder._add_field(_PatternFields.YEAR_OF_ERA, pattern.current)
            match count:
                case 2:
                    builder._add_parse_value_action(2, 2, "y", 0, 99, setter, type_)
                    # Force the year into the range 0-99.
                    builder.add_format_left_pad(2, selector, assume_non_negative=True, assume_fits_in_count=True)
                    # Just remember that we've set this particular field.
                    # We can't set it twice as we've already got the YearOfEra flag set.
                    builder._add_field(_PatternFields.YEAR_TWO_DIGITS, pattern.current)
                case 4:
                    # Left-pad to 4 digits when formatting; parse exactly 4 digits.
                    builder._add_parse_value_action(4, 4, "y", 1, 9999, setter, type_)
                    builder.add_format_left_pad(4, year_getter, assume_non_negative=False, assume_fits_in_count=True)
                case _:
                    raise InvalidPatternError(_TextErrorMessages.INVALID_REPEAT_COUNT, pattern.current, count)

        return year_of_era_handler

    @classmethod
    def _create_month_of_year_handler(
        cls,
        number_getter: Callable[[T], int],
        text_setter: Callable[[_ParseBucket[T], int], None],
        number_setter: Callable[[_ParseBucket[T], int], None],
        type_: type[T],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        def pattern_builder(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            count: int = pattern.get_repeat_count(4)
            field: _PatternFields
            match count:
                case 1 | 2:
                    field = _PatternFields.MONTH_OF_YEAR_NUMERIC
                    # Handle real maximum value in the bucket
                    builder._add_parse_value_action(count, 2, pattern.current, 1, 99, number_setter, type_)
                    builder.add_format_left_pad(
                        count, number_getter, assume_non_negative=True, assume_fits_in_count=(count == 2)
                    )
                case 3 | 4:
                    field = _PatternFields.MONTH_OF_YEAR_TEXT
                    format = builder._format_info
                    non_genitive_text_values = format.short_month_names if count == 3 else format.long_month_names
                    genitive_text_values = (
                        format.short_month_genitive_names if count == 3 else format.long_month_genitive_names
                    )
                    if non_genitive_text_values == genitive_text_values:
                        builder._add_parse_longest_text_action(
                            pattern.current,
                            text_setter,
                            # TODO: format.compare_info,
                            non_genitive_text_values,
                        )
                    else:
                        builder._add_parse_longest_text_action(
                            pattern.current,
                            text_setter,
                            # TODO: format.compare_info,
                            genitive_text_values,
                            non_genitive_text_values,
                        )
                    # Hack: see below
                    builder._add_format_action(
                        _DatePatternHelper._MonthFormatActionHandler(format, count, number_getter)._dummy_method
                    )
                case _:
                    raise RuntimeError("Invalid count!")
            builder._add_field(field, pattern.current)

        return pattern_builder

    @final
    @_sealed
    class _MonthFormatActionHandler(_SteppedPatternBuilder._IPostPatternParseFormatAction):
        """Hacky way of building an action which depends on the final set of pattern fields to determine whether to
        format a month using the genitive form or not."""

        def __init__(
            self,
            format_info: _PyodaFormatInfo,
            count: int,
            getter: Callable[[T], int],
        ) -> None:
            self.__format_info = format_info
            self.__count = count
            self.__getter = getter

        def _dummy_method(self, value: T, builder: StringBuilder) -> None:
            # This method is never called. We use it to create a delegate with a target that implements
            # IPostPatternParseFormatAction. There's no test for this throwing.
            # This method must be an instance method, so that we can get the target of the method in
            # SteppedPatternBuilder.Build.
            raise RuntimeError("This method should never be called")

        def build_format_action(self, final_fields: _PatternFields) -> Callable[[T, StringBuilder], None]:
            genitive: bool = (final_fields & _PatternFields.DAY_OF_MONTH) != _PatternFields.NONE
            text_values: Sequence[str]
            if self.__count == 3:
                if genitive:
                    text_values = self.__format_info.short_month_genitive_names
                else:
                    text_values = self.__format_info.short_month_names
            else:
                if genitive:
                    text_values = self.__format_info.long_month_genitive_names
                else:
                    text_values = self.__format_info.long_month_names

            def format_action(value: T, sb: StringBuilder) -> None:
                sb.append(text_values[self.__getter(value)])

            return format_action

    @classmethod
    def _create_day_handler(
        cls,
        day_of_month_getter: Callable[[T], int],
        day_of_week_getter: Callable[[T], int],
        day_of_month_setter: Callable[[_ParseBucket[T], int], None],
        day_of_week_setter: Callable[[_ParseBucket[T], int], None],
        type_: type[T],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        """Creates a character handler for the day specifier (d)."""

        def day_handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            count: int = pattern.get_repeat_count(4)
            field: _PatternFields
            match count:
                case 1 | 2:
                    field = _PatternFields.DAY_OF_MONTH
                    # Handle real maximum value in the bucket
                    builder._add_parse_value_action(count, 2, pattern.current, 1, 99, day_of_month_setter, type_)
                    builder.add_format_left_pad(
                        count, day_of_month_getter, assume_non_negative=True, assume_fits_in_count=(count == 2)
                    )
                case 3 | 4:
                    field = _PatternFields.DAY_OF_WEEK
                    format_info = builder._format_info
                    text_values: Sequence[str] = (
                        format_info.short_day_names if count == 3 else format_info.long_day_names
                    )
                    builder._add_parse_longest_text_action(
                        pattern.current,
                        day_of_week_setter,
                        # TODO: format_info.compare_info,
                        text_values,
                    )

                    def format_action(value: T, sb: StringBuilder) -> None:
                        sb.append(text_values[day_of_week_getter(value)])

                    builder._add_format_action(format_action)
                case _:
                    raise RuntimeError("Invalid Count!")
            builder._add_field(field, pattern.current)

        return day_handler

    @classmethod
    def _create_era_handler(
        cls,
        era_from_value: Callable[[T], Era],
        date_bucket_from_bucket: Callable[[_ParseBucket[T]], _LocalDatePatternParser._LocalDateParseBucket],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            pattern.get_repeat_count(2)
            builder._add_field(_PatternFields.ERA, pattern.current)
            format_info = builder._format_info

            def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                date_bucket = date_bucket_from_bucket(bucket)
                return date_bucket._parse_era(format_info, cursor)

            builder._add_parse_action(parse_action)

            def format_action(value: T, sb: StringBuilder) -> None:
                sb.append(format_info.get_era_primary_name(era_from_value(value)))

            builder._add_format_action(format_action)

        return handler

    @classmethod
    def _create_calendar_handler(
        cls,
        getter: Callable[[T], CalendarSystem],
        setter: Callable[[_ParseBucket[T], CalendarSystem], None],
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[T]], None]:
        """Creates a character handler for the calendar specifier (c)."""

        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[T]) -> None:
            builder._add_field(_PatternFields.CALENDAR, pattern.current)

            def parse_action(cursor: _ValueCursor, bucket: _ParseBucket[T]) -> ParseResult[T] | None:
                for calendar_id in CalendarSystem.ids:
                    if cursor._match(calendar_id):
                        setter(bucket, CalendarSystem.for_id(calendar_id))
                        return None
                return ParseResult._no_matching_calendar_system(cursor)

            builder._add_parse_action(parse_action)

            def format_action(value: T, sb: StringBuilder) -> None:
                sb.append(getter(value).id)

            builder._add_format_action(format_action)

        return handler
