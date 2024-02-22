# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import abstractmethod
from typing import Any, Final, Generic, TypeVar

import pytest

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._string_builder import StringBuilder
from pyoda_time.text import InvalidPatternError, UnparsableValueError, _ValueCursor
from pyoda_time.text._i_partial_pattern import _IPartialPattern
from pyoda_time.text._i_pattern import IPattern

T = TypeVar("T")


class PatternTestData(Generic[T]):
    @property
    @abstractmethod
    def default_template(self) -> T:
        raise NotImplementedError

    def __init__(
        self,
        value: T,
        *,
        culture: CultureInfo = CultureInfo.invariant_culture,
        standard_pattern: IPattern[T] | None = None,
        pattern: str | None = None,
        text: str | None = None,
        template: T | None = None,
        description: str | None = None,
        message: str | None = None,
        parameters: list | None = None,
    ) -> None:
        self.value: Final[T] = value
        self.culture: CultureInfo = culture
        self.standard_pattern: IPattern[T] | None = standard_pattern
        self.pattern: str | None = pattern
        self.text: str | None = text
        self.template: Final[T] = template or self.default_template
        self.description: str | None = description
        self.message: str | None = message
        self.parameters = parameters or []

    @abstractmethod
    def create_pattern(self) -> IPattern[T]:
        raise NotImplementedError

    def test_parse(self) -> None:
        assert self.message is None
        pattern: IPattern[T] = self.create_pattern()
        assert self.text is not None, "Must provide `text` for this test!"
        result = pattern.parse(self.text)
        actual_value: T = result.value
        assert self.value == actual_value

        if self.standard_pattern is not None:
            assert self.value == self.standard_pattern.parse(self.text).value

    def test_format(self) -> None:
        assert self.message is None
        pattern: IPattern[T] = self.create_pattern()
        assert self.text == pattern.format(self.value), f"expected `{self.text}` to be `{self.value}"

        if self.standard_pattern is not None:
            assert self.text == self.standard_pattern.format(self.value)

    def test_parse_partial(self) -> None:
        pattern = self.create_partial_pattern()
        assert self.message is None
        cursor = _ValueCursor(f"^{self.text}#")
        # Move to the ^
        cursor.move_next()
        # Move to the start of the text
        cursor.move_next()
        result = pattern.parse_partial(cursor)
        actual_value = result.value
        assert self.value == actual_value
        assert cursor.current == "#"

    def create_partial_pattern(self) -> _IPartialPattern[T]:
        raise NotImplementedError("Virtual method - implement in subclasses")

    def test_append_format(self) -> None:
        assert self.message is None
        pattern: IPattern[T] = self.create_pattern()
        builder = StringBuilder("x")
        pattern.append_format(self.value, builder)
        assert builder.to_string() == f"x{self.text}"

    def test_invalid_pattern(self) -> None:
        assert self.message is not None, "Expected `message` to be provided."
        expected_message: str = self.format_message(self.message, self.parameters)
        with pytest.raises(InvalidPatternError) as e:
            self.create_pattern()
        assert str(e.value) == expected_message

    def test_parse_failure(self) -> None:
        assert self.message is not None, "Expected `message` to be provided."
        expected_message: str = self.format_message(self.message, self.parameters)
        pattern: IPattern[T] = self.create_pattern()
        assert self.text is not None, "Expected `text` to be provided."
        result = pattern.parse(self.text)
        assert not result.success, "Expected parsing to fail, but it succeeded"
        with pytest.raises(UnparsableValueError) as e:
            result.get_value_or_throw()
        assert str(e.value).startswith(
            expected_message
        ), f"Expected message to start with {expected_message}; was actually {e.value!s}"

    # TODO: def __repr__() & delete parametrize ids= in tests

    def format_message(self, message: str, parameters: list[Any]) -> str:
        return message.format(*parameters)
