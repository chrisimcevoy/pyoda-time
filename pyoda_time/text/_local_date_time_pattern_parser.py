# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, final

from pyoda_time._local_date_time import LocalDateTime
from pyoda_time._local_time import LocalTime
from pyoda_time.text import ParseResult
from pyoda_time.text._invalid_pattern_exception import InvalidPatternError
from pyoda_time.text._local_date_pattern_parser import _LocalDatePatternParser
from pyoda_time.text._local_date_time_pattern import LocalDateTimePattern
from pyoda_time.text._local_time_pattern_parser import _LocalTimePatternParser
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._date_pattern_helper import _DatePatternHelper
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.text.patterns._time_pattern_helper import _TimePatternHelper
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from pyoda_time._calendar_system import CalendarSystem
    from pyoda_time._local_date import LocalDate
    from pyoda_time.calendars import Era
    from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
    from pyoda_time.text._i_pattern import IPattern
    from pyoda_time.text.patterns._pattern_cursor import _PatternCursor


@final
@_sealed
@_private
class _LocalDateTimeParseBucket(_ParseBucket[LocalDateTime]):
    _date: _LocalDatePatternParser._LocalDateParseBucket
    _time: _LocalTimePatternParser._LocalTimeParseBucket

    @classmethod
    def _ctor(
        cls, template_value_date: LocalDate, template_value_time: LocalTime, two_digit_year_max: int
    ) -> _LocalDateTimeParseBucket:
        self = super().__new__(cls)
        self._date = _LocalDatePatternParser._LocalDateParseBucket._ctor(template_value_date, two_digit_year_max)
        self._time = _LocalTimePatternParser._LocalTimeParseBucket._ctor(template_value_time)
        return self

    @classmethod
    def _combine_buckets(
        cls,
        used_fields: _PatternFields,
        date_bucket: _LocalDatePatternParser._LocalDateParseBucket,
        time_bucket: _LocalTimePatternParser._LocalTimeParseBucket,
        text: str,
    ) -> ParseResult[LocalDateTime]:
        """Combines the values in a date bucket with the values in a time bucket.

        This would normally be the ``calculate_value`` method, but we want
        to be able to use the same logic when parsing an ``OffsetDateTime``
        and ``ZonedDateTime``.
        """
        # Handle special case of hour = 24
        hour_24: bool = False
        if time_bucket._hours_24 == 24:
            time_bucket._hours_24 = 0
            hour_24 = True

        date_result: ParseResult[LocalDate] = date_bucket._calculate_value(
            used_fields & _PatternFields.ALL_DATE_FIELDS,
            text,
            LocalDateTime,
        )

        if not date_result.success:
            return date_result.convert_error(LocalDateTime)

        time_result: ParseResult[LocalTime] = time_bucket._calculate_value(
            used_fields & _PatternFields.ALL_TIME_FIELDS,
            text,
            LocalDateTime,
        )

        if not time_result.success:
            return time_result.convert_error(LocalDateTime)

        date: LocalDate = date_result.value
        time: LocalTime = time_result.value

        if hour_24:
            if time != LocalTime.midnight:
                return ParseResult._invalid_hour_24(text)
            date = date.plus_days(1)

        return ParseResult.for_value(date + time)

    def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[LocalDateTime]:
        return self._combine_buckets(used_fields, self._date, self._time, value)


def handle_forward_slash(pattern: _PatternCursor, builder: _SteppedPatternBuilder[LocalDateTime]) -> None:
    builder._add_literal(
        expected_text=builder._format_info.date_separator, failure=ParseResult._date_separator_mismatch
    )


def handle_uppercase_t(pattern: _PatternCursor, builder: _SteppedPatternBuilder[LocalDateTime]) -> None:
    builder._add_literal(expected_char="T", failure_selector=ParseResult._mismatched_character)


def handle_colon(pattern: _PatternCursor, builder: _SteppedPatternBuilder[LocalDateTime]) -> None:
    builder._add_literal(
        expected_text=builder._format_info.time_separator, failure=ParseResult._time_separator_mismatch
    )


def get_year(local_date_time: LocalDateTime) -> int:
    return local_date_time.year


def set_year(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._year = value


def get_year_of_era(local_date_time: LocalDateTime) -> int:
    return local_date_time.year_of_era


def set_year_of_era(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._year_of_era = value


def get_month(local_date_time: LocalDateTime) -> int:
    return local_date_time.month


def month_text_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._month_of_year_text = value


def month_number_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._month_of_year_numeric = value


def get_day_of_month(local_date_time: LocalDateTime) -> int:
    return local_date_time.day


def get_day_of_week(local_date_time: LocalDateTime) -> int:
    return local_date_time.day_of_week.value


def get_nanosecond_of_second(local_date_time: LocalDateTime) -> int:
    return local_date_time.nanosecond_of_second


def get_hour(local_date_time: LocalDateTime) -> int:
    return local_date_time.hour


def get_clock_hour_of_half_day(local_date_time: LocalDateTime) -> int:
    return local_date_time.clock_hour_of_half_day


def get_minute(local_date_time: LocalDateTime) -> int:
    return local_date_time.minute


def get_second(local_date_time: LocalDateTime) -> int:
    return local_date_time.second


def get_calendar(local_date_time: LocalDateTime) -> CalendarSystem:
    return local_date_time.calendar


def get_era(local_date_time: LocalDateTime) -> Era:
    return local_date_time.era


def fractional_seconds_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._fractional_seconds = value


def day_of_month_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._day_of_month = value


def day_of_week_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._day_of_week = value


def minutes_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._minutes = value


def seconds_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._seconds = value


def hours_12_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._hours_12 = value


def hours_24_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._hours_24 = value


def am_pm_setter(bucket: _ParseBucket[LocalDateTime], value: int) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._time._am_pm = value


def calendar_setter(bucket: _ParseBucket[LocalDateTime], value: CalendarSystem) -> None:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    bucket._date._calendar = value


def date_bucket_from_bucket(bucket: _ParseBucket[LocalDateTime]) -> _LocalDatePatternParser._LocalDateParseBucket:
    assert isinstance(bucket, _LocalDateTimeParseBucket)
    return bucket._date


def handle_l(cursor: _PatternCursor, builder: _SteppedPatternBuilder[LocalDateTime]) -> None:
    def date_bucket_extractor(bucket: _ParseBucket[LocalDateTime]) -> _LocalDatePatternParser._LocalDateParseBucket:
        assert isinstance(bucket, _LocalDateTimeParseBucket)
        return bucket._date

    def time_bucket_extractor(bucket: _ParseBucket[LocalDateTime]) -> _LocalTimePatternParser._LocalTimeParseBucket:
        assert isinstance(bucket, _LocalDateTimeParseBucket)
        return bucket._time

    def date_extractor(value: LocalDateTime) -> LocalDate:
        return value.date

    def time_extractor(value: LocalDateTime) -> LocalTime:
        return value.time_of_day

    builder._add_embedded_local_partial(
        cursor,
        date_bucket_extractor,
        time_bucket_extractor,
        date_extractor,
        time_extractor,
        None,
        LocalDateTime,
    )


@_sealed
@final
@_private
class _LocalDateTimePatternParser(_IPatternParser[LocalDateTime]):
    """Parser for patterns of ``LocalDateTime`` values."""

    __template_value_date: LocalDate
    __template_value_time: LocalTime
    __two_digit_year_max: int

    __pattern_character_handlers: Mapping[
        str, Callable[[_PatternCursor, _SteppedPatternBuilder[LocalDateTime]], None]
    ] = {
        "%": _SteppedPatternBuilder._handle_percent,
        "'": _SteppedPatternBuilder._handle_quote,
        '"': _SteppedPatternBuilder._handle_quote,
        "\\": _SteppedPatternBuilder._handle_backslash,
        "/": handle_forward_slash,
        "T": handle_uppercase_t,
        "y": _DatePatternHelper._create_year_of_era_handler(get_year_of_era, set_year_of_era, LocalDateTime),
        "u": _SteppedPatternBuilder._handle_padded_field(
            4, _PatternFields.YEAR, -9999, 9999, get_year, set_year, LocalDateTime
        ),
        "M": _DatePatternHelper._create_month_of_year_handler(
            get_month,
            month_text_setter,
            month_number_setter,
            LocalDateTime,
        ),
        "d": _DatePatternHelper._create_day_handler(
            get_day_of_month,
            get_day_of_week,
            day_of_month_setter,
            day_of_week_setter,
            LocalDateTime,
        ),
        ".": _TimePatternHelper._create_period_handler(
            9,
            get_nanosecond_of_second,
            fractional_seconds_setter,
        ),
        ";": _TimePatternHelper._create_comma_dot_handler(9, get_nanosecond_of_second, fractional_seconds_setter),
        ":": handle_colon,
        "h": _SteppedPatternBuilder._handle_padded_field(
            2,
            _PatternFields.HOURS_12,
            1,
            12,
            get_clock_hour_of_half_day,
            hours_12_setter,
            LocalDateTime,
        ),
        "H": _SteppedPatternBuilder._handle_padded_field(
            2,
            _PatternFields.HOURS_24,
            0,
            24,
            get_hour,
            hours_24_setter,
            LocalDateTime,
        ),
        "m": _SteppedPatternBuilder._handle_padded_field(
            2,
            _PatternFields.MINUTES,
            0,
            59,
            get_minute,
            minutes_setter,
            LocalDateTime,
        ),
        "s": _SteppedPatternBuilder._handle_padded_field(
            2,
            _PatternFields.SECONDS,
            0,
            59,
            get_second,
            seconds_setter,
            LocalDateTime,
        ),
        "f": _TimePatternHelper._create_fraction_handler(9, get_nanosecond_of_second, fractional_seconds_setter),
        "F": _TimePatternHelper._create_fraction_handler(9, get_nanosecond_of_second, fractional_seconds_setter),
        "t": _TimePatternHelper._create_am_pm_handler(get_hour, am_pm_setter),
        "c": _DatePatternHelper._create_calendar_handler(get_calendar, calendar_setter),
        "g": _DatePatternHelper._create_era_handler(get_era, date_bucket_from_bucket),
        "l": handle_l,
    }

    @classmethod
    def _ctor(cls, template_value: LocalDateTime, two_digit_year_max: int) -> _LocalDateTimePatternParser:
        _Preconditions._check_argument_range("two_digit_year_max", two_digit_year_max, 0, 99)
        self = super().__new__(cls)
        self.__template_value_date = template_value.date
        self.__template_value_time = template_value.time_of_day
        self.__two_digit_year_max = two_digit_year_max
        return self

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[LocalDateTime]:
        def parse_no_standard_expansion(pattern_text_local: str) -> IPattern[LocalDateTime]:
            def bucket_provider() -> _ParseBucket[LocalDateTime]:
                return _LocalDateTimeParseBucket._ctor(
                    self.__template_value_date, self.__template_value_time, self.__two_digit_year_max
                )

            pattern_builder = _SteppedPatternBuilder[LocalDateTime](
                format_info,
                bucket_provider,
            )
            pattern_builder._parse_custom_pattern(pattern_text_local, self.__pattern_character_handlers)
            pattern_builder._validate_used_fields()
            return pattern_builder._build(self.__template_value_date.at(self.__template_value_time))

        # Nullity check is performed in LocalDateTimePattern
        if len(pattern) == 0:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)

        if len(pattern) == 1:
            match pattern:
                # Invariant standard patterns return cached implementations.
                case "o" | "O":
                    return LocalDateTimePattern._Patterns._bcl_round_trip_pattern_impl
                case "r":
                    return LocalDateTimePattern._Patterns._full_round_trip_pattern_impl
                case "R":
                    return LocalDateTimePattern._Patterns._full_round_trip_without_calendar_impl
                case "s":
                    return LocalDateTimePattern._Patterns._general_iso_pattern_impl
                case "S":
                    return LocalDateTimePattern._Patterns._extended_iso_pattern_impl
                # Other standard patterns expand the pattern text to the appropriate custom pattern.
                # Note: we don't just recurse, as otherwise a FullDateTimePattern of 'F' would cause a stack overflow.
                case "f":
                    return parse_no_standard_expansion(
                        f"{format_info.date_time_format.long_date_pattern} "
                        f"{format_info.date_time_format.short_time_pattern}"
                    )
                case "F":
                    return parse_no_standard_expansion(format_info.date_time_format.full_date_time_pattern)
                case "g":
                    return parse_no_standard_expansion(
                        f"{format_info.date_time_format.short_date_pattern} "
                        f"{format_info.date_time_format.short_time_pattern}"
                    )
                case "G":
                    return parse_no_standard_expansion(
                        f"{format_info.date_time_format.short_date_pattern} "
                        f"{format_info.date_time_format.long_time_pattern}"
                    )
                # Unknown standard patterns fail.
                case _:
                    raise InvalidPatternError(
                        _TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern, LocalDateTime.__name__
                    )

        return parse_no_standard_expansion(pattern)
