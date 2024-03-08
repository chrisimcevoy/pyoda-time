# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

if _typing.TYPE_CHECKING:
    from . import Instant

__all__ = ["PyodaConstants"]


class _PyodaConstantsMeta(type):
    """Contains properties of the PyodaConstants class.

    These properties maintain the similarity in our API to that of Noda Time,
    but avoid issues with certain classes not being defined yet when declared
    as class attributes on the `PyodaConstants` class.
    """

    @property
    def BCL_EPOCH(cls) -> Instant:
        """The instant at the BCL epoch of midnight 1st January 0001 UTC."""
        from . import Instant

        return Instant.from_utc(1, 1, 1, 0, 0)

    @property
    def UNIX_EPOCH(cls) -> Instant:
        """The instant at the Unix epoch of midnight 1st January 1970 UTC."""
        from . import Instant

        return Instant.from_unix_time_ticks(0)


class PyodaConstants(metaclass=_PyodaConstantsMeta):
    HOURS_PER_DAY: _typing.Final[int] = 24
    DAYS_PER_WEEK: _typing.Final[int] = 7
    SECONDS_PER_MINUTE: _typing.Final[int] = 60
    MINUTES_PER_HOUR: _typing.Final[int] = 60
    MINUTES_PER_DAY: _typing.Final[int] = MINUTES_PER_HOUR * HOURS_PER_DAY
    SECONDS_PER_HOUR: _typing.Final[int] = SECONDS_PER_MINUTE * MINUTES_PER_HOUR
    SECONDS_PER_DAY: _typing.Final[int] = SECONDS_PER_HOUR * HOURS_PER_DAY
    MILLISECONDS_PER_SECOND: _typing.Final[int] = 1000
    MILLISECONDS_PER_MINUTE: _typing.Final[int] = MILLISECONDS_PER_SECOND * SECONDS_PER_MINUTE
    MILLISECONDS_PER_HOUR: _typing.Final[int] = MILLISECONDS_PER_MINUTE * MINUTES_PER_HOUR
    MILLISECONDS_PER_DAY: _typing.Final[int] = MILLISECONDS_PER_HOUR * HOURS_PER_DAY
    NANOSECONDS_PER_TICK: _typing.Final[int] = 100
    NANOSECONDS_PER_MILLISECOND: _typing.Final[int] = 1000000
    NANOSECONDS_PER_SECOND: _typing.Final[int] = 1000000000
    NANOSECONDS_PER_MINUTE: _typing.Final[int] = NANOSECONDS_PER_SECOND * SECONDS_PER_MINUTE
    NANOSECONDS_PER_HOUR: _typing.Final[int] = NANOSECONDS_PER_MINUTE * MINUTES_PER_HOUR
    NANOSECONDS_PER_DAY: _typing.Final[int] = NANOSECONDS_PER_HOUR * HOURS_PER_DAY
    NANOSECONDS_PER_WEEK: _typing.Final[int] = NANOSECONDS_PER_DAY * DAYS_PER_WEEK
    TICKS_PER_MILLISECOND: _typing.Final[int] = 10_000
    TICKS_PER_SECOND: _typing.Final[int] = TICKS_PER_MILLISECOND * MILLISECONDS_PER_SECOND
    TICKS_PER_MINUTE: _typing.Final[int] = TICKS_PER_SECOND * SECONDS_PER_MINUTE
    TICKS_PER_HOUR: _typing.Final[int] = TICKS_PER_MINUTE * MINUTES_PER_HOUR
    TICKS_PER_DAY: _typing.Final[int] = TICKS_PER_HOUR * HOURS_PER_DAY
    TICKS_PER_WEEK: _typing.Final[int] = TICKS_PER_DAY * DAYS_PER_WEEK

    # Constants which are specific to Pyoda Time
    NANOSECONDS_PER_MICROSECOND: _typing.Final[int] = 1000
    TICKS_PER_MICROSECOND: _typing.Final[int] = 10
    MICROSECONDS_PER_MILLISECOND: _typing.Final[int] = 1000
    MICROSECONDS_PER_SECOND: _typing.Final[int] = MICROSECONDS_PER_MILLISECOND * MILLISECONDS_PER_SECOND
    MICROSECONDS_PER_MINUTE: _typing.Final[int] = MICROSECONDS_PER_SECOND * SECONDS_PER_MINUTE
    MICROSECONDS_PER_HOUR: _typing.Final[int] = MICROSECONDS_PER_MINUTE * MINUTES_PER_HOUR
    MICROSECONDS_PER_DAY: _typing.Final[int] = MICROSECONDS_PER_HOUR * HOURS_PER_DAY
    MICROSECONDS_PER_WEEK: _typing.Final[int] = MICROSECONDS_PER_DAY * DAYS_PER_WEEK
