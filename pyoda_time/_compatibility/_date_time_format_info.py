# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Any

from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._culture_data import _CultureData
from pyoda_time._compatibility._i_format_provider import IFormatProvider


# TODO: ICloneable
class DateTimeFormatInfo(IFormatProvider):
    """Provides culture-specific information about the format of date and time values."""

    def __init__(self) -> None:
        from ._culture_info import CultureInfo
        from ._gregorian_calendar import GregorianCalendar

        self._culture_data: _CultureData = CultureInfo.invariant_culture._culture_data
        self._calendar: Calendar = GregorianCalendar()

        self._is_read_only: bool = False

        # Cached values exposed via lazy-initialising properties
        self.__time_separator: str | None = None

    @classmethod
    def _ctor(cls, culture_data: _CultureData, cal: Calendar) -> DateTimeFormatInfo:
        self = cls.__new__(cls)
        self._culture_data = culture_data
        self._calendar = cal
        self._is_read_only = False
        self.__initialize_overridable_properties(culture_data, cal._id)

        # Cached values exposed via lazy-initialising properties
        self.__time_separator = None

        return self

    @property
    def time_separator(self) -> str:
        """Gets or sets the string that separates the components of time, that is, the hour, minutes, and seconds."""
        if self.__time_separator is None:
            self.__time_separator = self._culture_data._time_separator
        return self.__time_separator

    @time_separator.setter
    def time_separator(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("DateTimeFormatInfo.value cannot be None")
        # TODO: this.ClearTokenHashTable();
        self.__time_separator = value

    def __verify_writable(self) -> None:
        if self._is_read_only:
            raise RuntimeError("Cannot write read-only DateFormatInfo")

    @property
    def is_read_only(self) -> bool:
        return self._is_read_only

    def __initialize_overridable_properties(self, culture_data: _CultureData, calendar_id: _CalendarId) -> None:
        # TODO: implement __initialize_overridable_properties()
        pass

    def get_format(self, format_type: type) -> Any | None:
        raise NotImplementedError
