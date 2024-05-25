# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    from .. import (
        Duration,
        Instant,
        LocalDateTime,
        Offset,
    )
    from .._local_instant import (
        _LocalInstant,
    )

from pyoda_time.utility._csharp_compatibility import _sealed
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions

__all__ = ["ZoneInterval"]


@_sealed
@final
class ZoneInterval:
    """Represents a range of time for which a particular Offset applies.

    Equality is defined component-wise in terms of all properties: the name, the start and end, and the offsets.
    There is no ordering defined between zone intervals.
    """

    @property
    def _raw_start(self) -> Instant:
        """Returns the underlying start instant of this zone interval.

        If the zone interval extends to the beginning of time, the return
        value will be ``Instant._before_min_value``; this value
        should *not* be exposed publicly.
        """
        return self.__raw_start

    @property
    def _raw_end(self) -> Instant:
        """Returns the underlying end instant of this zone interval.

        If the zone interval extends to the end of time, the return
        value will be ``Instant._after_max_value``; this value
        should *not* be exposed publicly.
        """
        return self.__raw_end

    @property
    def standard_offset(self) -> Offset:
        """Gets the standard offset for this period.

        This is the offset without any daylight savings contributions.
        """
        return self.wall_offset - self.savings

    @property
    def duration(self) -> Duration:
        """The Duration of this zone interval."""
        return self.end - self.start

    @property
    def has_start(self) -> bool:
        """Returns ``True`` if this zone interval has a fixed start point, or ``False`` if it extends to the beginning
        of time."""
        return self._raw_start._is_valid

    @property
    def end(self) -> Instant:
        """The last Instant (exclusive) that the Offset applies."""
        _Preconditions._check_state(self._raw_end._is_valid, "Zone interval extends to the end of time")
        return self._raw_end

    @property
    def has_end(self) -> bool:
        """Returns ``True`` if this zone interval has a fixed end point, or ``False`` if it extends to the beginning of
        time."""
        return self._raw_end._is_valid

    @property
    def iso_local_start(self) -> LocalDateTime:
        """Gets the local start time of the interval, as a ``LocalDateTime`` in the ISO calendar."""
        # Use the Start property to trigger the appropriate end-of-time exception.
        # Call Plus to trigger an appropriate out-of-range exception.
        from .. import LocalDateTime

        return LocalDateTime._ctor(local_instant=self.start._plus(self.wall_offset))

    @property
    def iso_local_end(self) -> LocalDateTime:
        """Gets the local end time of the interval, as a ``LocalDateTime`` in the ISO calendar."""
        # Use the End property to trigger the appropriate end-of-time exception.
        # Call Plus to trigger an appropriate out-of-range exception.
        from .. import LocalDateTime

        return LocalDateTime._ctor(local_instant=self.end._plus(self.wall_offset))

    @property
    def name(self) -> str:
        """The name of this offset period (e.g. PST or PDT)."""
        return self.__name

    @property
    def wall_offset(self) -> Offset:
        """The offset from UTC for this period.

        This includes any daylight savings value.
        """
        return self.__wall_offset

    @property
    def savings(self) -> Offset:
        """The daylight savings value for this period."""
        return self.__savings

    @property
    def start(self) -> Instant:
        """The first Instant that the Offset applies."""
        _Preconditions._check_state(self._raw_start._is_valid, "Zone interval extends to the beginning of time")
        return self._raw_start

    # Note: This initialiser is intended to replicate the functionality of both
    # of the private constructors for the equivalent Noda Time class.
    def __init__(
        self,
        *,
        name: str,
        start: Instant | None = None,
        end: Instant | None = None,
        wall_offset: Offset,
        savings: Offset,
    ) -> None:
        from .. import Instant

        # Do not expose these defaults in the __init__ signature.
        if start is None:
            start = Instant._before_min_value()
        if end is None:
            end = Instant._after_max_value()

        _Preconditions._check_not_null(name, "name")
        if start >= end:  # Needed to prevent infinite recursion calling Instant.__repr__
            _Preconditions._check_argument(
                start < end, "start", f"The start Instant must be less than the end Instant. start: {start}; end: {end}"
            )
        self.__name: Final[str] = name
        self.__raw_start: Final[Instant] = start
        self.__raw_end: Final[Instant] = end
        self.__wall_offset: Final[Offset] = wall_offset
        self.__savings: Final[Offset] = savings
        # Work out the corresponding local instants, taking care to "go infinite" appropriately.
        self.__local_start: Final[_LocalInstant] = start._safe_plus(wall_offset)
        self.__local_end: Final[_LocalInstant] = end._safe_plus(wall_offset)

    def _with_start(self, new_start: Instant) -> ZoneInterval:
        """Returns a copy of this zone interval, but with the given start instant."""
        return ZoneInterval(
            name=self.name,
            start=new_start,
            end=self._raw_end,
            wall_offset=self.wall_offset,
            savings=self.savings,
        )

    def _with_end(self, new_end: Instant) -> ZoneInterval:
        """Returns a copy of this zone interval, but with the given end instant."""
        return ZoneInterval(
            name=self.name,
            start=self._raw_start,
            end=new_end,
            wall_offset=self.wall_offset,
            savings=self.savings,
        )

    # region Contains

    def __contains__(self, instant: Instant) -> bool:
        """Determines whether this period contains the given Instant in its range."""
        # Implementation of ``public bool Contains(Instant instant)``
        return self._raw_start <= instant < self._raw_end

    def _contains(self, local_instant: _LocalInstant) -> bool:
        """Determines whether this period contains the given LocalInstant in its range."""
        # TODO: why is this not implemented in __contains__ above?
        # Implementation of ``internal bool Contains(LocalInstant localInstant)``
        return self.__local_start <= local_instant < self.__local_end

    def _equal_ignore_bounds(self, other: ZoneInterval) -> bool:
        """Returns whether this zone interval has the same offsets and name as another."""
        # TODO: Preconditions.DebugCheckNotNull(other, nameof(other));
        return other.wall_offset == self.wall_offset and other.savings == self.savings

    # endregion

    # region IEquatable<ZoneInterval> Members

    def equals(self, other: ZoneInterval) -> bool:
        return self == other

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ZoneInterval):
            return NotImplemented
        return (
            self.name == other.name
            and self._raw_start == other._raw_start
            and self._raw_end == other._raw_end
            and self.wall_offset == other.wall_offset
            and self.savings == other.savings
        )

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, ZoneInterval):
            return NotImplemented
        return not self == other

    # endregion

    # region Object overrides

    def __hash__(self) -> int:
        return _hash_code_helper(
            self.name,
            self._raw_start,
            self._raw_end,
            self.wall_offset,
            self.savings,
        )

    def __str__(self) -> str:
        # TODO: Only the simplest case in the default culture is covered (kind of)
        return f"{self.name}: [{self.__raw_start}, {self._raw_end}) {self.wall_offset} ({self.savings})"

    # endregion
