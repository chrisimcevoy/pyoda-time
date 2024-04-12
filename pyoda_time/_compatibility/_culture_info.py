# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import copy
import itertools
import string
import threading
from typing import Any, Final, Sequence, _ProtocolMeta

import icu

from ._argument_exception import ArgumentError
from ._calendar import Calendar
from ._calendar_id import _CalendarId
from ._culture_data import _CultureData
from ._culture_not_found_exception import CultureNotFoundError
from ._culture_types import CultureTypes
from ._date_time_format_info import DateTimeFormatInfo
from ._globalization_mode import _GlobalizationMode
from ._gregorian_calendar import GregorianCalendar
from ._hebrew_calendar import HebrewCalendar
from ._hijri_calendar import HijriCalendar
from ._i_format_provider import IFormatProvider
from ._japanese_calendar import JapaneseCalendar
from ._korean_calendar import KoreanCalendar
from ._number_format_info import NumberFormatInfo
from ._persian_calendar import PersianCalendar
from ._taiwan_calendar import TaiwanCalendar
from ._text_info import TextInfo
from ._thai_buddhist_calendar import ThaiBuddhistCalendar
from ._um_al_qura_calendar import UmAlQuraCalendar


class __CultureInfoMeta(type):
    """Metaclass for CultureInfo."""

    __CURRENT_CULTURE_ATTR_NAME: Final[str] = "s_currentThreadCulture"
    __CURRENT_UI_CULTURE_ATTR_NAME: Final[str] = "s_currentThreadUICulture"
    _LOCALE_CUSTOM_UNSPECIFIED: Final[int] = 0x1000
    __THREAD_LOCAL_STORAGE: Final[threading.local] = threading.local()

    __s_InvariantCultureInfo: CultureInfo | None = None
    __s_user_default_culture: CultureInfo | None = None
    __s_user_default_ui_culture: CultureInfo | None = None
    __s_default_thread_current_culture: CultureInfo | None = None
    __s_default_thread_current_ui_culture: CultureInfo | None = None

    @property
    def invariant_culture(cls) -> CultureInfo:
        """An instance of ``CultureInfo`` which is independent of system/user settings."""
        if not cls.__s_InvariantCultureInfo:
            cls.__s_InvariantCultureInfo = CultureInfo._ctor(_CultureData._invariant, is_read_only=True)
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
    def current_ui_culture(self) -> CultureInfo:
        """Gets or sets the locale information for the current thread."""
        return getattr(
            self.__THREAD_LOCAL_STORAGE,
            self.__CURRENT_UI_CULTURE_ATTR_NAME,
            CultureInfo.default_thread_current_ui_culture
            or self.__s_user_default_ui_culture
            or self.__initialize_user_default_culture(),
        )

    @current_ui_culture.setter
    def current_ui_culture(self, value: CultureInfo) -> None:
        setattr(self.__THREAD_LOCAL_STORAGE, self.__CURRENT_UI_CULTURE_ATTR_NAME, value)
        assert getattr(self.__THREAD_LOCAL_STORAGE, self.__CURRENT_UI_CULTURE_ATTR_NAME) == value

    @property
    def default_thread_current_culture(self) -> CultureInfo | None:
        """Gets or sets the default culture for threads."""
        return self.__s_default_thread_current_culture

    @default_thread_current_culture.setter
    def default_thread_current_culture(self, value: CultureInfo) -> None:
        self.__s_default_thread_current_culture = value

    @property
    def default_thread_current_ui_culture(self) -> CultureInfo | None:
        """Gets or sets the default UI culture for threads."""
        return self.__s_default_thread_current_ui_culture

    @default_thread_current_ui_culture.setter
    def default_thread_current_ui_culture(self, value: CultureInfo) -> None:
        self.__s_default_thread_current_ui_culture = value

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
        if _GlobalizationMode._invariant:
            return CultureInfo.invariant_culture
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

    __CACHED_CULTURES_BY_NAME: Final[dict[str, CultureInfo]] = dict()
    __GET_CULTURE_LOCK: Final[threading.Lock] = threading.Lock()
    _LOCALE_INVARIANT: Final[int] = 0x007F

    def __init__(self, name: str, use_user_override: bool = True) -> None:
        # TODO: ArgumentNullException.ThrowIfNull(name);

        culture_data: _CultureData | None = _CultureData._get_culture_data(name, use_user_override)

        if culture_data is None:
            raise CultureNotFoundError(
                param_name="name",
                invalid_culture_name=name,
                message=self.__get_culture_not_supported_exception_message(),
            )

        self._culture_data = culture_data
        self._name = self._culture_data._culture_name
        self._is_inherited = isinstance(self, CultureInfo)  # TODO: issubclass?
        self.__is_read_only = False

        # Cached attributes exposed via lazy-initialisation properties
        self._date_time_info: DateTimeFormatInfo | None = None
        self._num_info: NumberFormatInfo | None = None
        self.__text_info: TextInfo | None = None
        self.__calendar: Calendar | None = None
        self.__non_sort_name: str | None = None

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
        self.__is_read_only = is_read_only

        # Cached attributes exposed via lazy-initialisation properties
        self._date_time_info = None
        self._num_info = None
        self._date_time_info = None
        self._num_info = None
        self.__text_info = None
        self.__calendar = None
        self.__non_sort_name = None

        return self

    @classmethod
    def _verify_culture_name(cls, culture: CultureInfo | str, throw_exception: bool) -> bool:
        if isinstance(culture, CultureInfo):
            if not culture._is_inherited:
                return True
            culture = culture.name
        for char in culture:
            if char in itertools.chain(string.ascii_letters, string.digits, ("-", "_")):
                continue
            if throw_exception:
                msg = (
                    f"The given culture name '{culture}' cannot be used to locate a resource file. "
                    f"Resource filenames must consist of only letters, numbers, hyphens or underscores."
                )
                raise ArgumentError(message=msg)
            return False
        return True

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

    @classmethod
    def _get_calendar_instance(cls, cal_type: _CalendarId) -> Calendar:
        assert not _GlobalizationMode._invariant
        if cal_type is _CalendarId.GREGORIAN:
            return GregorianCalendar()
        return cls._get_calendar_instance_rare(cal_type)

    @classmethod
    def _get_calendar_instance_rare(cls, cal_type: _CalendarId) -> Calendar:
        assert cal_type is not _CalendarId.GREGORIAN, "cal_type!=_CalendarId.GREGORIAN"

        match cal_type:
            case (
                _CalendarId.GREGORIAN_US
                | _CalendarId.GREGORIAN_ME_FRENCH
                | _CalendarId.GREGORIAN_ARABIC
                | _CalendarId.GREGORIAN_XLIT_ENGLISH
                | _CalendarId.GREGORIAN_XLIT_FRENCH
            ):
                return GregorianCalendar()
            case _CalendarId.TAIWAN:
                return TaiwanCalendar()
            case _CalendarId.JAPAN:
                return JapaneseCalendar()
            case _CalendarId.KOREA:
                return KoreanCalendar()
            case _CalendarId.THAI:
                return ThaiBuddhistCalendar()
            case _CalendarId.HIJRI:
                return HijriCalendar()
            case _CalendarId.HEBREW:
                return HebrewCalendar()
            case _CalendarId.UMALQURA:
                return UmAlQuraCalendar()
            case _CalendarId.PERSIAN:
                return PersianCalendar()
            case _:
                # TODO: .NET defaults to returning GregorianCalendar, but this is safer for us...
                raise NotImplementedError(f"CalendarId {cal_type} is mapped to a Calendar implementation.")

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
        if self.__is_read_only:
            raise RuntimeError("Cannot write read-only CultureInfo")

    def clone(self) -> CultureInfo:  # TODO: ICloneable
        """Creates a copy of this ``CultureInfo``."""
        # TODO: This might be good enough for our purposes, but
        #  it isn't anything like the behaviour in .NET.
        return copy.deepcopy(self)

    def __deepcopy__(self, memo: dict[int, Any]) -> CultureInfo:
        """Implements copy functionality.

        In C# this class has no public constructor, so in Python we mimic that by monkeypatching __init__ and __new__ to
        raise an Exception.

        To get around that when copying such objects, we have to manage the instance creation on behalf of the copy
        module.
        """
        # Create a new instance of the class
        new_obj = super().__new__(self.__class__)

        # Copy the attributes to the new instance.
        for k, v in self.__dict__.items():
            setattr(new_obj, k, copy.deepcopy(v, memo))

        new_obj.__is_read_only = False

        memo[id(self)] = new_obj

        return new_obj

    @staticmethod
    def read_only(ci: CultureInfo) -> CultureInfo:
        """Returns a read-only wrapper around the specified ``CultureInfo`` object.

        :param ci: The ``CultureInfo`` object to wrap.
        :return: A read-only ``CultureInfo`` wrapper around ``ci``.
        """
        if ci is None:
            raise ValueError("ci cannot be None.")
        if ci.is_read_only:
            return ci
        culture_info: CultureInfo = copy.copy(ci)
        if not ci.is_neutral_culture:
            if not ci._is_inherited:
                if ci._date_time_info is not None:
                    culture_info._date_time_info = DateTimeFormatInfo.read_only(ci._date_time_info)
                if ci._num_info is not None:
                    culture_info._num_info = NumberFormatInfo.read_only(ci._num_info)
            else:
                culture_info.date_time_format = DateTimeFormatInfo.read_only(ci.date_time_format)
                culture_info.number_format = NumberFormatInfo.read_only(ci.number_format)
        if ci.__text_info is not None:
            culture_info.__text_info = TextInfo.read_only(ci.__text_info)
        if ci.__calendar is not None:
            culture_info.__calendar = Calendar.read_only(ci.__calendar)
        culture_info.__is_read_only = True
        return culture_info

    @property
    def is_read_only(self) -> bool:
        """Gets a value indicating whether the current ``CultureInfo`` is read-only."""
        return self.__is_read_only

    def get_format(self, format_type: type) -> Any | None:
        """Gets an object that defines how to format the specified type."""
        raise NotImplementedError

    @classmethod
    def get_cultures(cls, types: CultureTypes) -> Sequence[CultureInfo]:
        """Gets the list of supported cultures filtered by the specified ``CultureTypes`` parameter.

        :param types: A bitwise combination of the enumeration values that filter the cultures to retrieve.
        :return: An array that contains the cultures specified by the ``types`` parameter.
            The array of cultures is unsorted.
        """
        # TODO: This implementation is simplified
        return _CultureData._get_cultures(types)

    @property
    def name(self) -> str:
        """Returns the full name of the CultureInfo.

        The name is in format like "en-US".

        This version does NOT include sort information in the name.
        """
        if self.__non_sort_name is None:
            self.__non_sort_name = self._culture_data.name or ""
        return self.__non_sort_name

    @property
    def is_neutral_culture(self) -> bool:
        """Gets a value indicating whether the current ``CultureInfo`` represents a neutral culture.

        :return: ``True`` if the current ``CultureInfo`` represents a neutral culture; otherwise, ``False``.
        """
        return self._culture_data._is_neutral_culture

    @classmethod
    def get_culture_info(cls, name: str) -> CultureInfo:
        """Retrieves a cached, read-only instance of a culture using the specified culture name.

        :param name: The name of a culture. ``name`` is not case-sensitive.
        :return: A read-only ``CultureInfo`` object.
        """
        if name is None:
            raise TypeError("name cannot be None.")

        name = _CultureData._ansi_to_lower(name)
        name_table: dict[str, CultureInfo] = cls.__CACHED_CULTURES_BY_NAME
        result: CultureInfo | None

        with cls.__GET_CULTURE_LOCK:
            if (result := name_table.get(name)) is not None:
                return result

        result = cls.__create_culture_info_no_throw(name, use_user_override=False)

        if result is None:
            raise CultureNotFoundError(
                param_name="name",
                invalid_culture_name=name,
                message=cls.__get_culture_not_supported_exception_message(),
            )

        result.__is_read_only = True

        name = _CultureData._ansi_to_lower(result._name)

        with cls.__GET_CULTURE_LOCK:
            name_table[name] = result

        return result

    @staticmethod
    def __get_culture_not_supported_exception_message() -> str:
        if _GlobalizationMode._invariant:
            return "Only the invariant culture is supported in globalization-invariant mode."
        return "Culture is not supported."

    @classmethod
    def __create_culture_info_no_throw(cls, name: str, use_user_override: bool = False) -> CultureInfo | None:
        assert name is not None
        culture_data: _CultureData | None = _CultureData._get_culture_data(name, use_user_override)
        if culture_data is None:
            return None
        return CultureInfo._ctor(culture_data)
