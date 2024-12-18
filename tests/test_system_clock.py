# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from datetime import UTC, datetime
from random import Random
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from pyoda_time import Duration, Instant, PyodaConstants, SystemClock
from pyoda_time.utility._csharp_compatibility import _to_ticks


@patch("pyoda_time._system_clock.time")
def test_get_current_instant(mock_time: MagicMock) -> None:
    random: Random = Random(str(uuid4()))
    nanoseconds = random.randint(0, (Instant.max_value - PyodaConstants.UNIX_EPOCH).to_nanoseconds())
    mock_time.time_ns.return_value = nanoseconds

    current_instant = SystemClock.instance.get_current_instant()

    assert (current_instant - PyodaConstants.UNIX_EPOCH).to_nanoseconds() == nanoseconds
    mock_time.time_ns.assert_called_once_with()


def test_construction_raises() -> None:
    with pytest.raises(TypeError) as e:
        SystemClock()
    assert str(e.value) == "SystemClock is not intended to be initialised directly."


class TestSystemClock:
    def test_instance_now(self) -> None:
        stdlib_now_ticks = _to_ticks(datetime.now(tz=UTC))
        pyoda_ticks = SystemClock.instance.get_current_instant().to_unix_time_ticks()
        assert (pyoda_ticks - stdlib_now_ticks) < Duration.from_seconds(1).bcl_compatible_ticks

    def test_sanity(self) -> None:
        minimum_expected = Instant.from_utc(2019, 8, 1, 0, 0)
        maximum_expected = Instant.from_utc(2025, 1, 1, 0, 0)
        now = SystemClock.instance.get_current_instant()
        assert minimum_expected.to_unix_time_ticks() < now.to_unix_time_ticks() < maximum_expected.to_unix_time_ticks()
