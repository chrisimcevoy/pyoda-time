from ..pyoda_constants import *


def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
    if ticks >= 0:
        days = (ticks >> 14) / 52734375
        tick_of_day = ticks - days * TICKS_PER_DAY
    else:
        days = ((ticks + 1) / TICKS_PER_DAY) - 1
        tick_of_day = ticks - (days + 1) * TICKS_PER_DAY + TICKS_PER_DAY

    return days, tick_of_day
