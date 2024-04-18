# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from .. import Instant, Offset
    from . import ZoneInterval

from .._date_time_zone import DateTimeZone
from ..utility._csharp_compatibility import _sealed


@_sealed
@final
class _FixedDateTimeZone(DateTimeZone):
    def __init__(self, offset: Offset, id_: str | None = None, name: str | None = None) -> None:
        from .. import Instant, Offset
        from . import ZoneInterval

        if id_ is None:
            id_ = self.__make_id(offset)
        if name is None:
            name = id_
        super().__init__(id_, True, offset, offset)
        self.__interval = ZoneInterval(
            name=name,
            start=Instant._before_min_value(),
            end=Instant._after_max_value(),
            wall_offset=offset,
            savings=Offset.zero,
        )

    def __make_id(self, offset: Offset) -> str:
        from .. import Offset

        if offset == Offset.zero:
            return self._UTC_ID
        return self._UTC_ID + str(offset)

    @classmethod
    def _get_fixed_zone_or_null(cls, id_: str) -> DateTimeZone | None:
        if not id_.startswith(cls._UTC_ID):
            return None
        if id_ == cls._UTC_ID:
            return cls.utc
        from pyoda_time.text import OffsetPattern, ParseResult

        parse_result: ParseResult[Offset] = OffsetPattern.general_invariant.parse(id_[len(cls._UTC_ID) :])
        return cls.for_offset(parse_result.value) if parse_result.success else None

    @classmethod
    def for_offset(cls, offset: Offset) -> DateTimeZone:
        raise NotImplementedError

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        return self.__interval

    def get_utc_offset(self, instant: Instant) -> Offset:
        return self.max_offset
