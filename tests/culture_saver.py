# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from types import TracebackType
from typing import ContextManager

from pyoda_time._compatibility._culture_info import CultureInfo


class _BothSaver(ContextManager):
    @property
    def __current_culture(self) -> CultureInfo:
        return CultureInfo.current_culture

    @__current_culture.setter
    def __current_culture(self, value: CultureInfo) -> None:
        CultureInfo.current_culture = value

    @property
    def __current_ui_culture(self) -> CultureInfo:
        # TODO: fix or remove this - it's only here for completeness sake
        return CultureInfo.invariant_culture

    @__current_ui_culture.setter
    def __current_ui_culture(self, value: CultureInfo) -> None:
        # TODO: fix or remove this - it's only here for completeness sake
        CultureInfo.current_culture = value

    def __init__(self, new_culture: CultureInfo, new_ui_culture: CultureInfo) -> None:
        self.__old_culture = self.__current_culture
        self.__old_ui_culture = self.__current_ui_culture

        self.__current_culture = new_culture
        self.__new_ui_culture = new_ui_culture

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        self.__current_culture = self.__old_culture
        self.__new_ui_culture = self.__old_ui_culture
        return None  # Don't swallow exceptions


class CultureSaver:
    @classmethod
    def set_cultures(cls, new_culture_info: CultureInfo) -> ContextManager:
        return _BothSaver(new_culture_info, new_culture_info)
