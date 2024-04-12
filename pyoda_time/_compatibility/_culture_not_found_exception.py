# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

from ._argument_exception import ArgumentError


class CultureNotFoundError(ArgumentError):
    __DEFAULT_MESSAGE: Final[str] = "Culture is not supported."

    def __init__(
        self,
        *,
        message: str | None = None,
        param_name: str | None = None,
        invalid_culture_name: str | None = None,
        invalid_culture_id: int | None = None,
    ) -> None:
        super().__init__(
            message=message or self.__DEFAULT_MESSAGE,
            param_name=param_name,
        )
        # unrecognized culture name
        self.__invalid_culture_name: Final[str | None] = invalid_culture_name
        # unrecognized culture Lcid
        self.__invalid_culture_id: Final[int | None] = invalid_culture_id

    @property
    def invalid_culture_id(self) -> int | None:
        return self.__invalid_culture_id

    @property
    def invalid_culture_name(self) -> str | None:
        return self.__invalid_culture_name

    @property
    def __formatted_invalid_culture_id(self) -> str | None:
        if self.invalid_culture_id is not None:
            return "{0} (0x{0:04x})".format(int(self.invalid_culture_id))
        return self.invalid_culture_name

    def __str__(self) -> str:
        s = super().__str__()
        if self.__invalid_culture_id is not None or self.__invalid_culture_name is not None:
            value_message: str = f"{self.__formatted_invalid_culture_id} is an invalid culture identifier."
            if not s:
                return value_message
            return s + "\n" + value_message
        return s
