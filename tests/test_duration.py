# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
"""https://github.com/nodatime/nodatime/blob/main/src/NodaTime.Test/DurationTest.cs"""

from pyoda_time import Duration


class TestDuration:
    def test_default_initialiser(self) -> None:
        """Using the default constructor is equivalent to Duration.Zero."""
        actual = Duration()
        assert Duration.zero == actual
