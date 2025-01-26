# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import CalendarSystem, DateAdjusters, IsoDayOfWeek, LocalDate, Period


class TestDateAdjusters:
    def test_start_of_month(self) -> None:
        start = LocalDate(2014, 6, 27)
        end = LocalDate(2014, 6, 1)
        assert DateAdjusters.start_of_month(start) == end

    def test_end_of_month(self) -> None:
        start = LocalDate(2014, 6, 27)
        end = LocalDate(2014, 6, 30)
        assert DateAdjusters.end_of_month(start) == end

    def test_day_of_month(self) -> None:
        start = LocalDate(2014, 6, 27)
        end = LocalDate(2014, 6, 19)
        adjuster = DateAdjusters.day_of_month(19)
        assert adjuster(start) == end

    @pytest.mark.parametrize(
        "year,month,day,day_of_week,expected_year,expected_month,expected_day",
        [
            pytest.param(2014, 8, 18, IsoDayOfWeek.MONDAY, 2014, 8, 18, id="Same day-of-week"),
            (2014, 8, 18, IsoDayOfWeek.TUESDAY, 2014, 8, 19),
            (2014, 8, 18, IsoDayOfWeek.SUNDAY, 2014, 8, 24),
            pytest.param(2014, 8, 31, IsoDayOfWeek.MONDAY, 2014, 9, 1, id="Wrap month"),
        ],
    )
    def test_next_or_same(
        self,
        year: int,
        month: int,
        day: int,
        day_of_week: IsoDayOfWeek,
        expected_year: int,
        expected_month: int,
        expected_day: int,
    ) -> None:
        start = LocalDate(year, month, day)
        actual = start.with_date_adjuster(DateAdjusters.next_or_same(day_of_week))
        expected = LocalDate(expected_year, expected_month, expected_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "year,month,day,day_of_week,expected_year,expected_month,expected_day",
        [
            pytest.param(2014, 8, 18, IsoDayOfWeek.MONDAY, 2014, 8, 18, id="Same day-of-week"),
            (2014, 8, 18, IsoDayOfWeek.TUESDAY, 2014, 8, 12),
            (2014, 8, 18, IsoDayOfWeek.SUNDAY, 2014, 8, 17),
            pytest.param(2014, 8, 1, IsoDayOfWeek.THURSDAY, 2014, 7, 31, id="Wrap month"),
        ],
    )
    def test_previous_or_same(
        self,
        year: int,
        month: int,
        day: int,
        day_of_week: IsoDayOfWeek,
        expected_year: int,
        expected_month: int,
        expected_day: int,
    ) -> None:
        start = LocalDate(year, month, day)
        actual = start.with_date_adjuster(DateAdjusters.previous_or_same(day_of_week))
        expected = LocalDate(expected_year, expected_month, expected_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "year,month,day,day_of_week,expected_year,expected_month,expected_day",
        [
            pytest.param(2014, 8, 18, IsoDayOfWeek.MONDAY, 2014, 8, 25, id="Same day-of-week"),
            (2014, 8, 18, IsoDayOfWeek.TUESDAY, 2014, 8, 19),
            (2014, 8, 18, IsoDayOfWeek.SUNDAY, 2014, 8, 24),
            pytest.param(2014, 8, 31, IsoDayOfWeek.MONDAY, 2014, 9, 1, id="Wrap month"),
        ],
    )
    def test_next(
        self,
        year: int,
        month: int,
        day: int,
        day_of_week: IsoDayOfWeek,
        expected_year: int,
        expected_month: int,
        expected_day: int,
    ) -> None:
        start = LocalDate(year, month, day)
        actual = start.with_date_adjuster(DateAdjusters.next(day_of_week))
        expected = LocalDate(expected_year, expected_month, expected_day)
        assert actual == expected

    @pytest.mark.parametrize(
        "year,month,day,day_of_week,expected_year,expected_month,expected_day",
        [
            pytest.param(2014, 8, 18, IsoDayOfWeek.MONDAY, 2014, 8, 11, id="Same day-of-week"),
            (2014, 8, 18, IsoDayOfWeek.TUESDAY, 2014, 8, 12),
            (2014, 8, 18, IsoDayOfWeek.SUNDAY, 2014, 8, 17),
            pytest.param(2014, 8, 1, IsoDayOfWeek.THURSDAY, 2014, 7, 31, id="Wrap month"),
        ],
    )
    def test_previous(
        self,
        year: int,
        month: int,
        day: int,
        day_of_week: IsoDayOfWeek,
        expected_year: int,
        expected_month: int,
        expected_day: int,
    ) -> None:
        start = LocalDate(year, month, day)
        actual = start.with_date_adjuster(DateAdjusters.previous(day_of_week))
        expected = LocalDate(expected_year, expected_month, expected_day)
        assert actual == expected

    def test_month_valid(self) -> None:
        adjuster = DateAdjusters.month(2)
        start = LocalDate(2017, 8, 21, CalendarSystem.julian)
        actual = start.with_date_adjuster(adjuster)
        expected = LocalDate(2017, 2, 21, CalendarSystem.julian)
        assert actual == expected

    def test_month_invalid_adjustment(self) -> None:
        adjuster = DateAdjusters.month(2)
        start = LocalDate(2017, 8, 30, CalendarSystem.julian)
        with pytest.raises(ValueError):
            start.with_date_adjuster(adjuster)

    def test_iso_day_of_week_adjusters_invalid(self) -> None:
        invalid = IsoDayOfWeek.NONE
        with pytest.raises(ValueError):
            DateAdjusters.next(invalid)
        with pytest.raises(ValueError):
            DateAdjusters.next_or_same(invalid)
        with pytest.raises(ValueError):
            DateAdjusters.previous(invalid)
        with pytest.raises(ValueError):
            DateAdjusters.previous_or_same(invalid)

    def test_add_period_valid(self) -> None:
        period = Period.from_months(1) + Period.from_days(3)
        adjuster = DateAdjusters.add_period(period)
        start = LocalDate(2019, 5, 4)
        assert start.with_date_adjuster(adjuster) == LocalDate(2019, 6, 7)

    def test_add_period_null(self) -> None:
        with pytest.raises(TypeError):
            DateAdjusters.add_period(None)  # type: ignore

    def test_add_period_including_time_units(self) -> None:
        with pytest.raises(ValueError):
            DateAdjusters.add_period(Period.from_days(1) + Period.from_hours(1))
