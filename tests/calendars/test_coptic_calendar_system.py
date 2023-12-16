import pytest

from pyoda_time import CalendarSystem, DateTimeZone, IsoDayOfWeek, LocalDateTime, PyodaConstants
from pyoda_time.calendars import Era


class TestCopticCalendarSystem:
    """Tests for the Coptic calendar system."""

    def test_coptic_epoch(self) -> None:
        coptic: CalendarSystem = CalendarSystem.coptic
        coptic_epoch: LocalDateTime = LocalDateTime(1, 1, 1, 0, 0, calendar=coptic)

        julian: CalendarSystem = CalendarSystem.julian
        converted: LocalDateTime = coptic_epoch.with_calendar(julian)

        expected: LocalDateTime = LocalDateTime(284, 8, 29, 0, 0, calendar=julian)
        assert converted == expected

    def test_unix_epoch(self) -> None:
        coptic: CalendarSystem = CalendarSystem.coptic
        unix_epoch_in_coptic_calendar: LocalDateTime = PyodaConstants.UNIX_EPOCH.in_zone(
            DateTimeZone.utc, coptic
        ).local_date_time
        expected: LocalDateTime = LocalDateTime(1686, 4, 23, 0, 0, calendar=coptic)
        assert unix_epoch_in_coptic_calendar == expected

    def test_sample_date(self) -> None:
        coptic_calendar: CalendarSystem = CalendarSystem.coptic
        iso = LocalDateTime(2004, 6, 9, 0, 0, 0, 0)
        coptic = iso.with_calendar(coptic_calendar)

        assert coptic.era == Era.anno_martyrum
        assert coptic.year_of_era == 1720

        assert coptic.year == 1720
        assert not coptic_calendar.is_leap_year(1720)

        assert coptic.month == 10
        assert coptic.day == 2

        assert coptic.day_of_week == IsoDayOfWeek.WEDNESDAY

        assert coptic.day_of_year == 9 * 30 + 2

        assert coptic.hour == 0
        assert coptic.minute == 0
        assert coptic.second == 0
        assert coptic.millisecond == 0

    def test_invalid_era(self) -> None:
        # TODO: This is ArgumentNullException in Noda Time
        with pytest.raises(TypeError):
            CalendarSystem.coptic.get_absolute_year(1720, None)  # type: ignore
        # TODO: This is ArgumentException in Noda Time
        with pytest.raises(ValueError):
            CalendarSystem.coptic.get_absolute_year(1720, Era.anno_hegirae)
