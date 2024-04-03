# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from ...globalization._pyoda_format_info import _PyodaFormatInfo
    from .._i_pattern import IPattern

T = TypeVar("T")


class _IPatternParser(Protocol[T]):
    """Internal interface used by FixedFormatInfoPatternParser."""

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[T]: ...
