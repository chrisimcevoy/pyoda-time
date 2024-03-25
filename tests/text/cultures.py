# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final, Iterable

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._culture_types import CultureTypes


class _CulturesMeta(type):
    __cache: Final[dict[str, CultureInfo]] = {}

    @property
    def all_cultures(cls) -> Iterable[CultureInfo]:
        """Force the cultures to be read-only for tests, to take advantage of caching."""
        # In Pyoda Time, there is some special casing for cultures which
        # don't behave as expected on Mono and dotnet core.
        return [CultureInfo.read_only(culture) for culture in CultureInfo.get_cultures(CultureTypes.SPECIFIC_CULTURES)]

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
    """Cultures to use from various tests."""
