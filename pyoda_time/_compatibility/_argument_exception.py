# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final


class ArgumentError(ValueError):
    """The exception that is thrown when one of the arguments provided to a method is not valid."""

    def __init__(self, *, message: str | None = None, param_name: str | None = None) -> None:
        self.__message: Final[str | None] = message
        self.__param_name: Final[str | None] = param_name

    def __str__(self) -> str:
        message = self.__message or "Value does not fall within the expected range."
        if self.__param_name is not None:
            message += f" (Parameter '{self.__param_name}')"
        return message
