from pyoda_time import CalendarSystem, DateTimeZone, LocalDate, LocalDateTime, PyodaConstants
from pyoda_time.calendars import Era

JULIAN: CalendarSystem = CalendarSystem.julian


class TestJulianCalendarSystem:
    """Tests for the Julian calendar system via JulianYearMonthDayCalculator."""

    def test_epoch(self) -> None:
        """The Unix epoch is equivalent to December 19th 1969 in the Julian calendar."""
        julian_epoch: LocalDateTime = PyodaConstants.UNIX_EPOCH.in_zone(DateTimeZone.utc, JULIAN).local_date_time
        assert julian_epoch.year == 1969
        assert julian_epoch.month == 12
        assert julian_epoch.day == 19

    def test_leap_years(self) -> None:
        assert JULIAN.is_leap_year(1900)  # No 100 year rule...
        assert not JULIAN.is_leap_year(1901)
        assert JULIAN.is_leap_year(1904)
        assert JULIAN.is_leap_year(2000)
        assert JULIAN.is_leap_year(2100)  # No 100 year rule...
        assert JULIAN.is_leap_year(2400)
        # Check 1BC, 5BC etc...
        assert JULIAN.is_leap_year(0)
        assert JULIAN.is_leap_year(-4)


class TestJulianCalendarSystemEra:
    def test_get_max_year_of_era(self) -> None:
        date = LocalDate(year=JULIAN.max_year, month=1, day=1, calendar=JULIAN)
        assert JULIAN.get_max_year_of_era(Era.common) == date.year_of_era
        assert date.era == Era.common
        date = LocalDate(year=JULIAN.min_year, month=1, day=1, calendar=JULIAN)
        assert date.year == JULIAN.min_year
        assert JULIAN.get_max_year_of_era(Era.before_common) == date.year_of_era
        assert date.era == Era.before_common

    def test_get_min_year_of_era(self) -> None:
        date = LocalDate(year=1, month=1, day=1, calendar=JULIAN)
        assert JULIAN.get_min_year_of_era(Era.common) == date.year_of_era
        assert date.era == Era.common
        date = LocalDate(year=0, month=1, day=1, calendar=JULIAN)
        assert JULIAN.get_min_year_of_era(Era.before_common) == date.year_of_era
        assert date.era == Era.before_common

    def test_get_absolute_year(self) -> None:
        assert JULIAN.get_absolute_year(1, Era.common) == 1
        assert JULIAN.get_absolute_year(1, Era.before_common) == 0
        assert JULIAN.get_absolute_year(2, Era.before_common) == -1
        assert JULIAN.get_absolute_year(JULIAN.get_max_year_of_era(Era.common), Era.common) == JULIAN.max_year
        assert (
            JULIAN.get_absolute_year(JULIAN.get_max_year_of_era(Era.before_common), Era.before_common)
            == JULIAN.min_year
        )

    def test_era_property(self) -> None:
        start_of_era = LocalDateTime(1, 1, 1, 0, 0, 0, calendar=JULIAN)
        assert start_of_era.era == Era.common
        assert start_of_era.plus_ticks(-1).era == Era.before_common
