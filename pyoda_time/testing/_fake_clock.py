# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import threading
from typing import Final, final

from .._duration import Duration
from .._i_clock import IClock
from .._instant import Instant
from ..utility._csharp_compatibility import _sealed


@final
@_sealed
class FakeClock(IClock):
    """Clock which can be constructed with an initial instant, and then advanced programmatically (and optionally,
    automatically advanced on each read).

    This class is designed to be used when testing classes which take an ``IClock`` as a dependency.

    This class is somewhere between a fake and a stub, depending on how it's used - if it's set to
    ``auto_advance`` then time will pass, but in a pretty odd way (i.e. dependent on how often it's
    consulted).
    """

    __slots__ = (
        "__lock",
        "__now",
        "__auto_advance",
    )

    def __init__(self, initial: Instant, auto_advance: Duration = Duration.zero) -> None:
        """Creates a fake clock initially set to the given instant.

        The clock will advance by the given duration on each read, defaulting to ``Duration.zero``.

        :param initial: The initial instant.
        :param auto_advance: The duration to advance the clock on each read.
        """
        self.__lock: Final[threading.Lock] = threading.Lock()
        self.__now: Instant = initial
        self.__auto_advance: Duration = auto_advance

    @classmethod
    def from_utc(
        cls,
        year: int,
        month_of_year: int,
        day_of_month: int,
        hour_of_day: int = 0,
        minute_of_hour: int = 0,
        second_of_minute: int = 0,
    ) -> FakeClock:
        """Returns a fake clock initially set to the given year/month/day/time in UTC in the ISO calendar.

        The value of the ``auto_advance`` property will be initialised to zero.

        :param year: The year. This is the "absolute year", so a value of 0 means 1 BC, for example.
        :param month_of_year: The month of year.
        :param day_of_month: The day of month.
        :param hour_of_day: The hour.
        :param minute_of_hour: The minute.
        :param second_of_minute: The second.
        :return: A ``FakeClock`` initialised to the given instant, with no auto-advance.
        """
        return cls(Instant.from_utc(year, month_of_year, day_of_month, hour_of_day, minute_of_hour, second_of_minute))

    def advance(self, duration: Duration) -> None:
        """Advances the clock by the given duration.

        :param duration: The duration to advance the clock by (or if negative, the duration to move it back by).
        """
        with self.__lock:
            self.__now += duration

    def advance_nanoseconds(self, nanoseconds: int) -> None:
        """Advances the clock by the given number of nanoseconds.

        :param nanoseconds: The number of nanoseconds to advance the clock by (or if negative, the number to move it
            back by).
        """
        with self.__lock:
            self.advance(Duration.from_nanoseconds(nanoseconds))

    def advance_ticks(self, ticks: int) -> None:
        """Advances the clock by the given number of ticks.

        :param ticks: The number of ticks to advance the clock by (or if negative, the number to move it back by).
        """
        with self.__lock:
            self.advance(Duration.from_ticks(ticks))

    def advance_milliseconds(self, milliseconds: int) -> None:
        """Advances the clock by the given number of milliseconds.

        :param milliseconds: The number of milliseconds to advance the clock by (or if negative, the number to move it
            back by).
        """
        with self.__lock:
            self.advance(Duration.from_milliseconds(milliseconds))

    def advance_seconds(self, seconds: int) -> None:
        """Advances the clock by the given number of seconds.

        :param seconds: The number of seconds to advance the clock by (or if negative, the number to move it back by).
        """
        with self.__lock:
            self.advance(Duration.from_seconds(seconds))

    def advance_minutes(self, minutes: int) -> None:
        """Advances the clock by the given number of minutes.

        :param minutes: The number of minutes to advance the clock by (or if negative, the number to move it back by).
        """
        with self.__lock:
            self.advance(Duration.from_minutes(minutes))

    def advance_hours(self, hours: int) -> None:
        """Advances the clock by the given number of hours.

        :param hours: The number of hours to advance the clock by (or if negative, the number to move it back by).
        """
        with self.__lock:
            self.advance(Duration.from_hours(hours))

    def advance_days(self, days: int) -> None:
        """Advances the clock by the given number of days.

        :param days: The number of days to advance the clock by (or if negative, the number to move it back by).
        """
        with self.__lock:
            self.advance(Duration.from_days(days))

    def reset(self, instant: Instant) -> None:
        """Resets the clock to the given instant.

        The value of the ``auto_advance`` property will be unchanged.

        :param instant: The instant to set the clock to.
        """
        with self.__lock:
            self.__now = instant

    def get_current_instant(self) -> Instant:
        """Returns the "current time" for this clock.

        Unlike a normal clock, this property may return the same value from repeated calls until one of the methods to
        change the time is called.

        If the value of the ``auto_advance`` property is non-zero, then every call to this method will advance the
        current time by that value.

        :return: The "current time" from this (fake) clock.
        """
        with self.__lock:
            then = self.__now
            self.__now += self.__auto_advance
            return then

    @property
    def auto_advance(self) -> Duration:
        """Gets/Sets the amount of time to advance the clock by on each call to read the current time.

        If this is ``Duration.zero``, the current time as reported by this clock will not change other than by calls to
        ``reset`` or to one of the ``advance`` methods.

        The value could even be negative, to simulate particularly odd system clock effects.

        :return: The amount of time to advance the clock by on each call to read the current time.
        """
        with self.__lock:
            return self.__auto_advance

    @auto_advance.setter
    def auto_advance(self, value: Duration) -> None:
        with self.__lock:
            self.__auto_advance = value
