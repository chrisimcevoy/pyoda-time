import pytest

from pyoda_time import CalendarSystem, LocalDate


class TestPersianCalendarSystem:
    # TODO: test_bcl_through_history(self): [requires bcl]

    @pytest.mark.parametrize(
        "persian_year,gregorian_year,gregorian_day_of_march",
        [
            (1016, 1637, 21),
            (1049, 1670, 21),
            (1078, 1699, 21),
            (1082, 1703, 22),
            (1111, 1732, 21),
            (1115, 1736, 21),
            (1144, 1765, 21),
            (1177, 1798, 21),
            (1210, 1831, 22),
            (1243, 1864, 21),
            (1404, 2025, 20),
            (1437, 2058, 20),
            (1532, 2153, 20),
            (1565, 2186, 20),
            (1569, 2190, 20),
            (1598, 2219, 21),
            (1631, 2252, 20),
            (1660, 2281, 20),
            (1664, 2285, 20),
            (1693, 2314, 21),
            (1697, 2318, 21),
            (1726, 2347, 21),
            (1730, 2351, 21),
            (1759, 2380, 20),
            (1763, 2384, 20),
            (1788, 2409, 20),
            (1792, 2413, 20),
            (1796, 2417, 20),
        ],
    )
    def test_arithmetic_examples(self, persian_year: int, gregorian_year: int, gregorian_day_of_march: int) -> None:
        persian = LocalDate(year=persian_year, month=1, day=1, calendar=CalendarSystem.persian_arithmetic)
        gregorian = persian.with_calendar(CalendarSystem.gregorian)
        assert gregorian.year == gregorian_year
        assert gregorian.month == 3
        assert gregorian.day == gregorian_day_of_march

    # TODO: def test_generate_data(self): [requires bcl]
