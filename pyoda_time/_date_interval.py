# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from . import LocalDate

from .utility._csharp_compatibility import _sealed
from .utility._preconditions import _Preconditions

__all__ = ["DateInterval"]


@_sealed
@final
class DateInterval:
    """An interval between two dates."""

    @property
    def start(self) -> LocalDate:
        """The start date of the interval."""
        return self.__start

    @property
    def end(self) -> LocalDate:
        """The end date of the interval."""
        return self.__end

    def __init__(self, start: LocalDate, end: LocalDate) -> None:
        """Constructs a date interval from a start date and an end date, both of which are included in the interval.

        :param start: Start date of the interval
        :param end: End date of the interval
        """
        _Preconditions._check_argument(
            start.calendar == end.calendar, "end", "Calendars of start and end dates must be the same."
        )
        _Preconditions._check_argument(not end < start, "end", "End date must not be earlier than the start date")
        self.__start: LocalDate = start
        self.__end: LocalDate = end

    def __hash__(self) -> int:
        return hash((self.start, self.__end))

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if isinstance(other, DateInterval):
            return self.start == other.start and self.end == other.end
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, DateInterval):
            return not self == other
        return NotImplemented

    def equals(self, other: DateInterval) -> bool:
        return self == other
