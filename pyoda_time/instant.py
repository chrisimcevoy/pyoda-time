from __future__ import annotations

from .duration import Duration


class Instant:
    """Represents an instant on the global timeline, with nanosecond resolution.
    An Instant has no concept of a particular time zone or calendar: it simply represents a point in
    time that can be globally agreed-upon.
    Equality and ordering comparisons are defined in the natural way, with earlier points on the timeline
    being considered "less than" later points.
    """

    def __init__(self, days: int, nano_of_day: int) -> None:
        self.duration = Duration(days, nano_of_day)

    @classmethod
    def from_duration(cls, duration: Duration) -> Instant:
        return cls(duration.days, duration.nano_of_day)

    @property
    def days_since_epoch(self) -> int:
        return self.duration.floor_days
