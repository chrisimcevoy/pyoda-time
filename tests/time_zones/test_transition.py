# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from pyoda_time import Instant, Offset
from pyoda_time.time_zones._transition import _Transition

from .. import helpers


class TestTransition:
    def test_equality(self) -> None:
        equal_1 = _Transition._ctor(Instant.from_unix_time_seconds(100), Offset.from_hours(1))
        equal_2 = _Transition._ctor(Instant.from_unix_time_seconds(100), Offset.from_hours(1))
        unequal_1 = _Transition._ctor(Instant.from_unix_time_seconds(101), Offset.from_hours(1))
        unequal_2 = _Transition._ctor(Instant.from_unix_time_seconds(100), Offset.from_hours(2))

        helpers.test_equals_struct(equal_1, equal_2, unequal_1)
        helpers.test_equals_struct(equal_1, equal_2, unequal_2)
        helpers.test_operator_equality(equal_1, equal_2, unequal_1)
        helpers.test_operator_equality(equal_1, equal_2, unequal_2)

    def test_transition_to_string(self) -> None:
        transition = _Transition._ctor(Instant.from_utc(2017, 8, 25, 15, 26, 30), Offset.from_hours(1))
        assert str(transition) == "Transition to +01 at 2017-08-25T15:26:30Z"
