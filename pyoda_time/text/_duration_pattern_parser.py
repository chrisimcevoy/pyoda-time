# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Callable, Final, Mapping, cast, final

from pyoda_time._duration import Duration
from pyoda_time._pyoda_constants import PyodaConstants
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text import InvalidPatternError, ParseResult
from pyoda_time.text._format_helper import _FormatHelper
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.text.patterns._time_pattern_helper import _TimePatternHelper
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _sealed, _towards_zero_division
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class _DurationPatternParser(_IPatternParser[Duration]):
    @staticmethod
    def _get_positive_nanosecond_of_second(duration: Duration) -> int:
        return _csharp_modulo(abs(duration.nanosecond_of_day), PyodaConstants.NANOSECONDS_PER_SECOND)

    @staticmethod
    def _create_total_handler(
        field: _PatternFields, nanoseconds_per_unit: int, units_per_day: int, max_value: int
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[Duration]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Duration]) -> None:
            # Needs to be big enough for 92771293593600 seconds
            count = pattern.get_repeat_count(maximum_count=14)  # 13 in Pyoda Time
            # AddField would throw an inappropriate exception here, so handle it specially.
            if (builder._used_fields & _PatternFields.TOTAL_DURATION) != _PatternFields.NONE:
                raise InvalidPatternError(_TextErrorMessages.MULTIPLE_CAPITAL_DURATION_FIELDS)
            builder._add_field(field=field, character_in_pattern=pattern.current)
            builder._add_field(field=_PatternFields.TOTAL_DURATION, character_in_pattern=pattern.current)
            # Noda Time uses int64 variants of certain methods here, but in Python we just deal with int.
            builder._add_parse_value_action(
                minimum_digits=count,
                maximum_digits=14,  # 13 in Pyoda Time
                pattern_char=pattern.current,
                minimum_value=0,
                maximum_value=max_value,
                value_setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_units(
                    units=value, nanoseconds_per_unit=nanoseconds_per_unit
                ),
                type_=Duration,
            )
            builder._add_format_action(
                lambda value, sb: _FormatHelper._left_pad_non_negative(
                    _DurationPatternParser.__get_positive_nanosecond_units(value, nanoseconds_per_unit, units_per_day),
                    count,
                    sb,
                )
            )

        return handler

    @staticmethod
    def _create_day_handler() -> Callable[[_PatternCursor, _SteppedPatternBuilder[Duration]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Duration]) -> None:
            count = pattern.get_repeat_count(10)  # Enough for 1073741824
            # AddField would throw an inappropriate exception here, so handle it specially.
            if (builder._used_fields & _PatternFields.TOTAL_DURATION) != _PatternFields.NONE:
                raise InvalidPatternError(_TextErrorMessages.MULTIPLE_CAPITAL_DURATION_FIELDS)
            builder._add_field(field=_PatternFields.DAY_OF_MONTH, character_in_pattern=pattern.current)
            builder._add_field(field=_PatternFields.TOTAL_DURATION, character_in_pattern=pattern.current)
            builder._add_parse_value_action(
                minimum_digits=count,
                maximum_digits=10,
                pattern_char=pattern.current,
                minimum_value=0,
                maximum_value=1073741824,
                value_setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_days(
                    value
                ),
                type_=Duration,
            )
            builder.add_format_left_pad(
                count=count,
                selector=lambda duration: duration._floor_days
                if duration._floor_days >= 0
                # Round towards 0.
                else -duration._floor_days
                if duration._nanosecond_of_floor_day == 0
                else -(duration._floor_days + 1),
                assume_non_negative=True,
                assume_fits_in_count=False,
            )

        return handler

    @staticmethod
    def _create_partial_handler(
        field: _PatternFields, nanoseconds_per_unit: int, units_per_container: int
    ) -> Callable[[_PatternCursor, _SteppedPatternBuilder[Duration]], None]:
        def handler(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Duration]) -> None:
            count = pattern.get_repeat_count(2)
            builder._add_field(field, pattern.current)
            builder._add_parse_value_action(
                minimum_digits=count,
                maximum_digits=2,
                pattern_char=pattern.current,
                minimum_value=0,
                maximum_value=units_per_container - 1,
                value_setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_units(
                    value, nanoseconds_per_unit
                ),
                type_=Duration,
            )
            # This is never used for anything larger than a day, so the day part is irrelevant.
            builder.add_format_left_pad(
                count=count,
                selector=lambda duration: _csharp_modulo(
                    _towards_zero_division(abs(duration.nanosecond_of_day), nanoseconds_per_unit), units_per_container
                ),
                assume_non_negative=True,
                assume_fits_in_count=(count == 2),
            )

        return handler

    @staticmethod
    def _handle_plus(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Duration]) -> None:
        builder._add_field(_PatternFields.SIGN, pattern.current)
        builder.add_required_sign(
            sign_setter=lambda bucket, positive: setattr(bucket, "_is_negative", not positive),
            non_negative_predicate=lambda duration: duration._floor_days >= 0,
        )

    @staticmethod
    def _handle_minus(pattern: _PatternCursor, builder: _SteppedPatternBuilder[Duration]) -> None:
        builder._add_field(_PatternFields.SIGN, pattern.current)
        builder.add_negative_only_sign(
            sign_setter=lambda bucket, positive: setattr(bucket, "_is_negative", not positive),
            non_negative_predicate=lambda duration: duration._floor_days >= 0,
        )

    @staticmethod
    def __get_positive_nanosecond_units(duration: Duration, nanoseconds_per_unit: int, units_per_day: int) -> int:
        floor_days = duration._floor_days
        if floor_days >= 0:
            return floor_days * units_per_day + _towards_zero_division(
                duration._nanosecond_of_floor_day, nanoseconds_per_unit
            )

        nanosecond_of_day = duration.nanosecond_of_day
        # If it's not an exact number of days, FloorDays will overshoot (negatively) by 1.
        if nanosecond_of_day == 0:
            negative_value = floor_days * units_per_day
        else:
            negative_value = (floor_days + 1) * units_per_day + _towards_zero_division(
                nanosecond_of_day, nanoseconds_per_unit
            )
        return -negative_value

    class _DurationParseBucket(_ParseBucket[Duration]):
        def __init__(self) -> None:
            self._is_negative = False
            self.__current_nanos = 0

        def _add_nanoseconds(self, nanoseconds: int) -> None:
            self.__current_nanos += nanoseconds

        def _add_days(self, days: int) -> None:
            self.__current_nanos += days * PyodaConstants.NANOSECONDS_PER_DAY

        def _add_units(self, units: int, nanoseconds_per_unit: int) -> None:
            self.__current_nanos += units * nanoseconds_per_unit

        def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[Duration]:
            if self._is_negative:
                self.__current_nanos = -self.__current_nanos
            if self.__current_nanos < Duration._MIN_NANOSECONDS or self.__current_nanos > Duration._MAX_NANOSECONDS:
                return ParseResult._for_invalid_value_post_parse(
                    value, _TextErrorMessages.OVERALL_VALUE_OUT_OF_RANGE, Duration.__name__
                )
            return ParseResult.for_value(Duration.from_nanoseconds(self.__current_nanos))

    __PATTERN_CHARACTER_HANDLERS: Final[
        Mapping[str, Callable[[_PatternCursor, _SteppedPatternBuilder[Duration]], None]]
    ] = {
        "%": _SteppedPatternBuilder._handle_percent,
        "'": _SteppedPatternBuilder._handle_quote,
        '"': _SteppedPatternBuilder._handle_quote,
        "\\": _SteppedPatternBuilder._handle_backslash,
        ".": _TimePatternHelper._create_period_handler(
            max_count=9,
            getter=_get_positive_nanosecond_of_second,
            setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_nanoseconds(
                value
            ),
        ),
        ":": lambda pattern, builder: builder._add_literal(
            expected_text=builder._format_info.time_separator,
            failure=ParseResult._time_separator_mismatch,
        ),
        "D": _create_day_handler(),
        "H": _create_total_handler(
            field=_PatternFields.HOURS_24,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_HOUR,
            units_per_day=PyodaConstants.HOURS_PER_DAY,
            max_value=25769803776,  # 402653184L in Noda Time
        ),
        "h": _create_partial_handler(
            field=_PatternFields.HOURS_24,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_HOUR,
            units_per_container=PyodaConstants.HOURS_PER_DAY,
        ),
        "M": _create_total_handler(
            field=_PatternFields.MINUTES,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_MINUTE,
            units_per_day=PyodaConstants.MINUTES_PER_DAY,
            max_value=1546188226560,  # 24159191040L in Noda Time
        ),
        "m": _create_partial_handler(
            field=_PatternFields.MINUTES,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_MINUTE,
            units_per_container=PyodaConstants.MINUTES_PER_HOUR,
        ),
        "S": _create_total_handler(
            field=_PatternFields.SECONDS,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_SECOND,
            units_per_day=PyodaConstants.SECONDS_PER_DAY,
            max_value=92771293593600,  # 1449551462400L in Noda Time
        ),
        "s": _create_partial_handler(
            field=_PatternFields.SECONDS,
            nanoseconds_per_unit=PyodaConstants.NANOSECONDS_PER_SECOND,
            units_per_container=PyodaConstants.SECONDS_PER_MINUTE,
        ),
        "f": _TimePatternHelper._create_fraction_handler(
            max_count=9,
            getter=_get_positive_nanosecond_of_second,
            setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_nanoseconds(
                value
            ),
        ),
        "F": _TimePatternHelper._create_fraction_handler(
            max_count=9,
            getter=_get_positive_nanosecond_of_second,
            setter=lambda bucket, value: cast(_DurationPatternParser._DurationParseBucket, bucket)._add_nanoseconds(
                value
            ),
        ),
        "+": _handle_plus,
        "-": _handle_minus,
    }

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[Duration]:
        _Preconditions._check_not_null(pattern, "pattern")
        if not pattern:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)

        if len(pattern) == 1:
            from ._duration_pattern import DurationPattern

            match pattern:
                case "o":
                    return DurationPattern._Patterns._roundtrip_pattern_impl
                case "j":
                    return DurationPattern._Patterns._json_roundtrip_pattern_impl
                case _:
                    raise InvalidPatternError(_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern, Duration.__name__)

        pattern_builder = _SteppedPatternBuilder(format_info, self._DurationParseBucket)
        pattern_builder._parse_custom_pattern(pattern, self.__PATTERN_CHARACTER_HANDLERS)
        # Somewhat random sample, admittedly...
        return pattern_builder._build(
            Duration.from_hours(1)
            + Duration.from_minutes(30)
            + Duration.from_seconds(5)
            + Duration.from_milliseconds(500)
        )
