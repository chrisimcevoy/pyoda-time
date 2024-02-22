# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from typing import Self


class StringBuilder:
    """A bare-bones implementation of .NET's ``System.Text.StringBuilder``.

    Represents a mutable sequence of characters.
    """

    __slots__ = ("__string",)

    def __init__(
        self,
        string: str = "",
        start_index: int = 0,
        length: int = 0,
        capacity: int = 16,
    ) -> None:
        self.__string = string

    @property
    def length(self) -> int:
        return len(self.__string)

    def append(self, string: str) -> Self:
        self.__string += string
        return self

    def append_line(self, string: str = "") -> Self:
        self.append(string + "\n")
        return self

    def to_string(self) -> str:
        return self.__string
