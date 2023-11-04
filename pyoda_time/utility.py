from datetime import datetime
from typing import Any, TypeVar


class _Preconditions:
    @staticmethod
    def _check_argument_range(value: int, min_inclusive: int, max_inclusive: int) -> None:
        if (value < min_inclusive) or (value > max_inclusive):
            raise ValueError(f"Value should be in range [{min_inclusive}-{max_inclusive}]")


class _TickArithmetic:
    """Common operations on ticks."""

    @staticmethod
    def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
        """Cautiously converts a number of ticks (which can have any value) into a number of days and a tick within that
        day."""
        from pyoda_time import TICKS_PER_DAY

        if ticks >= 0:
            days = int((ticks >> 14) / 52734375)
            tick_of_day = ticks - days * TICKS_PER_DAY
        else:
            days = _towards_zero_division(ticks + 1, TICKS_PER_DAY) - 1
            tick_of_day = ticks - (days + 1) * TICKS_PER_DAY + TICKS_PER_DAY

        return days, tick_of_day

    @staticmethod
    def bounded_days_and_tick_of_day_to_ticks(days: int, tick_of_day: int) -> int:
        """Computes a number of ticks from a day/tick-of-day value which is trusted not to overflow, even when computed
        in the simplest way.

        Only call this method from places where there are suitable constraints on the input.
        """
        from pyoda_time import TICKS_PER_DAY

        return days * TICKS_PER_DAY + tick_of_day


def _towards_zero_division(x: int, y: int) -> int:
    """Divide two integers using "towards zero" rounding.

    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import ROUND_DOWN, Decimal

    return int((Decimal(x) / y).quantize(0, ROUND_DOWN))


def _to_ticks(dt: datetime) -> int:
    """Get a value akin to C#'s DateTime.Ticks property from a python datetime."""
    # Gratefully stolen from https://stackoverflow.com/a/29368771
    import pytz

    return int((dt - datetime(1, 1, 1, tzinfo=pytz.UTC)).total_seconds() * 10000000)


T = TypeVar("T", bound=type)


def sealed(cls: T) -> T:
    """Prevents the decorated class from being subclassed.

    This is intended to loosely emulate the behaviour of the `sealed` keyword in C#.
    Its use should be accompanied by the `typing.final` decorator to aid static analysis.
    """

    def __init_subclass__() -> None:
        raise TypeError(f"{cls.__name__} is not intended to be subclassed.")

    # Use setattr to stop mypy shouting
    setattr(cls, "__init_subclass__", __init_subclass__)

    return cls


def private(klass: T) -> T:
    """Prevents the decorated class from being instantiated.

    This is used to decorate Python classes which have been ported from C#, where the C# class has no public
    constructor.
    """

    msg = f"{klass.__name__} is not intended to be initialised directly."

    def __init__(*_args: Any, **_kwargs: Any) -> None:
        raise TypeError(msg)

    def __new__(*_args: Any, **_kwargs: Any) -> T:
        raise TypeError(msg)

    def __call__(*_args: Any, **_kwargs: Any) -> T:
        raise TypeError(msg)

    # Use setattr to stop mypy shouting
    setattr(klass, "__init__", __init__)
    setattr(klass, "__new__", __new__)
    setattr(klass, "__call__", __call__)

    return klass
