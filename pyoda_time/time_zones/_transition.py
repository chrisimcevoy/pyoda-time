# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time._instant import Instant
from pyoda_time._offset import Offset
from pyoda_time.utility._csharp_compatibility import _private, _sealed


@final
@_sealed
@_private
class _Transition:
    """A transition between two offsets, usually for daylight saving reasons.

    This type only knows about the new offset, and the transition point.
    """

    __instant: Instant
    __new_offset: Offset

    @property
    def _instant(self) -> Instant:
        return self.__instant

    @property
    def _new_offset(self) -> Offset:
        """The offset from the time when this transition occurs until the next transition."""
        return self.__new_offset

    @classmethod
    def _ctor(cls, instant: Instant, new_offset: Offset) -> _Transition:
        self = super().__new__(cls)
        self.__instant = instant
        self.__new_offset = new_offset
        return self

    def equals(self, other: _Transition) -> bool:
        return self == other

    # region Operators

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Transition):
            return NotImplemented
        return self.__instant == other.__instant and self.__new_offset == other.__new_offset

    def __ne__(self, other: object) -> bool:
        return not self == other

    # endregion

    # region Object overrides

    def __hash__(self) -> int:
        # TODO unchecked
        h = 23
        h = h * 31 + hash(self.__instant)
        h = h * 31 + hash(self.__new_offset)
        return h

    def __repr__(self) -> str:
        return f"Transition to {self.__new_offset} at {self.__instant}"

    # endregion
