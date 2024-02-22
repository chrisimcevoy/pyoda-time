# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from abc import ABC, abstractmethod

from pyoda_time.text import _TextCursor


class TextCursorTestBase(ABC):
    def test_constructor(self) -> None:
        test_string = "test"
        cursor: _TextCursor = self._make_cursor(test_string)
        self._validate_contents(cursor, test_string)
        self._validate_beginning_of_string(cursor)

    def test_move(self) -> None:
        cursor: _TextCursor = self._make_cursor("test")
        self._validate_beginning_of_string(cursor)
        assert cursor.move(0)
        self._validate_current_character(cursor, 0, "t")
        assert cursor.move(1)
        self._validate_current_character(cursor, 1, "e")
        assert cursor.move(2)
        self._validate_current_character(cursor, 2, "s")
        assert cursor.move(3)
        self._validate_current_character(cursor, 3, "t")
        assert not cursor.move(4)
        self._validate_end_of_string(cursor)

    def test_move_next_previous(self) -> None:
        cursor: _TextCursor = self._make_cursor("test")
        self._validate_beginning_of_string(cursor)
        assert cursor.move(2), "move(2)"
        self._validate_current_character(cursor, 2, "s")
        assert cursor.move_previous(), "move_previous()"
        self._validate_current_character(cursor, 1, "e")
        assert cursor.move_next(), "move_next()"
        self._validate_current_character(cursor, 2, "s")
        assert cursor.move_previous(), "move_previous()"  # 1
        assert cursor.move_previous(), "move_previous()"  # 0
        assert not cursor.move_previous()
        self._validate_current_character(cursor, -1, "\0")
        assert not cursor.move_previous()
        self._validate_current_character(cursor, -1, "\0")

    def test_move_invalid(self) -> None:
        cursor: _TextCursor = self._make_cursor("test")
        self._validate_beginning_of_string(cursor)
        assert not cursor.move(-1000)
        self._validate_beginning_of_string(cursor)
        assert not cursor.move(1000)
        self._validate_end_of_string(cursor)
        assert not cursor.move(-1000)
        self._validate_beginning_of_string(cursor)

    def _get_next_character(self, cursor: _TextCursor) -> str:
        assert cursor.move_next()
        return cursor.current

    @classmethod
    def _validate_beginning_of_string(cls, cursor: _TextCursor) -> None:
        cls._validate_current_character(cursor, -1, _TextCursor._NUL)

    @staticmethod
    def _validate_current_character(
        cursor: _TextCursor, expected_current_index: int, expected_current_character: str
    ) -> None:
        assert cursor.current == expected_current_character
        assert cursor.index == expected_current_index

    @classmethod
    def _validate_end_of_string(cls, cursor: _TextCursor) -> None:
        cls._validate_current_character(cursor, cursor.length, _TextCursor._NUL)

    @staticmethod
    def _validate_contents(cursor: _TextCursor, value: str, length: int = -1) -> None:
        if length < 0:
            length = len(value)
        assert cursor.value == value, "cursor value mismatch"
        assert cursor.length == length, "cursor length mismatch"

    @abstractmethod
    def _make_cursor(self, value: str) -> _TextCursor:
        raise NotImplementedError
