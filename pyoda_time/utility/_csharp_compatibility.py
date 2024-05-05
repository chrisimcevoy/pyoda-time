# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import datetime
import decimal
from typing import Any, Final, Literal, TypeVar

__all__: list[str] = []

SEALED_CLASSES: Final[list[type]] = []
_T = TypeVar("_T")
_Ttype = TypeVar("_Ttype", bound=type)


def _as_span(text: str | None, start: int) -> str:
    """Roughly equivalent to:
    public static ReadOnlySpan<char> AsSpan(this string? text, int start)
    """
    if text is None:
        if start != 0:
            raise IndexError("start index out of range")
        return ""
    if not (0 <= start <= len(text)):
        raise IndexError("start index out of range")
    return text[start:]


def _towards_zero_division(x: int | float | decimal.Decimal, y: int | float | decimal.Decimal) -> int:
    """Divide two numbers using "towards zero" rounding.

    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import ROUND_DOWN, Decimal

    return int((Decimal(x) / Decimal(y)).quantize(0, ROUND_DOWN))


def _to_ticks(dt: datetime.datetime) -> int:
    """Get a value akin to C#'s DateTime.Ticks property from a python datetime."""
    # Gratefully stolen from https://stackoverflow.com/a/29368771
    return int((dt - datetime.datetime(1, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds() * 10000000)


def _sealed(cls: _Ttype) -> _Ttype:
    """Prevents the decorated class from being subclassed.

    This is intended to loosely emulate the behaviour of the ``sealed`` keyword in C#.
    Its use should be accompanied by the ``typing.final`` decorator to aid static analysis.
    """

    def __init_subclass__() -> None:
        raise TypeError(f"{cls.__name__} is not intended to be subclassed.")

    # Use setattr to stop mypy shouting
    setattr(cls, "__init_subclass__", __init_subclass__)

    SEALED_CLASSES.append(cls)

    return cls


def _private(klass: _Ttype) -> _Ttype:
    """Prevents the decorated class from being instantiated.

    This is used to decorate Python classes which have been ported from C#, where the C# class has no public
    constructor.
    """

    msg = f"{klass.__name__} is not intended to be initialised directly."

    def __init__(self: Any) -> None:
        """

        :raises TypeError: This class is not intended to be instantiated directly.
        """
        raise TypeError(msg)

    def __new__(cls: _Ttype) -> _Ttype:
        """

        :raises TypeError: This class is not intended to be instantiated directly.
        """
        raise TypeError(msg)

    def __call__(*_args: Any, **_kwargs: Any) -> _Ttype:
        """

        :raises TypeError: This class is not intended to be instantiated directly.
        """
        raise TypeError(msg)

    # Use setattr to stop mypy shouting
    setattr(klass, "__init__", __init__)
    setattr(klass, "__new__", __new__)
    setattr(klass, "__call__", __call__)

    # This is used in sphinx docs to ignore the special methods assigned above.
    setattr(klass, "__no_public_constructor__", True)

    return klass


class _CsharpConstants:
    INT_MIN_VALUE: Final[int] = -2147483648
    INT_MAX_VALUE: Final[int] = 2147483647
    LONG_MIN_VALUE: Final[int] = -9223372036854775808
    LONG_MAX_VALUE: Final[int] = 9223372036854775807


def __int_overflow(value: int, bits: Literal[32, 64]) -> int:
    """Simulates C# signed integer overflow behavior for a specified bit width.

    :param value: The integer value to apply overflow to.
    :param bits: The bit width of the integer.
    :return: The result after simulating overflow for the specified bit width.
    """
    max_value: int = 2 ** (bits - 1)
    result: int = (value + max_value) % (2**bits) - max_value
    return result


def _int32_overflow(value: int) -> int:
    """Simulates C# 32-bit signed integer overflow behavior.

    :param value: The integer value to apply 32-bit overflow to.
    :return: The result after simulating 32-bit overflow.
    """
    return __int_overflow(value, 32)


def _int64_overflow(value: int) -> int:
    """Simulates C# 64-bit signed integer overflow behavior.

    :param value: The integer value to apply 64-bit overflow to.
    :return: The result after simulating 64-bit overflow.
    """
    return __int_overflow(value, 64)


def _csharp_modulo(dividend: int, divisor: int) -> int:
    """Perform a modulo operation with C# behavior, where the result has the same sign as the divisor.

    In C#, the result of a modulo operation takes the sign of the divisor, unlike Python where it
    takes the sign of the dividend. This function adjusts the Python modulo result to mimic C#'s behavior.

    Args:
    dividend (int): The number to be divided.
    divisor (int): The number by which to divide.

    Returns:
    int: The result of the modulo operation, adjusted for C# behavior.
    """
    result = dividend % divisor
    if dividend < 0 < result:
        result -= abs(divisor)
    return result
