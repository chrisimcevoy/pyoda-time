# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import final

from pyoda_time._compatibility._culture_data import _CultureData
from pyoda_time.utility import _private, _sealed


@_sealed
@final
@_private
class TextInfo:  # TODO: ICloneable, IDeserializationCallback?
    __culture_data: _CultureData
    __culture_name: str
    __text_info_name: str

    @classmethod
    def _ctor(cls, culture_data: _CultureData) -> TextInfo:
        self = cls.__new__(cls)
        self.__culture_data = culture_data
        self.__culture_name = culture_data._culture_name
        self.__text_info_name = culture_data._text_info_name
        return self

    @classmethod
    def read_only(cls, text_info: TextInfo) -> TextInfo:
        raise NotImplementedError
