# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from pyoda_time import DateAdjusters, LocalDateTime, Offset, OffsetDateTime, TimeAdjusters


class TestOffsetDateTime:
    def test_with_offset(self) -> None:
        morning = LocalDateTime(2014, 1, 31, 9, 30)
        original = OffsetDateTime(morning, Offset.from_hours(-8))
        evening = LocalDateTime(2014, 1, 31, 19, 30)
        new_offset = Offset.from_hours(2)
        expected = OffsetDateTime(evening, new_offset)
        assert original.with_offset(new_offset) == expected

    def test_with_offset_cross_dates(self) -> None:
        noon = OffsetDateTime(LocalDateTime(2017, 8, 22, 12, 0, 0), Offset.from_hours(0))
        previous_night = noon.with_offset(Offset.from_hours(-14))
        next_morning = noon.with_offset(Offset.from_hours(14))
        assert previous_night.local_date_time == LocalDateTime(2017, 8, 21, 22, 0, 0)
        assert next_morning.local_date_time == LocalDateTime(2017, 8, 23, 2, 0, 0)

    def test_with_offset_two_days_forward_and_back(self) -> None:
        # Go from UTC-18 to UTC+18
        night = OffsetDateTime(LocalDateTime(2017, 8, 21, 18, 0, 0), Offset.from_hours(-18))
        morning = night.with_offset(Offset.from_hours(18))
        assert morning.local_date_time == LocalDateTime(2017, 8, 23, 6, 0, 0)
        back_again = morning.with_offset(Offset.from_hours(-18))
        assert back_again == night

    def test_with_time_adjuster(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = LocalDateTime(2014, 6, 27, 12, 5, 8).with_offset(offset)
        assert start.with_time_adjuster(TimeAdjusters.truncate_to_second) == expected

    def test_with_date_adjuster(self) -> None:
        offset = Offset.from_hours_and_minutes(2, 30)
        start = LocalDateTime(2014, 6, 27, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        expected = LocalDateTime(2014, 6, 30, 12, 5, 8).plus_nanoseconds(123456789).with_offset(offset)
        assert start.with_date_adjuster(DateAdjusters.end_of_month) == expected
