import pytest

from pyoda_time import (
    MILLISECONDS_PER_HOUR,
    MILLISECONDS_PER_MINUTE,
    NANOSECONDS_PER_HOUR,
    NANOSECONDS_PER_MINUTE,
    SECONDS_PER_HOUR,
    SECONDS_PER_MINUTE,
    TICKS_PER_HOUR,
    TICKS_PER_MINUTE,
    Offset,
)


class TestOffset:
    def test_zero(self) -> None:
        test = Offset.zero
        assert test.milliseconds == 0

    def test_from_seconds_valid(self) -> None:
        test = Offset.from_seconds(12345)
        assert test.seconds == 12345

    def from_seconds_invalid(self) -> None:
        seconds = 18 * SECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_seconds(seconds)
        with pytest.raises(ValueError):
            Offset.from_seconds(-seconds)

    def from_milliseconds_valid(self) -> None:
        value = Offset.from_milliseconds(-15 * MILLISECONDS_PER_MINUTE)
        assert value.seconds == -15
        assert value.milliseconds == 15 * MILLISECONDS_PER_MINUTE

    def from_milliseconds_invalid(self) -> None:
        millis = 18 * MILLISECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_milliseconds(millis)
        with pytest.raises(ValueError):
            Offset.from_milliseconds(-millis)

    def from_ticks_valid(self) -> None:
        value = Offset.from_ticks(-15 * TICKS_PER_MINUTE)
        assert value.seconds == -15 * SECONDS_PER_MINUTE
        assert value.ticks == -15 * TICKS_PER_MINUTE

    def from_ticks_invalid(self) -> None:
        ticks = 18 * TICKS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_ticks(ticks)
        with pytest.raises(ValueError):
            Offset.from_ticks(-ticks)

    def from_nanoseconds_valid(self) -> None:
        value = Offset.from_nanoseconds(-15 * NANOSECONDS_PER_MINUTE)
        assert value.seconds == -15 * SECONDS_PER_MINUTE
        assert value.nanoseconds == -15 * NANOSECONDS_PER_MINUTE

    def from_nanoseconds_invalid(self) -> None:
        nanos = 18 * NANOSECONDS_PER_HOUR + 1
        with pytest.raises(ValueError):
            Offset.from_nanoseconds(nanos)
        with pytest.raises(ValueError):
            Offset.from_nanoseconds(-nanos)

    def from_hours_valid(self) -> None:
        value = Offset.from_hours(-15)
        assert value.seconds == -15 * SECONDS_PER_HOUR

    def from_hours_invalid(self) -> None:
        with pytest.raises(ValueError):
            Offset.from_hours(19)
        with pytest.raises(ValueError):
            Offset.from_hours(-19)

    def from_hours_and_minutes_valid(self) -> None:
        value = Offset.from_hours_and_minutes(5, 30)
        assert value.seconds == 5 * SECONDS_PER_HOUR + 30 * SECONDS_PER_MINUTE
