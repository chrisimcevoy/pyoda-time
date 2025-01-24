# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import CalendarSystem, DateAdjusters, LocalDate, LocalTime, Offset, OffsetDate

from . import helpers
from .test_offset_time import get_class_properties


class TestOffsetDate:
    @pytest.mark.parametrize(
        "property_name", [name for name in get_class_properties(OffsetDate) if name in get_class_properties(LocalDate)]
    )
    def test_local_date_properties(self, property_name: str) -> None:
        local = LocalDate(2012, 6, 19, CalendarSystem.julian)
        offset = Offset.from_hours(5)

        od = OffsetDate(local, offset)

        actual = getattr(od, property_name)
        expected = getattr(local, property_name)

        assert actual == expected

    def test_component_properties(self) -> None:
        date = LocalDate(2012, 6, 19, CalendarSystem.julian)
        offset = Offset.from_hours(5)

        offset_date = OffsetDate(date, offset)
        assert offset_date.offset == offset
        assert offset_date.date == date

    def test_equality(self) -> None:
        date1 = LocalDate(2012, 10, 6)
        date2 = LocalDate(2012, 9, 5)
        offset1 = Offset.from_hours(1)
        offset2 = Offset.from_hours(2)

        equal1 = OffsetDate(date1, offset1)
        equal2 = OffsetDate(date1, offset1)
        unequal_by_offset = OffsetDate(date1, offset2)
        unequal_by_local = OffsetDate(date2, offset1)

        helpers.test_equals_struct(equal1, equal2, unequal_by_offset)
        helpers.test_equals_struct(equal1, equal2, unequal_by_local)

        helpers.test_operator_equality(equal1, equal2, unequal_by_offset)
        helpers.test_operator_equality(equal1, equal2, unequal_by_local)

    def test_at(self) -> None:
        date = LocalDate(2012, 6, 19, CalendarSystem.julian)
        offset = Offset.from_hours(5)
        time = LocalTime(14, 15, 12).plus_nanoseconds(123456789)

        assert date.at(time).with_offset(offset) == OffsetDate(date, offset).at(time)

    def test_with_offset(self) -> None:
        date = LocalDate(2012, 6, 19)
        initial = OffsetDate(date, Offset.from_hours(2))
        actual = initial.with_offset(Offset.from_hours(5))
        expected = OffsetDate(date, Offset.from_hours(5))
        assert actual == expected

    def test_with_calendar(self) -> None:
        julian_date = LocalDate(2012, 6, 19, CalendarSystem.julian)
        iso_date = julian_date.with_calendar(CalendarSystem.iso)
        offset = Offset.from_hours(5)
        actual = OffsetDate(julian_date, offset).with_calendar(CalendarSystem.iso)
        expected = OffsetDate(iso_date, offset)
        assert actual == expected

    def test_with_adjuster(self) -> None:
        initial = OffsetDate(LocalDate(2016, 6, 19), Offset.from_hours(-5))
        actual = initial.with_(DateAdjusters.start_of_month)
        expected = OffsetDate(LocalDate(2016, 6, 1), Offset.from_hours(-5))
        assert actual == expected

    @pytest.mark.xfail(reason="requires OffsetDatePattern")
    def test_to_string_with_format(self) -> None:
        date = LocalDate(2012, 10, 6)
        offset = Offset.from_hours(1)
        offset_date = OffsetDate(date, offset)
        assert f"{offset_date}:uuuu/MM/dd o<-HH>" == "2012/10/06 01"

    # TODO: def test_to_string_with_null_format(self) -> None:
    # TODO: def test_to_string_no_format(self) -> None:

    @pytest.mark.xfail(reason="Deconstruct not implemented")
    def test_deconstruction(self) -> None:
        date = LocalDate(2015, 3, 28)
        offset = Offset.from_hours(-2)
        offset_date = OffsetDate(date, offset)

        actual_date, actual_offset = offset_date  # type: ignore[misc]

        assert actual_date == date  # type: ignore[has-type]
        assert actual_offset == offset  # type: ignore[has-type]

    # TODO: test_xml_serialization_iso() -> None:
    # TODO: test_xml_serialization_bce() -> None:
    # TODO: test_xml_serialization_non_iso() -> None:
