# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, _ProtocolMeta, final

from pyoda_time._duration import Duration
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text.patterns._pattern_bcl_support import _PatternBclSupport
from pyoda_time.utility._csharp_compatibility import _private, _sealed
from pyoda_time.utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from pyoda_time._compatibility._culture_info import CultureInfo
    from pyoda_time._compatibility._string_builder import StringBuilder
    from pyoda_time.text._parse_result import ParseResult


class __DurationPatternMeta(_ProtocolMeta):
    __pattern_bcl_support: _PatternBclSupport[Duration] | None = None

    @property
    def roundtrip(self) -> DurationPattern:
        """Gets the general pattern for durations using the invariant culture, with a format string of
        "-D:hh:mm:ss.FFFFFFFFF".

        This pattern round-trips. This corresponds to the "o" standard pattern.

        :return: The general pattern for durations using the invariant culture.
        """
        return DurationPattern._Patterns._roundtrip_pattern_impl

    @property
    def json_roundtrip(self) -> DurationPattern:
        """Gets a pattern for durations using the invariant culture, with a format string of "-H:mm:ss.FFFFFFFFF".

        This pattern round-trips. This corresponds to the "j" standard pattern.

        :return: The pattern for durations using the invariant culture.
        """
        return DurationPattern._Patterns._json_roundtrip_pattern_impl

    @property
    def _bcl_support(self) -> _PatternBclSupport[Duration]:
        if self.__pattern_bcl_support is None:
            self.__pattern_bcl_support = _PatternBclSupport("o", lambda fi: fi._duration_pattern_parser)
        return self.__pattern_bcl_support


@final
@_sealed
@_private
class DurationPattern(IPattern[Duration], metaclass=__DurationPatternMeta):
    """Represents a pattern for parsing and formatting ``Duration`` values."""

    class __PatternsMeta(type):
        __roundtrip_pattern_impl: DurationPattern | None = None
        __json_roundtrip_pattern_impl: DurationPattern | None = None

        @property
        def _roundtrip_pattern_impl(self) -> DurationPattern:
            if self.__roundtrip_pattern_impl is None:
                self.__roundtrip_pattern_impl = DurationPattern.create_with_invariant_culture("-D:hh:mm:ss.FFFFFFFFF")
            return self.__roundtrip_pattern_impl

        @property
        def _json_roundtrip_pattern_impl(self) -> DurationPattern:
            if self.__json_roundtrip_pattern_impl is None:
                self.__json_roundtrip_pattern_impl = DurationPattern.create_with_invariant_culture("-H:mm:ss.FFFFFFFFF")
            return self.__json_roundtrip_pattern_impl

    class _Patterns(metaclass=__PatternsMeta):
        pass

    __pattern: IPattern[Duration]
    __pattern_text: str

    @property
    def pattern_text(self) -> str:
        """Gets the pattern text for this pattern, as supplied on creation.

        :return: The pattern text for this pattern, as supplied on creation.
        """
        return self.__pattern_text

    @classmethod
    def __ctor(cls, pattern_text: str, pattern: IPattern[Duration]) -> DurationPattern:
        self = super().__new__(cls)
        self.__pattern_text = pattern_text
        self.__pattern = pattern
        return self

    def parse(self, text: str) -> ParseResult[Duration]:
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Pyoda Time itself). Even errors such as the argument
        being null are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self.__pattern.parse(text)

    def format(self, value: Duration) -> str:
        """Formats the given duration as text according to the rules of this pattern.

        :param value: The duration to format.
        :return: The duration formatted according to this pattern.
        """
        return self.__pattern.format(value)

    def append_format(self, value: Duration, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        return self.__pattern.append_format(value, builder)

    @classmethod
    def __create(cls, pattern_text: str, format_info: _PyodaFormatInfo) -> DurationPattern:
        """Creates a pattern for the given pattern text and format info.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: Localization information
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        pattern = format_info._duration_pattern_parser._parse_pattern(pattern_text)
        return DurationPattern.__ctor(pattern_text, pattern)

    @classmethod
    def create(cls, pattern_text: str, culture_info: CultureInfo) -> DurationPattern:
        """Creates a pattern for the given pattern text and culture.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        return cls.__create(pattern_text, _PyodaFormatInfo._get_format_info(culture_info))

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> DurationPattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        return cls.__create(pattern_text, _PyodaFormatInfo.current_info)

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> DurationPattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternError: The pattern text was invalid.
        """
        return cls.__create(pattern_text, _PyodaFormatInfo.invariant_info)

    def with_culture(self, culture_info: CultureInfo) -> DurationPattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self.__create(self.pattern_text, _PyodaFormatInfo._get_format_info(culture_info))
