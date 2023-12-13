import inspect

import pytest

from pyoda_time.calendars import Era, _EraMeta

ALL_ERAS = [getattr(Era, name) for name, member in inspect.getmembers(_EraMeta) if isinstance(member, property)]


class TestEra:
    # TODO: test_resource_presence(self, era: Era) -> None:

    @pytest.mark.parametrize("era", ALL_ERAS, ids=lambda x: x.name)
    def test_to_string_returns_name(self, era: Era) -> None:
        assert str(era) == era.name
