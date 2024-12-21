# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import itertools

import pytest

from pyoda_time import IsoDayOfWeek, LocalDateTime, LocalTime
from pyoda_time._compatibility._day_of_week import DayOfWeek
from pyoda_time._local_instant import _LocalInstant
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset

from .. import helpers
from ..time_zones.io.dtz_io_helper import _DtzIoHelper


class TestZoneYearOffset:
    @pytest.mark.parametrize("month", [0, 34, -3])
    def test_construct_invalid_month_exception(self, month: int) -> None:
        with pytest.raises(ValueError) as e:
            _ZoneYearOffset._ctor(_TransitionMode.STANDARD, month, 1, 1, True, LocalTime.midnight)
        assert str(e.value) == "month_of_year is not in the valid range: [1, 12]"

    @pytest.mark.parametrize("day_of_month", [0, 32, 475, -32])
    def test_construct_invalid_day_of_month_exception(self, day_of_month: int) -> None:
        with pytest.raises(ValueError) as e:
            _ZoneYearOffset._ctor(_TransitionMode.STANDARD, 2, day_of_month, 1, True, LocalTime.midnight)
        assert str(e.value) == "day_of_month is not in the valid range: [1, 31] or [-31, -1]"

    @pytest.mark.parametrize("day_of_week", [-1, 8, 5756, -347])
    def test_construct_invalid_day_of_week_exception(self, day_of_week: int) -> None:
        with pytest.raises(ValueError) as e:
            _ZoneYearOffset._ctor(_TransitionMode.STANDARD, 2, 3, day_of_week, True, LocalTime.midnight)
        assert str(e.value) == "day_of_week is not in the valid range: [1, 7]"

    @pytest.mark.parametrize("month", range(1, 13))
    def test_construct_valid_months(self, month: int) -> None:
        _ZoneYearOffset._ctor(_TransitionMode.STANDARD, month, 1, 1, True, LocalTime.midnight)

    @pytest.mark.parametrize("day", itertools.chain(range(1, 13), range(-1, -32, -1)))
    def test_construct_valid_days(self, day: int) -> None:
        _ZoneYearOffset._ctor(_TransitionMode.STANDARD, 1, day, 1, True, LocalTime.midnight)

    @pytest.mark.parametrize("day_of_week", range(8))
    def test_construct_valid_days_of_week(self, day_of_week: int) -> None:
        _ZoneYearOffset._ctor(_TransitionMode.STANDARD, 1, 1, day_of_week, True, LocalTime.midnight)

    def test_get_occurrence_for_year_defaults_epoch(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        expected = LocalDateTime(1970, 1, 1, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_year_1971(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1971)
        expected = LocalDateTime(1971, 1, 1, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_milliseconds(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 0, True, LocalTime(0, 0, 0, 1))
        actual = offset._get_occurrence_for_year(1970)
        expected = LocalDateTime(1970, 1, 1, 0, 0, 0, 1)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_wednesday_forward(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, int(DayOfWeek.Wednesday), True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        # 1970-01-01 was a Thursday
        expected = LocalDateTime(1970, 1, 7, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_wednesday_backward(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 15, int(DayOfWeek.Wednesday), False, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        # 1970-01-15 was a Thursday
        expected = LocalDateTime(1970, 1, 14, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_jan_minus_two(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, -2, 0, True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        expected = LocalDateTime(1970, 1, 30, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_jan_five(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 5, 0, True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        expected = LocalDateTime(1970, 1, 5, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_feb(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 1, 0, True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1970)
        expected = LocalDateTime(1970, 2, 1, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_last_sunday_in_october(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 10, -1, int(IsoDayOfWeek.SUNDAY), False, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(1996)
        expected = LocalDateTime(1996, 10, 27, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_exactly_feb_29th_leap_year(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 29, 0, False, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(2012)
        expected = LocalDateTime(2012, 2, 29, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_exactly_feb_29th_not_leap_year(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 29, 0, False, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(2013)
        # For "exact", go to Feb 28th
        expected = LocalDateTime(2013, 2, 28, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_at_least_feb_29th_leap_year(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 29, int(IsoDayOfWeek.SUNDAY), True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(2012)
        # March 4th is the first Sunday after 2012-02-29
        expected = LocalDateTime(2012, 3, 4, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_at_least_feb_29th_not_leap_year(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 29, int(IsoDayOfWeek.SUNDAY), True, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(2013)
        # March 3rd is the first Sunday after the non-existent 2013-02-29
        expected = LocalDateTime(2013, 3, 3, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_at_most_feb_29th_not_leap_year(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 2, 29, int(IsoDayOfWeek.SUNDAY), False, LocalTime.midnight)
        actual = offset._get_occurrence_for_year(2013)
        # Feb 24th is the last Sunday is February 2013
        expected = LocalDateTime(2013, 2, 24, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_with_add_day(self) -> None:
        # Last Thursday in October, then add 24 hours. The last Thursday in October 2013 is the 31st, so
        # we should get the start of November 1st.
        offset = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, -1, int(IsoDayOfWeek.THURSDAY), False, LocalTime.midnight, True
        )
        actual = offset._get_occurrence_for_year(2013)
        # Feb 24th is the last Sunday is February 2013
        expected = LocalDateTime(2013, 11, 1, 0, 0)._to_local_instant()
        assert actual == expected

    def test_get_occurrence_for_year_with_add_day_dec_31st_9999(self) -> None:
        offset = _ZoneYearOffset._ctor(_TransitionMode.UTC, 12, 31, 0, False, LocalTime.midnight, True)
        actual = offset._get_occurrence_for_year(9999)
        # Feb 24th is the last Sunday is February 2013
        expected = _LocalInstant.after_max_value()
        assert actual == expected

    def test_serialization(self) -> None:
        dio = _DtzIoHelper._create_no_string_pool()
        expected = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime(12, 34, 45, 678)
        )
        dio.test_zone_year_offset(expected)

        dio.reset()
        expected = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, -31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        dio.test_zone_year_offset(expected)

    def test_iequatable(self) -> None:
        value = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        equal_value = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )
        unequal_value = _ZoneYearOffset._ctor(
            _TransitionMode.UTC, 9, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight
        )

        helpers.test_equals_class(value, equal_value, unequal_value)
