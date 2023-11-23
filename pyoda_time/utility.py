__all__: list[str] = []

import datetime as _datetime
import typing as _typing

_T = _typing.TypeVar("_T")
_Ttype = _typing.TypeVar("_Ttype", bound=type)


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
    def _check_argument_range(cls, param_name: str, value: int, min_inclusive: int, max_inclusive: int) -> None:
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


class _TickArithmetic:
    """Common operations on ticks."""

    @staticmethod
    def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
        """Cautiously converts a number of ticks (which can have any value) into a number of days and a tick within that
        day."""

        from pyoda_time import PyodaConstants

        if ticks >= 0:
            days = int((ticks >> 14) / 52734375)
            tick_of_day = ticks - days * PyodaConstants.TICKS_PER_DAY
        else:
            days = _towards_zero_division(ticks + 1, PyodaConstants.TICKS_PER_DAY) - 1
            tick_of_day = ticks - (days + 1) * PyodaConstants.TICKS_PER_DAY + PyodaConstants.TICKS_PER_DAY

        return days, tick_of_day

    @staticmethod
    def bounded_days_and_tick_of_day_to_ticks(days: int, tick_of_day: int) -> int:
        """Computes a number of ticks from a day/tick-of-day value which is trusted not to overflow, even when computed
        in the simplest way.

        Only call this method from places where there are suitable constraints on the input.
        """

        from pyoda_time import PyodaConstants

        return days * PyodaConstants.TICKS_PER_DAY + tick_of_day


def _towards_zero_division(x: int | float, y: int) -> int:
    """Divide two integers using "towards zero" rounding.

    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import ROUND_DOWN, Decimal

    return int((Decimal(x) / y).quantize(0, ROUND_DOWN))


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
