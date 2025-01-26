# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import inspect
from collections.abc import Iterable

import pytest

from pyoda_time import CalendarSystem, LocalDate, LocalTime, Offset, OffsetTime, TimeAdjusters

from . import helpers


def get_class_properties(cls: type) -> Iterable[str]:
    """Return the names of all properties of a class."""
    return [name for name, _ in inspect.getmembers(cls, lambda o: isinstance(o, property))]


class TestOffsetTime:
    @pytest.mark.parametrize(
        "property_name", [name for name in get_class_properties(OffsetTime) if name in get_class_properties(LocalTime)]
    )
    def test_local_time_properties(self, property_name: str) -> None:
        local = LocalTime(5, 23, 45).plus_nanoseconds(987654321)
        offset = Offset.from_hours(5)

        od = OffsetTime(local, offset)

        actual = getattr(od, property_name)
        expected = getattr(local, property_name)

        assert actual == expected

    def test_component_properties(self) -> None:
        time = LocalTime(12, 34, 15)
        offset = Offset.from_hours(5)

        offset_time = OffsetTime(time, offset)

        assert offset_time.offset == offset
        assert offset_time.time_of_day == time

    def test_equality(self) -> None:
        time_1 = LocalTime(4, 56, 23, 123)
        time_2 = LocalTime(6, 23, 12, 987)
        offset_1 = Offset.from_hours(1)
        offset_2 = Offset.from_hours(2)

        equal_1 = OffsetTime(time_1, offset_1)
        equal_2 = OffsetTime(time_1, offset_1)
        unequal_by_offset = OffsetTime(time_1, offset_2)
        unequal_by_local = OffsetTime(time_2, offset_1)

        helpers.test_equals_struct(equal_1, equal_2, unequal_by_offset)
        helpers.test_equals_struct(equal_1, equal_2, unequal_by_local)

        helpers.test_operator_equality(equal_1, equal_2, unequal_by_offset)
        helpers.test_operator_equality(equal_1, equal_2, unequal_by_local)

    def test_on(self) -> None:
        time = LocalTime(14, 15, 12).plus_nanoseconds(123456789)
        date = LocalDate(2012, 6, 19, CalendarSystem.julian)
        offset = Offset.from_hours(5)

        assert time.on(date).with_offset(offset) == OffsetTime(time, offset).on(date)

    def test_with_offset(self) -> None:
        time = LocalTime(14, 15, 12).plus_nanoseconds(123456789)
        initial = OffsetTime(time, Offset.from_hours(2))
        actual = initial.with_offset(Offset.from_hours(5))
        expected = OffsetTime(time, Offset.from_hours(5))
        assert actual == expected

    def test_with_adjuster(self) -> None:
        initial = OffsetTime(LocalTime(14, 15, 12), Offset.from_hours(-5))
        actual = initial.with_time_adjuster(TimeAdjusters.truncate_to_hour)
        expected = OffsetTime(LocalTime(14), Offset.from_hours(-5))
        assert actual == expected

    # TODO: [requires OffsetTimePattern
    #  def test_to_string_with_format(self) -> None:
    #  def test_to_string_with_null_format(self) -> None:
    #  def test_to_string_no_format(self) -> None:

    # TODO:  def test_deconstruction(self) -> None:
