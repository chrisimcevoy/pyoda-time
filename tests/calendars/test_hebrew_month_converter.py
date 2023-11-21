import pytest

from pyoda_time.calendars import _HebrewMonthConverter


class TestHebrewMonthConverter:
    SAMPLE_LEAP_YEAR = 5502
    SAMPLE_NON_LEAP_YEAR = 5501

    @pytest.mark.parametrize(
        "scriptural,civil",
        [
            (1, 7),  # Nisan
            (2, 8),  # Iyyar
            (3, 9),  # Sivan
            (4, 10),  # Tammuz
            (5, 11),  # Av
            (6, 12),  # Elul
            (7, 1),  # Tishri
            (8, 2),  # Heshvan
            (9, 3),  # Kislev
            (10, 4),  # Teveth
            (11, 5),  # Shevat
            (12, 6),  # Adar
        ],
    )
    def test_non_leap_year(self, scriptural: int, civil: int) -> None:
        assert _HebrewMonthConverter._civil_to_scriptural(self.SAMPLE_NON_LEAP_YEAR, civil) == scriptural
        assert _HebrewMonthConverter._scriptural_to_civil(self.SAMPLE_NON_LEAP_YEAR, scriptural) == civil

    @pytest.mark.parametrize(
        "scriptural,civil",
        [
            (1, 8),  # Nisan
            (2, 9),  # Iyyar
            (3, 10),  # Sivan
            (4, 11),  # Tammuz
            (5, 12),  # Av
            (6, 13),  # Elul
            (7, 1),  # Tishri
            (8, 2),  # Heshvan
            (9, 3),  # Kislev
            (10, 4),  # Teveth
            (11, 5),  # Shevat
            (12, 6),  # Adar I
            (13, 7),  # Adar II
        ],
    )
    def test_leap_year(self, scriptural: int, civil: int) -> None:
        assert _HebrewMonthConverter._civil_to_scriptural(self.SAMPLE_LEAP_YEAR, civil) == scriptural
        assert _HebrewMonthConverter._scriptural_to_civil(self.SAMPLE_LEAP_YEAR, scriptural) == civil
