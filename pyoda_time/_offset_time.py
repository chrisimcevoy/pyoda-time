# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

if _typing.TYPE_CHECKING:
    from . import LocalTime
    from ._offset import Offset

__all__ = ["OffsetTime"]


class OffsetTime:
    __NANOSECONDS_BITS: _typing.Final[int] = 47
    __NANOSECONDS_MASK: _typing.Final[int] = (1 << __NANOSECONDS_BITS) - 1

    def __init__(self, time: LocalTime, offset: Offset) -> None:
        nanosecond_of_day = time.nanosecond_of_day
        offset_seconds = offset.seconds
        self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)

    @classmethod
    @_typing.overload
    def _ctor(cls, *, nanosecond_of_day_zero_offset: int) -> OffsetTime: ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, nanosecond_of_day: int, offset_seconds: int) -> OffsetTime: ...

    @classmethod
    def _ctor(
        cls,
        *,
        nanosecond_of_day_zero_offset: int | None = None,
        nanosecond_of_day: int | None = None,
        offset_seconds: int | None = None,
    ) -> OffsetTime:
        self = super().__new__(cls)
        if nanosecond_of_day_zero_offset is not None:
            # TODO: Preconditions.DebugCheckArgument
            self.__nanoseconds_and_offset = nanosecond_of_day_zero_offset
        elif nanosecond_of_day is not None and offset_seconds is not None:
            self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)
        else:
            raise ValueError
        return self

    @property
    def nanosecond_of_day(self) -> int:
        return self.__nanoseconds_and_offset & self.__NANOSECONDS_MASK
