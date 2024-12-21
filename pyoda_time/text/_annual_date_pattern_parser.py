# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from pyoda_time._annual_date import AnnualDate
from pyoda_time._calendar_system import CalendarSystem
from pyoda_time.text import AnnualDatePattern, InvalidPatternError, ParseResult
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._date_pattern_helper import _DatePatternHelper
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.utility._csharp_compatibility import _private, _sealed

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
    from pyoda_time.text._i_pattern import IPattern
    from pyoda_time.text.patterns._pattern_cursor import _PatternCursor


def _handle_day_of_month(pattern: _PatternCursor, builder: _SteppedPatternBuilder[AnnualDate]) -> None:
    count = pattern.get_repeat_count(2)
    field: _PatternFields
    match count:
        case 1 | 2:
            field = _PatternFields.DAY_OF_MONTH

            def value_setter(bucket: _ParseBucket[AnnualDate], value: int) -> None:
                assert isinstance(bucket, _AnnualDatePatternParser._AnnualDateParseBucket)
                bucket._day_of_month = value

            # Handle real maximum value in the bucket
            builder._add_parse_value_action(count, 2, pattern.current, 1, 99, value_setter, AnnualDate)
            builder.add_format_left_pad(
                count, lambda value: value.day, assume_non_negative=True, assume_fits_in_count=(count == 2)
            )
        case _:
            raise RuntimeError("Invalid count!")
    builder._add_field(field, pattern.current)


@final
@_sealed
@_private
class _AnnualDatePatternParser(_IPatternParser[AnnualDate]):
    """Parser for patterns of ``AnnualDate`` values."""

    @final
    @_sealed
    @_private
    class _AnnualDateParseBucket(_ParseBucket[AnnualDate]):
        """Bucket to put parsed values in, ready for later result calculation.

        This type is also used by AnnualDatePattern to store and calculate values.
        """

        _template_value: AnnualDate
        _month_of_year_numeric: int
        _month_of_year_text: int
        _day_of_month: int

        @classmethod
        def _ctor(cls, template_value: AnnualDate) -> _AnnualDatePatternParser._AnnualDateParseBucket:
            self = super().__new__(cls)
            self._template_value = template_value
            return self

        def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[AnnualDate]:
            # This will set MonthOfYearNumeric if necessary
            if (failure := self.__determine_month(used_fields, value)) is not None:
                return failure

            day = self._day_of_month if used_fields.has_any(_PatternFields.DAY_OF_MONTH) else self._template_value.day
            # Validate for the year 2000, just like the AnnualDate constructor does.
            if day > CalendarSystem.iso.get_days_in_month(2000, self._month_of_year_numeric):
                return ParseResult._day_of_month_out_of_range_no_year(value, day, self._month_of_year_numeric)

            return ParseResult.for_value(AnnualDate(self._month_of_year_numeric, day))

        def __determine_month(self, used_fields: _PatternFields, text: str) -> ParseResult[AnnualDate] | None:
            # In Noda Time, this code block is implemented as a switch statement.
            # If we were to use `match` in Python, the `|` would be treated as an "or".
            # So we use good old if-statements instead.
            fields = used_fields & (_PatternFields.MONTH_OF_YEAR_NUMERIC | _PatternFields.MONTH_OF_YEAR_TEXT)
            if fields == _PatternFields.MONTH_OF_YEAR_NUMERIC:
                # No-op
                pass
            if fields == _PatternFields.MONTH_OF_YEAR_TEXT:
                self._month_of_year_numeric = self._month_of_year_text
            if fields == _PatternFields.MONTH_OF_YEAR_NUMERIC | _PatternFields.MONTH_OF_YEAR_TEXT:
                if self._month_of_year_numeric != self._month_of_year_text:
                    return ParseResult._inconsistent_month_values(text)
                # No need to change MonthOfYearNumeric - this was just a check
            if fields == _PatternFields.NONE:
                self._month_of_year_numeric = self._template_value.month

            if self._month_of_year_numeric > CalendarSystem.iso.get_months_in_year(2000):
                return ParseResult._iso_month_out_of_range(text, self._month_of_year_numeric)

            return None

    __template_value: AnnualDate

    __PATTERN_CHARACTER_HANDLERS: Final[
        Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[AnnualDate]], None]]
    ] = {
        "%": _SteppedPatternBuilder._handle_percent,
        "'": _SteppedPatternBuilder._handle_quote,
        '"': _SteppedPatternBuilder._handle_quote,
        "\\": _SteppedPatternBuilder._handle_backslash,
        "/": lambda pattern, builder: builder._add_literal(
            expected_text=builder._format_info.date_separator, failure=ParseResult._date_separator_mismatch
        ),
        "M": _DatePatternHelper._create_month_of_year_handler(
            lambda value: value.month,
            lambda bucket, value: setattr(bucket, "_month_of_year_text", value),
            lambda bucket, value: setattr(bucket, "_month_of_year_numeric", value),
            AnnualDate,
        ),
        "d": _handle_day_of_month,
    }

    @classmethod
    def _ctor(cls, template_value: AnnualDate) -> _AnnualDatePatternParser:
        self = super().__new__(cls)
        self.__template_value = template_value
        return self

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[AnnualDate]:
        # Nullity check is performed in AnnualDatePattern.
        if not pattern:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)

        if len(pattern) == 1:
            match pattern:
                case "G":
                    return AnnualDatePattern.iso
                case _:
                    raise InvalidPatternError(_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern, AnnualDate.__name__)

        pattern_builder: _SteppedPatternBuilder[AnnualDate] = _SteppedPatternBuilder(
            format_info, lambda: self._AnnualDateParseBucket._ctor(self.__template_value)
        )  # TODO: bucket provider
        pattern_builder._parse_custom_pattern(pattern, self.__PATTERN_CHARACTER_HANDLERS)
        pattern_builder._validate_used_fields()
        return pattern_builder._build(self.__template_value)
