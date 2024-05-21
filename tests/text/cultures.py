# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from typing import Callable, Iterable, Sequence

from pyoda_time._compatibility._culture_info import CultureInfo
from pyoda_time._compatibility._culture_types import CultureTypes
from pyoda_time._compatibility._date_time_format_info import DateTimeFormatInfo
from pyoda_time._compatibility._day_of_week import DayOfWeek


class _CulturesMeta(type):
    __awkward_am_pm_designator_culture: CultureInfo | None = None
    __awkward_day_of_week_culture: CultureInfo | None = None
    __genitive_name_test_culture: CultureInfo | None = None
    __genitive_name_test_culture_with_leading_names: CultureInfo | None = None

    @property
    def all_cultures(cls) -> Iterable[CultureInfo]:
        """Force the cultures to be read-only for tests, to take advantage of caching."""
        # In Pyoda Time, there is some special casing for cultures which
        # don't behave as expected on Mono and dotnet core.
        return [CultureInfo.read_only(culture) for culture in CultureInfo.get_cultures(CultureTypes.SPECIFIC_CULTURES)]

    @property
    def invariant(cls) -> CultureInfo:
        return CultureInfo.invariant_culture

    @property
    def en_us(self) -> CultureInfo:
        return CultureInfo.read_only(CultureInfo("en-US"))

    @property
    def fr_fr(self) -> CultureInfo:
        ci = CultureInfo("fr-FR")
        ci.date_time_format.long_date_pattern = "dddd d MMMM yyyy"
        ci.date_time_format.long_time_pattern = "HH:mm:ss"
        ci.date_time_format.short_date_pattern = "dd/MM/yyyy"
        ci.date_time_format.short_time_pattern = "HH:mm"
        ci.date_time_format.abbreviated_day_names = self.__lower_case_french(lambda dtf: dtf.abbreviated_day_names)
        ci.date_time_format.day_names = self.__lower_case_french(lambda dtf: dtf.day_names)
        ci.date_time_format.month_names = self.__lower_case_french(lambda dtf: dtf.month_names)
        ci.date_time_format.month_genitive_names = self.__lower_case_french(lambda dtf: dtf.month_genitive_names)
        return CultureInfo.read_only(ci)

    @property
    def fr_ca(self) -> CultureInfo:
        ci = CultureInfo("fr-CA")
        ci.date_time_format.long_date_pattern = "d MMMM yyyy"
        ci.date_time_format.long_time_pattern = "HH:mm:ss"
        ci.date_time_format.short_date_pattern = "yyyy-MM-dd"
        ci.date_time_format.short_time_pattern = "HH:mm"
        # Some flavours of Linux have a very odd setting here.
        ci.date_time_format.time_separator = ":"
        return CultureInfo.read_only(ci)

    @staticmethod
    def __lower_case_french(property_selector: Callable[[DateTimeFormatInfo], Iterable[str]]) -> list[str]:
        values: Iterable[str] = property_selector(CultureInfo("fr-FR").date_time_format)
        return [value.lower() for value in values]

    @property
    def dot_time_separator(self) -> CultureInfo:
        # We don't use this culture for anything other than hosting
        # the dot time separator, so it should be fine to cache it.
        ci: CultureInfo = CultureInfo("fi-FI")
        ci.date_time_format.time_separator = "."
        return CultureInfo.read_only(ci)

    @property
    def _awkward_am_pm_designator_culture(self) -> CultureInfo:
        if self.__awkward_am_pm_designator_culture is None:
            self.__awkward_am_pm_designator_culture = self.__create_awkward_am_pm_designator_culture()
        return self.__awkward_am_pm_designator_culture

    @classmethod
    def __create_awkward_am_pm_designator_culture(cls) -> CultureInfo:
        """Like the invariant culture, but Thursday is called "FooBa" (or "Foobaz" for short, despite being longer), and
        Friday is called "FooBar" (or "Foo" for short).

        This is expected to confuse our parser if we're not careful.
        """
        clone: CultureInfo = CultureInfo.invariant_culture.clone()
        date_format = clone.date_time_format
        date_format.am_designator = "Foo"
        date_format.pm_designator = "FooBar"
        return clone

    @property
    def _genitive_name_test_culture(cls) -> CultureInfo:
        if cls.__genitive_name_test_culture is None:
            cls.__genitive_name_test_culture = cls.__create_genitive_name_test_culture()
        return cls.__genitive_name_test_culture

    @classmethod
    def __create_genitive_name_test_culture(cls) -> CultureInfo:
        """.NET 3.5 doesn't contain any cultures where the abbreviated month names differ from the non-abbreviated month
        names.

        As we're testing under .NET 3.5, we'll need to create our own. This is just a clone of the invariant culture,
        with month 1 changed.
        """
        clone = CultureInfo.invariant_culture.clone()
        dtf: DateTimeFormatInfo = clone.date_time_format
        dtf.month_names = cls.__replace_first_element(dtf.month_names, "FullNonGenName")
        dtf.month_genitive_names = cls.__replace_first_element(dtf.month_genitive_names, "FullGenName")
        dtf.abbreviated_month_names = cls.__replace_first_element(dtf.abbreviated_month_names, "AbbrNonGenName")
        dtf.abbreviated_month_genitive_names = cls.__replace_first_element(
            dtf.abbreviated_month_genitive_names, "AbbrGenName"
        )
        # Note: Do *not* use CultureInfo.ReadOnly here, as it's broken in .NET 3.5 and lower; the month names
        # get reset to the original values, making the customization pointless :(
        return clone

    @property
    def _genitive_name_test_culture_with_leading_names(self) -> CultureInfo:
        if self.__genitive_name_test_culture_with_leading_names is None:
            self.__genitive_name_test_culture_with_leading_names = (
                self.__create_genitive_name_test_culture_with_leading_names()
            )
        return self.__genitive_name_test_culture_with_leading_names

    @classmethod
    def __create_genitive_name_test_culture_with_leading_names(cls) -> CultureInfo:
        clone = CultureInfo.invariant_culture.clone()
        dtf: DateTimeFormatInfo = clone.date_time_format
        dtf.month_names = cls.__replace_first_element(dtf.month_names, "MonthName")
        dtf.month_genitive_names = cls.__replace_first_element(dtf.month_genitive_names, "MonthName-Genitive")
        dtf.abbreviated_month_names = cls.__replace_first_element(dtf.abbreviated_month_names, "MN")
        dtf.abbreviated_month_genitive_names = cls.__replace_first_element(
            dtf.abbreviated_month_genitive_names, "MN-Gen"
        )
        # Note: Do *not* use CultureInfo.ReadOnly here, as it's broken in .NET 3.5 and lower; the month names
        # get reset to the original values, making the customization pointless :(
        return clone

    @classmethod
    def __replace_first_element(cls, elements: Sequence[str], new_element: str) -> Sequence[str]:
        # Cloning so we don't accidentally *really* change any read-only cultures, to work around a bug in Mono.
        clone = list(elements)
        clone[0] = new_element
        return clone

    @property
    def _awkward_day_of_week_culture(self) -> CultureInfo:
        if self.__awkward_day_of_week_culture is None:
            self.__awkward_day_of_week_culture = self.__create_awkward_day_of_week_culture()
        return self.__awkward_day_of_week_culture

    def __create_awkward_day_of_week_culture(cls) -> CultureInfo:
        """Like the invariant culture, but Thursday is called "FooBa" (or "Foobaz" for short, despite being longer), and
        Friday is called "FooBar" (or "Foo" for short).

        This is expected to confuse our parser if we're not careful.
        """
        clone = CultureInfo.invariant_culture.clone()
        dtf: DateTimeFormatInfo = clone.date_time_format
        long_day_names = dtf.day_names
        short_day_names = dtf.abbreviated_day_names
        long_day_names[int(DayOfWeek.Thursday)] = "FooBa"
        short_day_names[int(DayOfWeek.Thursday)] = "FooBaz"
        long_day_names[int(DayOfWeek.Friday)] = "FooBar"
        short_day_names[int(DayOfWeek.Friday)] = "Foo"
        dtf.day_names = long_day_names
        dtf.abbreviated_day_names = short_day_names
        return clone


class Cultures(metaclass=_CulturesMeta):
    """Cultures to use from various tests."""
