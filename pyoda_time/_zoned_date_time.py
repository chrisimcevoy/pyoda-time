# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, overload

if TYPE_CHECKING:
    from . import (
        CalendarSystem,
        DateTimeZone,
        Instant,
        LocalDateTime,
        Offset,
        OffsetDateTime,
    )

from .utility._preconditions import _Preconditions

__all__ = ["ZonedDateTime"]


class ZonedDateTime:
    @classmethod
    def _ctor(cls, offset_date_time: OffsetDateTime, zone: DateTimeZone) -> ZonedDateTime:
        self = super().__new__(cls)
        self.__offset_date_time = offset_date_time
        self.__zone = zone
        return self

    @overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone) -> None: ...

    @overload
    def __init__(self, *, local_date_time: LocalDateTime, zone: DateTimeZone, offset: Offset) -> None: ...

    @overload
    def __init__(self, *, instant: Instant, zone: DateTimeZone, calendar: CalendarSystem) -> None: ...

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

    @property
    def year(self) -> int:
        """Gets the year of this zoned date and time.

        This returns the "absolute year", so, for the ISO calendar, a value of 0 means 1 BC, for example.

        :return: The year of this zoned date and time.
        """
        return self.__offset_date_time.year

    def to_instant(self) -> Instant:
        """Converts this value to the instant it represents on the timeline.

        This is always an unambiguous conversion. Any difficulties due to daylight saving
        transitions or other changes in time zone are handled when converting from a
        ``LocalDateTime`` to a ``ZonedDateTime``; the ``ZonedDateTime`` remembers
        the actual offset from UTC to local time, so it always knows the exact instant represented.

        :return: The instant corresponding to this value.
        """
        return self.__offset_date_time.to_instant()
