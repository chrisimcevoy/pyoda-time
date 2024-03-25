# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import ClassVar

from pyoda_time._compatibility._culture_info import CultureInfo


class _ResourceManager:
    __dict: ClassVar[dict[str, str]] = {
        "Eras_AnnoHegirae": "A.H.|AH",
        "Eras_AnnoMartyrum": "A.M.|AM",
        "Eras_AnnoMundi": "A.M.|AM",
        "Eras_AnnoPersico": "A.P.|AP",
        "Eras_Bahai": "B.E.|BE",
        "Eras_BeforeCommon": "B.C.|B.C.E.|BC|BCE",
        "Eras_Common": "A.D.|AD|C.E.|CE",
        "OffsetPatternLong": "+HH:mm:ss",
        "OffsetPatternLongNoPunctuation": "+HHmmss",
        "OffsetPatternMedium": "+HH:mm",
        "OffsetPatternMediumNoPunctuation": "+HHmm",
        "OffsetPatternShort": "+HH",
        "OffsetPatternShortNoPunctuation": "+HH",
    }

    @classmethod
    def get_string(cls, name: str, culture: CultureInfo | None) -> str | None:
        # TODO: This is nothing like a C# ResourceManager. CultureInfo isn't used.
        return cls.__dict.get(name)


class _PatternResources:
    """In Noda Time, this is a wrapper around a ResourceManager and the eponymous .resx."""

    _resource_manager: type[_ResourceManager] = _ResourceManager
