from datetime import datetime

import pytest
import pytz

from pyoda_time import (
    TICKS_PER_MILLISECOND,
    TICKS_PER_SECOND,
    UNIX_EPOCH,
    Duration,
    Instant,
    Offset,
    _LocalInstant,
)
from pyoda_time.utility import _towards_zero_division


class TestInstant:
    # TODO def test_julian_date_conversions(self):

    # TODO def test_from_utc_no_seconds(self):

    # TODO def test_from_utc_with_seconds(self):

    # TODO def test_in_utc(self):

    # TODO def test_in_zone(self):

    # TODO def test_with_offset(self):

    # TODO def test_with_offset_non_iso_calendar(self):

    def test_from_ticks_since_unix_epoch(self) -> None:
        instant = Instant.from_unix_time_ticks(12345)
        assert instant.to_unix_time_ticks() == 12345

    def test_from_unix_time_milliseconds_valid(self) -> None:
        actual = Instant.from_unix_time_milliseconds(12345)
        expected = Instant.from_unix_time_ticks(12345 * TICKS_PER_MILLISECOND)
        assert actual == expected

    def test_from_unix_time_milliseconds_too_large(self) -> None:
        with pytest.raises(ValueError):
            Instant.from_unix_time_milliseconds(int(9223372036854775807 / 100))

    def test_from_unix_time_milliseconds_too_small(self) -> None:
        with pytest.raises(ValueError):
            Instant.from_unix_time_milliseconds(int(-9223372036854775808 / 100))

    def test_from_unix_time_seconds_valid(self) -> None:
        actual = Instant.from_unix_time_seconds(12345)
        expected = Instant.from_unix_time_ticks(12345 * TICKS_PER_SECOND)
        assert actual == expected

    def test_from_unix_time_seconds_too_large(self) -> None:
        with pytest.raises(ValueError):
            Instant.from_unix_time_seconds(int(9223372036854775807 / 1_000_000))

    def test_from_unix_time_seconds_too_small(self) -> None:
        with pytest.raises(ValueError):
            Instant.from_unix_time_seconds(int(-9223372036854775808 / 1_000_000))

    @pytest.mark.parametrize(
        "milliseconds,expected_seconds",
        [
            (-1500, -2),
            (-1001, -2),
            (-1000, -1),
            (-999, -1),
            (-500, -1),
            (0, 0),
            (500, 0),
            (999, 0),
            (1000, 1),
            (1001, 1),
            (1500, 1),
        ],
    )
    def test_to_unix_time_seconds(self, milliseconds: int, expected_seconds: int) -> None:
        instant = Instant.from_unix_time_milliseconds(milliseconds)
        assert instant.to_unix_time_seconds() == expected_seconds

    @pytest.mark.parametrize(
        "ticks,expected_milliseconds",
        [
            (-15000, -2),
            (-10001, -2),
            (-10000, -1),
            (-9999, -1),
            (-5000, -1),
            (0, 0),
            (5000, 0),
            (9999, 0),
            (10000, 1),
            (10001, 1),
            (15000, 1),
        ],
    )
    def test_to_unix_time_milliseconds(self, ticks: int, expected_milliseconds: int) -> None:
        instant = Instant.from_unix_time_ticks(ticks)
        assert instant.to_unix_time_milliseconds() == expected_milliseconds

    def test_unix_conversions_extreme_values(self) -> None:
        max_ = Instant.max_value() - Duration.from_seconds(1) + Duration.epsilon()
        assert Instant.from_unix_time_seconds(max_.to_unix_time_seconds()) == max_
        assert Instant.from_unix_time_milliseconds(max_.to_unix_time_milliseconds()) == max_
        assert Instant.from_unix_time_ticks(max_.to_unix_time_ticks()) == max_

        min_ = Instant.min_value()
        assert Instant.from_unix_time_seconds(min_.to_unix_time_seconds()) == min_
        assert Instant.from_unix_time_milliseconds(min_.to_unix_time_milliseconds()) == min_
        assert Instant.from_unix_time_ticks(min_.to_unix_time_ticks()) == min_

    def test_in_zone_with_calendar(self) -> None:
        ...  # TODO

    def test_max(self) -> None:
        """This follows the Noda Time test which covers Instant.Max(), but additionally covers support for the max()
        python builtin."""
        x = Instant.from_unix_time_ticks(100)
        y = Instant.from_unix_time_ticks(200)
        assert y == Instant.max(x, y) == max(x, y)
        assert y == Instant.max(y, x) == max(y, x)
        assert x == Instant.max(x, Instant.min_value()) == max(x, Instant.min_value())
        assert x == Instant.max(Instant.min_value(), x) == max(Instant.min_value(), x)
        assert Instant.max_value() == Instant.max(Instant.max_value(), x) == max(Instant.max_value(), x)
        assert Instant.max_value() == Instant.max(x, Instant.max_value()) == max(x, Instant.max_value())

    def test_min(self) -> None:
        """This follows the Noda Time test which covers Instant.Min(), but additionally covers support for the min()
        python builtin."""
        x = Instant.from_unix_time_ticks(100)
        y = Instant.from_unix_time_ticks(200)
        assert x == Instant.min(x, y) == min(x, y)
        assert x == Instant.min(y, x) == min(y, x)
        assert Instant.min_value() == Instant.min(x, Instant.min_value()) == min(x, Instant.min_value())
        assert Instant.min_value() == Instant.min(Instant.min_value(), x) == min(Instant.min_value(), x)
        assert x == Instant.min(Instant.max_value(), x) == min(Instant.max_value(), x)
        assert x == Instant.min(x, Instant.max_value()) == min(x, Instant.max_value())

    # TODO def test_to_datetime_utc(self):

    # TODO def test_to_bcl_types_date_out_of_range(self):

    # TODO def test_to_bcl_types_truncate_nanos_towards_start_of_time(self):

    # TODO def test_to_datetimeoffset(self):

    # TODO def test_from_datetimeoffset(self):

    def test_from_datetime_utc_invalid(self) -> None:
        with pytest.raises(ValueError):
            # Roughly equivalent to `DateTimeKind.Local`
            tz = pytz.timezone("America/New_York")
            Instant.from_datetime_utc(datetime(2011, 8, 18, 20, 53, 0, 0, tz))
        with pytest.raises(ValueError):
            # Roughly equivalent to `DateTimeKind.Unspecified`
            Instant.from_datetime_utc(datetime(2011, 8, 18, 20, 53, 0, 0))

    def test_from_datetime_utc_valid(self) -> None:
        x = datetime(2011, 8, 18, 20, 53, 0, 0, pytz.UTC)
        expected = Instant.from_utc(2011, 8, 18, 20, 53)
        actual = Instant.from_datetime_utc(x)
        assert actual == expected

    def test_default_constructor(self) -> None:
        actual = Instant()
        assert actual == UNIX_EPOCH

    # TODO def test_xml_serialization(self):
    # TODO def test_xml_serialization_invalid(self):

    @pytest.mark.parametrize(
        "nanoseconds,expected_ticks",
        [
            (-101, -2),
            (-100, -1),
            (-99, -1),
            (-1, -1),
            (0, 0),
            (99, 0),
            (100, 1),
            (101, 1),
        ],
    )
    def test_ticks_truncates_down(self, nanoseconds: int, expected_ticks: int) -> None:
        nanos = Duration.from_nanoseconds(nanoseconds)
        instant = Instant._from_untrusted_duration(nanos)
        assert instant.to_unix_time_ticks() == expected_ticks

    def test_is_valid(self) -> None:
        assert not Instant._before_min_value()._is_valid
        assert Instant.min_value()._is_valid
        assert Instant.max_value()._is_valid
        assert not Instant._after_max_value()._is_valid

    def test_invalid_values(self) -> None:
        assert Instant._after_max_value() > Instant.max_value()
        assert Instant._before_min_value() < Instant.min_value()

    def test_plus_duration_overflow(self) -> None:
        with pytest.raises(OverflowError):
            Instant.min_value().plus(-Duration.epsilon())
        with pytest.raises(OverflowError):
            Instant.max_value().plus(Duration.epsilon())

    def test_extreme_arithmetic(self) -> None:
        huge_and_positive = Instant.max_value() - Instant.min_value()
        huge_and_negative = Instant.min_value() - Instant.max_value()
        assert huge_and_negative == -huge_and_positive
        assert Instant.max_value() == Instant.min_value() - huge_and_negative
        assert Instant.max_value() == Instant.min_value() + huge_and_positive
        assert Instant.min_value() == Instant.max_value() + huge_and_negative
        assert Instant.min_value() == Instant.max_value() - huge_and_positive

    # TODO def test_plus_offset_overflow(self):

    def test_from_unix_time_milliseconds_range(self) -> None:
        smallest_valid = _towards_zero_division(Instant.min_value().to_unix_time_ticks(), TICKS_PER_MILLISECOND)
        largest_valid = _towards_zero_division(Instant.max_value().to_unix_time_ticks(), TICKS_PER_MILLISECOND)
        assert Instant.from_unix_time_milliseconds(smallest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_milliseconds(smallest_valid - 1)
        assert Instant.from_unix_time_milliseconds(largest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_milliseconds(largest_valid + 1)

    def test_from_unix_time_seconds_range(self) -> None:
        smallest_valid = _towards_zero_division(Instant.min_value().to_unix_time_ticks(), TICKS_PER_SECOND)
        largest_valid = _towards_zero_division(Instant.max_value().to_unix_time_ticks(), TICKS_PER_SECOND)
        assert Instant.from_unix_time_seconds(smallest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_seconds(smallest_valid - 1)
        assert Instant.from_unix_time_seconds(largest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_seconds(largest_valid + 1)

    def test_from_ticks_since_unix_epoch_range(self) -> None:
        smallest_valid = Instant.min_value().to_unix_time_ticks()
        largest_valid = Instant.max_value().to_unix_time_ticks()
        assert Instant.from_unix_time_ticks(smallest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_ticks(smallest_valid - 1)
        assert Instant.from_unix_time_ticks(largest_valid)._is_valid
        with pytest.raises(ValueError):
            Instant.from_unix_time_ticks(largest_valid + 1)

    def test_plus_offset(self) -> None:
        local_instant = UNIX_EPOCH._plus(Offset.from_hours(1))
        assert local_instant._time_since_local_epoch == Duration.from_hours(1)

    def test_safe_plus_normal_time(self) -> None:
        local_instant = UNIX_EPOCH._safe_plus(Offset.from_hours(1))
        assert local_instant._time_since_local_epoch == Duration.from_hours(1)

    @pytest.mark.parametrize(
        "initial_offset,offset_to_add,final_offset",
        [
            (None, 0, None),
            (None, 1, None),
            (None, -1, None),
            (1, -1, 0),
            (1, -2, None),
            (2, 1, 3),
        ],
    )
    def test_safe_plus_near_start_of_time(
        self, initial_offset: int | None, offset_to_add: int, final_offset: int | None
    ) -> None:
        start = (
            Instant._before_min_value()
            if initial_offset is None
            else Instant.min_value() + Duration.from_hours(initial_offset)
        )
        expected = (
            _LocalInstant.before_min_value()
            if final_offset is None
            else Instant.min_value()._plus(Offset.from_hours(final_offset))
        )
        actual = start._safe_plus(Offset.from_hours(offset_to_add))
        assert actual == expected

    @pytest.mark.parametrize(
        "initial_offset,offset_to_add,final_offset",
        [
            (None, 0, None),
            (None, 1, None),
            (None, -1, None),
            (-1, 1, 0),
            (-1, 2, None),
            (-2, -1, -3),
        ],
    )
    def test_safe_plus_near_end_of_time(
        self, initial_offset: int | None, offset_to_add: int, final_offset: int | None
    ) -> None:
        start = (
            Instant._after_max_value()
            if initial_offset is None
            else Instant.max_value() + Duration.from_hours(initial_offset)
        )
        expected = (
            _LocalInstant.after_max_value()
            if final_offset is None
            else Instant.max_value()._plus(Offset.from_hours(final_offset))
        )
        actual = start._safe_plus(Offset.from_hours(offset_to_add))
        assert actual == expected
