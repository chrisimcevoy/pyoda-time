import inspect
from typing import Final

import pytest

from pyoda_time import CalendarSystem, LocalDate


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


class TestCalendarSystem:
    __SUPPORTED_IDS: Final[list[str]] = list(CalendarSystem.ids())
    __SUPPORTED_CALENDARS: Final[list[CalendarSystem]] = [CalendarSystem.for_id(id_) for id_ in __SUPPORTED_IDS]

    @pytest.mark.parametrize("calendar", __SUPPORTED_CALENDARS)
    def test_max_date(self, calendar: CalendarSystem) -> None:
        self.__validate_properties(calendar, calendar._max_days, calendar.max_year)

    @pytest.mark.parametrize("calendar", __SUPPORTED_CALENDARS)
    def test_min_date(self, calendar: CalendarSystem) -> None:
        self.__validate_properties(calendar, calendar._min_days, calendar.min_year)

    def __validate_properties(self, calendar: CalendarSystem, days_since_epoch: int, expected_year: int) -> None:
        local_date = LocalDate._ctor(days_since_epoch=days_since_epoch, calendar=calendar)
        assert local_date.year == expected_year

        for name, prop in inspect.getmembers(LocalDate, lambda p: isinstance(p, property)):
            _ = getattr(local_date, name) is None
