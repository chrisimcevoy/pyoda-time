# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from abc import ABC


class _TextCursor(ABC):
    """Provides a cursor over text being parsed.

    None of the methods in this class throw exceptions (unless there is a bug in Pyoda Time, in which case an exception
    is appropriate) and none of the methods have ref parameters indicating failures, unlike subclasses. This class is
    used as the basis for both value and pattern parsing, so can make no judgement about what's wrong (i.e. it wouldn't
    know what type of failure to indicate). Instead, methods return Boolean values to indicate success or failure.
    """

    @property
    def length(self) -> int:
        """Gets the length of the string being parsed."""
        return self.__length

    @property
    def value(self) -> str:
        """Gets the string being parsed."""
        return self.__value

    # A nul character. This character is not allowed in any parsable string and is used to
    # indicate that the current character is not set.
    _NUL: str = "\0"

    def __init__(self, value: str) -> None:
        self.__value = value
        self.__length = len(value)
        self.__current = self._NUL
        self.__index = self.length
        self.move(-1)

    @property
    def current(self) -> str:
        """Gets the current character."""
        return self.__current

    @property
    def has_more_characters(self) -> bool:
        """Gets a value indicating whether this instance has more characters."""
        return (self.index + 1) < self.length

    @property
    def index(self) -> int:
        """Gets the current index into the string being parsed."""
        return self.__index

    @property
    def remainder(self) -> str:
        """Gets the remainder the string that has not been parsed yet."""
        return self.value[self.index :]

    def __str__(self) -> str:
        if self.index <= 0:
            return f"^{self.value}"
        if self.index >= self.length:
            return f"{self.value}^"
        return self.value[: self.index] + "^" + self.value[self.index :]

    def peek_next(self) -> str:
        """Eturns the next character if there is one or `_NUL` if there isn't."""
        return self.value[self.index + 1] if self.has_more_characters else self._NUL

    def move(self, target_index: int) -> bool:
        """Moves the specified target index. If the new index is out of range of the valid indices for this string then
        the index is set to the beginning or the end of the string whichever is nearest the requested index.

        :param target_index: Index of the target.
        :return: ``True`` if the requested index is in range.
        """
        if target_index >= 0:
            if target_index < self.length:
                self.__index = target_index
                self.__current = self.value[self.index]
                return True
            else:
                self.__current = self._NUL
                self.__index = self.length
                return False
        self.__current = self._NUL
        self.__index = -1
        return False

    def move_next(self) -> bool:
        """Moves to the next character.

        :return: ``True`` if the requested index is in range.
        """
        return self.move(self.index + 1)

    def move_previous(self) -> bool:
        """Moves to the previous character.

        :return: ``True`` if the requested index is in range.
        """
        return self.move(self.index - 1)
