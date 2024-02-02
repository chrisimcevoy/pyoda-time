# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations as _annotations

import datetime as _datetime
import decimal as _decimal
import typing as _typing

__all__: list[str] = []

_T = _typing.TypeVar("_T")
_Ttype = _typing.TypeVar("_Ttype", bound=type)


def _towards_zero_division(x: int | float | _decimal.Decimal, y: int | float | _decimal.Decimal) -> int:
    """Divide two numbers using "towards zero" rounding.

    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import ROUND_DOWN, Decimal

    return int((Decimal(x) / Decimal(y)).quantize(0, ROUND_DOWN))


def _to_ticks(dt: _datetime.datetime) -> int:
    """Get a value akin to C#'s DateTime.Ticks property from a python datetime."""
    # Gratefully stolen from https://stackoverflow.com/a/29368771
    return int((dt - _datetime.datetime(1, 1, 1, tzinfo=_datetime.timezone.utc)).total_seconds() * 10000000)


def _sealed(cls: _Ttype) -> _Ttype:
    """Prevents the decorated class from being subclassed.

    This is intended to loosely emulate the behaviour of the `sealed` keyword in C#.
    Its use should be accompanied by the `typing.final` decorator to aid static analysis.
    """

    def __init_subclass__() -> None:
        raise TypeError(f"{cls.__name__} is not intended to be subclassed.")

    # Use setattr to stop mypy shouting
    setattr(cls, "__init_subclass__", __init_subclass__)

    return cls


def _private(klass: _Ttype) -> _Ttype:
    """Prevents the decorated class from being instantiated.

    This is used to decorate Python classes which have been ported from C#, where the C# class has no public
    constructor.
    """

    msg = f"{klass.__name__} is not intended to be initialised directly."

    def __init__(*_args: _typing.Any, **_kwargs: _typing.Any) -> None:
        raise TypeError(msg)

    def __new__(*_args: _typing.Any, **_kwargs: _typing.Any) -> _Ttype:
        raise TypeError(msg)

    def __call__(*_args: _typing.Any, **_kwargs: _typing.Any) -> _Ttype:
        raise TypeError(msg)

    # Use setattr to stop mypy shouting
    setattr(klass, "__init__", __init__)
    setattr(klass, "__new__", __new__)
    setattr(klass, "__call__", __call__)

    return klass


class _CsharpConstants:
    LONG_MAX_VALUE: _typing.Final[int] = 9223372036854775807
    LONG_MIN_VALUE: _typing.Final[int] = -9223372036854775808


def _int32_overflow(value: int) -> int:
    """Simulates 32-bit signed integer overflow behavior.

    Args:
        value (int): The integer value to apply 32-bit overflow to.

    Returns:
        int: The result after simulating 32-bit overflow.
    """
    return (value + 2**31) % 2**32 - 2**31


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
