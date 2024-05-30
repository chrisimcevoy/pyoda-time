# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Final, _ProtocolMeta, cast, final

from pyoda_time._annual_date import AnnualDate
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


class __AnnualDatePatternMeta(_ProtocolMeta):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "G"  # General, ISO-like
    __bcl_support: _PatternBclSupport[AnnualDate] | None = None

    @property
    def _bcl_support(self) -> _PatternBclSupport[AnnualDate]:
        if self.__bcl_support is None:

            def get_parser(fi: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[AnnualDate]:
                return fi._annual_date_pattern_parser

            self.__bcl_support = _PatternBclSupport(self.__DEFAULT_FORMAT_PATTERN, get_parser)
        return self.__bcl_support

    @property
    def iso(self) -> AnnualDatePattern:
        """Gets an invariant annual date pattern which is compatible with the month/day part of ISO-8601.

        This corresponds to the text pattern "MM'-'dd".

        :return: An invariant annual date pattern which is compatible with the month/day part of ISO-8601.
        """
        return AnnualDatePattern._Patterns._iso_pattern_impl


@final
@_sealed
@_private
class AnnualDatePattern(IPattern[AnnualDate], metaclass=__AnnualDatePatternMeta):
    """Represents a pattern for parsing and formatting ``AnnualDate`` values."""

    _DEFAULT_TEMPLATE_VALUE: Final[AnnualDate] = AnnualDate(1, 1)

    __pattern_text: str
    __format_info: _PyodaFormatInfo
    __template_value: AnnualDate
    __underlying_pattern: _IPartialPattern[AnnualDate]

    class __PatternMeta(type):
        @property
        def _iso_pattern_impl(self) -> AnnualDatePattern:
            return AnnualDatePattern.create_with_invariant_culture("MM'-'dd")

    class _Patterns(metaclass=__PatternMeta):
        pass

    @property
    def _underlying_pattern(self) -> _IPartialPattern[AnnualDate]:
        return self.__underlying_pattern

    @property
    def pattern_text(self) -> str:
        return self.__pattern_text

    @property
    def template_value(self) -> AnnualDate:
        return self.__template_value

    @classmethod
    def __ctor(
        cls,
        pattern_text: str,
        format_info: _PyodaFormatInfo,
        template_value: AnnualDate,
        pattern: _IPartialPattern[AnnualDate],
    ) -> AnnualDatePattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__format_info = format_info
        self.__template_value = template_value
        self.__underlying_pattern = pattern
        return self

    def parse(self, text: str) -> ParseResult[AnnualDate]:
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Pyoda Time itself). Even errors such as the argument
        being None are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self.__underlying_pattern.parse(text)

    def format(self, value: AnnualDate) -> str:
        """Formats the given annual date as text according to the rules of this pattern.

        :param value: The annual date to format.
        :return: The annual date formatted according to this pattern.
        """
        return self.__underlying_pattern.format(value)

    def append_format(self, value: AnnualDate, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        return self.__underlying_pattern.append_format(value, builder)

    @classmethod
    def _create(cls, pattern_text: str, format_info: _PyodaFormatInfo, template_value: AnnualDate) -> AnnualDatePattern:
        """Creates a pattern for the given pattern text, format info, and template value.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: The format info to use in the pattern
        :param template_value: Template value to use for unspecified fields
        :return: A pattern for parsing and formatting annual dates.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        # Use the "fixed" parser for the common case of the default template value.
        if template_value == cls._DEFAULT_TEMPLATE_VALUE:
            pattern = format_info._annual_date_pattern_parser._parse_pattern(pattern_text)
        else:
            from ._annual_date_pattern_parser import _AnnualDatePatternParser

            pattern = _AnnualDatePatternParser._ctor(template_value).parse_pattern(pattern_text, format_info)
        pattern = pattern._underlying_pattern if isinstance(pattern, AnnualDatePattern) else pattern
        partial_pattern = cast(_IPartialPattern[AnnualDate], pattern)
        return cls.__ctor(pattern_text, format_info, template_value, partial_pattern)

    @classmethod
    def create(
        cls,
        pattern_text: str,
        culture_info: CultureInfo = CultureInfo.current_culture,
        template_value: AnnualDate | None = None,
    ) -> AnnualDatePattern:
        """Creates a pattern for the given pattern text and culture, with a template value of 2000-01-01.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for.
        :param culture_info: The culture to use in the pattern; defaults to the current culture.
        :param template_value: Template value to use for unspecified fields. Defaults to 2001-01-01 if not provided.
        :return: A pattern for parsing and formatting annual dates.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        if template_value is None:
            template_value = cls._DEFAULT_TEMPLATE_VALUE
        return cls._create(pattern_text, _PyodaFormatInfo._get_format_info(culture_info), template_value)

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> AnnualDatePattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting annual dates.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.current_info, cls._DEFAULT_TEMPLATE_VALUE)

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> AnnualDatePattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting annual dates.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.invariant_info, cls._DEFAULT_TEMPLATE_VALUE)

    def __with_format_info(self, format_info: _PyodaFormatInfo) -> AnnualDatePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified localization
        information.

        :param format_info: The localization information to use in the new pattern.
        :return: A new pattern with the given localization information.
        """
        return self._create(self.__pattern_text, format_info, self.__template_value)

    def with_culture(self, culture_info: CultureInfo) -> AnnualDatePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__with_format_info(_PyodaFormatInfo._get_format_info(culture_info))

    def with_template_value(self, template_value: AnnualDate) -> AnnualDatePattern:
        """Creates a pattern like this one, but with the specified template value.

        :param template_value: The template value for the new pattern, used to fill in unspecified fields.
        :return: A new pattern with the given template value.
        """
        return self._create(self.__pattern_text, self.__format_info, template_value)
