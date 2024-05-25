# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Final, _ProtocolMeta, final

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._instant import Instant
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._instant_pattern_parser import _InstantPatternParser
from pyoda_time.text._local_date_pattern import LocalDatePattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


class _InstantPatternMeta(type):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "g"
    __bcl_support: _PatternBclSupport[Instant] | None = None

    @property
    def _bcl_support(self) -> _PatternBclSupport[Instant]:
        if self.__bcl_support is None:

            def get_instant_pattern_parser(fi: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[Instant]:
                return fi._instant_pattern_parser

            self.__bcl_support = _PatternBclSupport(
                self.__DEFAULT_FORMAT_PATTERN,
                get_instant_pattern_parser,
            )
        return self.__bcl_support

    @property
    def general(cls) -> InstantPattern:
        """Gets the general pattern, which always uses an invariant culture. The general pattern represents an instant
        as a UTC date/time in ISO-8601 style "uuuu-MM-ddTHH:mm:ss'Z'".

        :return: The general pattern, which always uses an invariant culture.
        """
        return InstantPattern.create_with_invariant_culture("uuuu-MM-ddTHH:mm:ss'Z'")

    @property
    def extended_iso(self) -> InstantPattern:
        """Gets an invariant instant pattern which is ISO-8601 compatible, providing up to 9 decimal places of sub-
        second accuracy. (These digits are omitted when unnecessary.) This corresponds to the text pattern
        "uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF'Z'".

        :return: An invariant instant pattern which is ISO-8601 compatible, providing up to 9 decimal places of sub-
            second accuracy.
        """
        return InstantPattern.create_with_invariant_culture("uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF'Z'")


class __CombinedMeta(_ProtocolMeta, _InstantPatternMeta):
    """Intermediary class which prevents a metaclass conflict in InstantPattern."""


@final
@_sealed
@_private
class InstantPattern(IPattern[Instant], metaclass=__CombinedMeta):
    """Represents a pattern for parsing and formatting ``Instant`` values."""

    _DEFAULT_TEMPLATE_VALUE: Final[Instant] = Instant.from_utc(2000, 1, 1, 0, 0)

    __pattern: IPattern[Instant]
    __pattern_text: str
    __template_value: Instant
    __two_digit_year_max: int
    __format_info: _PyodaFormatInfo

    @classmethod
    def __ctor(
        cls,
        pattern_text: str,
        format_info: _PyodaFormatInfo,
        template_value: Instant,
        two_digit_year_max: int,
        pattern: IPattern[Instant],
    ) -> InstantPattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__format_info = format_info
        self.__template_value = template_value
        self.__two_digit_year_max = two_digit_year_max
        self.__pattern = pattern
        return self

    @property
    def pattern_text(self) -> str:
        """Gets the pattern text for this pattern, as supplied on creation.

        :return: The pattern text for this pattern, as supplied on creation.
        """
        return self.__pattern_text

    @property
    def template_value(self) -> Instant:
        """Gets the value used as a template for parsing: any field values unspecified
        in the pattern are taken from the template.

        :return: The value used as a template for parsing.
        """
        return self.__template_value

    @property
    def two_digit_year_max(self) -> int:
        """Maximum two-digit-year in the template to treat as the current century. If the value parsed is higher than
        this, the result is adjusted to the previous century. This value defaults to 30. To create a pattern with a
        different value, use ``with_two_digit_year_max(int)``.

        :return: The value used for the maximum two-digit-year, in the range 0-99 inclusive.
        """
        return self.__two_digit_year_max

    # TODO: check docstring inheritance in sphinx for these methods:

    def parse(self, text: str) -> ParseResult[Instant]:
        return self.__pattern.parse(text)

    def format(self, value: Instant) -> str:
        return self.__pattern.format(value)

    def append_format(self, value: Instant, builder: StringBuilder) -> StringBuilder:
        return self.__pattern.append_format(value, builder)

    @classmethod
    def __create(
        cls, pattern_text: str, format_info: _PyodaFormatInfo, template_value: Instant, two_digit_year_max: int
    ) -> InstantPattern:
        """Creates a pattern for the given pattern text and format info.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: The format info to use in the pattern
        :param template_value: The template value to use in the pattern
        :param two_digit_year_max: Maximum two-digit-year in the template to treat as the current century.
        :return: A pattern for parsing and formatting instants.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        # Note: no check for the default template value, as that ends up being done in the
        # underlying LocalDateTimePattern creation.
        pattern: IPattern[Instant] = _InstantPatternParser._ctor(template_value, two_digit_year_max).parse_pattern(
            pattern_text, format_info
        )
        return InstantPattern.__ctor(pattern_text, format_info, template_value, two_digit_year_max, pattern)

    @classmethod
    def create(cls, pattern_text: str, culture_info: CultureInfo) -> InstantPattern:
        """Creates a pattern for the given pattern text and culture.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :return: A pattern for parsing and formatting instants.
        """
        return cls.__create(
            pattern_text,
            _PyodaFormatInfo._get_format_info(culture_info),
            cls._DEFAULT_TEMPLATE_VALUE,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> InstantPattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting instants.
        """
        return cls.__create(
            pattern_text,
            _PyodaFormatInfo.current_info,
            cls._DEFAULT_TEMPLATE_VALUE,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> InstantPattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting instants.
        """
        return cls.__create(
            pattern_text,
            _PyodaFormatInfo.invariant_info,
            cls._DEFAULT_TEMPLATE_VALUE,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    def __with_format_info(self, format_info: _PyodaFormatInfo) -> InstantPattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified localization
        information.

        :param format_info: The localization information to use in the new pattern.
        :return: A new pattern with the given localization information.
        """
        return self.__create(
            self.pattern_text,
            format_info,
            self.template_value,
            self.two_digit_year_max,
        )

    def with_culture(self, culture_info: CultureInfo) -> InstantPattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__with_format_info(_PyodaFormatInfo._get_format_info(culture_info))

    def with_template_value(self, new_template_value: Instant) -> InstantPattern:
        """Creates a pattern like this one, but with the specified template value.

        :param new_template_value: The template value for the new pattern, used to fill in unspecified fields.
        :return: A new pattern with the given template value.
        """
        return self.__create(self.pattern_text, self.__format_info, new_template_value, self.two_digit_year_max)

    def with_two_digit_year_max(self, two_digit_year_max: int) -> InstantPattern:
        """Creates a pattern like this one, but with a different ``two_digit_year_max`` value.

        :param two_digit_year_max: The value to use for ``two_digit_year_max`` in the new pattern, in the range 0-99
            inclusive.
        :return: A new pattern with the specified maximum two-digit-year.
        """
        return self.__create(self.pattern_text, self.__format_info, self.template_value, two_digit_year_max)
