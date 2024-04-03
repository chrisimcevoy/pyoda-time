# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Final, Self, final

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._instant import Instant
from pyoda_time._local_date_time import LocalDateTime
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._invalid_pattern_exception import InvalidPatternError
from pyoda_time.text._local_date_time_pattern import LocalDateTimePattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text._text_error_messages import _TextErrorMessages
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class _InstantPatternParser(_IPatternParser[Instant]):
    """Pattern parsing support for ``Instant``.

    Supported standard patterns:
        * g: general; the UTC ISO-8601 instant in the style uuuu-MM-ddTHH:mm:ssZ
    """

    __GENERAL_PATTERN_TEXT: Final[str] = "uuuu'-'MM'-'dd'T'HH':'mm':'ss'Z'"
    _BEFORE_MIN_VALUE_TEXT: Final[str] = "StartOfTime"
    _AFTER_MIN_VALUE_TEXT: Final[str] = "EndOfTime"

    __local_template_value: LocalDateTime
    __two_digit_year_max: int

    @classmethod
    def _ctor(cls, template_value: Instant, two_digit_year_max: int) -> _InstantPatternParser:
        self = super().__new__(cls)
        self.__local_template_value = template_value.in_utc().local_date_time
        self.__two_digit_year_max = two_digit_year_max
        return self

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[Instant]:
        _Preconditions._check_not_null(pattern, "pattern")
        if len(pattern) == 0:
            raise InvalidPatternError(_TextErrorMessages.FORMAT_STRING_EMPTY)
        if len(pattern) == 1:
            match pattern[0]:
                # Simplest way of handling the general pattern...
                case "g":
                    pattern = self.__GENERAL_PATTERN_TEXT
                case _:
                    raise InvalidPatternError(_TextErrorMessages.UNKNOWN_STANDARD_FORMAT, pattern, Instant.__name__)

        local_pattern: IPattern[LocalDateTime] = LocalDateTimePattern._create(
            pattern, format_info, self.__local_template_value, self.__two_digit_year_max
        )._underlying_pattern
        return self.__LocalDateTimePatternAdapter._ctor(local_pattern)

    @_sealed
    @final
    @_private
    class __LocalDateTimePatternAdapter(IPattern[Instant]):
        """This not only converts between LocalDateTime and Instant; it also handles infinity."""

        __pattern: IPattern[LocalDateTime]

        @classmethod
        def _ctor(cls, pattern: IPattern[LocalDateTime]) -> Self:
            self = super().__new__(cls)
            self.__pattern = pattern
            return self

        def format(self, value: Instant) -> str:
            # We don't need to be able to parse before-min/after-max values, but it's convenient to be
            # able to format them - mostly for the sake of testing (but also for ZoneInterval).
            if value._is_valid:
                return self.__pattern.format(value.in_utc().local_date_time)
            if value == Instant._before_min_value():
                return _InstantPatternParser._BEFORE_MIN_VALUE_TEXT
            return _InstantPatternParser._AFTER_MIN_VALUE_TEXT

        def append_format(self, value: Instant, builder: StringBuilder) -> StringBuilder:
            return self.__pattern.append_format(value.in_utc().local_date_time, builder)

        def parse(self, text: str) -> ParseResult[Instant]:
            def to_instant(value: LocalDateTime) -> Instant:
                return Instant._ctor(days=value.date._days_since_epoch, nano_of_day=value.nanosecond_of_day)

            return self.__pattern.parse(text).convert(to_instant)
