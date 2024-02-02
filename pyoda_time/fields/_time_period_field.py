# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

if _typing.TYPE_CHECKING:
    pass

from .._duration import Duration as _Duration
from .._local_date_time import LocalDateTime as _LocalDateTime
from .._local_time import LocalTime as _LocalTime
from .._pyoda_constants import PyodaConstants as _PyodaConstants
from ..utility import _csharp_modulo, _towards_zero_division


class _TimePeriodFieldMeta(type):
    @property
    def _nanoseconds(cls) -> _TimePeriodField:
        return _TimePeriodField(1)

    @property
    def _ticks(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_TICK)

    @property
    def _milliseconds(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_MILLISECOND)

    @property
    def _seconds(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_SECOND)

    @property
    def _minutes(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_MINUTE)

    @property
    def _hours(self) -> _TimePeriodField:
        return _TimePeriodField(_PyodaConstants.NANOSECONDS_PER_HOUR)


class _TimePeriodField(metaclass=_TimePeriodFieldMeta):
    def __init__(self, unit_nanoseconds: int) -> None:
        self.__unit_nanoseconds = unit_nanoseconds
        self.__units_per_day = int(_PyodaConstants.NANOSECONDS_PER_DAY / unit_nanoseconds)

    def _add_local_date_time(self, start: _LocalDateTime, units: int) -> _LocalDateTime:
        time, extra_days = self._add_local_time_with_extra_days(start.time_of_day, units)
        date = start.date if extra_days == 0 else start.date.plus_days(extra_days)
        return _LocalDateTime._ctor(local_date=date, local_time=time)

    # TODO: def _add_local_time(self, local_time: _LocalTime, value: int) -> _LocalTime:

    def _add_local_time_with_extra_days(self, local_time: _LocalTime, value: int) -> tuple[_LocalTime, int]:
        extra_days = 0
        # TODO: unchecked
        if value == 0:
            return local_time, extra_days
        days = 0
        # It's possible that there are better ways to do this, but this at least feels simple.
        if value >= 0:
            if value >= self.__units_per_day:
                # TODO: checked
                # If this overflows, that's fine. (An OverflowException is a reasonable outcome.)
                # days = checked((int) longDays);
                value = _csharp_modulo(value, self.__units_per_day)
            nanos_to_add = value * self.__unit_nanoseconds
            new_nanos = local_time.nanosecond_of_day + nanos_to_add
            if new_nanos >= _PyodaConstants.NANOSECONDS_PER_DAY:
                new_nanos -= _PyodaConstants.NANOSECONDS_PER_DAY
                # TODO: checked
                days += 1
            # TODO: checked
            extra_days += days
            return _LocalTime._ctor(nanoseconds=new_nanos), extra_days
        else:
            if value <= self.__units_per_day:
                long_days = _towards_zero_division(value, self.__units_per_day)  # noqa
                # TODO: checked
                # If this overflows, that's fine. (An OverflowException is a reasonable outcome.)
                # days = checked((int) longDays);
                value = _csharp_modulo(value, self.__units_per_day)
            nanos_to_add = value * self.__unit_nanoseconds
            new_nanos = local_time.nanosecond_of_day + nanos_to_add
            if new_nanos < 0:
                new_nanos += _PyodaConstants.NANOSECONDS_PER_DAY
                # TODO: checked
                days -= 1
            # TODO: checked
            extra_days += days
            return _LocalTime._ctor(nanoseconds=new_nanos), extra_days

    def _units_between(self, start: _LocalDateTime, end: _LocalDateTime) -> int:
        start_local_instant = start._to_local_instant()
        end_local_instant = end._to_local_instant()
        duration = end_local_instant._time_since_local_epoch - start_local_instant._time_since_local_epoch
        return self._get_units_in_duration(duration)

    def _get_units_in_duration(self, duration: _Duration) -> int:
        return _towards_zero_division(duration.to_nanoseconds(), self.__unit_nanoseconds)
