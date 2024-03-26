# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import datetime
from typing import final

from pyoda_time.utility._csharp_compatibility import _sealed


@_sealed
@final
class _EraInfo:
    def __init__(
        self,
        era: int,
        start_year: int,
        start_month: int,
        start_day: int,
        year_offset: int,
        min_era_year: int,
        max_era_year: int,
        era_name: str | None = None,
        abbrev_era_name: str | None = None,
        english_era_name: str | None = None,
    ) -> None:
        self._era = era
        self._year_offset = year_offset
        self._min_era_year = min_era_year
        self._max_era_year = max_era_year
        from pyoda_time.utility._csharp_compatibility import _to_ticks

        self._ticks = _to_ticks(datetime(start_year, start_month, start_day))
        self._era_name = era_name
        self._abbrev_era_name = abbrev_era_name
        self._english_era_name = english_era_name
