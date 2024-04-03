# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Final, _ProtocolMeta, cast, final

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._local_date_time import LocalDateTime
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern, T
from pyoda_time.text._local_date_pattern import LocalDatePattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


class _LocalDateTimePatternMeta(type):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "G"  # General (long time)
    __pattern_bcl_support: _PatternBclSupport[LocalDateTime] | None = None

    @property
    def _pattern_bcl_support(self) -> _PatternBclSupport[LocalDateTime]:
        if self.__pattern_bcl_support is None:

            def pattern_parser(format_info: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[LocalDateTime]:
                return format_info._local_date_time_pattern_parser

            self.__pattern_bcl_support = _PatternBclSupport(self.__DEFAULT_FORMAT_PATTERN, pattern_parser)
        return self.__pattern_bcl_support


class _CombinedMeta(_ProtocolMeta, _LocalDateTimePatternMeta):
    """Intermediary class which prevents a metaclass conflict."""


@_sealed
@final
@_private
class LocalDateTimePattern(IPattern[LocalDateTime], metaclass=_CombinedMeta):
    """Represents a pattern for parsing and formatting ``LocalDateTime`` values."""

    _DEFAULT_TEMPLATE_VALUE: Final[LocalDateTime] = LocalDateTime(2000, 1, 1, 0, 0)

    __pattern_text: str
    __format_info: _PyodaFormatInfo
    __underlying_pattern: _IPartialPattern[LocalDateTime]
    __template_value: LocalDateTime
    __two_digit_year_max: int

    class _PatternsMeta(type):
        @property
        def _general_iso_pattern_impl(self) -> LocalDateTimePattern:
            raise NotImplementedError

        @property
        def _extended_iso_pattern_impl(self) -> LocalDateTimePattern:
            raise NotImplementedError

        @property
        def _bcl_round_trip_pattern_impl(self) -> LocalDateTimePattern:
            raise NotImplementedError

        @property
        def _full_round_trip_without_calendar_impl(self) -> LocalDateTimePattern:
            raise NotImplementedError

        @property
        def _full_round_trip_pattern_impl(self) -> LocalDateTimePattern:
            raise NotImplementedError

    class _Patterns(metaclass=_PatternsMeta):
        pass

    @property
    def _underlying_pattern(self) -> _IPartialPattern[LocalDateTime]:
        """Returns the pattern that this object delegates to.

        Mostly useful to avoid this public class implementing an internal interface.
        """
        return self.__underlying_pattern

    @classmethod
    def __ctor(
        cls,
        pattern_text: str,
        format_info: _PyodaFormatInfo,
        template_value: LocalDateTime,
        two_digit_year_max: int,
        pattern: _IPartialPattern[LocalDateTime],
    ) -> LocalDateTimePattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__format_info = format_info
        self.__underlying_pattern = pattern
        self.__template_value = template_value
        self.__two_digit_year_max = two_digit_year_max
        return self

    def parse(self, text: str) -> ParseResult[T]:
        raise NotImplementedError

    def format(self, value: LocalDateTime) -> str:
        raise NotImplementedError

    def append_format(self, value: LocalDateTime, builder: StringBuilder) -> StringBuilder:
        raise NotImplementedError

    @classmethod
    def _create(
        cls, pattern_text: str, format_info: _PyodaFormatInfo, template_value: LocalDateTime, two_digit_year_max: int
    ) -> LocalDateTimePattern:
        """Creates a pattern for the given pattern text, format info, and template value.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: The format info to use in the pattern
        :param template_value: Template value to use for unspecified fields
        :param two_digit_year_max: Maximum two-digit-year in the template to treat as the current century.
        :return: A pattern for parsing and formatting local date/times.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        # Use the "fixed" parser for the common case of the default template value.
        pattern: IPattern[LocalDateTime]
        if (
            template_value == cls._DEFAULT_TEMPLATE_VALUE
            and two_digit_year_max == LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX
        ):
            pattern = format_info._local_date_time_pattern_parser._parse_pattern(pattern_text)
        else:
            from pyoda_time.text._local_date_time_pattern_parser import _LocalDateTimePatternParser

            pattern = _LocalDateTimePatternParser._ctor(template_value, two_digit_year_max).parse_pattern(
                pattern_text, format_info
            )
        # If ParsePattern returns a standard pattern instance, we need to get the underlying partial pattern.
        if isinstance(pattern, LocalDateTimePattern):
            pattern = pattern.__underlying_pattern
        partial_pattern: _IPartialPattern[LocalDateTime] = cast(_IPartialPattern[LocalDateTime], pattern)
        return LocalDateTimePattern.__ctor(
            pattern_text, format_info, template_value, two_digit_year_max, partial_pattern
        )
