# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
import threading
from typing import Any, Final, _ProtocolMeta

import icu

from ._calendar import Calendar
from ._culture_data import _CultureData
from ._date_time_format_info import DateTimeFormatInfo
from ._i_format_provider import IFormatProvider
from ._number_format_info import NumberFormatInfo


class __CultureInfoMeta(type):
    """Metaclass for CultureInfo."""

    __CURRENT_CULTURE_ATTR_NAME: Final[str] = "s_currentThreadCulture"
    __THREAD_LOCAL_STORAGE: Final[threading.local] = threading.local()

    __s_InvariantCultureInfo: CultureInfo | None = None
    __s_user_default_culture: CultureInfo | None = None
    __s_default_thread_current_culture: CultureInfo | None = None

    @property
    def invariant_culture(cls) -> CultureInfo:
        """An instance of ``CultureInfo`` which is independent of system/user settings."""
        if not cls.__s_InvariantCultureInfo:
            cls.__s_InvariantCultureInfo = CultureInfo._ctor(_CultureData.invariant, is_read_only=True)
        return cls.__s_InvariantCultureInfo

    @property
    def current_culture(self) -> CultureInfo:
        """Gets or sets the locale information for the current thread."""
        return getattr(
            self.__THREAD_LOCAL_STORAGE,
            self.__CURRENT_CULTURE_ATTR_NAME,
            CultureInfo.default_thread_current_culture
            or self.__s_user_default_culture
            or self.__initialize_user_default_culture(),
        )

    @current_culture.setter
    def current_culture(self, value: CultureInfo) -> None:
        setattr(self.__THREAD_LOCAL_STORAGE, self.__CURRENT_CULTURE_ATTR_NAME, value)
        assert getattr(self.__THREAD_LOCAL_STORAGE, self.__CURRENT_CULTURE_ATTR_NAME) == value

    @property
    def default_thread_current_culture(self) -> CultureInfo | None:
        """Gets or sets the default culture for threads."""
        return self.__s_default_thread_current_culture

    @default_thread_current_culture.setter
    def default_thread_current_culture(self, value: CultureInfo) -> None:
        self.__s_default_thread_current_culture = value

    def __initialize_user_default_culture(self) -> CultureInfo:
        self.__s_user_default_culture = self._get_user_default_culture()
        return self.__s_user_default_culture

    @staticmethod
    def _get_default_locale_name() -> str | None:
        """Return the name of the default ICU Locale."""
        # Much like .NET defers to their ICU interop layer.
        locale: icu.Locale = icu.Locale.getDefault()
        if locale is None:
            return None
        return str(locale.getName())

    @staticmethod
    def __get_culture_by_name(name: str) -> CultureInfo:
        """Return the CultureInfo for the given name if it exists.

        Otherwise, return the invariant CultureInfo.
        """
        # TODO: Not keen on this try/except, but this is how .NET does it
        try:
            return CultureInfo(name)
        except:  # noqa
            return CultureInfo.invariant_culture

    def _get_user_default_culture(self) -> CultureInfo:
        # TODO: if GlobalizationMode.Invariant:
        #      return CultureInfo.Invariant
        if (default_locale_name := CultureInfo._get_default_locale_name()) is None:
            return CultureInfo.invariant_culture
        return self.__get_culture_by_name(default_locale_name)


class __CombinedMeta(_ProtocolMeta, __CultureInfoMeta):
    """Intermediary class which prevents a metaclass conflict in CultureInfo."""


class CultureInfo(IFormatProvider, metaclass=__CombinedMeta):  # TODO: ICloneable
    """Provides information about a specific culture (aka locale).

    The information includes the names for the culture, the writing system, the calendar used, the sort order of
    strings, and formatting for dates and numbers.
    """

    def __init__(self, name: str, use_user_override: bool = True) -> None:
        self._culture_data: _CultureData = _CultureData(name)
        self._name = self._culture_data._culture_name
        self._is_inherited = isinstance(self, CultureInfo)  # TODO: issubclass?
        self._is_read_only = False

        # Cached attributes exposed via lazy-initialisation properties
        self._date_time_info: DateTimeFormatInfo | None = None
        self._num_info: NumberFormatInfo | None = None

    def __repr__(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    @classmethod
    def _ctor(cls, culture_data: _CultureData, is_read_only: bool = False) -> CultureInfo:
        self = cls.__new__(cls)
        self._culture_data = culture_data
        self._name = culture_data.name
        self._is_inherited = cls != CultureInfo
        self._is_read_only = is_read_only

        # Cached attributes exposed via lazy-initialisation properties
        self._date_time_info = None
        self._num_info = None

        return self

    @property
    def calendar(self) -> Calendar:
        """Gets the default calendar used by the culture."""
        return self._culture_data._default_calendar

    @property
    def date_time_format(self) -> DateTimeFormatInfo:
        """Gets or sets a ``DateTimeFormatInfo`` that defines the culturally appropriate format of displaying dates and
        times."""
        if self._date_time_info is None:
            self._date_time_info = DateTimeFormatInfo._ctor(self._culture_data, self.calendar)
        return self._date_time_info

    @date_time_format.setter
    def date_time_format(self, value: DateTimeFormatInfo | None) -> None:
        if value is None:
            raise ValueError("date_time_format cannot be None")
        if not isinstance(value, DateTimeFormatInfo):
            raise TypeError("date_time_format must be an instance of DateTimeFormatInfo")
        self.__verify_writable()
        self._date_time_info = value

    @property
    def number_format(self) -> NumberFormatInfo:
        """Gets or sets a ``NumberFormatInfo`` that defines the culturally appropriate format of displaying numbers,
        currency, and percentage."""
        if self._num_info is None:
            self._num_info = NumberFormatInfo._ctor(self._culture_data)
        return self._num_info

    @number_format.setter
    def number_format(self, value: NumberFormatInfo) -> None:
        if value is None:
            raise ValueError("number_format cannot be None")
        if not isinstance(value, NumberFormatInfo):
            raise TypeError("number_format must be an instance of NumberFormatInfo")
        self.__verify_writable()
        self._num_info = value

    def __verify_writable(self) -> None:
        if self._is_read_only:
            raise RuntimeError("Cannot write read-only CultureInfo")

    def clone(self) -> CultureInfo:  # TODO: ICloneable
        """Creates a copy of this ``CultureInfo``."""
        # TODO: This might be good enough for our purposes, but
        #  it isn't anything like the behaviour in .NET.
        # Refer to CultureData.__deepcopy__() implementation
        return copy.deepcopy(self)

    def get_format(self, format_type: type) -> Any | None:
        """Gets an object that defines how to format the specified type."""
        raise NotImplementedError
