"""This module ports various helper classes from NodaTime.Test into Python.

Originally, these helpers are contained within classes like `TestHelpers`
and `TestObjects`. To prevent accidental triggering of pytest's test
discovery, which could happen with direct porting of these class names
due to their 'Test' prefixes, the helpers are implemented here as
module-level functions.
"""


from typing import Any, Iterable, Protocol, Self, TypeVar

import pytest

from pyoda_time import SECONDS_PER_HOUR, SECONDS_PER_MINUTE, Offset
from pyoda_time.utility import _Preconditions


class IEquatable(Protocol):
    def equals(self, other: Any) -> bool:
        ...


class IComparable(Protocol):
    def compare_to(self, other: Self) -> int:
        ...


class SupportsComparison(Protocol):
    def __gt__(self, other: Any) -> bool:
        ...

    def __ge__(self, other: Any) -> bool:
        ...

    def __lt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...


T = TypeVar("T")
T_IComparable = TypeVar("T_IComparable", bound=IComparable)
T_IEquatable = TypeVar("T_IEquatable", bound=IEquatable)
T_SupportsComparison = TypeVar("T_SupportsComparison", bound=SupportsComparison)


def _validate_input(value: T, equal_value: T, unequal_values: T | Iterable[T], unequal_name: str) -> None:
    assert value is not None, "Value cannot be null"
    assert equal_value is not None, "equal_value cannot be null"
    assert value is not equal_value, "value and equal_value MUST be different objects"
    if not isinstance(unequal_values, Iterable):
        unequal_values = [unequal_values]
    for unequal_value in unequal_values:
        assert unequal_value is not None, f"{unequal_name} cannot be null"
        assert unequal_value is not value, f"{unequal_name} and value MUST be different objects"


def test_equals(value: T_IEquatable, equal_value: T_IEquatable, *unequal_values: T_IEquatable) -> None:
    """A combination of ``TestHelpers.TestEqualsStruct`` and ``TestHelpers.TestObjectEquals`` from Noda Time.

    In Pyoda Time we don't have structs, so we don't need separate helpers for "value types".

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param unequal_values: The value not equal to the base value.
    """
    _validate_input(value, equal_value, unequal_values, "unequal_value")
    assert value is not None
    assert value.equals(value)
    assert value.equals(equal_value)
    assert equal_value.equals(value)
    for unequal_value in unequal_values:
        assert not value.equals(unequal_value)
    assert hash(value) == hash(value)
    assert hash(value) == hash(equal_value)


def test_compare_to(value: T_IComparable, equal_value: T_IComparable, *greater_values: T_IComparable) -> None:
    """A combination of ``TestHelpers.TestCompareToStruct()`` and ``TestHelpers.TestNonGenericCompareTo()`` from Noda
    Time.

    In Python, we don't need a separate helper method for structs.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param greater_values: The values greater than the base value, in ascending order.
    """
    _validate_input(value, equal_value, greater_values, "greater_values")
    assert value.compare_to(value) == 0
    assert value.compare_to(equal_value) == 0
    assert equal_value.compare_to(value) == 0
    for greater_value in greater_values:
        assert value.compare_to(greater_value) < 0
        assert greater_value.compare_to(value) > 0
        # Now move up to the next pair...
        value = greater_value
    # In Noda Time, they expect an ArgumentException to be raised when comparing incompatible types:
    # `Assert.Throws<ArgumentException>(() => value2.CompareTo(new object()));`
    # In Python, TypeError is more idiomatic.
    with pytest.raises(TypeError):
        value.compare_to(object())  # type: ignore


def test_operator_equality(value: T, equal_value: T, unequal_value: T) -> None:
    """Tests the equality and inequality operators (==, !=) if they exist on the object.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param unequal_value: The value not equal to the base value.
    """
    _validate_input(value, equal_value, unequal_value, "unequal_value")
    # TODO: no reflection here, or differentiation between struct/class
    assert not value == None, "value == None"  # noqa: E711
    assert not None == value, "None == value"  # noqa: E711
    assert value == value, "value == value"
    assert value == equal_value, "value == equal_value"
    assert equal_value == value, "equal_value == value"

    assert value != unequal_value, "value == unequal_value"
    assert value != None, "value != None"  # noqa: E711
    assert None != value, "None != value"  # noqa: E711
    assert not value != value, "value != value"
    assert not value != equal_value, "value != equal_value"
    assert not equal_value != value, "equal_value != value"
    assert value != unequal_value, "value != unequal_value"


def test_operator_comparison(
    value: T_SupportsComparison, equal_value: T_SupportsComparison, *greater_values: T_SupportsComparison
) -> None:
    """Tests the less than (<) and greater than (>) operators if they exist on the object.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param greater_values: The values greater than the base value, in ascending order.
    :return:
    """
    _validate_input(value, equal_value, greater_values, "greater_value")

    # TODO: no reflection here, or differentiation between struct/class

    # Comparisons only involving equal values

    assert value > None, "value > None"
    assert not None > value, "None > value"
    assert not value > value, "value > value"
    assert not value > equal_value, "value > equal_value"
    assert not equal_value > value, "equal_value > value"

    assert not value < None, "value < None"
    assert None < value, "None < value"
    assert not value < value, "value < value"
    assert not value < equal_value, "value < equal_value"
    assert not equal_value < value, "equal_value < value"

    # Then comparisons involving the greater values

    for greater_value in greater_values:
        assert not value > greater_value, "value > greater_value"
        assert greater_value > value, "greater_value > value"
        assert value < greater_value, "value < greater_value"
        assert not greater_value < value, "greater_value < value"
        # Now move up to the next pair...
        value = greater_value


def test_operator_comparison_equality(
    value: T_SupportsComparison, equal_value: T_SupportsComparison, *greater_values: T_SupportsComparison
) -> None:
    """Tests the equality (==), inequality (!=), less than (<), greater than (>), less than or equals (<=), and greater
    than or equals (>=) operators if they exist on the object.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param greater_values: The values greater than the base value, in ascending order.
    """
    for greater_value in greater_values:
        test_operator_equality(value, equal_value, greater_value)
    test_operator_comparison(value, equal_value, *greater_values)
    # TODO: no reflection or differentiation between type and struct here

    # First the comparisons with equal values
    assert value >= None
    assert not None >= value
    assert value >= value
    assert value >= equal_value
    assert equal_value >= value

    assert not value <= None
    assert None <= value
    assert value <= value
    assert value <= equal_value
    assert equal_value <= value

    # Now the "greater than" values
    for greater_value in greater_values:
        assert not value >= greater_value
        assert greater_value >= value
        assert value <= greater_value
        assert not greater_value <= value
        # Now move up to the next pair...
        value = greater_value


def create_positive_offset(hours: int, minutes: int, seconds: int) -> Offset:
    """Creates a positive offset from the given values.

    :param hours: The number of hours, in the range [0, 24).
    :param minutes: The number of minutes, in the range [0, 60).
    :param seconds: The number of seconds, in the range [0, 60).
    :return: A new ``Offset`` representing the given values.
    :exception ValueError: The result of the operation is outside the range of Offset.
    """
    _Preconditions._check_argument_range("hours", hours, 0, 23)
    _Preconditions._check_argument_range("minutes", minutes, 0, 59)
    _Preconditions._check_argument_range("seconds", seconds, 0, 59)
    seconds += minutes * SECONDS_PER_MINUTE
    seconds += hours * SECONDS_PER_HOUR
    return Offset.from_seconds(seconds)


def create_negative_offset(hours: int, minutes: int, seconds: int) -> Offset:
    """Creates a negative offset from the given values.

    :param hours: The number of hours, in the range [0, 24).
    :param minutes: The number of minutes, in the range [0, 60).
    :param seconds: The number of seconds, in the range [0, 60).
    :return: A new ``Offset`` representing the given values.
    :exception ValueError: The result of the operation is outside the range of Offset.
    """
    return Offset.from_seconds(-create_positive_offset(hours, minutes, seconds).seconds)
