# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from types import TracebackType
from typing import ContextManager

from pyoda_time._compatibility._culture_info import CultureInfo


class _BothSaver(ContextManager):
    """A context manager for temporarily changing cultures and which resets the culture on exit."""

    @property
    def __current_culture(self) -> CultureInfo:
        return CultureInfo.current_culture

    @__current_culture.setter
    def __current_culture(self, value: CultureInfo) -> None:
        CultureInfo.current_culture = value

    @property
    def __current_ui_culture(self) -> CultureInfo:
        return CultureInfo.current_ui_culture

    @__current_ui_culture.setter
    def __current_ui_culture(self, value: CultureInfo) -> None:
        CultureInfo.current_ui_culture = value

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
    """Provides a simple context manager for temporarily setting the culture of a thread.

    Usage::

        with CultureSaver.set_cultures(CultureInfo("en-US")):
            # code to run under the United States English culture
    """

    @classmethod
    def set_cultures(
        cls, new_culture_info: CultureInfo, new_ui_culture_info: CultureInfo | None = None
    ) -> ContextManager:
        """Sets both the UI and basic cultures of the current thread.

        :param new_culture_info: The new culture info.
        :param new_ui_culture_info: The new ui culture info.
        :return: A context manager which temporarily sets the current culture, then resets the culture upon exit.
        """
        if new_ui_culture_info is None:
            new_ui_culture_info = new_culture_info
        return _BothSaver(new_culture_info, new_ui_culture_info)
