# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time import LocalTime, TimeAdjusters


class TestTimeAdjusters:
    def test_truncate_to_second(self) -> None:
        start = LocalTime.from_hour_minute_second_millisecond_tick(7, 4, 30, 123, 4567)
        end = LocalTime(7, 4, 30)
        assert TimeAdjusters.truncate_to_second(start) == end

    def test_truncate_to_minute(self) -> None:
        start = LocalTime.from_hour_minute_second_millisecond_tick(7, 4, 30, 123, 4567)
        end = LocalTime(7, 4, 0)
        assert TimeAdjusters.truncate_to_minute(start) == end

    def test_truncate_to_hour(self) -> None:
        start = LocalTime.from_hour_minute_second_millisecond_tick(7, 4, 30, 123, 4567)
        end = LocalTime(7, 0, 0)
        assert TimeAdjusters.truncate_to_hour(start) == end
