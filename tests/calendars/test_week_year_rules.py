import pytest

from pyoda_time import IsoDayOfWeek
from pyoda_time.calendars import WeekYearRules


class TestWeekYearRules:
    def test_unsupported_calendar_week_rule(self) -> None:
        with pytest.raises(ValueError):
            WeekYearRules.from_calendar_week_rule(1000, IsoDayOfWeek.MONDAY)  # type: ignore
