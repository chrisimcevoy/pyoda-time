# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations as _annotations

__all__: list[str] = []

import typing as _typing

_T = _typing.TypeVar("_T")


class _Preconditions:
    """Helper static methods for argument/state validation."""

    @classmethod
    def _check_not_null(cls, argument: _T, param_name: str) -> _T:
        """Returns the given argument after checking whether it's null.

        This is useful for putting nullity checks in parameters which are passed to base class constructors.
        """
        if argument is None:
            raise TypeError(f"{param_name} cannot be None.")
        return argument

    @classmethod
    def _check_argument_range(
        cls, param_name: str, value: int | float, min_inclusive: int | float, max_inclusive: int | float
    ) -> None:
        if (value < min_inclusive) or (value > max_inclusive):
            cls._throw_argument_out_of_range_exception(param_name, value, min_inclusive, max_inclusive)

    @staticmethod
    def _throw_argument_out_of_range_exception(
        param_name: str, value: _T, min_inclusive: _T, max_inclusive: _T
    ) -> None:
        raise ValueError(
            f"Value should be in range [{min_inclusive}-{max_inclusive}]\n"
            f"Parameter name: {param_name}\n"
            f"Actual value was {value}"
        )

    @classmethod
    def _check_argument(cls, expession: bool, parameter: str, message: str, *message_args: _typing.Any) -> None:
        if not expession:
            if message_args:
                message = message.format(*message_args)
            raise ValueError(f"{message}\nParameter name: {parameter}")

    @classmethod
    def _check_state(cls, expression: bool, message: str) -> None:
        if not expression:
            raise RuntimeError(message)
