import inspect
from typing import Final

import pytest

from pyoda_time import CalendarSystem, LocalDate, _CalendarOrdinal
from pyoda_time.calendars import Era
from tests import helpers


def test_is_private() -> None:
    with pytest.raises(TypeError) as e:
        CalendarSystem()
    assert str(e.value) == "CalendarSystem is not intended to be initialised directly."


def test_is_sealed() -> None:
    with pytest.raises(TypeError) as e:
        # mypy complains because CalendarSystem is decorated with @final
        class Foo(CalendarSystem):  # type: ignore
            pass

    assert str(e.value) == "CalendarSystem is not intended to be subclassed."


def test_is_final() -> None:
    # mypy complains that his attribute does not exist.
    # It is added to the class by the @final decorator.
    assert CalendarSystem.__final__  # type: ignore


_SUPPORTED_IDS: Final[list[str]] = list(CalendarSystem.ids)
_SUPPORTED_CALENDARS: Final[list[CalendarSystem]] = [CalendarSystem.for_id(id_) for id_ in _SUPPORTED_IDS]


def test_supported_ids() -> None:
    """This is a manual test to ensure that the Calendar IDs in pyoda time match those in noda time."""
    noda_time_calendar_ids = [
        "ISO",
        "Gregorian",
        "Coptic",
        "Badi",
        "Julian",
        "Hijri Civil-Indian",
        "Hijri Civil-Base15",
        "Hijri Civil-Base16",
        "Hijri Civil-HabashAlHasib",
        "Hijri Astronomical-Indian",
        "Hijri Astronomical-Base15",
        "Hijri Astronomical-Base16",
        "Hijri Astronomical-HabashAlHasib",
        "Persian Simple",
        "Persian Arithmetic",
        "Persian Algorithmic",
        "Um Al Qura",
        "Hebrew Civil",
        "Hebrew Scriptural",
    ]
    assert sorted(_SUPPORTED_IDS) == sorted(noda_time_calendar_ids)


class TestCalendarSystem:
    @pytest.mark.parametrize("calendar", _SUPPORTED_CALENDARS, ids=lambda x: x.id)
    def test_max_date(self, calendar: CalendarSystem) -> None:
        self.__validate_properties(calendar, calendar._max_days, calendar.max_year)

    @pytest.mark.parametrize("calendar", _SUPPORTED_CALENDARS, ids=lambda x: x.id)
    def test_min_date(self, calendar: CalendarSystem) -> None:
        self.__validate_properties(calendar, calendar._min_days, calendar.min_year)

    def __validate_properties(self, calendar: CalendarSystem, days_since_epoch: int, expected_year: int) -> None:
        local_date = LocalDate._ctor(days_since_epoch=days_since_epoch, calendar=calendar)
        assert local_date.year == expected_year

        for name, prop in inspect.getmembers(LocalDate, lambda p: isinstance(p, property)):
            _ = getattr(local_date, name) is None


class TestCalendarSystemEra:
    """Tests using CopticCalendar as a simple example which doesn't override anything."""

    COPTIC_CALENDAR: Final[CalendarSystem] = CalendarSystem.coptic

    def test_get_absolute_year(self) -> None:
        assert self.COPTIC_CALENDAR.get_absolute_year(5, Era.anno_martyrum) == 5
        # Prove it's right...
        local_date = LocalDate(year=5, month=1, day=1, calendar=self.COPTIC_CALENDAR)
        assert local_date.year == 5
        assert local_date.year_of_era == 5
        assert local_date.era == Era.anno_martyrum

    def test_get_min_year_of_era(self) -> None:
        assert self.COPTIC_CALENDAR.get_min_year_of_era(Era.anno_martyrum) == 1

    def test_get_max_year_of_era(self) -> None:
        assert self.COPTIC_CALENDAR.get_max_year_of_era(Era.anno_martyrum) == self.COPTIC_CALENDAR.max_year


class TestCalendarSystemIds:
    @pytest.mark.parametrize("id_", _SUPPORTED_IDS)
    def test_valid_id(self, id_: str) -> None:
        assert isinstance(CalendarSystem.for_id(id_), CalendarSystem)

    @pytest.mark.parametrize("id_", _SUPPORTED_IDS)
    def test_ids_are_case_sensitive(self, id_: str) -> None:
        with pytest.raises(KeyError):
            assert CalendarSystem.for_id(id_.lower())

    def test_all_ids_give_different_calendars(self) -> None:
        assert len(set(_SUPPORTED_IDS)) == len(set(_SUPPORTED_CALENDARS))

    def test_bad_id(self) -> None:
        with pytest.raises(KeyError):
            CalendarSystem.for_id("bad")

    def test_no_substrings(self) -> None:
        for first_id in CalendarSystem.ids:
            for second_id in CalendarSystem.ids:
                # We're looking for firstId being a substring of secondId, which can only
                # happen if firstId is shorter...
                if len(first_id) >= len(second_id):
                    continue
                assert not second_id.startswith(first_id)

    # Ordinals are similar enough to IDs to keep the tests in this file too...

    @pytest.mark.parametrize("calendar", _SUPPORTED_CALENDARS, ids=lambda x: x.name)
    def test_for_ordinal_roundtrip(self, calendar: CalendarSystem) -> None:
        assert CalendarSystem._for_ordinal(calendar._ordinal) is calendar

    @pytest.mark.parametrize("calendar", _SUPPORTED_CALENDARS, ids=lambda x: x.name)
    def test_for_ordinal_uncached_roundtrip(self, calendar: CalendarSystem) -> None:
        assert CalendarSystem._for_ordinal_uncached(calendar._ordinal) is calendar

    def test_for_ordinal_uncached_invalid(self) -> None:
        # In noda time, they use:
        # `CalendarSystem.ForOrdinalUncached((CalendarOrdinal)9999))`
        with pytest.raises(RuntimeError):
            CalendarSystem._for_ordinal_uncached(9999)  # type: ignore
        with pytest.raises(RuntimeError):
            CalendarSystem._for_ordinal_uncached(_CalendarOrdinal.SIZE)


class TestCalendarSystemTestValidation:
    """Tests for validation of public methods on CalendarSystem.

    These typically use the ISO calendar, just for simplicity.
    """

    iso: Final[CalendarSystem] = CalendarSystem.iso

    @pytest.mark.parametrize("year", (-9998, 9999))
    def test_get_months_in_year_valid(self, year: int) -> None:
        helpers.assert_valid(self.iso.get_months_in_year, year)

    @pytest.mark.parametrize("year", (-9999, 10000))
    def test_get_months_in_year_invalid(self, year: int) -> None:
        helpers.assert_out_of_range(self.iso.get_months_in_year, year)

    @pytest.mark.parametrize(
        "year,month",
        [
            (-9998, 1),
            (9999, 12),
        ],
    )
    def test_get_days_in_month_valid(self, year: int, month: int) -> None:
        helpers.assert_valid(self.iso.get_days_in_month, year, month)

    @pytest.mark.parametrize(
        "year,month",
        [
            (-9999, 1),
            (1, 0),
            (1, 13),
            (10000, 1),
        ],
    )
    def test_get_days_in_month_invalid(self, year: int, month: int) -> None:
        helpers.assert_out_of_range(self.iso.get_days_in_month, year, month)

    def test_get_days_in_month_hebrew(self) -> None:
        helpers.assert_valid(CalendarSystem.hebrew_civil.get_days_in_month, 5402, 13)  # Leap year
        helpers.assert_out_of_range(CalendarSystem.hebrew_civil.get_days_in_month, 5401, 13)  # Not a leap year

    @pytest.mark.parametrize("year", (-9998, 9999))
    def test_is_leap_year_valid(self, year: int) -> None:
        helpers.assert_valid(self.iso.is_leap_year, year)

    @pytest.mark.parametrize("year", (-9999, 10000))
    def test_is_leap_year_invalid(self, year: int) -> None:
        helpers.assert_out_of_range(self.iso.is_leap_year, year)

    @pytest.mark.parametrize("year", (1, 9999))
    def test_get_absolute_year_valid_ce(self, year: int) -> None:
        helpers.assert_valid(self.iso.get_absolute_year, year, Era.common)

    @pytest.mark.parametrize("year", (1, 9999))
    def test_get_absolute_year_valid_bce(self, year: int) -> None:
        helpers.assert_valid(self.iso.get_absolute_year, year, Era.before_common)

    @pytest.mark.parametrize("year", (0, 10000))
    def test_get_absolute_year_invalid_ce(self, year: int) -> None:
        helpers.assert_out_of_range(self.iso.get_absolute_year, year, Era.common)

    @pytest.mark.parametrize("year", (0, 10000))
    def test_get_absolute_year_invalid_bce(self, year: int) -> None:
        helpers.assert_out_of_range(self.iso.get_absolute_year, year, Era.before_common)

    def test_get_absolute_year_invalid_era(self) -> None:
        helpers.assert_invalid(self.iso.get_absolute_year, 1, Era.anno_persico)

    def test_get_absolute_year_null_era(self) -> None:
        helpers.assert_argument_null(self.iso.get_absolute_year, 1, None)

    def test_get_min_year_of_era_null_era(self) -> None:
        helpers.assert_argument_null(self.iso.get_min_year_of_era, None)

    def test_get_min_year_of_era_invalid_era(self) -> None:
        helpers.assert_invalid(self.iso.get_min_year_of_era, Era.anno_persico)

    def test_get_max_year_of_era_null_era(self) -> None:
        helpers.assert_argument_null(self.iso.get_max_year_of_era, None)

    def test_get_max_year_of_era_invalid_era(self) -> None:
        helpers.assert_invalid(self.iso.get_max_year_of_era, Era.anno_persico)
