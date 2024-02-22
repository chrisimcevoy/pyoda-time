# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time.text import ParseResult, UnparsableValueError, _ValueCursor


class TestParseResult:
    FAILURE_RESULT = ParseResult[int]._for_invalid_value(_ValueCursor("text"), "text")

    def test_value_success(self) -> None:
        result = ParseResult.for_value(5)
        assert result.value == 5

    def test_value_failure(self) -> None:
        with pytest.raises(UnparsableValueError) as e:
            _ = self.FAILURE_RESULT.value

        assert str(e.value) == "text Value being parsed: '^text'. (^ indicates error position.)"

    def test_exception_success(self) -> None:
        result: ParseResult[int] = ParseResult.for_value(5)
        with pytest.raises(RuntimeError) as e:
            _ = result.exception
        assert str(e.value) == "Parse operation succeeded, so no exception is available"

    def test_exception_failure(self) -> None:
        assert isinstance(self.FAILURE_RESULT.exception, UnparsableValueError)

    def test_get_value_or_throw_success(self) -> None:
        result: ParseResult[int] = ParseResult.for_value(5)
        assert result.get_value_or_throw() == 5

    def test_get_value_or_throw_failure(self) -> None:
        with pytest.raises(UnparsableValueError) as e:
            self.FAILURE_RESULT.get_value_or_throw()
        assert str(e.value) == "text Value being parsed: '^text'. (^ indicates error position.)"

    def test_try_get_value_success(self) -> None:
        result: ParseResult[int] = ParseResult.for_value(5)
        success, actual = result.try_get_value(5)
        assert success
        assert actual == 5

    def test_try_get_value_failure(self) -> None:
        success, actual = self.FAILURE_RESULT.try_get_value(-1)
        assert not success
        assert actual == -1

    def test_convert_for_failure_result(self) -> None:
        converted: ParseResult[str] = self.FAILURE_RESULT.convert(lambda x: f"xx{x}xx")
        with pytest.raises(UnparsableValueError) as e:
            converted.get_value_or_throw()
        assert str(e.value) == "text Value being parsed: '^text'. (^ indicates error position.)"

    def test_convert_for_success_result(self) -> None:
        original = ParseResult[int].for_value(10)
        converted = original.convert(lambda x: f"xx{x}xx")
        assert converted.value == "xx10xx"

    def test_convert_error_for_failure_result(self) -> None:
        converted: ParseResult[str] = self.FAILURE_RESULT.convert_error(str)
        with pytest.raises(UnparsableValueError) as e:
            converted.get_value_or_throw()
        assert str(e.value) == "text Value being parsed: '^text'. (^ indicates error position.)"

    def test_convert_error_for_success_result(self) -> None:
        original: ParseResult[int] = ParseResult[int].for_value(10)
        with pytest.raises(RuntimeError) as e:
            original.convert_error(str)
        assert str(e.value) == "convert_error should not be called on a successful parse result"

    def test_for_exception(self) -> None:
        e = Exception()
        result: ParseResult[int] = ParseResult[int].for_exception(lambda: e)
        assert not result.success
        assert result.exception is e
