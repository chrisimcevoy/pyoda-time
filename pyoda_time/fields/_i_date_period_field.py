# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc as _abc
import typing as _typing

if _typing.TYPE_CHECKING:
    from .._local_date import LocalDate as _LocalDate


class _IDatePeriodField:
    """General representation of the difference between two dates in a particular time unit, such as "days" or
    "months"."""

    @_abc.abstractmethod
    def add(self, local_date: _LocalDate, value: int) -> _LocalDate:
        """Adds a duration value (which may be negative) to the date. This may not be reversible; for example, adding a
        month to January 30th will result in February 28th or February 29th.

        :param local_date: The local date to add to.
        :param value: The value to add, in the units of the field.
        :return: The updated local date.
        """
        raise NotImplementedError

    @_abc.abstractmethod
    def units_between(self, start: _LocalDate, end: _LocalDate) -> int:
        """Computes the difference between two local dates, as measured in the units of this field, rounding towards
        zero. This rounding means that unit.Add(start, unit.UnitsBetween(start, end)) always ends up with a date between
        start and end. (Ideally equal to end, but importantly, it never overshoots.)

        :param start: The start date.
        :param end: The end date.
        :return: The difference in the units of this field.
        """
        raise NotImplementedError
