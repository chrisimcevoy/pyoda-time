# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Final, overload

from ._local_time import LocalTime
from ._offset import Offset

__all__ = ["OffsetTime"]


class OffsetTime:
    __NANOSECONDS_BITS: Final[int] = 47
    __NANOSECONDS_MASK: Final[int] = (1 << __NANOSECONDS_BITS) - 1

    def __init__(self, time: LocalTime, offset: Offset) -> None:
        nanosecond_of_day = time.nanosecond_of_day
        offset_seconds = offset.seconds
        self.__nanoseconds_and_offset = nanosecond_of_day | (offset_seconds << self.__NANOSECONDS_BITS)

    @classmethod
    @overload
    def _ctor(cls, *, nanosecond_of_day_zero_offset: int) -> OffsetTime: ...

    @classmethod
    @overload
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
    def time_of_day(self) -> LocalTime:
        """Gets the time-of-day represented by this value.

        :return: The time-of-day represented by this value.
        """
        return LocalTime._ctor(nanoseconds=self.nanosecond_of_day)

    @property
    def offset(self) -> Offset:
        """Gets the offset from UTC of this value.

        :return: The offset from UTC of this value.
        """
        return Offset._ctor(seconds=self.__nanoseconds_and_offset >> self.__NANOSECONDS_BITS)

    @property
    def _offset_nanoseconds(self) -> int:
        """Returns the number of nanoseconds in the offset, without going via an Offset."""
        return self.__nanoseconds_and_offset >> self.__NANOSECONDS_BITS

    @property
    def nanosecond_of_day(self) -> int:
        return self.__nanoseconds_and_offset & self.__NANOSECONDS_MASK

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OffsetTime):
            return NotImplemented
        return self.time_of_day == other.time_of_day and self.offset == other.offset
