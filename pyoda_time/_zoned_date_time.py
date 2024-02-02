# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

if _typing.TYPE_CHECKING:
    from . import (
        CalendarSystem,
        DateTimeZone,
        Instant,
        LocalDateTime,
        Offset,
        OffsetDateTime,
    )

from .utility import _Preconditions

__all__ = ["ZonedDateTime"]


class ZonedDateTime:
    @classmethod
    def _ctor(cls, offset_date_time: OffsetDateTime, zone: DateTimeZone) -> ZonedDateTime:
        self = super().__new__(cls)
        self.__offset_date_time = offset_date_time
        self.__zone = zone
        return self

    @_typing.overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone) -> None:
        ...

    @_typing.overload
    def __init__(self, *, local_date_time: LocalDateTime, zone: DateTimeZone, offset: Offset) -> None:
        ...

    @_typing.overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone, calendar: CalendarSystem) -> None:
        ...

    def __init__(
        self,
        *,
        zone: DateTimeZone,
        instant: Instant | None = None,
        local_date_time: LocalDateTime | None = None,
        offset: Offset | None = None,
        calendar: CalendarSystem | None = None,
    ) -> None:
        from . import OffsetDateTime

        if offset is not None and calendar is not None:
            raise ValueError("offset and calendar are mutually exclusive")

        offset_date_time: OffsetDateTime
        if local_date_time is not None and offset is not None:
            candidate_instant = local_date_time._to_local_instant().minus(offset)
            correct_offset: Offset = zone.get_utc_offset(candidate_instant)
            if correct_offset != offset:
                raise ValueError(
                    f"Offset {offset} is invalid for local date and time {local_date_time} in time zone {zone.id}"
                )
            offset_date_time = OffsetDateTime(local_date_time=local_date_time, offset=offset)
        elif calendar is not None and instant is not None:
            offset_date_time = OffsetDateTime._ctor(
                instant=instant, offset=zone.get_utc_offset(instant), calendar=calendar
            )
        elif instant is not None:
            offset_date_time = OffsetDateTime._ctor(instant=instant, offset=zone.get_utc_offset(instant))
        else:
            raise ValueError

        self.__offset_date_time: OffsetDateTime = offset_date_time
        self.__zone: DateTimeZone = _Preconditions._check_not_null(zone, "zone")

    @property
    def local_date_time(self) -> LocalDateTime:
        return self.__offset_date_time.local_date_time
