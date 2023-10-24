from decimal import Decimal, ROUND_DOWN


class Preconditions:
    @staticmethod
    def check_argument_range(
        value: int, min_inclusive: int, max_inclusive: int
    ) -> None:
        if (value < min_inclusive) or (value > max_inclusive):
            raise ValueError(
                f"Value should be in range [{min_inclusive}-{max_inclusive}]"
            )


class TickArithmetic:
    @staticmethod
    def ticks_to_days_and_tick_of_day(ticks: int) -> tuple[int, int]:
        from pyoda_time import TICKS_PER_DAY

        if ticks >= 0:
            days = int((ticks >> 14) / 52734375)
            tick_of_day = ticks - days * TICKS_PER_DAY
        else:
            # In C#, the `days` expression forces integer division:
            #     `int days = (int) ((ticks + 1) / TicksPerDay) - 1;`
            # Importantly, integer division in C# rounds towards zero.
            #
            # In Python, we need to emulate that behaviour by forcing
            # `Decimal` division and then passing a rounding strategy
            # to `Decimal.quantize()`. Don't worry, it is "towards zero"
            # despite the name `ROUND_DOWN`.
            #
            # Relevant test:
            #     `TestInstant.test_unix_conversions_extreme_values`
            days = int(
                (((Decimal(ticks) + 1) / TICKS_PER_DAY) - 1).quantize(0, ROUND_DOWN)
            )
            tick_of_day = ticks - (days + 1) * TICKS_PER_DAY + TICKS_PER_DAY

        return days, tick_of_day

    @staticmethod
    def bounded_days_and_tick_of_day_to_ticks(days: int, tick_of_day: int):
        from pyoda_time import TICKS_PER_DAY

        return days * TICKS_PER_DAY + tick_of_day
