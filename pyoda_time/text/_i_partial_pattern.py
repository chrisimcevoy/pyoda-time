# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import abstractmethod

from pyoda_time.text._i_pattern import IPattern, T
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.text._value_cursor import _ValueCursor


class _IPartialPattern(IPattern[T]):
    """Internal interface supporting partial parsing and formatting.

    This is used when one pattern is embedded within another.
    """

    @abstractmethod
    def parse_partial(self, cursor: _ValueCursor) -> ParseResult[T]:
        """Parses a value from the current position in the cursor. This will
        not fail if the pattern ends before the cursor does - that's expected
        in most cases.

        :param cursor: The cursor to parse from.
        :return: The result of parsing from the cursor.
        """
        ...
