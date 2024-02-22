# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from functools import cache
from typing import Final, _ProtocolMeta, cast, final

from pyoda_time import Offset
from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.globalization import _PyodaFormatInfo
from pyoda_time.text import ParseResult
from pyoda_time.text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text.patterns import _PatternBclSupport
from pyoda_time.utility import _Preconditions, _sealed


class _OffsetPatternMeta(type):
    @property
    @cache
    def _bcl_support(self) -> _PatternBclSupport[Offset]:
        def pattern_parser(format_info: _PyodaFormatInfo) -> _FixedFormatInfoPatternParser[Offset]:
            return format_info.offset_pattern_parser

        return _PatternBclSupport(
            OffsetPattern._DEFAULT_FORMAT_PATTERN,
            pattern_parser,
        )

    @property
    @cache
    def general_invariant(self) -> OffsetPattern:
        """The "general" offset pattern (e.g. +HH, +HH:mm, +HH:mm:ss, +HH:mm:ss.fff) for the invariant culture."""
        return OffsetPattern.create_with_invariant_culture("g")

    @property
    @cache
    def general_invariant_with_z(self) -> OffsetPattern:
        """The "general" offset pattern (e.g. +HH, +HH:mm, +HH:mm:ss, +HH:mm:ss.fff) for the invariant culture, but
        producing (and allowing) Z as a value for a zero offset."""
        return OffsetPattern.create_with_invariant_culture("G")


class _CombinedMeta(_ProtocolMeta, _OffsetPatternMeta):
    """Intermediary class which prevents a metaclass conflict."""


@_sealed
@final
class OffsetPattern(IPattern[Offset], metaclass=_CombinedMeta):
    """Represents a pattern for parsing and formatting ``Offset`` values."""

    _DEFAULT_FORMAT_PATTERN: Final[str] = "g"

    def __init__(self, pattern_text: str, pattern: _IPartialPattern[Offset]):
        self.__pattern_text: Final[str] = pattern_text
        self.__underlying_pattern: Final[_IPartialPattern[Offset]] = pattern

    @property
    def pattern_text(self) -> str:
        """Gets the pattern text for this pattern, as supplied on creation."""
        return self.__pattern_text

    @property
    def _underlying_pattern(self) -> _IPartialPattern[Offset]:
        """Returns the pattern that this object delegates to.

        Mostly useful to avoid this public class implementing an internal interface.
        """
        return self.__underlying_pattern

    def parse(self, text: str) -> ParseResult[Offset]:
        """Parses the given text value according to the rules of this pattern.

        This method never throws an exception (barring a bug in Pyoda Time itself). Even errors such as the argument
        being null are wrapped in a parse result.

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        return self._underlying_pattern.parse(text)

    def format(self, value: Offset) -> str:
        """Formats the given offset as text according to the rules of this pattern.

        :param value: The offset to format.
        :return: The offset formatted according to this pattern.
        """
        return self._underlying_pattern.format(value)

    def append_format(self, value: Offset, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        return self._underlying_pattern.append_format(value, builder)

    @classmethod
    def _create(cls, pattern_text: str, format_info: _PyodaFormatInfo) -> OffsetPattern:
        """Creates a pattern for the given pattern text and format info.

        :param pattern_text: Pattern text to create the pattern for
        :param format_info: Localization information
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternException: The pattern text was invalid.
        """
        _Preconditions._check_not_null(pattern_text, "pattern_text")
        _Preconditions._check_not_null(format_info, "format_info")
        if isinstance(format_info, CultureInfo):
            format_info = _PyodaFormatInfo.get_format_info(format_info)
        pattern = cast(_IPartialPattern[Offset], format_info.offset_pattern_parser._parse_pattern(pattern_text))
        return OffsetPattern(pattern_text, pattern)

    @classmethod
    def create(cls, pattern_text: str, culture_info: CultureInfo) -> OffsetPattern:
        """Creates a pattern for the given pattern text and culture.

        See the user guide for the available pattern text options.

        :param pattern_text: Pattern text to create the pattern for
        :param culture_info: The culture to use in the pattern
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternException: The pattern text was invalid.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.get_instance(culture_info))

    @classmethod
    def create_with_current_culture(cls, pattern_text: str) -> OffsetPattern:
        """Creates a pattern for the given pattern text in the current thread's current culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternException: The pattern text was invalid.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.current_info)

    @classmethod
    def create_with_invariant_culture(cls, pattern_text: str) -> OffsetPattern:
        """Creates a pattern for the given pattern text in the invariant culture.

        See the user guide for the available pattern text options. Note that the current culture
        is captured at the time this method is called - it is not captured at the point of parsing
        or formatting values.

        :param pattern_text: Pattern text to create the pattern for
        :return: A pattern for parsing and formatting offsets.
        :raises InvalidPatternException: The pattern text was invalid.
        """
        return cls._create(pattern_text, _PyodaFormatInfo.invariant_info)

    def with_culture(self, culture_info: CultureInfo) -> OffsetPattern:
        """Creates a pattern for the same original pattern text as this pattern, but with the specified culture.

        :param culture_info: The culture to use in the new pattern.
        :return: A new pattern with the given culture.
        """
        return self._create(self.pattern_text, _PyodaFormatInfo.get_format_info(culture_info))
