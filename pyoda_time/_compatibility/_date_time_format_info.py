# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, _ProtocolMeta

from pyoda_time._compatibility._calendar import Calendar

if TYPE_CHECKING:
    from collections.abc import Sequence

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
        self.__am_designator: str | None = None
        self.__pm_designator: str | None = None
        self.__day_names: Sequence[str] | None = None
        self.__abbreviated_day_names: Sequence[str] | None = None
        self.__m_era_names: list[str] | None = None
        self.__month_names: Sequence[str] | None = None
        self.__abbreviated_month_names: Sequence[str] | None = None
        self.__genitive_month_names: Sequence[str] | None = None
        self.__m_genitive_abbreviated_month_names: Sequence[str] | None = None
        self.__all_long_date_patterns: Sequence[str] | None = None
        self.__all_short_date_patterns: Sequence[str] | None = None
        self.__all_short_time_patterns: Sequence[str] | None = None
        self.__all_long_time_patterns: Sequence[str] | None = None
        self.__long_date_pattern: str | None = None
        self.__short_date_pattern: str | None = None
        self.__short_time_pattern: str | None = None
        self.__long_time_pattern: str | None = None
        self.__general_long_time_pattern: str | None = None
        self.__general_short_time_pattern: str | None = None
        self.__full_date_time_pattern: str | None = None
        self.__date_time_offset_pattern: str | None = None
        self.__month_day_pattern: str | None = None

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
        self.__am_designator = None
        self.__pm_designator = None
        self.__day_names = None
        self.__abbreviated_day_names = None
        self.__m_era_names = None
        self.__month_names = None
        self.__abbreviated_month_names = None
        self.__genitive_month_names = None
        self.__m_genitive_abbreviated_month_names = None
        self.__all_long_date_patterns = None
        self.__all_short_date_patterns = None
        self.__all_short_time_patterns = None
        self.__all_long_time_patterns = None
        self.__long_date_pattern = None
        self.__short_date_pattern = None
        self.__short_time_pattern = None
        self.__long_time_pattern = None
        self.__general_long_time_pattern = None
        self.__general_short_time_pattern = None
        self.__full_date_time_pattern = None
        self.__date_time_offset_pattern = None
        self.__month_day_pattern = None

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
    def full_date_time_pattern(self) -> str:
        if self.__full_date_time_pattern is None:
            self.__full_date_time_pattern = self.long_date_pattern + " " + self.long_time_pattern
        return self.__full_date_time_pattern

    @property
    def __uncloned_long_date_patterns(self) -> Sequence[str]:
        if self.__all_long_date_patterns is None:
            assert self.calendar._id.value > 0
            self.__all_long_date_patterns = self._culture_data._long_dates(self.calendar._id)
            assert len(self.__all_long_date_patterns) > 0
        return self.__all_long_date_patterns

    @property
    def long_date_pattern(self) -> str:
        if self.__long_date_pattern is None:
            # initialize from the 1st array value if not set
            self.__long_date_pattern = self.__uncloned_long_date_patterns[0]
        return self.__long_date_pattern

    @long_date_pattern.setter
    def long_date_pattern(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("value cannot be None")

        # Remember the new string
        self.__long_date_pattern = value

        self.__on_long_date_pattern_changed()

    def __on_long_date_pattern_changed(self) -> None:
        # Clear the token hash table
        # TODO: ClearTokenHashTable();

        # Clean up cached values that will be affected by this property.
        self.__full_date_time_pattern = None

    @property
    def __uncloned_long_time_patterns(self) -> Sequence[str]:
        if self.__all_long_time_patterns is None:
            assert self.calendar._id.value > 0
            self.__all_long_time_patterns = self._culture_data._long_times
            assert len(self.__all_long_time_patterns) > 0
        return self.__all_long_time_patterns

    @property
    def long_time_pattern(self) -> str:
        if self.__long_time_pattern is None:
            self.__long_time_pattern = self.__uncloned_long_time_patterns[0]
        return self.__long_time_pattern

    @long_time_pattern.setter
    def long_time_pattern(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("value cannot be None")

        # Remember the new string
        self.__long_time_pattern = value

        self.__on_long_time_pattern_changed()

    def __on_long_time_pattern_changed(self) -> None:
        # Clear the token hash table
        # TODO: ClearTokenHashTable()

        # Clean up cached values that will be affected by this property.
        self.__full_date_time_pattern = None  # Full date = long date + long Time
        self.__general_long_time_pattern = None  # General long date = short date + long Time
        self.__date_time_offset_pattern = None

    @property
    def __uncloned_short_date_patterns(self) -> Sequence[str]:
        if self.__all_short_date_patterns is None:
            assert self.calendar._id.value > 0
            self.__all_short_date_patterns = self._culture_data._short_dates(self.calendar._id)
            assert len(self.__all_short_date_patterns) > 0
        return self.__all_short_date_patterns

    @property
    def short_date_pattern(self) -> str:
        if self.__short_date_pattern is None:
            self.__short_date_pattern = self.__uncloned_short_date_patterns[0]
        return self.__short_date_pattern

    @short_date_pattern.setter
    def short_date_pattern(self, value: str) -> None:
        self.__verify_writable()
        # TODO: ArgumentNullException
        if value is None:
            raise ValueError("value cannot be None")

        # Remember the new string
        self.__short_date_pattern = value

        self.__on_short_date_pattern_changed()

    def __on_short_date_pattern_changed(self) -> None:
        # Clear the token hash table, note that even short dates could require this
        # TODO: ClearTokenHashTable()

        # Clean up cached values that will be affected by this property.
        self.__general_long_time_pattern = None  # General long time = short date + long time
        self.__general_short_time_pattern = None  # General short time = short date + short Time
        self.__date_time_offset_pattern = None

    @property
    def __uncloned_short_time_patterns(self) -> Sequence[str]:
        if self.__all_short_time_patterns is None:
            assert self.calendar._id.value > 0
            self.__all_short_time_patterns = self._culture_data._short_times
            assert len(self.__all_short_time_patterns) > 0
        return self.__all_short_time_patterns

    @property
    def short_time_pattern(self) -> str:
        if self.__short_time_pattern is None:
            self.__short_time_pattern = self.__uncloned_short_time_patterns[0]
        return self.__short_time_pattern

    @short_time_pattern.setter
    def short_time_pattern(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("value cannot be None")

        # Remember the new string
        self.__short_time_pattern = value

        self.__on_short_time_pattern_changed()

    def __on_short_time_pattern_changed(self) -> None:
        # Clear the token hash table, note that even short times could require this
        # TODO: ClearTokenHashTable()

        # Clean up cached values that will be affected by this property.
        self.__general_short_time_pattern = None  # General short date = short date + short time.

    @property
    def month_day_pattern(self) -> str:
        if self.__month_day_pattern is None:
            self.__month_day_pattern = self._culture_data._month_day(self.calendar._id)
        assert self.__month_day_pattern is not None
        return self.__month_day_pattern

    @property
    def time_separator(self) -> str:
        """Gets or sets the string that separates the components of time, that is, the hour, minutes, and seconds."""
        if self.__time_separator is None:
            self.__time_separator = self._culture_data._time_separator
            assert self.__time_separator is not None
        return self.__time_separator

    @time_separator.setter
    def time_separator(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("value cannot be None")
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
    def am_designator(self) -> str:
        if self.__am_designator is None:
            self.__am_designator = self._culture_data._am_designator
        assert self.__am_designator is not None
        return self.__am_designator

    @am_designator.setter
    def am_designator(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("DateTimeFormatInfo.am_designator cannot be None")
        # TODO: ClearTokenHashTable()
        self.__am_designator = value
        # TODO: self.__am_designator_utf8 = None

    @property
    def pm_designator(self) -> str:
        if self.__pm_designator is None:
            self.__pm_designator = self._culture_data._pm_designator
        assert self.__pm_designator is not None
        return self.__pm_designator

    @pm_designator.setter
    def pm_designator(self, value: str) -> None:
        self.__verify_writable()
        if value is None:
            raise ValueError("DateTimeFormatInfo.pm_designator cannot be None")
        # TODO: ClearTokenHashTable()
        self.__pm_designator = value
        # TODO: self.__pm_designator_utf8 = None

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
    def abbreviated_month_names(self) -> Sequence[str]:
        """Gets or sets the culture-specific abbreviated names of the months.

        :return:
        """
        return self.__internal_get_abbreviated_month_names()

    @abbreviated_month_names.setter
    def abbreviated_month_names(self, value: Sequence[str]) -> None:
        self.__verify_writable()
        if value is None:
            raise TypeError("value cannot be None")
        if len(value) != 13:
            raise ValueError("Expected value to contain 13 items")

        self.__check_null_value(value, len(value) - 1)
        # TODO: ClearTokenHashTable()
        self.__abbreviated_month_names = value

    @property
    def month_names(self) -> Sequence[str]:
        """Gets or sets the culture-specific full names of the months.

        In a 12-month calendar, the 13th element of the array is an empty string.

        The array for ``DateTimeFormatInfo.invariant_info`` contains "January",
        "February", "March", "April", "May", "June", "July", "August", "September",
        "October", "November", "December", and "".

        :return: The culture-specific full names of the months.
        """
        return self.__internal_get_month_names()

    @month_names.setter
    def month_names(self, value: Sequence[str]) -> None:
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
                assert len(self.__m_genitive_abbreviated_month_names) == 13, (
                    "Expected 13 abbreviated genitive month names in a year"
                )
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

    def get_era_name(self, era: int) -> str:
        """Get the name of the era for the specified era value.

        Era names are 1 indexed
        """
        if era == Calendar.CURRENT_ERA:
            era = self.calendar._current_era_value

        # The following is based on the assumption that the era value is starting from 1, and has a
        # serial values. If that ever changes, the code has to be changed.

        names = self._era_names
        era -= 1
        if era > len(names):
            # TODO: ArgumentOutOfRangeException
            raise ValueError("era out of range")
        return names[era]
