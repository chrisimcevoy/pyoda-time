# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Final, _ProtocolMeta, cast, final

from pyoda_time._local_date_time import LocalDateTime
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._local_date_pattern import LocalDatePattern
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from pyoda_time._calendar_system import CalendarSystem
    from pyoda_time._compatibility._culture_info import CultureInfo
    from pyoda_time._compatibility._string_builder import StringBuilder
    from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
    from pyoda_time.text._parse_result import ParseResult


class _LocalDateTimePatternMeta(type):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "G"  # General (long time)
    __pattern_bcl_support: _PatternBclSupport[LocalDateTime] | None = None

    @property
    def _bcl_support(self) -> _PatternBclSupport[LocalDateTime]:
        if self.__pattern_bcl_support is None:

            def pattern_parser(format_info: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[LocalDateTime]:
                return format_info._local_date_time_pattern_parser

            self.__pattern_bcl_support = _PatternBclSupport(self.__DEFAULT_FORMAT_PATTERN, pattern_parser)
        return self.__pattern_bcl_support

    @property
    def general_iso(cls) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which is ISO-8601 compatible, down to the second. This corresponds
        to the text pattern "uuuu'-'MM'-'dd'T'HH':'mm':'ss".

        This pattern corresponds to the 's' standard pattern ("shorter sortable").

        :return: An invariant local date/time pattern which is ISO-8601 compatible, down to the second.
        """
        return LocalDateTimePattern._Patterns._general_iso_pattern_impl

    @property
    def extended_iso(cls) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which is ISO-8601 compatible, providing up to 9 decimal places of
        sub-second accuracy. (These digits are omitted when unnecessary.) This corresponds to the text pattern
        "uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF".

        This pattern corresponds to the 'S' standard pattern ("longer sortable").

        :return: An invariant local date/time pattern which is ISO-8601 compatible, providing up to 9 decimal places of
            sub-second accuracy.
        """
        return LocalDateTimePattern._Patterns._extended_iso_pattern_impl

    @property
    def bcl_round_trip(self) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which is ISO-8601 compatible, providing up to 7 decimal places of
        sub-second accuracy which are always present (including trailing zeroes). This is compatible with the BCL round-
        trip formatting of <see cref="DateTime"/> values with a kind of "unspecified". This corresponds to the text
        pattern "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffff". It does not necessarily round-trip all ``LocalDateTime``
        values as it will lose sub-tick information. Use ``full_roundtrip_without_calendar`` for full precision.

        This pattern corresponds to the 'o' and 'O' standard patterns.

        :return: An invariant local date/time pattern which is ISO-8601 compatible, providing up to 7 decimal places of
            sub-second accuracy which are always present (including trailing zeroes).
        """
        return LocalDateTimePattern._Patterns._bcl_round_trip_pattern_impl

    @property
    def full_roundtrip_without_calendar(self) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which round trips values, but doesn't include the calendar system.
        It provides up to 9 decimal places of sub-second accuracy which are always present (including trailing zeroes).
        This corresponds to the text pattern "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffff". It will round-trip all
        ``LocalDateTime`` values if the calendar system of the template value is the same as the calendar system of the
        original value.

        This pattern corresponds to the 'r' standard pattern.

        :return: An invariant local date/time pattern which is ISO-8601 compatible, providing up to 7 decimal places of
            sub-second accuracy which are always present (including trailing zeroes).
        """
        return LocalDateTimePattern._Patterns._full_round_trip_without_calendar_impl

    @property
    def full_roundtrip(self) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which round trips values including the calendar system. This
        corresponds to the text pattern "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffff '('c')'".

        This pattern corresponds to the 'R' standard pattern.

        :return: An invariant local date/time pattern which round trips values including the calendar system.
        """
        return LocalDateTimePattern._Patterns._full_round_trip_pattern_impl

    @property
    def date_hour_minute_iso(cls) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which is ISO-8601 compatible, with precision of just minutes. This
        corresponds to the text pattern "uuuu'-'MM'-'dd'T'HH':'mm".

        :return: An invariant local time pattern which is ISO-8601 compatible, with no sub-minute precision.
        """
        return LocalDateTimePattern._Patterns._date_hour_minute_iso_pattern_impl

    @property
    def date_hour_iso(self) -> LocalDateTimePattern:
        """Gets an invariant local date/time pattern which is ISO-8601 compatible, with a precision of just hours. This
        corresponds to the text pattern "uuuu'-'MM'-'dd'T'HH".

        :return: An invariant local time pattern which is ISO-8601 compatible, with no sub-hour precision.
        """
        return LocalDateTimePattern._Patterns._date_hour_iso_pattern_impl

    @property
    def variable_precision_iso(self) -> IPattern[LocalDateTime]:
        """Gets an invariant local date/time pattern which can parse any ISO-8601 compatible value with a calendar date
        (in extended format, that is, with separators), regardless of precision in the time part. Valid values for time
        include "just hours", "hours and minutes", "hours, minutes and seconds", and values with fractions of seconds
        (as far as nanoseconds). The time part must be present, however; this pattern will not parse date-only values.
        (It will also not parse ordinal dates or week dates, as described in ISO-8601.)

        :return: This is expressed as an ``IPattern[LocalDateTime]`` rather than a ``LocalDateTimePattern``,
            as it has no single pattern text.
        """
        return LocalDateTimePattern._Patterns._variable_precision_iso_pattern_impl


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
        __general_iso_pattern_impl: LocalDateTimePattern | None = None
        __extended_iso_pattern_impl: LocalDateTimePattern | None = None
        __bcl_round_trip_pattern_impl: LocalDateTimePattern | None = None
        __full_round_trip_without_calendar_impl: LocalDateTimePattern | None = None
        __full_round_trip_pattern_impl: LocalDateTimePattern | None = None
        __date_hour_iso_pattern_impl: LocalDateTimePattern | None = None
        __date_hour_minute_iso_pattern_impl: LocalDateTimePattern | None = None
        __variable_precision_iso_pattern_impl: IPattern[LocalDateTime] | None = None

        @property
        def _general_iso_pattern_impl(self) -> LocalDateTimePattern:
            if self.__general_iso_pattern_impl is None:
                self.__general_iso_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm':'ss"
                )
            return self.__general_iso_pattern_impl

        @property
        def _extended_iso_pattern_impl(self) -> LocalDateTimePattern:
            if self.__extended_iso_pattern_impl is None:
                self.__extended_iso_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm':'ss;FFFFFFFFF"
                )
            return self.__extended_iso_pattern_impl

        @property
        def _bcl_round_trip_pattern_impl(self) -> LocalDateTimePattern:
            if self.__bcl_round_trip_pattern_impl is None:
                self.__bcl_round_trip_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffff"
                )
            return self.__bcl_round_trip_pattern_impl

        @property
        def _full_round_trip_without_calendar_impl(self) -> LocalDateTimePattern:
            if self.__full_round_trip_without_calendar_impl is None:
                self.__full_round_trip_without_calendar_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffff"
                )
            return self.__full_round_trip_without_calendar_impl

        @property
        def _full_round_trip_pattern_impl(self) -> LocalDateTimePattern:
            if self.__full_round_trip_pattern_impl is None:
                self.__full_round_trip_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm':'ss'.'fffffffff '('c')'"
                )
            return self.__full_round_trip_pattern_impl

        @property
        def _date_hour_iso_pattern_impl(self) -> LocalDateTimePattern:
            if self.__date_hour_iso_pattern_impl is None:
                self.__date_hour_iso_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH"
                )
            return self.__date_hour_iso_pattern_impl

        @property
        def _date_hour_minute_iso_pattern_impl(self) -> LocalDateTimePattern:
            if self.__date_hour_minute_iso_pattern_impl is None:
                self.__date_hour_minute_iso_pattern_impl = LocalDateTimePattern.create_with_invariant_culture(
                    "uuuu'-'MM'-'dd'T'HH':'mm"
                )
            return self.__date_hour_minute_iso_pattern_impl

        @property
        def _variable_precision_iso_pattern_impl(cls) -> IPattern[LocalDateTime]:
            if cls.__variable_precision_iso_pattern_impl is None:
                from pyoda_time.text._composite_pattern_builder import CompositePatternBuilder

                cls.__variable_precision_iso_pattern_impl = CompositePatternBuilder(
                    patterns=[
                        cls._extended_iso_pattern_impl,
                        cls._date_hour_minute_iso_pattern_impl,
                        cls._date_hour_iso_pattern_impl,
                    ],
                    format_predicates=[
                        lambda time: True,
                        lambda time: time.second == 0 and time.nanosecond_of_second == 0,
                        lambda time: time.minute == 0 and time.second == 0 and time.nanosecond_of_second == 0,
                    ],
                ).build()
            return cls.__variable_precision_iso_pattern_impl

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

    def parse(self, text: str) -> ParseResult[LocalDateTime]:
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Noda Time itself). Even errors such as the argument
        being null are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self.__underlying_pattern.parse(text)

    def format(self, value: LocalDateTime) -> str:
        """Formats the given local date/time as text according to the rules of this pattern.

        :param value: The local date/time to format.
        :return: The local date/time formatted according to this pattern.
        """
        return self.__underlying_pattern.format(value)

    def append_format(self, value: LocalDateTime, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        return self.__underlying_pattern.append_format(value, builder)

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
            pattern = pattern._underlying_pattern
        partial_pattern: _IPartialPattern[LocalDateTime] = cast(_IPartialPattern[LocalDateTime], pattern)
        return LocalDateTimePattern.__ctor(
            pattern_text, format_info, template_value, two_digit_year_max, partial_pattern
        )

    @classmethod
    def create(
        cls, pattern_text: str, culture_info: CultureInfo, template_value: LocalDateTime | None = None
    ) -> LocalDateTimePattern:
        """Creates a pattern for the given pattern text, format info, and template value.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :param template_value: Template value to use for unspecified fields. Defaults to midnight on 2000-01-01 if not
            provided.
        :return: A pattern for parsing and formatting local date/times.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        if template_value is None:
            template_value = cls._DEFAULT_TEMPLATE_VALUE
        return cls._create(
            pattern_text,
            _PyodaFormatInfo._get_format_info(culture_info),
            template_value,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> LocalDateTimePattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local date/times.
        """
        return cls._create(
            pattern_text,
            _PyodaFormatInfo.current_info,
            cls._DEFAULT_TEMPLATE_VALUE,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> LocalDateTimePattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local date/times.
        """
        return cls._create(
            pattern_text,
            _PyodaFormatInfo.invariant_info,
            cls._DEFAULT_TEMPLATE_VALUE,
            LocalDatePattern._DEFAULT_TWO_DIGIT_YEAR_MAX,
        )

    def __with_format_info(self, format_info: _PyodaFormatInfo) -> LocalDateTimePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified localization
        information.

        :param format_info: The localization information to use in the new pattern.
        :return: A new pattern with the given localization information.
        """
        return self._create(self.__pattern_text, format_info, self.__template_value, self.__two_digit_year_max)

    def with_culture(self, culture_info: CultureInfo) -> LocalDateTimePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__with_format_info(_PyodaFormatInfo._get_format_info(culture_info))

    def with_template_value(self, new_template_value: LocalDateTime) -> LocalDateTimePattern:
        """Creates a pattern like this one, but with the specified template value.

        :param new_template_value: The template value for the new pattern, used to fill in unspecified fields.
        :return: A new pattern with the given template value.
        """
        return self._create(self.__pattern_text, self.__format_info, new_template_value, self.__two_digit_year_max)

    def with_calendar(self, calendar: CalendarSystem) -> LocalDateTimePattern:
        """Creates a pattern like this one, but with the template value modified to use the specified calendar system.

        Care should be taken in two (relatively rare) scenarios. Although the default template value is supported by all
        Pyoda Time calendar systems, if a pattern is created with a different template value and then this method is
        called with a calendar system which doesn't support that date, an exception will be thrown. Additionally, if the
        pattern only specifies some date fields, it's possible that the new template value will not be suitable for all
        values.

        :param calendar: The calendar system to convert the template value into.
        :return: A new pattern with a template value in the specified calendar system.
        """
        return self.with_template_value(self.__template_value.with_calendar(calendar))

    def with_two_digit_year_max(self, two_digit_year_max: int) -> LocalDateTimePattern:
        """Creates a pattern like this one, but with a different ``two_digit_year_max`` value.

        :param two_digit_year_max: The value to use for ``two_digit_year_max`` in the new pattern,
            in the range 0-99 inclusive.
        :return: A new pattern with the specified maximum two-digit-year.
        """
        return self._create(self.__pattern_text, self.__format_info, self.__template_value, two_digit_year_max)
