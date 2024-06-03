# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final, overload

from .utility._csharp_compatibility import _private, _sealed

if TYPE_CHECKING:
    from . import Duration, Instant, Offset

__all__ = ["_LocalInstant"]


@final
@_sealed
@_private
class _LocalInstant:
    """Represents a local date and time without reference to a calendar system. Essentially.

    this is a duration since a Unix epoch shifted by an offset (but we don't store what that
    offset is). This class has been slimmed down considerably over time - it's used much less
    than it used to be... almost solely for time zones.
    """

    @classmethod
    def before_min_value(cls) -> _LocalInstant:
        # TODO: In Noda Time this is a public static readonly field
        from . import Instant

        return _LocalInstant.__ctor(days=Instant._before_min_value()._days_since_epoch, deliberately_invalid=True)

    @classmethod
    def after_max_value(cls) -> _LocalInstant:
        # TODO: In Noda Time this is a public static readonly field
        from . import Instant

        return _LocalInstant.__ctor(days=Instant._after_max_value()._days_since_epoch, deliberately_invalid=True)

    __duration: Duration
    """Elapsed time since the local 1970-01-01T00:00:00."""

    @classmethod
    def __ctor(cls, *, days: int, deliberately_invalid: bool) -> _LocalInstant:
        """Constructor which should *only* be used to construct the invalid instances."""
        from . import Duration

        self = super().__new__(cls)
        self.__duration = Duration._ctor(days=days, nano_of_day=0)
        return self

    @classmethod
    @overload
    def _ctor(cls, *, nanoseconds: Duration) -> _LocalInstant: ...

    @classmethod
    @overload
    def _ctor(cls, *, days: int, nano_of_day: int) -> _LocalInstant: ...

    @classmethod
    def _ctor(cls, nanoseconds: Duration | None = None, days: int | None = None, nano_of_day: int = 0) -> _LocalInstant:
        from . import Duration, Instant

        self = super().__new__(cls)
        if nanoseconds is not None:
            days = nanoseconds._floor_days
            if days < Instant._MIN_DAYS or days > Instant._MAX_DAYS:
                raise OverflowError("Operation would overflow bounds of local date/time")
            self.__duration = nanoseconds
        elif days is not None:
            self.__duration = Duration._ctor(days=days, nano_of_day=nano_of_day)
        else:
            raise TypeError
        return self

    @property
    def _is_valid(self) -> bool:
        """Returns whether or not this is a valid instant.

        Returns true for all but ``before_min_value`` and ``after_max_value``.
        """
        from . import Instant

        return Instant._MIN_DAYS <= self._days_since_epoch <= Instant._MAX_DAYS

    @property
    def _time_since_local_epoch(self) -> Duration:
        """Number of nanoseconds since the local unix epoch."""
        return self.__duration

    @property
    def _days_since_epoch(self) -> int:
        """Number of days since the local unix epoch."""
        return self.__duration._floor_days

    @property
    def _nanosecond_of_day(self) -> int:
        """Nanosecond within the day."""
        return self.__duration._nanosecond_of_floor_day

    # region Operators

    def _minus_zero_offset(self) -> Instant:
        """Returns a new instant based on this local instant, as if we'd applied a zero offset.

        This is just a slight optimization over calling ``self.minus(Offset.zero)``.
        """
        from . import Instant

        return Instant._from_trusted_duration(self.__duration)

    def minus(self, offset: Offset) -> Instant:
        """Subtracts the given time zone offset from this local instant, to give an ``Instant``.

        This would normally be implemented as an operator, but as the corresponding "plus" operation
        on Instant cannot be written (as Instant is a public type and LocalInstant is an internal type)
        it makes sense to keep them both as methods for consistency.

        :param offset: The offset between UTC and a time zone for this local instant
        :return: A new ``Instant`` representing the difference of the given values.
        """
        from . import Instant

        return Instant._from_untrusted_duration(self.__duration._minus_small_nanoseconds(offset.nanoseconds))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented
        return self.__duration == other.__duration

    def _safe_minus(self, offset: Offset) -> Instant:
        """Equivalent to ``Instant._safe_plus``, but in the opposite direction."""
        from . import Instant

        days = self.__duration._floor_days
        # If we can do the arithmetic safely, do so.
        if Instant._MIN_DAYS < days < Instant._MAX_DAYS:
            return self.minus(offset)
        # Handle BeforeMinValue and BeforeMaxValue simply.
        if days < Instant._MIN_DAYS:
            return Instant._before_min_value()
        if days > Instant._MAX_DAYS:
            return Instant._after_max_value()
        # Okay, do the arithmetic as a Duration, then check the result for overflow, effectively.
        as_duration = self.__duration._minus_small_nanoseconds(offset.nanoseconds)
        if as_duration._floor_days < Instant._MIN_DAYS:
            return Instant._before_min_value()
        if as_duration._floor_days > Instant._MAX_DAYS:
            return Instant._after_max_value()
        # And now we don't need any more checks.
        return Instant._from_trusted_duration(as_duration)

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented
        return not (self.__duration == other.__duration)

    def __lt__(self, other: _LocalInstant) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration < other.__duration

    def __le__(self, other: _LocalInstant) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration <= other.__duration

    def __gt__(self, other: _LocalInstant) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration > other.__duration

    def __ge__(self, other: _LocalInstant) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented  # type: ignore[unreachable]
        return self.__duration >= other.__duration

    # endregion

    # region Object overrides

    def __hash__(self) -> int:
        return hash(self.__duration)

    def __repr__(self) -> str:
        from .text._instant_pattern_parser import _InstantPatternParser

        if self == _LocalInstant.before_min_value():
            return _InstantPatternParser._BEFORE_MIN_VALUE_TEXT
        if self == _LocalInstant.after_max_value():
            return _InstantPatternParser._AFTER_MAX_VALUE_TEXT
        from . import LocalDate

        date = LocalDate._ctor(days_since_epoch=self.__duration._floor_days)
        from pyoda_time.text import LocalDateTimePattern

        pattern = LocalDateTimePattern.create_with_invariant_culture("uuuu-MM-ddTHH:mm:ss.FFFFFFFFF 'LOC'")
        from pyoda_time._local_date_time import LocalDateTime
        from pyoda_time._local_time import LocalTime

        utc = LocalDateTime._ctor(
            local_date=date,
            local_time=LocalTime.from_nanoseconds_since_midnight(self.__duration._nanosecond_of_floor_day),
        )
        return pattern.format(utc)

    # endregion

    # region IEquatable<LocalInstant> Members

    def equals(self, other: _LocalInstant) -> bool:
        return self == other

    # endregion
