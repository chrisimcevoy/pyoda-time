# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Final, cast, final

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._local_date import LocalDate
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._local_date_pattern_parser import _LocalDatePatternParser
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class LocalDatePattern(IPattern[LocalDate]):
    """Represents a pattern for parsing and formatting ``Instant`` values."""

    _DEFAULT_TWO_DIGIT_YEAR_MAX: Final[int] = 30
    _DEFAULT_TEMPLATE_VALUE: Final[LocalDate] = LocalDate(year=2000, month=1, day=1)

    __pattern_text: str
    __format_info: _PyodaFormatInfo
    __template_value: LocalDate
    __two_digit_year_max: int
    __underlying_pattern: _IPartialPattern[LocalDate]

    @property
    def _underlying_pattern(self) -> _IPartialPattern[LocalDate]:
        """Returns the pattern that this object delegates to.

        Mostly useful to avoid this public class implementing an internal interface.
        """
        return self.__underlying_pattern

    @property
    def pattern_text(self) -> str:
        """Gets the pattern text for this pattern, as supplied on creation.

        :return: The pattern text for this pattern, as supplied on creation.
        """
        return self.__pattern_text

    @property
    def template_value(self) -> LocalDate:
        """Gets the value used as a template for parsing: any field values unspecified
        in the pattern are taken from the template.

        :return: The value used as a template for parsing.
        """
        return self.__template_value

    @classmethod
    def __ctor(
        cls,
        pattern_text: str,
        format_info: _PyodaFormatInfo,
        template_value: LocalDate,
        two_digit_year_max: int,
        pattern: _IPartialPattern[LocalDate],
    ) -> LocalDatePattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__format_info = format_info
        self.__template_value = template_value
        self.__two_digit_year_max = two_digit_year_max
        self.__underlying_pattern = pattern
        return self

    def parse(self, text: str) -> ParseResult[LocalDate]:
        raise NotImplementedError

    def format(self, value: LocalDate) -> str:
        raise NotImplementedError

    def append_format(self, value: LocalDate, builder: StringBuilder) -> StringBuilder:
        raise NotImplementedError

    @classmethod
    def _create(
        cls, pattern_text: str, format_info: _PyodaFormatInfo, template_value: LocalDate, two_digit_year_max: int
    ) -> LocalDatePattern:
        """Creates a pattern for the given pattern text, format info, and template value.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: The format info to use in the pattern
        :param template_value: Template value to use for unspecified fields
        :param two_digit_year_max: Maximum two-digit-year in the template to treat as the current century.
        :return: A pattern for parsing and formatting local dates.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        # Use the "fixed" parser for the common case of the default template value.
        if template_value == cls._DEFAULT_TEMPLATE_VALUE and two_digit_year_max == cls._DEFAULT_TWO_DIGIT_YEAR_MAX:
            pattern = format_info._local_date_pattern_parser._parse_pattern(pattern_text)
        else:
            pattern = _LocalDatePatternParser._ctor(template_value, two_digit_year_max).parse_pattern(
                pattern_text, format_info
            )
        # If ParsePattern returns a standard pattern instance, we need to get the underlying partial pattern.
        if isinstance(pattern, LocalDatePattern):
            pattern = pattern._underlying_pattern
        partial_pattern = cast(_IPartialPattern[LocalDate], pattern)
        return LocalDatePattern.__ctor(pattern_text, format_info, template_value, two_digit_year_max, partial_pattern)
