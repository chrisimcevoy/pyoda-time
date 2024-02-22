# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from pyoda_time._compatibility._culture_data import _CultureData


class NumberFormatInfo:
    """Provides culture-specific information for formatting and parsing numeric values."""

    def __init__(self) -> None:
        self._positive_sign = "+"
        self._negative_sign = "-"
        self._is_read_only: bool = False

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

    def __verify_writable(self) -> None:
        if self._is_read_only:
            raise RuntimeError("Cannot write read-only CultureInfo")
