# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

import copy
from typing import Any

from pyoda_time._compatibility._culture_data import _CultureData
from pyoda_time._compatibility._i_format_provider import IFormatProvider


class NumberFormatInfo(IFormatProvider):  # TODO: ICloneable
    """Provides culture-specific information for formatting and parsing numeric values."""

    def __init__(self) -> None:
        self._positive_sign = "+"
        self._negative_sign = "-"
        self._is_read_only: bool = False

    def __verify_writable(self) -> None:
        if self._is_read_only:
            raise RuntimeError("Cannot write read-only CultureInfo")

    @property
    def is_read_only(self) -> bool:
        """Gets a value that indicates whether this ``NumberFormatInfo`` is read-only."""
        return self._is_read_only

    @classmethod
    def _ctor(cls, culture_data: _CultureData) -> NumberFormatInfo:
        instance = NumberFormatInfo()
        culture_data._get_nfi_values(instance)
        instance.__initialize_invariant_and_negative_sign_flags()
        return instance

    def __initialize_invariant_and_negative_sign_flags(self) -> None:
        # TODO: implement whatever this is
        pass

    @property
    def positive_sign(self) -> str:
        """Gets or sets the string that denotes that the associated number is positive."""
        return self._positive_sign

    @positive_sign.setter
    def positive_sign(self, value: str) -> None:
        self._positive_sign = value

    @property
    def negative_sign(self) -> str:
        """Gets or sets the string that denotes that the associated number is negative."""
        return self._negative_sign

    @negative_sign.setter
    def negative_sign(self, value: str) -> None:
        self.__verify_writable()
        self._negative_sign = value

    @staticmethod
    def read_only(nfi: NumberFormatInfo) -> NumberFormatInfo:
        """Returns a read-only ``NumberFormatInfo`` wrapper."""
        if nfi is None:
            raise ValueError("nfi cannot be None")
        if nfi.is_read_only:
            return nfi
        number_format_info = copy.copy(nfi)
        number_format_info._is_read_only = True
        return number_format_info

    def get_format(self, format_type: type) -> Any | None:
        raise NotImplementedError

    def clone(self) -> NumberFormatInfo:
        return copy.deepcopy(self)

    def __deepcopy__(self, memo: dict[int, Any]) -> NumberFormatInfo:
        # Create a new instance of the class
        new_obj = super().__new__(self.__class__)

        # Copy the attributes to the new instance.
        for k, v in self.__dict__.items():
            setattr(new_obj, k, copy.deepcopy(v, memo))

        new_obj._is_read_only = False

        memo[id(self)] = new_obj

        return new_obj
