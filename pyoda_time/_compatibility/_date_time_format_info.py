# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
from typing import Any, Sequence, _ProtocolMeta

from pyoda_time._compatibility._calendar import Calendar
from pyoda_time._compatibility._calendar_id import _CalendarId
from pyoda_time._compatibility._culture_data import _CultureData


class _DateTimeFormatInfoMeta(type):
    __s_invariantInfo: DateTimeFormatInfo | None = None

    @property
    def invariant_info(self) -> DateTimeFormatInfo:
        """Gets the default read-only ``DateTimeFormatInfo`` object that is culture-independent (invariant).

        :return: A read-only object that is culture-independent (invariant).
        """
        if self.__s_invariantInfo is None:
            date_time_format_info = DateTimeFormatInfo()
            date_time_format_info.calendar._set_read_only_state(True)
            date_time_format_info._is_read_only = True
            self.__s_invariantInfo = date_time_format_info
        return self.__s_invariantInfo


class _CombinedMeta(_ProtocolMeta, _DateTimeFormatInfoMeta):
    """Intermediary class which prevents a metaclass conflict."""


# TODO: ICloneable
class DateTimeFormatInfo(metaclass=_CombinedMeta):
    """Provides culture-specific information about the format of date and time values."""

    def __init__(self) -> None:
        from ._culture_info import CultureInfo
        from ._gregorian_calendar import GregorianCalendar

        self._culture_data: _CultureData = CultureInfo.invariant_culture._culture_data
        self.__calendar: Calendar = GregorianCalendar()

        self._is_read_only: bool = False

        # Cached values exposed via lazy-initialising properties
        self.__date_separator: str | None = None
        self.__time_separator: str | None = None
        self.__day_names: Sequence[str] | None = None
        self.__abbreviated_day_names: Sequence[str] | None = None
        self.__m_era_names: list[str] | None = None
        self.__month_names: list[str] | None = None
        self.__abbreviated_month_names: Sequence[str] | None = None
        self.__genitive_month_names: Sequence[str] | None = None
        self.__m_genitive_abbreviated_month_names: Sequence[str] | None = None

    @classmethod
    def _ctor(cls, culture_data: _CultureData, cal: Calendar) -> DateTimeFormatInfo:
        self = cls.__new__(cls)
        self._culture_data = culture_data
        self.__calendar = cal
        self._is_read_only = False
        self.__initialize_overridable_properties(culture_data, cal._id)

        # Cached values exposed via lazy-initialising properties
        self.__date_separator = None
        self.__time_separator = None
        self.__day_names = None
        self.__abbreviated_day_names = None
        self.__m_era_names = None
        self.__month_names = None
        self.__abbreviated_month_names = None
        self.__genitive_month_names = None
        self.__m_genitive_abbreviated_month_names = None

        return self

    def __internal_get_abbreviated_day_of_week_names(self) -> Sequence[str]:
        return self.__abbreviated_day_names or self.__internal_get_abbreviated_day_of_week_names_core()

    def __internal_get_abbreviated_day_of_week_names_core(self) -> Sequence[str]:
        # Get the abbreviated day names for our current calendar
        self.__abbreviated_day_names = self._culture_data._abbreviated_day_names(self.calendar._id)
        assert len(self.__abbreviated_day_names) == 7
        return self.__abbreviated_day_names

    def __internal_get_day_of_week_names(self) -> Sequence[str]:
        """Create an array of string which contains the day names."""
        return self.__day_names or self.__internal_get_day_of_week_names_core()

    def __internal_get_day_of_week_names_core(self) -> Sequence[str]:
        self.__day_names = self._culture_data._day_names(self.calendar._id)
        assert len(self.__day_names) == 7, "Expected 7 day names in a week"
        return self.__day_names

    def __internal_get_abbreviated_month_names(self) -> Sequence[str]:
        if self.__abbreviated_month_names is None:
            self.__abbreviated_month_names = self.__internal_get_abbreviated_month_names_core()
        return self.__abbreviated_month_names

    def __internal_get_abbreviated_month_names_core(self) -> Sequence[str]:
        self.__abbreviated_month_names = self._culture_data._abbreviated_month_names(self.calendar._id)
        return self.__abbreviated_month_names

    def __internal_get_month_names(self) -> Sequence[str]:
        """Create an array of string which contains the month names."""
        return self.__month_names or self.__internal_get_month_names_core()

    def __internal_get_month_names_core(self) -> Sequence[str]:
        month_names = self._culture_data._month_names(self.calendar._id)
        assert len(month_names) in (12, 13), "Expected 12 or 13 month names in a year"
        return month_names

    @property
    def date_separator(self) -> str:
        if self.__date_separator is None:
            self.__date_separator = self._culture_data._date_separator(self.calendar._id)
        return self.__date_separator

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

    def __initialize_overridable_properties(self, culture_data: _CultureData, calendar_id: _CalendarId) -> None:
        # TODO: implement __initialize_overridable_properties()
        pass

    def get_format(self, format_type: type) -> Any | None:
        raise NotImplementedError

    @property
    def calendar(self) -> Calendar:
        """Gets or sets the calendar to use for the current culture.

        :return: The calendar to use for the current culture.
        """
        return self.__calendar

    @calendar.setter
    def calendar(self, calendar: Calendar) -> None:
        if self.is_read_only:
            raise RuntimeError("Cannot assign calendar to read-only DateFormatInfo")
        if calendar is None:
            raise ValueError("Calendar cannot be None")
        if calendar != self.__calendar:
            # TODO: There is a bunch of other stuff that happens here...
            self.__calendar = calendar

    @property
    def _era_names(self) -> list[str]:
        if not self.__m_era_names:
            self.__m_era_names = self._culture_data._era_names(self.calendar._id)
        return self.__m_era_names

    @staticmethod
    def __check_null_value(values: Sequence[str], length: int) -> None:
        """Check if a string array contains a null value, and throw ArgumentNullException with parameter name
        'value'."""
        assert values is not None, "value != null"
        assert len(values) >= length
        for i in range(length):
            if values[i] is None:
                raise ValueError("values contains null values")

    @property
    def abbreviated_day_names(self) -> list[str]:
        return list(self.__internal_get_abbreviated_day_of_week_names())

    @abbreviated_day_names.setter
    def abbreviated_day_names(self, value: list[str]) -> None:
        if self.is_read_only:
            raise RuntimeError("Cannot assign to read-only DateFormatInfo")
        if value is None:
            raise ValueError("day_names cannot be None")
        if len(value) != 7:
            raise ValueError("Expected value to contain 7 items")
        self.__check_null_value(value, len(value))
        # TODO: ClearTokenHashTable()
        self.__abbreviated_day_names = value

    @property
    def day_names(self) -> list[str]:
        """Gets or sets a one-dimensional string array that contains the culture-specific full names of the days of the
        week.

        :return: A one-dimensional string array that contains the culture-specific full names of the days of the week.
            The array for ``DateTimeFormatInfo.invariant_info`` contains "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", and "Saturday".
        """
        return list(self.__internal_get_day_of_week_names())

    @day_names.setter
    def day_names(self, value: list[str]) -> None:
        if self.is_read_only:
            raise RuntimeError("Cannot assign to read-only DateFormatInfo")
        if value is None:
            raise ValueError("day_names cannot be None")
        if len(value) != 7:
            raise ValueError("Expected day_names to contain 7 items")
        self.__check_null_value(value, len(value))
        # TODO: ClearTokenHashTable();
        self.__day_names = value

    @property
    def abbreviated_month_names(self) -> list[str]:
        """Gets or sets the culture-specific abbreviated names of the months.

        :return:
        """
        return list(self.__internal_get_abbreviated_month_names())

    @abbreviated_month_names.setter
    def abbreviated_month_names(self, value: list[str]) -> None:
        self.__verify_writable()
        if value is None:
            raise TypeError("value cannot be None")
        if len(value) != 13:
            raise ValueError("Expected value to contain 13 items")

        self.__check_null_value(value, len(value) - 1)
        # TODO: ClearTokenHashTable()
        self.__abbreviated_month_names = value

    @property
    def month_names(self) -> list[str]:
        """Gets or sets the culture-specific full names of the months.

        In a 12-month calendar, the 13th element of the array is an empty string.

        The array for ``DateTimeFormatInfo.invariant_info`` contains "January",
        "February", "March", "April", "May", "June", "July", "August", "September",
        "October", "November", "December", and "".

        :return: A list containing the culture-specific full names of the months.
        """
        return list(self.__internal_get_month_names())

    @month_names.setter
    def month_names(self, value: list[str]) -> None:
        self.__verify_writable()
        if value is None:
            raise TypeError("value cannot be None")
        if len(value) != 13:
            raise ValueError("Expected value to contain 13 items")

        self.__check_null_value(value, len(value) - 1)
        self.__month_names = value
        # TODO: ClearTokenHashTable()

    @property
    def abbreviated_month_genitive_names(self) -> Sequence[str]:
        """Gets or sets a string array of abbreviated month names associated with the current ``DateTimeFormatInfo``
        object.

        :return: An array of abbreviated month names.
        """
        return list(self.__internal_get_genitive_month_names(abbreviated=True))

    @abbreviated_month_genitive_names.setter
    def abbreviated_month_genitive_names(self, value: Sequence[str]) -> None:
        self.__verify_writable()
        if value is None:
            raise TypeError("value cannot be None")
        if len(value) != 13:
            raise ValueError("Expected value to contain 13 items")

        self.__check_null_value(value, len(value) - 1)
        # TODO: ClearTokenHashTable()
        self.__m_genitive_abbreviated_month_names = value

    @property
    def month_genitive_names(self) -> Sequence[str]:
        """Gets or sets a string array of month names associated with the current ``DateTimeFormatInfo`` object.

        :return: A string array of month names.
        """
        return tuple(self.__internal_get_genitive_month_names(abbreviated=False))

    @month_genitive_names.setter
    def month_genitive_names(self, value: Sequence[str]) -> None:
        self.__verify_writable()
        if value is None:
            raise TypeError("value cannot be None")
        if len(value) != 13:
            raise ValueError("Expected value to contain 13 items")

        self.__check_null_value(value, len(value) - 1)
        self.__genitive_month_names = value
        # TODO: ClearTokenHashTable()

    def __internal_get_genitive_month_names(self, abbreviated: bool) -> Sequence[str]:
        """Retrieve the array which contains the month names in genitive form.

        If this culture does not use the genitive form, the normal month name is returned.
        """
        if abbreviated:
            if self.__m_genitive_abbreviated_month_names is None:
                self.__m_genitive_abbreviated_month_names = self._culture_data._abbreviated_genitive_month_names(
                    self.calendar._id
                )
                assert (
                    len(self.__m_genitive_abbreviated_month_names) == 13
                ), "Expected 13 abbreviated genitive month names in a year"
            return self.__m_genitive_abbreviated_month_names

        if self.__genitive_month_names is None:
            self.__genitive_month_names = self._culture_data._genitive_month_names(self.calendar._id)
            assert len(self.__genitive_month_names) == 13, "Expected 13 genitive month names in a year"
        return self.__genitive_month_names

    @staticmethod
    def read_only(dtfi: DateTimeFormatInfo) -> DateTimeFormatInfo:
        if dtfi is None:
            raise ValueError("dtfi cannot be None")
        if dtfi.is_read_only:
            return dtfi
        date_time_format_info: DateTimeFormatInfo = copy.copy(dtfi)
        date_time_format_info.__calendar = Calendar.read_only(dtfi.calendar)
        date_time_format_info._is_read_only = True
        return date_time_format_info

    @property
    def is_read_only(self) -> bool:
        """Gets a value indicating whether the ``DateTimeFormatInfo`` object is read-only."""
        return self._is_read_only
