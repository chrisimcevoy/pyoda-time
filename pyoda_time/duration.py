from __future__ import annotations

from .pyoda_constants import NANOSECONDS_PER_TICK
from .utility import tick_arithmetic


class Duration:

    def __init__(self, days: int = 0, nano_of_day: int = 0) -> None:
        self.days = days
        self.nano_of_day = nano_of_day

    def __eq__(self, other):
        return isinstance(other, Duration) and (self.days == other.days) and (self.nano_of_day == other.nano_of_day)

    @classmethod
    def from_ticks(cls, ticks: int) -> Duration:
        """Returns a Duration that represents the given number of ticks."""
        days, tick_of_day = tick_arithmetic.ticks_to_days_and_tick_of_day(ticks)
        return Duration(days, tick_of_day * NANOSECONDS_PER_TICK)

    @classmethod
    @property
    def zero(cls) -> Duration:
        return Duration()

    @property
    def floor_days(self) -> int:
        """Days portion of this duration."""
        return self.days
