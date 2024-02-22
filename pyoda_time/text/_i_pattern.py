# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import abstractmethod
from typing import Protocol, TypeVar

from .._compatibility._string_builder import StringBuilder
from ._parse_result import ParseResult

T = TypeVar("T")


class IPattern(Protocol[T]):
    """Generic interface supporting parsing and formatting.

    Parsing always results in a ``ParseResult[T]`` which can represent success or failure.

    Idiomatic text handling in Pyoda Time involves creating a pattern once and reusing it multiple
    times, rather than specifying the pattern text repeatedly.
    """

    @abstractmethod
    def parse(self, text: str) -> ParseResult[T]:
        """Parses the given text value according to the rules of this pattern.

        This method never raises an Exception (barring a bug in Pyoda Time itself).

        :param text: The text value to parse.
        :return: The result of parsing, which may be successful or unsuccessful.
        """
        ...

    @abstractmethod
    def format(self, value: T) -> str:
        """Formats the given value as text according to the rules of this pattern.

        :param value: The value to format.
        :return: The value formatted according to this pattern.
        """
        ...

    @abstractmethod
    def append_format(self, value: T, builder: StringBuilder) -> StringBuilder:
        """Formats the given value as text according to the rules of this pattern, appending to the given
        ``StringBuilder``.

        :param value: The value to format.
        :param builder: The ``StringBuilder`` to append to.
        :return: The builder passed in as ``builder``.
        """
        ...
