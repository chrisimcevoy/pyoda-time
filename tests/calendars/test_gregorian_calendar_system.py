from pyoda_time import CalendarSystem, LocalDate, LocalDateTime
from pyoda_time.calendars import Era


class TestGregorianCalendarSystem:
    def test_leap_year(self) -> None:
        calendar = CalendarSystem.gregorian
        assert not calendar.is_leap_year(1900)
        assert not calendar.is_leap_year(1901)
        assert calendar.is_leap_year(1904)
        assert calendar.is_leap_year(1996)
        assert calendar.is_leap_year(2000)
        assert not calendar.is_leap_year(2100)
        assert calendar.is_leap_year(2400)

    def test_era_property(self) -> None:
        calendar = CalendarSystem.gregorian
        start_of_era = LocalDateTime(1, 1, 1, 0, 0, 0, calendar=calendar)
        assert start_of_era.era == Era.common
        assert start_of_era.plus_ticks(-1).era == Era.before_common

    def test_add_months_boundary_condition(self) -> None:
        start = LocalDate(year=2017, month=8, day=20)
        end = start.plus_months(-19)
        expected = LocalDate(year=2016, month=1, day=20)
        assert end == expected
