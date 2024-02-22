# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

from pyoda_time._compatibility._culture_info import CultureInfo


class _CulturesMeta(type):
    __cache: Final[dict[str, CultureInfo]] = {}

    @classmethod
    def __get_or_create(cls, name: str) -> CultureInfo:
        """Manages the cache of CultureInfo objects in metaclass properties."""
        if not (culture_info := cls.__cache.get(name)):
            culture_info = cls.__cache[name] = CultureInfo(name)
        return culture_info

    @property
    def en_us(self) -> CultureInfo:
        # TODO: CultureInfo.ReadOnly()
        return self.__get_or_create("en-US")

    @property
    def fr_fr(self) -> CultureInfo:
        # TODO: CultureInfo.ReadOnly()
        return self.__get_or_create(name="fr-FR")

    @property
    def dot_time_separator(self) -> CultureInfo:
        # TODO: CultureInfo.ReadOnly()
        # We don't use this culture for anything other than hosting
        # the dot time separator, so it should be fine to cache it.
        ci: CultureInfo = self.__get_or_create("fi-FI")
        ci.date_time_format.time_separator = "."
        return ci


class Cultures(metaclass=_CulturesMeta):
    pass
