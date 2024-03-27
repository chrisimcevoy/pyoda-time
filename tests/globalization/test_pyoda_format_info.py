# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Final

import pytest

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._date_time_format_info import DateTimeFormatInfo
from pyoda_time.calendars import Era
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo

from ..culture_saver import CultureSaver
from ..globalization.failing_culture_info import FailingCultureInfo
from ..text.cultures import Cultures

EN_US: Final[CultureInfo] = CultureInfo.get_culture_info("en-US")
EN_GB: Final[CultureInfo] = CultureInfo.get_culture_info("en-GB")


class TestPyodaFormatInfo:
    @pytest.mark.parametrize(
        "culture", sorted(Cultures.all_cultures, key=lambda c: str(c)), ids=lambda culture: f"{culture=}"
    )
    def test_convert_culture(self, culture: CultureInfo) -> None:
        """Just check we can actually build a NodaFormatInfo for every culture, outside text-specific tests."""
        _PyodaFormatInfo._get_format_info(culture)

    def test_caching_with_read_only(self) -> None:
        original = CultureInfo("en-US")
        # Use a read-only wrapper so that it gets cached
        wrapper = CultureInfo.read_only(original)

        pyoda_wrapper_1 = _PyodaFormatInfo._get_format_info(wrapper)
        pyoda_wrapper_2 = _PyodaFormatInfo._get_format_info(wrapper)
        assert pyoda_wrapper_1 is pyoda_wrapper_2

    def test_caching_with_cloned_culture(self) -> None:
        original = CultureInfo("en-US")
        clone = original.clone()
        assert original._name == clone._name
        day_names = clone.date_time_format.day_names
        day_names[1] = "@@@"
        clone.date_time_format.day_names = day_names

        # Fool Pyoda Time into believing both are read-only, so it can use a cache...
        original = CultureInfo.read_only(original)
        clone = CultureInfo.read_only(clone)

        pyoda_original = _PyodaFormatInfo._get_format_info(original)
        pyoda_clone = _PyodaFormatInfo._get_format_info(clone)
        assert original.date_time_format.day_names[1] == pyoda_original.long_day_names[1] == "Monday"
        assert clone.date_time_format.day_names[1] == pyoda_clone.long_day_names[1] == "@@@"
        # Just check we made a difference...
        assert pyoda_original.long_day_names[1] != pyoda_clone.long_day_names[1]

    def test_constructor(self) -> None:
        info = _PyodaFormatInfo(EN_US)
        assert EN_US is info.culture_info
        assert info.date_time_format is not None
        assert info.time_separator == ":"
        assert info.date_separator == "/"
        assert isinstance(info.offset_pattern_long, str)
        assert isinstance(info.offset_pattern_medium, str)
        assert isinstance(info.offset_pattern_short, str)
        assert str(info) == "PyodaFormatInfo[en-US]"

    def test_constructor_null(self) -> None:
        with pytest.raises(TypeError):
            _PyodaFormatInfo(None)  # type: ignore

    def test_date_time_format(self) -> None:
        date_time_format = DateTimeFormatInfo.invariant_info
        info = _PyodaFormatInfo(EN_US)
        assert info.date_time_format != date_time_format

    def test_get_format_info(self) -> None:
        _PyodaFormatInfo._clear_cache()
        info_1 = _PyodaFormatInfo._get_format_info(EN_US)
        assert info_1 is not None

        info_2 = _PyodaFormatInfo._get_format_info(EN_US)
        assert info_1 is info_2

        info_3 = _PyodaFormatInfo._get_format_info(EN_GB)
        assert info_1 is not info_3

    def test_get_format_info_null(self) -> None:
        _PyodaFormatInfo._clear_cache()
        with pytest.raises(TypeError):
            _PyodaFormatInfo._get_format_info(None)  # type: ignore

    def test_get_instance_culture_info(self) -> None:
        _PyodaFormatInfo._clear_cache()
        with CultureSaver.set_cultures(EN_US, FailingCultureInfo.instance):
            actual = _PyodaFormatInfo.get_instance(EN_GB)
            assert actual.culture_info is EN_GB

    def test_get_instance_unusable_type(self) -> None:
        _PyodaFormatInfo._clear_cache()
        with pytest.raises(ValueError) as e:
            _PyodaFormatInfo.get_instance(CultureInfo.invariant_culture.number_format)
        assert str(e.value) == "Cannot use provider of type NumberFormatInfo in Pyoda Time"

    def test_get_instance_date_time_format_info(self) -> None:
        _PyodaFormatInfo._clear_cache()
        with CultureSaver.set_cultures(EN_US, FailingCultureInfo.instance):
            info = _PyodaFormatInfo.get_instance(EN_GB.date_time_format)
            assert info.date_time_format == EN_GB.date_time_format
            assert info.culture_info == CultureInfo.invariant_culture

    def test_get_instance_null(self) -> None:
        _PyodaFormatInfo._clear_cache()
        with CultureSaver.set_cultures(EN_US, FailingCultureInfo.instance):
            info = _PyodaFormatInfo.get_instance(None)
            assert info.culture_info == CultureInfo.current_culture == EN_US
        with CultureSaver.set_cultures(EN_GB, FailingCultureInfo.instance):
            info = _PyodaFormatInfo.get_instance(None)
            assert info.culture_info == CultureInfo.current_culture == EN_GB

    def test_offset_pattern_long(self) -> None:
        pattern = "This is a test"
        info = _PyodaFormatInfo(EN_US)
        assert info.offset_pattern_long != pattern

    def test_offset_pattern_medium(self) -> None:
        pattern = "This is a test"
        info = _PyodaFormatInfo(EN_US)
        assert info.offset_pattern_medium != pattern

    def test_offset_pattern_short(self) -> None:
        pattern = "This is a test"
        info = _PyodaFormatInfo(EN_US)
        assert info.offset_pattern_short != pattern

    def test_get_era_names(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        names = info.get_era_names(Era.before_common)
        assert names == ["B.C.E.", "B.C.", "BCE", "BC"]

    def test_get_era_names_no_such_era(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        names = info.get_era_names(Era._ctor("Ignored", "NonExistentResource"))
        assert len(names) == 0

    def test_get_era_names_null(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        with pytest.raises(TypeError):
            info.get_era_names(None)  # type: ignore

    def test_get_era_primary_name(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        assert info.get_era_primary_name(Era.before_common) == "B.C."

    def test_get_era_primary_name_no_such_era(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        assert info.get_era_primary_name(Era._ctor("Ignored", "NonExistentResource")) == ""

    def test_era_get_primary_name_null(self) -> None:
        info = _PyodaFormatInfo._get_format_info(EN_US)
        with pytest.raises(TypeError):
            info.get_era_primary_name(None)  # type: ignore

    def test_integer_genitive_month_names(self) -> None:
        # Emulate behaviour of Mono 3.0.6
        culture: CultureInfo = CultureInfo.invariant_culture.clone()
        culture.date_time_format.month_genitive_names = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]
        culture.date_time_format.abbreviated_month_genitive_names = [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
        ]
        info = _PyodaFormatInfo._get_format_info(culture)
        assert info.long_month_names == info.long_month_genitive_names
        assert info.short_month_names == info.short_month_genitive_names
