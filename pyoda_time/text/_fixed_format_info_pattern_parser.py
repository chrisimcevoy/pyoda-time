# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Final, Generic, TypeVar, final

from ..globalization import _PyodaFormatInfo
from ..utility import _sealed
from ._i_pattern import IPattern
from .patterns._i_pattern_parser import _IPatternParser

T = TypeVar("T")


@_sealed
@final
class _FixedFormatInfoPatternParser(Generic[T]):
    """A pattern parser for a single format info, which caches patterns by text/style."""

    # TODO: This is dramatically simplified compared to Noda Time

    def __init__(self, pattern_parser: _IPatternParser[T], format_info: _PyodaFormatInfo) -> None:
        self.__pattern_parser = pattern_parser
        self.__format_info = format_info
        # TODO: Noda Time uses the Cache class from utility here...
        self.__cache: Final[dict[str, IPattern[T]]] = dict()

    def _parse_pattern(self, pattern: str) -> IPattern[T]:
        if not (ret := self.__cache.get(pattern)):
            ret = self.__cache[pattern] = self.__pattern_parser.parse_pattern(pattern, self.__format_info)
        return ret
