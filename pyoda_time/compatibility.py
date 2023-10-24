"""Functions which help achieve parity with Noda Time / .NET"""
from datetime import datetime

import pytz


def towards_zero_division(x: int, y: int) -> int:
    """Divide two integers using "towards zero" rounding.
    This ensures that integer division produces the same result as it would do in C#.
    """
    from decimal import Decimal, ROUND_DOWN

    return int((Decimal(x) / y).quantize(0, ROUND_DOWN))


def to_ticks(dt: datetime) -> int:
    """Get a value akin to C#'s DateTime.Ticks property from a python datetime."""
    # Gratefully stolen from https://stackoverflow.com/a/29368771
    return int((dt - datetime(1, 1, 1, tzinfo=pytz.UTC)).total_seconds() * 10000000)
