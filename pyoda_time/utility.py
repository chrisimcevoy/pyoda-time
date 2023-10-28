from datetime import datetime


class _Preconditions:
    @staticmethod
    def _check_argument_range(
        value: int, min_inclusive: int, max_inclusive: int
    ) -> None:
        if (value < min_inclusive) or (value > max_inclusive):
            raise ValueError(
                f"Value should be in range [{min_inclusive}-{max_inclusive}]"
            )


class _TickArithmetic:
    """Common operations on ticks."""

    @staticmethod
    def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
        """Cautiously converts a number of ticks (which can have any value) into a number of
        days and a tick within that day.
        """
        from pyoda_time import TICKS_PER_DAY

        if ticks >= 0:
            days = int((ticks >> 14) / 52734375)
            tick_of_day = ticks - days * TICKS_PER_DAY
        else:
            days = _towards_zero_division(ticks + 1, TICKS_PER_DAY) - 1
            tick_of_day = ticks - (days + 1) * TICKS_PER_DAY + TICKS_PER_DAY

        return days, tick_of_day

    @staticmethod
    def bounded_days_and_tick_of_day_to_ticks(days: int, tick_of_day: int):
        """Computes a number of ticks from a day/tick-of-day value which is trusted not to overflow,
        even when computed in the simplest way. Only call this method from places where there
        are suitable constraints on the input.
        """
        from pyoda_time import TICKS_PER_DAY

        return days * TICKS_PER_DAY + tick_of_day


def _towards_zero_division(x: int, y: int) -> int:
    """Divide two integers using "towards zero" rounding.
    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import Decimal, ROUND_DOWN

    return int((Decimal(x) / y).quantize(0, ROUND_DOWN))


def _to_ticks(dt: datetime) -> int:
    """Get a value akin to C#'s DateTime.Ticks property from a python datetime."""
    # Gratefully stolen from https://stackoverflow.com/a/29368771
    import pytz

    return int((dt - datetime(1, 1, 1, tzinfo=pytz.UTC)).total_seconds() * 10000000)
