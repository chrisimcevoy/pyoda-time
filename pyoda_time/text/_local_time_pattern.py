# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import threading
from typing import Final, _ProtocolMeta, cast, final

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._local_time import LocalTime
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._composite_pattern_builder import CompositePatternBuilder
from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions


class _LocalTimePatternMeta(type):
    __DEFAULT_FORMAT_PATTERN: Final[str] = "T"  # Long

    @property
    def extended_iso(cls) -> LocalTimePattern:
        """Gets an invariant local time pattern which is ISO-8601 compatible, providing up to 9 decimal places. (These
        digits are omitted when unnecessary.) This corresponds to the text pattern "HH':'mm':'ss;FFFFFFFFF".

        This pattern corresponds to the 'o' standard pattern.

        :return: An invariant local time pattern which is ISO-8601 compatible, providing up to 9 decimal places.
        """
        return cls._Patterns._extended_iso_pattern_impl

    @property
    def long_extended_iso(cls) -> LocalTimePattern:
        """Gets an invariant local time pattern which is ISO-8601 compatible, providing exactly 9 decimal places. This
        corresponds to the text pattern "HH':'mm':'ss;fffffffff".

        This pattern corresponds to the 'O' standard pattern.

        :return: An invariant local time pattern which is ISO-8601 compatible, providing exactly 9 decimal places.
        """
        return cls._Patterns._long_extended_iso_pattern_impl

    @property
    def general_iso(cls) -> LocalTimePattern:
        """Gets an invariant local time pattern which is ISO-8601 compatible, with precision of just seconds. This
        corresponds to the text pattern "HH':'mm':'ss".

        :return: An invariant local time pattern which is ISO-8601 compatible, with no sub-second precision.
        """
        return cls._Patterns._general_iso_pattern_impl

    @property
    def hour_minute_iso(cls) -> LocalTimePattern:
        """Gets an invariant local time pattern which is ISO-8601 compatible, with precision of just minutes. This
        corresponds to the text pattern "HH':'mm".

        :return: An invariant local time pattern which is ISO-8601 compatible, with no sub-minute precision.
        """
        return cls._Patterns._hour_minute_iso_pattern_impl

    @property
    def hour_iso(cls) -> LocalTimePattern:
        """Gets an invariant local time pattern which is ISO-8601 compatible, with a precision of just hours. This
        corresponds to the text pattern "HH".

        :return: An invariant local time pattern which is ISO-8601 compatible, with no sub-hour precision.
        """
        return cls._Patterns._hour_iso_pattern_impl

    @property
    def variable_precision_iso(cls) -> IPattern[LocalTime]:
        """Gets an invariant local time pattern which can parse any ISO-8601 compatible value (in extended format, that
        is, with separators), regardless of precision. Valid values include "just hours", "hours and minutes", "hours,
        minutes and seconds", and values with fractions of seconds (as far as nanoseconds).

        This is expressed as an ``IPattern[LocalTime]`` rather than a ``LocalTimePattern``,
        as it has no single pattern text.

        :return: An invariant local time pattern which is ISO-8601 compatible for all precisions.
        """
        return cls._Patterns._variable_precision_iso_pattern_impl

    @property
    def _bcl_support(cls) -> _PatternBclSupport[LocalTime]:
        def pattern_parser(format_info: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[LocalTime]:
            return format_info._local_time_pattern_parser

        return _PatternBclSupport(cls.__DEFAULT_FORMAT_PATTERN, pattern_parser)

    class _PatternsMeta(type):
        __lock: Final[threading.Lock] = threading.Lock()
        __extended_iso_pattern_impl: LocalTimePattern | None = None
        __long_extended_iso_pattern_impl: LocalTimePattern | None = None
        __general_iso_pattern_impl: LocalTimePattern | None = None
        __hour_iso_pattern_impl: LocalTimePattern | None = None
        __hour_minute_iso_pattern_impl: LocalTimePattern | None = None
        __variable_precision_iso_pattern_impl: IPattern[LocalTime] | None = None

        @property
        def _extended_iso_pattern_impl(self) -> LocalTimePattern:
            if self.__extended_iso_pattern_impl is None:
                with self.__lock:
                    if self.__extended_iso_pattern_impl is None:
                        self.__extended_iso_pattern_impl = LocalTimePattern.create_with_invariant_culture(
                            "HH':'mm':'ss;FFFFFFFFF"
                        )
            return self.__extended_iso_pattern_impl

        @property
        def _long_extended_iso_pattern_impl(self) -> LocalTimePattern:
            if self.__long_extended_iso_pattern_impl is None:
                with self.__lock:
                    if self.__long_extended_iso_pattern_impl is None:
                        self.__long_extended_iso_pattern_impl = LocalTimePattern.create_with_invariant_culture(
                            "HH':'mm':'ss;fffffffff"
                        )
            return self.__long_extended_iso_pattern_impl

        @property
        def _general_iso_pattern_impl(self) -> LocalTimePattern:
            if self.__general_iso_pattern_impl is None:
                with self.__lock:
                    if self.__general_iso_pattern_impl is None:
                        self.__general_iso_pattern_impl = LocalTimePattern.create_with_invariant_culture("HH':'mm':'ss")
            return self.__general_iso_pattern_impl

        @property
        def _hour_iso_pattern_impl(self) -> LocalTimePattern:
            if self.__hour_iso_pattern_impl is None:
                with self.__lock:
                    if self.__hour_iso_pattern_impl is None:
                        self.__hour_iso_pattern_impl = LocalTimePattern.create_with_invariant_culture("HH")
            return self.__hour_iso_pattern_impl

        @property
        def _hour_minute_iso_pattern_impl(self) -> LocalTimePattern:
            if self.__hour_minute_iso_pattern_impl is None:
                with self.__lock:
                    if self.__hour_minute_iso_pattern_impl is None:
                        self.__hour_minute_iso_pattern_impl = LocalTimePattern.create_with_invariant_culture("HH':'mm")
            return self.__hour_minute_iso_pattern_impl

        @property
        def _variable_precision_iso_pattern_impl(self) -> IPattern[LocalTime]:
            if self.__variable_precision_iso_pattern_impl is None:
                with self.__lock:
                    if self.__variable_precision_iso_pattern_impl is None:

                        def format_predicate_for_extended_iso_pattern(time: LocalTime) -> bool:
                            return True

                        def format_predicate_for_hour_minute_iso_pattern(time: LocalTime) -> bool:
                            return time.second == 0 and time.nanosecond_of_second == 0

                        def format_predicate_for_hour_iso_pattern(time: LocalTime) -> bool:
                            return time.minute == 0 and time.second == 0 and time.nanosecond_of_second == 0

                        patterns = [
                            self._extended_iso_pattern_impl,
                            self._hour_minute_iso_pattern_impl,
                            self._hour_iso_pattern_impl,
                        ]

                        format_predicates = [
                            format_predicate_for_extended_iso_pattern,
                            format_predicate_for_hour_minute_iso_pattern,
                            format_predicate_for_hour_iso_pattern,
                        ]

                        self.__variable_precision_iso_pattern_impl = CompositePatternBuilder(
                            patterns, format_predicates
                        ).build()
            return self.__variable_precision_iso_pattern_impl

    class _Patterns(metaclass=_PatternsMeta):
        """Class whose existence is solely to avoid type initialization order issues, most of which stem from needing
        NodaFormatInfo.InvariantInfo..."""


class _CombinedMeta(_ProtocolMeta, _LocalTimePatternMeta):
    """Intermediary class which prevents a metaclass conflict."""


@final
@_sealed
@_private
class LocalTimePattern(IPattern[LocalTime], metaclass=_CombinedMeta):
    @property
    def _underlying_pattern(self) -> _IPartialPattern[LocalTime]:
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
    def template_value(self) -> LocalTime:
        """Gets the value used as a template for parsing.

        Any field values unspecified in the pattern are taken from the template.

        :return: The value used as a template for parsing.
        """
        return self.__template_value

    __pattern_text: str
    __format_info: _PyodaFormatInfo
    __template_value: LocalTime
    __underlying_pattern: _IPartialPattern[LocalTime]

    @classmethod
    def __ctor(
        cls,
        pattern_text: str,
        format_info: _PyodaFormatInfo,
        template_value: LocalTime,
        pattern: _IPartialPattern[LocalTime],
    ) -> LocalTimePattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__format_info = format_info
        self.__template_value = template_value
        self.__underlying_pattern = pattern
        return self

    def parse(self, text: str) -> ParseResult[LocalTime]:
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Noda Time itself). Even errors such as the argument
        being null are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self.__underlying_pattern.parse(text)

    def format(self, value: LocalTime) -> str:
        """Formats the given local time as text according to the rules of this pattern.

        :param value: The local time to format.
        :return: The local time formatted according to this pattern.
        """
        return self.__underlying_pattern.format(value)

    def append_format(self, value: LocalTime, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The StringBuilder to append to.
        :return: The builder passed in as ``builder``.
        """
        return self.__underlying_pattern.append_format(value, builder)

    @classmethod
    def _create(cls, pattern_text: str, format_info: _PyodaFormatInfo, template_value: LocalTime) -> LocalTimePattern:
        """Creates a pattern for the given pattern text, format info, and template value.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: The format info to use in the pattern
        :param template_value: Template value to use for unspecified fields
        :return: A pattern for parsing and formatting local times.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        # Use the "fixed" parser for the common case of the default template value.
        if template_value == LocalTime.midnight:
            pattern = format_info._local_time_pattern_parser._parse_pattern(pattern_text)
        else:
            from ._local_time_pattern_parser import _LocalTimePatternParser

            pattern = _LocalTimePatternParser._ctor(template_value).parse_pattern(pattern_text, format_info)
        # If ParsePattern returns a standard pattern instance, we need to get the underlying partial pattern.
        # (Alternatively, we could just return it directly, instead of creating a new object.)
        if isinstance(pattern, LocalTimePattern):
            pattern = pattern._underlying_pattern or pattern
        partial_pattern = cast(_IPartialPattern[LocalTime], pattern)
        return LocalTimePattern.__ctor(pattern_text, format_info, template_value, partial_pattern)

    @classmethod
    def create(
        cls, pattern_text: str, culture_info: CultureInfo, template_value: LocalTime = LocalTime.midnight
    ) -> LocalTimePattern:
        """Creates a pattern for the given pattern text, culture, and template value, with a default template value of
        midnight.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :param template_value: Template value to use for unspecified fields
        :return: A pattern for parsing and formatting local times.
        """
        return cls._create(pattern_text, _PyodaFormatInfo._get_format_info(culture_info), template_value)

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> LocalTimePattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local times.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.current_info, LocalTime.midnight)

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> LocalTimePattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting local times.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.invariant_info, LocalTime.midnight)

    def __with_format_info(self, format_info: _PyodaFormatInfo) -> LocalTimePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified localization
        information.

        :param format_info: The localization information to use in the new pattern.
        :return: A new pattern with the given localization information.
        """
        return self._create(self.pattern_text, format_info, self.template_value)

    def with_culture(self, culture_info: CultureInfo) -> LocalTimePattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__with_format_info(_PyodaFormatInfo._get_format_info(culture_info))

    def with_template_value(self, template_value: LocalTime) -> LocalTimePattern:
        """Creates a pattern like this one, but with the specified template value.

        :param template_value: The template value for the new pattern, used to fill in unspecified fields.
        :return: A new pattern with the given template value.
        """
        return self._create(self.pattern_text, self.__format_info, template_value)
