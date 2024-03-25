# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import threading
from typing import Any, Final

from pyoda_time._compatibility._culture_info import CultureInfo, __CombinedMeta
from pyoda_time._compatibility._date_time_format_info import DateTimeFormatInfo
from pyoda_time._compatibility._number_format_info import NumberFormatInfo


class _FailingCultureInfoMeta(type):
    __lock: Final[threading.Lock] = threading.Lock()
    __instance: FailingCultureInfo | None = None

    @property
    def instance(self) -> FailingCultureInfo:
        if self.__instance is None:
            with self.__lock:
                if self.__instance is None:
                    self.__instance = FailingCultureInfo()
        return self.__instance


class _CombinedMeta(_FailingCultureInfoMeta, __CombinedMeta):
    pass


class FailingCultureInfo(CultureInfo, metaclass=_CombinedMeta):
    """Throws an exception if called.

    This forces the testing code to set or pass a valid culture in all tests. The tests cannot be guaranteed to work if
    the culture is not set as formatting and parsing are culture dependent.
    """

    __CULTURE_NOT_SET: Final[str] = "The formatting and parsing code tests should have set the correct culture."

    def __init__(self) -> None:
        super().__init__("en-US")

    @property
    def date_time_format(self) -> DateTimeFormatInfo:
        raise NotImplementedError(self.__CULTURE_NOT_SET)

    @date_time_format.setter
    def date_time_format(self, value: DateTimeFormatInfo) -> None:
        raise NotImplementedError(self.__CULTURE_NOT_SET)

    @property
    def number_format(self) -> NumberFormatInfo:
        raise NotImplementedError(self.__CULTURE_NOT_SET)

    @number_format.setter
    def number_format(self, value: NumberFormatInfo) -> None:
        raise NotImplementedError(self.__CULTURE_NOT_SET)

    @property
    def name(self) -> str:
        return "Failing"

    def get_format(self, format_type: type) -> Any | None:
        raise NotImplementedError(self.__CULTURE_NOT_SET)
