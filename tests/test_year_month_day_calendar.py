from pyoda_time import _CalendarOrdinal, _YearMonthDayCalendar


class TestYearMonthDayCalendar:
    def test_all_years(self) -> None:
        for year in range(-9_999, 10_000):
            ymdc = _YearMonthDayCalendar._ctor(year=year, month=5, day=20, calendar_ordinal=_CalendarOrdinal(0))
            assert ymdc._year == year
            assert ymdc._month == 5
            assert ymdc._day == 20
            assert _CalendarOrdinal.ISO == ymdc._calendar_ordinal

    def test_all_months(self) -> None:
        for month in range(1, 33):
            ymdc = _YearMonthDayCalendar._ctor(
                year=-123, month=month, day=20, calendar_ordinal=_CalendarOrdinal.HEBREW_CIVIL
            )
            assert ymdc._year == -123
            assert ymdc._month == month
            assert ymdc._day == 20
            assert _CalendarOrdinal.HEBREW_CIVIL == ymdc._calendar_ordinal

    def test_all_days(self) -> None:
        for day in range(1, 65):
            ymdc = _YearMonthDayCalendar._ctor(
                year=-123, month=12, day=day, calendar_ordinal=_CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15
            )
            assert ymdc._year == -123
            assert ymdc._month == 12
            assert ymdc._day == day
            assert ymdc._calendar_ordinal == _CalendarOrdinal.ISLAMIC_ASTRONOMICAL_BASE15

    def test_all_calendars(self) -> None:
        # TODO: In C# this test casts integers to CalendarOrdinal which are outisde the range of the enum - why??
        for calendar in _CalendarOrdinal:
            ymdc = _YearMonthDayCalendar._ctor(year=-123, month=30, day=64, calendar_ordinal=calendar)
            assert ymdc._year == -123
            assert ymdc._month == 30
            assert ymdc._day == 64
            assert ymdc._calendar_ordinal == calendar
