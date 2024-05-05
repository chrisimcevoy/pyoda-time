# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from pyoda_time import LocalDateTime


class TestLocalDateTime:
    def test_default_constructor(self) -> None:
        """Using the default constructor is equivalent to January 1st 1970, midnight, UTC, ISO calendar."""
        actual = LocalDateTime()
        assert actual == LocalDateTime(1, 1, 1, 0, 0)
