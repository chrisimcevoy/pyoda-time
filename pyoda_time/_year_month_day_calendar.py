# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ._calendar_ordinal import _CalendarOrdinal
from .utility._csharp_compatibility import _int32_overflow, _sealed

if typing.TYPE_CHECKING:
    from ._year_month_day import _YearMonthDay


@typing.final
@_sealed
class _YearMonthDayCalendar:
    """A compact representation of a year, month, day and calendar ordinal (integer ID) in a single 32-bit integer."""

    # These constants are internal so they can be used in YearMonthDay
    _CALENDAR_BITS: typing.Final[int] = 6  # Up to 64 calendars.
    _DAY_BITS: typing.Final[int] = 6  # Up to 64 days in a month.
    _MONTH_BITS: typing.Final[int] = 5  # Up to 32 months per year.
    _YEAR_BITS: typing.Final[int] = 15  # 32K range; only need -10K to +10K.

    # Just handy constants to use for shifting and masking.
    __CALENDAR_DAY_BITS: typing.Final[int] = _CALENDAR_BITS + _DAY_BITS
    __CALENDAR_DAY_MONTH_BITS: typing.Final[int] = __CALENDAR_DAY_BITS + _MONTH_BITS

    __CALENDAR_MASK: typing.Final[int] = (1 << _CALENDAR_BITS) - 1
    __DAY_MASK: typing.Final[int] = ((1 << _DAY_BITS) - 1) << _CALENDAR_BITS
    __MONTH_MASK: typing.Final[int] = ((1 << _MONTH_BITS) - 1) << __CALENDAR_DAY_BITS
    __YEAR_MASK: typing.Final[int] = ((1 << _YEAR_BITS) - 1) << __CALENDAR_DAY_MONTH_BITS

    def __init__(self) -> None:
        self.__value: int = 0

    @classmethod
    @typing.overload
    def _ctor(cls, *, year_month_day: int, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar: ...

    @classmethod
    @typing.overload
    def _ctor(cls, *, year: int, month: int, day: int, calendar_ordinal: _CalendarOrdinal) -> _YearMonthDayCalendar: ...

    @classmethod
    def _ctor(
        cls,
        *,
        year_month_day: int | None = None,
        calendar_ordinal: _CalendarOrdinal | None = None,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
    ) -> _YearMonthDayCalendar:
        """Implementation of internal constructors (see overloads)."""
        self = super().__new__(cls)
        if year is not None and month is not None and day is not None and calendar_ordinal is not None:
            self.__value = (
                ((year - 1) << self.__CALENDAR_DAY_MONTH_BITS)
                | ((month - 1) << self.__CALENDAR_DAY_BITS)
                | ((day - 1) << self._CALENDAR_BITS)
                | int(calendar_ordinal)
            )
        elif year_month_day is not None and calendar_ordinal is not None:
            year_month_day = year_month_day
            calendar_ordinal = calendar_ordinal
            self.__value = (year_month_day << cls._CALENDAR_BITS) | int(calendar_ordinal)
        else:
            raise TypeError
        return self

    @property
    def _calendar_ordinal(self) -> _CalendarOrdinal:
        return _CalendarOrdinal(self.__value & self.__CALENDAR_MASK)

    @property
    def _year(self) -> int:
        return (_int32_overflow(self.__value & self.__YEAR_MASK) >> self.__CALENDAR_DAY_MONTH_BITS) + 1

    @property
    def _month(self) -> int:
        return ((self.__value & self.__MONTH_MASK) >> self.__CALENDAR_DAY_BITS) + 1

    @property
    def _day(self) -> int:
        return ((self.__value & self.__DAY_MASK) >> self._CALENDAR_BITS) + 1

    @classmethod
    def _parse(cls, text: str) -> _YearMonthDayCalendar:
        # Handle a leading - to negate the year
        if text[0] == "-":
            ymdc = cls._parse(text[1:])
            return _YearMonthDayCalendar._ctor(
                year=-ymdc._year,
                month=ymdc._month,
                day=ymdc._day,
                calendar_ordinal=ymdc._calendar_ordinal,
            )

        bits = text.split("-")
        return _YearMonthDayCalendar._ctor(
            year=int(bits[0]),
            month=int(bits[1]),
            day=int(bits[2]),
            calendar_ordinal=getattr(_CalendarOrdinal, bits[3]),
        )

    def _to_year_month_day(self) -> _YearMonthDay:
        from ._year_month_day import _YearMonthDay

        return _YearMonthDay._ctor(raw_value=self.__value >> self._CALENDAR_BITS)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, _YearMonthDayCalendar):
            return self.__value == other.__value
        return NotImplemented

    def __hash__(self) -> int:
        return self.__value
