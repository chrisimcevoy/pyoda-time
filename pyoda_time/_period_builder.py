# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing

from ._period_units import PeriodUnits
from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

if typing.TYPE_CHECKING:
    from ._period import Period

__all__ = ["PeriodBuilder"]


@typing.final
@_sealed
class PeriodBuilder:
    """A mutable builder class for ``Period`` values.

    Each property can be set independently, and then a ``Period`` can be
    created from the result using the ``build`` method.
    """

    def __init__(
        self,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
        milliseconds: int = 0,
        ticks: int = 0,
        nanoseconds: int = 0,
    ) -> None:
        self.years: int = years
        self.months: int = months
        self.weeks: int = weeks
        self.days: int = days
        self.hours: int = hours
        self.minutes: int = minutes
        self.seconds: int = seconds
        self.milliseconds: int = milliseconds
        self.ticks: int = ticks
        self.nanoseconds: int = nanoseconds

    @classmethod
    def from_period(cls, period: Period) -> PeriodBuilder:
        # TODO: In Noda Time this is a public ctor, but I don't want yet another @typing.overload situation
        _Preconditions._check_not_null(period, "period")
        return cls(
            years=period.years,
            months=period.months,
            weeks=period.weeks,
            days=period.days,
            hours=period.hours,
            minutes=period.minutes,
            seconds=period.seconds,
            milliseconds=period.milliseconds,
            ticks=period.ticks,
            nanoseconds=period.nanoseconds,
        )

    def __getitem__(self, key: PeriodUnits) -> int:
        if not isinstance(key, PeriodUnits):
            raise TypeError(f"key must be {PeriodUnits.__name__}, not {type(key).__name__}")
        match key:
            case PeriodUnits.YEARS:
                return self.years
            case PeriodUnits.MONTHS:
                return self.months
            case PeriodUnits.WEEKS:
                return self.weeks
            case PeriodUnits.DAYS:
                return self.days
            case PeriodUnits.HOURS:
                return self.hours
            case PeriodUnits.MINUTES:
                return self.minutes
            case PeriodUnits.SECONDS:
                return self.seconds
            case PeriodUnits.MILLISECONDS:
                return self.milliseconds
            case PeriodUnits.TICKS:
                return self.ticks
            case PeriodUnits.NANOSECONDS:
                return self.nanoseconds
            case _:
                raise ValueError("Indexer for PeriodBuilder only takes a single unit")

    def __setitem__(self, key: PeriodUnits, value: int) -> None:
        if not isinstance(key, PeriodUnits):
            raise TypeError(f"Key must be {PeriodUnits.__name__}, not {type(key).__name__}")
        match key:
            case PeriodUnits.YEARS:
                self.years = value
            case PeriodUnits.MONTHS:
                self.months = value
            case PeriodUnits.WEEKS:
                self.weeks = value
            case PeriodUnits.DAYS:
                self.days = value
            case PeriodUnits.HOURS:
                self.hours = value
            case PeriodUnits.MINUTES:
                self.minutes = value
            case PeriodUnits.SECONDS:
                self.seconds = value
            case PeriodUnits.MILLISECONDS:
                self.milliseconds = value
            case PeriodUnits.TICKS:
                self.ticks = value
            case PeriodUnits.NANOSECONDS:
                self.nanoseconds = value
            case _:
                raise ValueError("Indexer for PeriodBuilder only takes a single unit")

    def build(self) -> Period:
        from ._period import Period

        return Period._ctor(
            years=self.years,
            months=self.months,
            weeks=self.weeks,
            days=self.days,
            hours=self.hours,
            minutes=self.minutes,
            seconds=self.seconds,
            milliseconds=self.milliseconds,
            ticks=self.ticks,
            nanoseconds=self.nanoseconds,
        )
