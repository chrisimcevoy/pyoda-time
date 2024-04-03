# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Final, final

from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time._local_date import LocalDate
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_result import ParseResult
from pyoda_time.utility._csharp_compatibility import _private, _sealed


@final
@_sealed
@_private
class LocalDatePattern(IPattern[LocalDate]):
    """Represents a pattern for parsing and formatting ``Instant`` values."""

    _DEFAULT_TWO_DIGIT_YEAR_MAX: Final[int] = 30

    def parse(self, text: str) -> ParseResult[LocalDate]:
        raise NotImplementedError

    def format(self, value: LocalDate) -> str:
        raise NotImplementedError

    def append_format(self, value: LocalDate, builder: StringBuilder) -> StringBuilder:
        raise NotImplementedError
