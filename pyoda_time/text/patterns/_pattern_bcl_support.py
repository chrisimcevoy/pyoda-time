# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from collections.abc import Callable
from typing import TYPE_CHECKING, Final, final

from ..._compatibility._i_format_provider import IFormatProvider
from ...globalization._pyoda_format_info import _PyodaFormatInfo
from ...utility._csharp_compatibility import _sealed
from .._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser

if TYPE_CHECKING:
    from .._i_pattern import IPattern


@_sealed
@final
class _PatternBclSupport[T]:
    """Class providing simple support for the various Parse/TryParse/ParseExact/TryParseExact/Format overloads provided
    by individual types."""

    def __init__(
        self,
        default_format_pattern: str,
        pattern_parser: Callable[[_PyodaFormatInfo], _FixedFormatInfoPatternParser[T]],
    ) -> None:
        self.__pattern_parser: Final[Callable[[_PyodaFormatInfo], _FixedFormatInfoPatternParser[T]]] = pattern_parser
        self.__default_format_pattern: Final[str] = default_format_pattern

    def format(self, value: T, pattern_text: str | None, format_provider: IFormatProvider) -> str:
        if pattern_text is None or not pattern_text.strip():
            pattern_text = self.__default_format_pattern
        format_info: _PyodaFormatInfo = _PyodaFormatInfo.get_instance(format_provider)
        pattern: IPattern[T] = self.__pattern_parser(format_info)._parse_pattern(pattern_text)
        return pattern.format(value)
