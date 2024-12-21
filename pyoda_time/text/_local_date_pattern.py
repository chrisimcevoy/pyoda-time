# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, Final, _ProtocolMeta, cast, final

from pyoda_time._local_date import LocalDate
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._local_date_pattern_parser import _LocalDatePatternParser
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from pyoda_time._calendar_system import CalendarSystem
    from pyoda_time._compatibility._culture_info import CultureInfo
    from pyoda_time._compatibility._string_builder import StringBuilder
    from pyoda_time.text._parse_result import ParseResult


class __LocalDatePatternMeta(_ProtocolMeta):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "D"  # Long

    @property
    def _bcl_support(self) -> _PatternBclSupport[LocalDate]:
        return _PatternBclSupport(self.__DEFAULT_FORMAT_PATTERN, lambda fi: fi._local_date_pattern_parser)

    @property
    def iso(self) -> LocalDatePattern:
        """Gets an invariant local date pattern which is ISO-8601 compatible and which round trips values, but doesn't
        include the calendar system. This corresponds to the text pattern "uuuu'-'MM'-'dd".

        This pattern corresponds to the 'R' standard pattern.

        :return: An invariant local date pattern which is ISO-8601 compatible.
        """
        return self._Patterns._iso_pattern_impl

    @property
    def full_roundtrip(self) -> LocalDatePattern:
        """Gets an invariant local date pattern which round trips values including the calendar system. This corresponds
        to the text pattern "uuuu'-'MM'-'dd '('c')'".

        This pattern corresponds to the 'r' standard pattern.

        :return: An invariant local date pattern which round trips values including the calendar system.
        """
        return self._Patterns._full_roundtrip_pattern_impl

    class __PatternsMeta(type):
        @property
        def _iso_pattern_impl(self) -> LocalDatePattern:
            return LocalDatePattern.create_with_invariant_culture("uuuu'-'MM'-'dd")

        @property
        def _full_roundtrip_pattern_impl(self) -> LocalDatePattern:
            return LocalDatePattern.create_with_invariant_culture("uuuu'-'MM'-'dd '('c')'")

    class _Patterns(metaclass=__PatternsMeta):
        pass


@final
@_sealed
@_private
class LocalDatePattern(IPattern[LocalDate], metaclass=__LocalDatePatternMeta):
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

    @property
    def two_digit_year_max(self) -> int:
        """Maximum two-digit-year in the template to treat as the current century. If the value parsed is higher than
        this, the result is adjusted to the previous century. This value defaults to 30. To create a pattern with a
        different value, use ``with_two_digit_year_max``.

        :return: The value used for the maximum two-digit-year, in the range 0-99 inclusive.
        """
        return self.__two_digit_year_max

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
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Pyoda Time itself). Even errors such as the argument
        being null are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self._underlying_pattern.parse(text)

    def format(self, value: LocalDate) -> str:
        """Formats the given local date as text according to the rules of this pattern.

        :param value: The local date to format.
        :return: The local date formatted according to this pattern.
        """
        return self._underlying_pattern.format(value)

    def append_format(self, value: LocalDate, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        return self._underlying_pattern.append_format(value, builder)

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

    @classmethod
    def create(
        cls, pattern_text: str, culture_info: CultureInfo, template_value: LocalDate | None = None
    ) -> LocalDatePattern:
        """Creates a pattern for the given pattern text, culture, and template value.

        If no template value is provided, the default template value of 2000-01-01 will be used.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :param template_value: Maximum two-digit-year in the template to treat as the current century.
        :return: A pattern for parsing and formatting local dates. :exception InvalidPatternError: The pattern text was
            invalid.
        """
        if template_value is None:
            template_value = cls._DEFAULT_TEMPLATE_VALUE
        return cls._create(
            pattern_text,
            _PyodaFormatInfo._get_format_info(culture_info),
            template_value,
            cls._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> LocalDatePattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local dates.
        :exception InvalidPatternError: The pattern text was invalid.
        """
        return cls._create(
            pattern_text, _PyodaFormatInfo.current_info, cls._DEFAULT_TEMPLATE_VALUE, cls._DEFAULT_TWO_DIGIT_YEAR_MAX
        )

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> LocalDatePattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local dates.
        """
        return cls._create(
            pattern_text, _PyodaFormatInfo.invariant_info, cls._DEFAULT_TEMPLATE_VALUE, cls._DEFAULT_TWO_DIGIT_YEAR_MAX
        )

    def __with_format_info(self, format_info: _PyodaFormatInfo) -> LocalDatePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified localization
        information.

        :param format_info: The localization information to use in the new pattern.
        :return: A new pattern with the given localization information.
        """
        return self._create(self.pattern_text, format_info, self.template_value, self.two_digit_year_max)

    def with_culture(self, culture_info: CultureInfo) -> LocalDatePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__with_format_info(_PyodaFormatInfo._get_format_info(culture_info))

    def with_template_value(self, new_template_value: LocalDate) -> LocalDatePattern:
        """Creates a pattern like this one, but with the specified template value.

        :param new_template_value: The template value for the new pattern, used to fill in unspecified fields.
        :return: A new pattern with the given template value.
        """
        return self._create(self.pattern_text, self.__format_info, new_template_value, self.two_digit_year_max)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDatePattern:
        """Creates a pattern like this one, but with the template value modified to use the specified calendar system.

        Care should be taken in two (relatively rare) scenarios. Although the default template value is supported by all
        Noda Time calendar systems, if a pattern is created with a different template value and then this method is
        called with a calendar system which doesn't support that date, an exception will be thrown. Additionally, if the
        pattern only specifies some date fields, it's possible that the new template value will not be suitable for all
        values.

        :param calendar: The calendar system to convert the template value into.
        :return: A new pattern with a template value in the specified calendar system.
        """
        return self.with_template_value(self.template_value.with_calendar(calendar))

    def with_two_digit_year_max(self, two_digit_year_max: int) -> LocalDatePattern:
        """Creates a pattern like this one, but with a different ``two_digit_year_max`` value.

        :param two_digit_year_max: The value to use for ``two_digit_year_max`` in the new pattern, in the range 0-99
            inclusive.
        :return: A new pattern with the specified maximum two-digit-year.
        """
        return self._create(self.pattern_text, self.__format_info, self.template_value, two_digit_year_max)
