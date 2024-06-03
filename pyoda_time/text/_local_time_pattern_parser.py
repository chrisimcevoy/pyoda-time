# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Callable, Final, Mapping, final

from pyoda_time._local_time import LocalTime
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text import InvalidPatternError, ParseResult
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._local_time_pattern import LocalTimePattern
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.text.patterns._time_pattern_helper import _TimePatternHelper
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _private, _sealed, _towards_zero_division


def hours_12_getter(value: LocalTime) -> int:
    return value.clock_hour_of_half_day


def hours_12_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._hours_12 = value


def hours_24_getter(value: LocalTime) -> int:
    return value.hour


def hours_24_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._hours_24 = value


def minutes_getter(value: LocalTime) -> int:
    return value.minute


def minutes_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._minutes = value


def seconds_getter(value: LocalTime) -> int:
    return value.second


def seconds_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._seconds = value


def am_pm_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._am_pm = value


def nanosecond_of_second_getter(value: LocalTime) -> int:
    return value.nanosecond_of_second


def fractional_seconds_setter(bucket: _ParseBucket[LocalTime], value: int) -> None:
    assert isinstance(bucket, _LocalTimePatternParser._LocalTimeParseBucket)
    bucket._fractional_seconds = value


def _handle_colon(pattern: _PatternCursor, builder: _SteppedPatternBuilder[LocalTime]) -> None:
    builder._add_literal(
        expected_text=builder._format_info.time_separator,
        failure=ParseResult._time_separator_mismatch,
    )


@final
@_sealed
@_private
class _LocalTimePatternParser(_IPatternParser[LocalTime]):
    """Pattern parser for ``LocalTime`` values."""

    __template_value: LocalTime

    __pattern_character_handlers: Final[
        Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[LocalTime]], None]]
    ] = {
        "%": _SteppedPatternBuilder._handle_percent,
        "'": _SteppedPatternBuilder._handle_quote,
        '"': _SteppedPatternBuilder._handle_quote,
        "\\": _SteppedPatternBuilder._handle_backslash,
        ".": _TimePatternHelper._create_period_handler(9, nanosecond_of_second_getter, fractional_seconds_setter),
        ";": _TimePatternHelper._create_comma_dot_handler(9, nanosecond_of_second_getter, fractional_seconds_setter),
        ":": _handle_colon,
        "h": _SteppedPatternBuilder._handle_padded_field(
            2, _PatternFields.HOURS_12, 1, 12, hours_12_getter, hours_12_setter, LocalTime
        ),
        "H": _SteppedPatternBuilder._handle_padded_field(
            2, _PatternFields.HOURS_24, 0, 23, hours_24_getter, hours_24_setter, LocalTime
        ),
        "m": _SteppedPatternBuilder._handle_padded_field(
            2, _PatternFields.MINUTES, 0, 59, minutes_getter, minutes_setter, LocalTime
        ),
        "s": _SteppedPatternBuilder._handle_padded_field(
            2, _PatternFields.SECONDS, 0, 59, seconds_getter, seconds_setter, LocalTime
        ),
        "f": _TimePatternHelper._create_fraction_handler(9, nanosecond_of_second_getter, fractional_seconds_setter),
        "F": _TimePatternHelper._create_fraction_handler(9, nanosecond_of_second_getter, fractional_seconds_setter),
        "t": _TimePatternHelper._create_am_pm_handler(hours_24_getter, am_pm_setter),
    }

    @classmethod
    def _ctor(cls, template_value: LocalTime) -> _LocalTimePatternParser:
        self = super().__new__(cls)
        self.__template_value = template_value
        return self

    # Note: public to implement the interface. It does no harm, and it's simpler than using explicit
    # interface implementation.
    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[LocalTime]:
        def parse_no_standard_expansion(pattern_text_local: str) -> IPattern[LocalTime]:
            def bucket_provider() -> _LocalTimePatternParser._LocalTimeParseBucket:
                return self._LocalTimeParseBucket._ctor(self.__template_value)

            pattern_builder = _SteppedPatternBuilder(format_info, bucket_provider)
            pattern_builder._parse_custom_pattern(pattern_text_local, self.__pattern_character_handlers)
            pattern_builder._validate_used_fields()
            return pattern_builder._build(self.__template_value)

        # Nullity check is performed in LocalTimePattern.
        if len(pattern) == 0:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)

        if len(pattern) == 1:
            match pattern:
                # Invariant standard patterns return cached implementations.
                case "o":
                    return LocalTimePattern._Patterns._extended_iso_pattern_impl
                case "O":
                    return LocalTimePattern._Patterns._long_extended_iso_pattern_impl
                # Other standard patterns expand the pattern text to the appropriate custom pattern.
                # Note: we don't just recurse, as otherwise a ShortTimePattern of 't' (for example)
                # would cause a stack overflow.
                case "t":
                    return parse_no_standard_expansion(format_info.date_time_format.short_time_pattern)
                case "T":
                    return parse_no_standard_expansion(format_info.date_time_format.long_time_pattern)
                case "r":
                    return parse_no_standard_expansion("HH:mm:ss.FFFFFFFFF")
                case _:
                    raise InvalidPatternError(_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern, LocalTime.__name__)

        return parse_no_standard_expansion(pattern)

    @_private
    class _LocalTimeParseBucket(_ParseBucket[LocalTime]):
        """Bucket to put parsed values in, ready for later result calculation.

        This type is also used by LocalDateTimePattern to store and calculate values.
        """

        _template_value: LocalTime
        _fractional_seconds: int
        _hours_24: int
        _hours_12: int
        _minutes: int
        _seconds: int
        _am_pm: int

        @classmethod
        def _ctor(cls, template_value: LocalTime) -> _LocalTimePatternParser._LocalTimeParseBucket:
            self = super().__new__(cls)
            self._template_value = template_value
            # By copying these out of the template value now, we don't have to use any conditional
            # logic later on.
            # The minutes in the range [0, 59].
            self._minutes = template_value.minute
            # The seconds in the range [0, 59].
            self._seconds = template_value.second
            # The fractions of a second in nanoseconds, in the range [0, 999999999]
            self._fractional_seconds = template_value.nanosecond_of_second

            # The following attributes are all defaulted to 0, because in C#
            # they are internal non-nullable fields which aren't set by the constructor.
            # The hours in the range [0, 23].
            self._hours_24 = 0
            # The hours in the range [1, 12].
            self._hours_12 = 0
            # AM (0) or PM (1) - or "take from the template" (2). The latter is used in situations
            # where we're parsing but there is no AM or PM designator.
            self._am_pm = 0
            return self

        def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[LocalTime]:
            """Calculates the value from the parsed pieces."""
            return self._calculate_value(used_fields, value, LocalTime)

        __HOUR_24_MINUTE_SECOND: Final[_PatternFields] = (
            _PatternFields.HOURS_24 | _PatternFields.MINUTES | _PatternFields.SECONDS
        )
        __ALL_TIME_FIELDS_EXCEPT_FRACTIONAL_SECONDS: Final[_PatternFields] = (
            _PatternFields.ALL_TIME_FIELDS ^ _PatternFields.FRACTIONAL_SECONDS
        )

        def _calculate_value(
            self, used_fields: _PatternFields, text: str, eventual_result_type: type
        ) -> ParseResult[LocalTime]:
            # Optimize common situation for ISO values.
            if (used_fields & self.__ALL_TIME_FIELDS_EXCEPT_FRACTIONAL_SECONDS) == self.__HOUR_24_MINUTE_SECOND:
                return ParseResult.for_value(
                    LocalTime._from_hour_minute_second_nanosecond_trusted(
                        self._hours_24,
                        self._minutes,
                        self._seconds,
                        self._fractional_seconds,
                    )
                )

            # If this bucket was created from an embedded pattern, it's already been computed.
            if used_fields.has_any(_PatternFields.EMBEDDED_TIME):
                return ParseResult.for_value(
                    LocalTime._from_hour_minute_second_nanosecond_trusted(
                        self._hours_24,
                        self._minutes,
                        self._seconds,
                        self._fractional_seconds,
                    )
                )

            if self._am_pm == 2:
                self._am_pm = _towards_zero_division(self._template_value.hour, 12)

            failure, hour = self.__determine_hour(
                used_fields,
                text,
                eventual_result_type,
            )

            if failure is not None:
                return failure

            return ParseResult.for_value(
                LocalTime._from_hour_minute_second_nanosecond_trusted(
                    hour,
                    self._minutes,
                    self._seconds,
                    self._fractional_seconds,
                )
            )

        def __determine_hour(
            self, used_fields: _PatternFields, text: str, eventual_result_type: type
        ) -> tuple[ParseResult[LocalTime] | None, int]:
            hour = 0

            if used_fields.has_any(_PatternFields.HOURS_24):
                if used_fields.has_all(_PatternFields.HOURS_12 | _PatternFields.HOURS_24):
                    if _csharp_modulo(self._hours_12, 12) != _csharp_modulo(self._hours_24, 12):
                        return ParseResult._inconsistent_values(text, "H", "h", eventual_result_type), hour
                if used_fields.has_any(_PatternFields.AM_PM):
                    if _towards_zero_division(self._hours_24, 12) != self._am_pm:
                        return ParseResult._inconsistent_values(text, "H", "t", eventual_result_type), hour
                return None, self._hours_24

            # Okay, it's definitely valid - but we've still got 8 possibilities for what's been specified.
            flags = used_fields & (_PatternFields.HOURS_12 | _PatternFields.AM_PM)
            if flags == _PatternFields.HOURS_12 | _PatternFields.AM_PM:
                hour = _csharp_modulo(self._hours_12, 12) + self._am_pm * 12
            elif flags == _PatternFields.HOURS_12:
                # Preserve AM/PM from template value
                hour = _csharp_modulo(self._hours_12, 12) + _towards_zero_division(self._template_value.hour, 12) * 12
            elif flags == _PatternFields.AM_PM:
                # Preserve 12-hour hour of day from template value, use specified AM/PM
                hour = _csharp_modulo(self._template_value.hour, 12) + self._am_pm * 12
            elif flags == _PatternFields.NONE:
                hour = self._template_value.hour

            return None, hour
