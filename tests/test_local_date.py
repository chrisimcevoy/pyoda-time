# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from pyoda_time import CalendarSystem, LocalDate, LocalDateTime, LocalTime


class TestLocalDate:
    def test_default_constructor(self) -> None:
        actual = LocalDate()
        assert actual == LocalDate(year=1, month=1, day=1)

    def test_combination_with_time(self) -> None:
        # Test all three approaches in the same test - they're logically equivalent.
        calendar = CalendarSystem.julian
        date = LocalDate(year=2014, month=3, day=28, calendar=calendar)
        time = LocalTime(hour=20, minute=17, second=30)
        expected = LocalDateTime(year=2014, month=3, day=28, hour=20, minute=17, second=30, calendar=calendar)
        assert date + time == expected
        assert date.at(time) == expected
        assert time.on(date) == expected
