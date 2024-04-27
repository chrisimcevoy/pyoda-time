# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final, overload

from .utility._csharp_compatibility import _sealed

if TYPE_CHECKING:
    from . import Duration, Instant, Offset


__all__ = ["_LocalInstant"]


@final
@_sealed
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

    def __init__(self) -> None:
        from . import Duration

        self.__duration = Duration()

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

    @classmethod
    def __ctor(cls, *, days: int, deliberately_invalid: bool) -> _LocalInstant:
        """Constructor which should *only* be used to construct the invalid instances."""
        from . import Duration

        self = super().__new__(cls)
        self.__duration = Duration._ctor(days=days, nano_of_day=0)
        return self

    @property
    def _is_valid(self) -> bool:
        from . import Instant

        return Instant._MIN_DAYS < self._days_since_epoch < Instant._MAX_DAYS

    @property
    def _time_since_local_epoch(self) -> Duration:
        """Number of nanoseconds since the local unix epoch."""
        return self.__duration

    @property
    def _days_since_epoch(self) -> int:
        return self.__duration._floor_days

    @property
    def _nanosecond_of_day(self) -> int:
        return self.__duration._nanosecond_of_floor_day

    # region Operators

    def minus(self, offset: Offset) -> Instant:
        from . import Instant

        return Instant._from_untrusted_duration(self.__duration._minus_small_nanoseconds(offset.nanoseconds))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _LocalInstant):
            return NotImplemented
        return self.__duration == other.__duration

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

    # endregion

    # region IEquatable<LocalInstant> Members

    # endregion
