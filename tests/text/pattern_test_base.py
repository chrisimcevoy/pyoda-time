# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from abc import ABC
from typing import Generic, TypeVar

from pyoda_time.text._i_pattern import IPattern

from .pattern_test_data import PatternTestData

T = TypeVar("T")


class PatternTestBase(ABC, Generic[T]):
    @staticmethod
    def test_invalid_patterns(invalid_pattern_data: PatternTestData[T]) -> None:
        invalid_pattern_data.test_invalid_pattern()

    @staticmethod
    def test_parse_failures(parse_failure_data: PatternTestData[T]) -> None:
        parse_failure_data.test_parse_failure()

    @staticmethod
    def test_parse(parse_data: PatternTestData[T]) -> None:
        parse_data.test_parse()

    @staticmethod
    def test_format(format_data: PatternTestData[T]) -> None:
        format_data.test_format()

    @staticmethod
    def test_append_format(format_data: PatternTestData[T]) -> None:
        format_data.test_append_format()

    def assert_round_trip(self, value: T, pattern: IPattern[T]) -> None:
        text = pattern.format(value)
        parse_result = pattern.parse(text)
        assert parse_result.value == value, f"{value} != {parse_result.value}"

    def assert_parse_null(self, pattern: IPattern[T]) -> None:
        result = pattern.parse(None)  # type: ignore
        assert not result.success
        assert isinstance(result.exception, ValueError)
