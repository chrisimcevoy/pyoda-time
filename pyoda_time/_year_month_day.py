# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

from ._calendar_ordinal import _CalendarOrdinal
from ._year_month_day_calendar import _YearMonthDayCalendar
from .utility import _sealed

if _typing.TYPE_CHECKING:
    from . import CalendarSystem


@_typing.final
@_sealed
class _YearMonthDay:
    """A compact representation of a year, month and day in a single 32-bit integer."""

    __DAY_MASK: _typing.Final[int] = (1 << _YearMonthDayCalendar._DAY_BITS) - 1
    __MONTH_MASK: _typing.Final[int] = ((1 << _YearMonthDayCalendar._MONTH_BITS) - 1) << _YearMonthDayCalendar._DAY_BITS

    def __init__(self) -> None:
        self.__value: int = 0

    @classmethod
    @_typing.overload
    def _ctor(cls, *, raw_value: int) -> _YearMonthDay: ...

    @classmethod
    @_typing.overload
    def _ctor(cls, *, year: int, month: int, day: int) -> _YearMonthDay: ...

    @classmethod
    def _ctor(
        cls, *, raw_value: int | None = None, year: int | None = None, month: int | None = None, day: int | None = None
    ) -> _YearMonthDay:
        """Internal constructor implementation."""
        self = super().__new__(cls)

        if raw_value is not None and year is None and month is None and day is None:
            self.__value = raw_value
        elif raw_value is None and year is not None and month is not None and day is not None:
            self.__value = (
                ((year - 1) << (_YearMonthDayCalendar._DAY_BITS + _YearMonthDayCalendar._MONTH_BITS))
                | ((month - 1) << _YearMonthDayCalendar._DAY_BITS)
                | (day - 1)
            )
        else:
            raise TypeError
        return self

    @property
    def _year(self) -> int:
        return (self.__value >> (_YearMonthDayCalendar._DAY_BITS + _YearMonthDayCalendar._MONTH_BITS)) + 1

    @property
    def _month(self) -> int:
        return ((self.__value & self.__MONTH_MASK) >> _YearMonthDayCalendar._DAY_BITS) + 1

    @property
    def _day(self) -> int:
        return (self.__value & self.__DAY_MASK) + 1

    def _with_calendar(self, calendar: CalendarSystem) -> _YearMonthDayCalendar:
        return _YearMonthDayCalendar._ctor(year_month_day=self.__value, calendar_ordinal=calendar._ordinal)

    def _with_calendar_ordinal(self, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar:
        return _YearMonthDayCalendar._ctor(year_month_day=self.__value, calendar_ordinal=calendar_ordinal)

    def compare_to(self, other: _YearMonthDay) -> int:
        # In Noda Time, this method calls `int.CompareTo(otherInt)`
        return self.__value - other.__value

    def equals(self, other: _YearMonthDay) -> bool:
        return isinstance(other, _YearMonthDay) and self.__value == other.__value

    def __hash__(self) -> int:
        return self.__value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value == other.__value
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDay):
            return not (self == other)
        return NotImplemented

    def __lt__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value < other.__value
        return NotImplemented

    def __le__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value <= other.__value
        return NotImplemented

    def __gt__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value > other.__value
        return NotImplemented

    def __ge__(self, other: _YearMonthDay) -> bool:
        if isinstance(other, _YearMonthDay):
            return self.__value >= other.__value
        return NotImplemented
