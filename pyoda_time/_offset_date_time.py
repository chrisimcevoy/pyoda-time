# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ._pyoda_constants import PyodaConstants

if typing.TYPE_CHECKING:
    from . import Instant, LocalDate, LocalDateTime, LocalTime, OffsetTime
    from ._calendar_system import CalendarSystem
    from ._offset import Offset


__all__ = ["OffsetDateTime"]


class OffsetDateTime:
    def __init__(self, local_date_time: LocalDateTime, offset: Offset) -> None:
        from . import OffsetTime

        self.__local_date = local_date_time.date
        self.__offset_time = OffsetTime._ctor(
            nanosecond_of_day=local_date_time.nanosecond_of_day, offset_seconds=offset.seconds
        )

    @classmethod
    @typing.overload
    def _ctor(cls, *, local_date: LocalDate, offset_time: OffsetTime) -> OffsetDateTime: ...

    @classmethod
    @typing.overload
    def _ctor(cls, *, instant: Instant, offset: Offset) -> OffsetDateTime: ...

    @classmethod
    @typing.overload
    def _ctor(cls, *, instant: Instant, offset: Offset, calendar: CalendarSystem) -> OffsetDateTime: ...

    @classmethod
    def _ctor(
        cls,
        *,
        local_date: LocalDate | None = None,
        offset_time: OffsetTime | None = None,
        instant: Instant | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> OffsetDateTime:
        from . import LocalDate, OffsetTime

        if instant is not None and offset is not None:
            days = instant._days_since_epoch
            nano_of_day = instant._nanosecond_of_day + offset.nanoseconds
            if nano_of_day >= PyodaConstants.NANOSECONDS_PER_DAY:
                days += 1
                nano_of_day -= PyodaConstants.NANOSECONDS_PER_DAY
            elif nano_of_day < 0:
                days -= 1
                nano_of_day += PyodaConstants.NANOSECONDS_PER_DAY
            local_date = (
                LocalDate._ctor(days_since_epoch=days)
                if calendar is None
                else LocalDate._ctor(days_since_epoch=days, calendar=calendar)
            )
            offset_time = OffsetTime._ctor(nanosecond_of_day=nano_of_day, offset_seconds=offset.seconds)
        if local_date is not None and offset_time is not None:
            self = super().__new__(cls)
            self.__local_date = local_date
            self.__offset_time = offset_time
            return self
        raise TypeError

    @property
    def nanosecond_of_day(self) -> int:
        return self.__offset_time.nanosecond_of_day

    @property
    def local_date_time(self) -> LocalDateTime:
        from . import LocalDateTime

        return LocalDateTime._ctor(local_date=self.date, local_time=self.time_of_day)

    @property
    def date(self) -> LocalDate:
        return self.__local_date

    @property
    def time_of_day(self) -> LocalTime:
        from . import LocalTime

        return LocalTime._ctor(nanoseconds=self.nanosecond_of_day)
