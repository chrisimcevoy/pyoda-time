# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
"""Tests to ensure that comparison operators are implemented consistently across the entire Pyoda Time package."""

import inspect
import pkgutil
from types import ModuleType
from typing import Any

import pytest

import pyoda_time
from pyoda_time import (
    AnnualDate,
    DateInterval,
    Duration,
    Instant,
    Interval,
    IsoDayOfWeek,
    LocalDate,
    LocalDateTime,
    LocalTime,
    Offset,
    OffsetDateTime,
    OffsetTime,
    Period,
    YearMonth,
)
from pyoda_time._calendar_ordinal import _CalendarOrdinal
from pyoda_time._compatibility._calendar_data import _IcuEnumCalendarsData
from pyoda_time._local_instant import _LocalInstant
from pyoda_time._year_month_day import _YearMonthDay
from pyoda_time._year_month_day_calendar import _YearMonthDayCalendar
from pyoda_time.time_zones import ZoneInterval
from pyoda_time.time_zones._fixed_date_time_zone import _FixedDateTimeZone
from pyoda_time.time_zones._transition import _Transition
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.cldr import MapZone

from .time_zones.test_standard_daylight_alternating_map import TEST_MAP as standard_daylight_alternating_map

VALUES = [
    AnnualDate(),
    DateInterval(LocalDate.min_iso_value, LocalDate.max_iso_value),
    Duration.zero,
    _FixedDateTimeZone(Offset.zero, None, None),
    Instant.max_value,
    Interval(),
    _LocalInstant.after_max_value(),
    _IcuEnumCalendarsData(),
    LocalDate.max_iso_value,
    LocalTime.max_value,
    LocalDate.max_iso_value + LocalTime.max_value,
    MapZone("windowsId", "territory", ["tzdbId1"]),
    Offset.zero,
    OffsetDateTime(LocalDateTime(), Offset.zero),
    OffsetTime(LocalTime.midnight, Offset.zero),
    Period.zero,
    standard_daylight_alternating_map,
    _Transition._ctor(Instant.max_value, Offset.zero),
    YearMonth(year=1, month=1),
    _YearMonthDay._ctor(raw_value=1),
    _YearMonthDayCalendar._ctor(year_month_day=1, calendar_ordinal=_CalendarOrdinal.BADI),
    ZoneInterval(name="", start=Instant.min_value, end=Instant.max_value, wall_offset=Offset.zero, savings=Offset.zero),
    _ZoneRecurrence(
        "name",
        Offset.zero,
        _ZoneYearOffset._ctor(_TransitionMode.UTC, 10, 31, int(IsoDayOfWeek.WEDNESDAY), True, LocalTime.midnight),
        1971,
        2009,
    ),
    _ZoneYearOffset._ctor(_TransitionMode.UTC, 1, 1, 1, True, LocalTime.midnight),
]


def find_classes(module: ModuleType) -> list[type]:
    """Return all classes defined in `module`."""
    return [cls for name, cls in inspect.getmembers(module, inspect.isclass) if cls.__module__ == module.__name__]


def get_package_classes(package: ModuleType) -> list[type]:
    """Return all classes defined in `package`."""
    classes = []
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix=package.__name__ + "."):
        # Import the module
        module = __import__(modname, fromlist="dummy")
        # Find and collect all classes from the module
        module_classes = find_classes(module)
        classes.extend(module_classes)
    return classes


def test_are_all_pyoda_time_classes_covered() -> None:
    """Test that all comparison operator implementations in Pyoda Time types are covered by the other tests in this
    module.

    First, we inspect all the types defined in the pyoda_time package which implement at least one comparison operator.

    Then we compare that collection to the VALUES list.

    There should be no difference between those two collections.
    """
    classes = get_package_classes(pyoda_time)
    comparison_operators = [
        "__eq__",
        "__ne__",
        "__gt__",
        "__ge__",
        "__lt__",
        "__le__",
    ]
    classes_which_define_comparison_operators = {
        cls.__name__ for cls in classes if any(op in cls.__dict__ for op in comparison_operators)
    }
    classes_covered_by_tests = {value.__class__.__name__ for value in VALUES}
    uncovered = sorted(classes_which_define_comparison_operators.difference(classes_covered_by_tests))
    assert not uncovered


def generate_test_param_id(test_param: Any) -> str:
    """Return the class name as a string."""
    return type(test_param).__name__


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_eq_is_false(value: Any) -> None:
    """Test that the == operator returns false when the given value is compared for equality to None."""
    assert (value == None) is False  # noqa: E711


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_ne_is_true(value: Any) -> None:
    """Test that the != operator returns True when the given value is compared for inequality to None."""
    assert (value != None) is True  # noqa: E711


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_gt_raises(value: Any) -> None:
    """Test that the > operator raises TypeError when the given value is compared to None."""
    with pytest.raises(TypeError) as e:
        value > None
    assert str(e.value) == f"'>' not supported between instances of '{type(value).__name__}' and 'NoneType'"


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_ge_raises(value: Any) -> None:
    """Test that the >= operator raises TypeError when the given value is compared to None."""
    with pytest.raises(TypeError) as e:
        value >= None
    assert str(e.value) == f"'>=' not supported between instances of '{type(value).__name__}' and 'NoneType'"


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_lt_raises(value: Any) -> None:
    """Test that the < operator raises TypeError when the given value is compared to None."""
    with pytest.raises(TypeError) as e:
        value < None
    assert str(e.value) == f"'<' not supported between instances of '{type(value).__name__}' and 'NoneType'"


@pytest.mark.parametrize("value", VALUES, ids=generate_test_param_id)
def test_le_raises(value: Any) -> None:
    """Test that the <= operator raises TypeError when the given value is compared to None."""
    with pytest.raises(TypeError) as e:
        value <= None
    assert str(e.value) == f"'<=' not supported between instances of '{type(value).__name__}' and 'NoneType'"
