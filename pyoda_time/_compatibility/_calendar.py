# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import ABC

from pyoda_time._compatibility._calendar_id import _CalendarId


class Calendar(ABC):  # TODO: ICloneable
    """A bare-bones equivalent to the ``System.Globalization.Calendar`` abstract class in .NET."""

    @property
    def _id(self) -> _CalendarId:
        return _CalendarId.UNINITIALIZED_VALUE
