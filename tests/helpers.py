# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
"""This module ports various helper classes from NodaTime.Test into Python.

Originally, these helpers are contained within classes like `TestHelpers`
and `TestObjects`. To prevent accidental triggering of pytest's test
discovery, which could happen with direct porting of these class names
due to their 'Test' prefixes, the helpers are implemented here as
module-level functions.
"""

from collections.abc import Callable, Sequence
from typing import Any, Protocol, TypeVar

import pytest

from pyoda_time import Offset, PyodaConstants
from pyoda_time.utility._preconditions import _Preconditions


class IEquatable(Protocol):
    def equals(self, other: Any) -> bool: ...


class IComparable(Protocol):
    def compare_to(self, other: Any) -> int: ...


class SupportsComparison(Protocol):
    def __gt__(self, other: Any) -> bool: ...

    def __ge__(self, other: Any) -> bool: ...

    def __lt__(self, other: Any) -> bool: ...

    def __le__(self, other: Any) -> bool: ...


T = TypeVar("T")
TArg = TypeVar("TArg")
TOut = TypeVar("TOut")
T_IComparable = TypeVar("T_IComparable", bound=IComparable)
T_IEquatable = TypeVar("T_IEquatable", bound=IEquatable)
T_SupportsComparison = TypeVar("T_SupportsComparison", bound=SupportsComparison)


def assert_invalid(func: Callable[..., TOut], *args: Any) -> None:
    """Asserts that calling func with the specified value(s) raises ValueError."""
    # TODO: In Noda Time ArgumentException is thrown
    with pytest.raises(ValueError):
        func(*args)


def assert_argument_null(func: Callable[..., TOut], *args: Any) -> None:
    """Asserts that calling func with the specified value(s) raises TypeError."""
    # TODO: In Noda Time ArgumentNullException is thrown
    with pytest.raises(TypeError):
        func(*args)


def assert_out_of_range(func: Callable[..., TOut], *args: TArg) -> None:
    """Asserts that calling func with the specified value(s) raises ValueError."""
    # TODO: In Noda Time ArgumentOutOfRangeException is thrown
    with pytest.raises(ValueError):
        func(*args)


def assert_valid(func: Callable[..., TOut], *args: TArg) -> TOut:
    """Asserts that calling the specified callable with the specified value(s) doesn't raise an exception."""
    return func(*args)


def assert_overflow(func: Callable[[TArg], TOut], param: TArg) -> None:
    with pytest.raises(OverflowError):
        func(param)


def test_compare_to_struct(value: T_IComparable, equal_value: T_IComparable, *greater_values: T_IComparable) -> None:
    """Tests the <see cref="IComparable{T}.CompareTo" /> method for value objects.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param greater_values: The values greater than the base value, in ascending order.
    """
    assert value.compare_to(value) == 0
    assert value.compare_to(equal_value) == 0
    assert equal_value.compare_to(value) == 0
    for greater_value in greater_values:
        assert value.compare_to(greater_value) < 0
        assert greater_value.compare_to(value) > 0
        # Now move up to the next pair...
        value = greater_value


def test_non_generic_compare_to(
    value: T_IComparable, equal_value: T_IComparable, *greater_values: T_IComparable
) -> None:
    """Tests the <see cref="IComparable.CompareTo" /> method - note that this is the non-generic interface.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param greater_values: The values greater than the base value, in ascending order.
    """

    # Just type the values as plain IComparable for simplicity
    value_2: IComparable = value
    equal_value_2: IComparable = equal_value

    _validate_input(value_2, equal_value_2, greater_values, "greater_values")
    assert value_2.compare_to(None) > 0, "value.CompareTo(null)"
    assert value_2.compare_to(value_2) == 0, "value.CompareTo(value)"
    assert value_2.compare_to(equal_value_2) == 0, "value.CompareTo(equalValue)"
    assert equal_value_2.compare_to(value_2) == 0, "equalValue.CompareTo(value)"

    for greater_value in greater_values:
        assert value_2.compare_to(greater_value) < 0
        assert greater_value.compare_to(value_2) > 0
        # Now move up to the next pair...
        value_2 = greater_value

    # In Noda Time, they expect an ArgumentException to be raised when comparing incompatible types:
    # `Assert.Throws<ArgumentException>(() => value2.CompareTo(new object()));`
    # In Python, TypeError is more idiomatic.
    with pytest.raises(TypeError) as e:
        value.compare_to(object())
    assert str(e.value) == f"{value.__class__.__name__} cannot be compared to object"


def test_equals_class(value: T_IEquatable, equal_value: T_IEquatable, *unequal_values: T_IEquatable) -> None:
    """Tests the IEquatable.Equals method for reference objects. Also tests the object equals method.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param unequal_values: Values not equal to the base value.
    """
    test_object_equals(value, equal_value, *unequal_values)
    assert not value.equals(None)
    assert value.equals(value)
    assert value.equals(equal_value)
    assert equal_value.equals(value)
    for unequal_value in unequal_values:
        assert not value.equals(unequal_value)


def test_equals_struct(value: T_IEquatable, equal_value: T_IEquatable, *unequal_values: T_IEquatable) -> None:
    """Tests the IEquatable.Equals method for value objects. Also tests the object equals method.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param unequal_values: The values not equal to the base value.
    :return:
    """

    test_object_equals(value, equal_value, *unequal_values)
    assert value.equals(value)
    assert value.equals(equal_value)
    assert equal_value.equals(value)
    for unequal_value in unequal_values:
        assert not value.equals(unequal_value)


def test_object_equals(value: T_IEquatable, equal_value: T_IEquatable, *unequal_values: T_IEquatable) -> None:
    _validate_input(value, equal_value, unequal_values, "unequal_values")
    assert not value.equals(None)
    assert value.equals(value)
    assert value.equals(equal_value)
    assert equal_value.equals(value)
    for unequal_value in unequal_values:
        assert not value.equals(unequal_value)
    assert hash(value) == hash(value)
    assert hash(value) == hash(equal_value)


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

    assert not value > value
    assert not value > equal_value
    assert not equal_value > value
    with pytest.raises(TypeError) as e:
        value > None
    assert str(e.value) == f"'>' not supported between instances of '{value.__class__.__name__}' and 'NoneType'"
    with pytest.raises(TypeError) as e:
        None > value
    assert str(e.value) == f"'>' not supported between instances of 'NoneType' and '{value.__class__.__name__}'"

    assert not value < value
    assert not value < equal_value
    assert not equal_value < value
    with pytest.raises(TypeError) as e:
        value < None
    with pytest.raises(TypeError) as e:
        None < value

    # Then comparisons involving the greater values

    for greater_value in greater_values:
        assert not value > greater_value
        assert greater_value > value
        assert value < greater_value
        assert not greater_value < value
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

    assert value >= value
    assert value >= equal_value
    assert equal_value >= value

    with pytest.raises(TypeError) as e:
        value >= None
    assert str(e.value) == f"'>=' not supported between instances of '{value.__class__.__name__}' and 'NoneType'"
    with pytest.raises(TypeError) as e:
        None >= value
    assert str(e.value) == f"'>=' not supported between instances of 'NoneType' and '{value.__class__.__name__}'"

    assert value <= value
    assert value <= equal_value
    assert equal_value <= value

    with pytest.raises(TypeError) as e:
        value <= None
    assert str(e.value) == f"'<=' not supported between instances of '{value.__class__.__name__}' and 'NoneType'"
    with pytest.raises(TypeError) as e:
        None <= value
    assert str(e.value) == f"'<=' not supported between instances of 'NoneType' and '{value.__class__.__name__}'"

    # Now the "greater than" values
    for greater_value in greater_values:
        assert not value >= greater_value
        assert greater_value >= value
        assert value <= greater_value
        assert not greater_value <= value
        # Now move up to the next pair...
        value = greater_value


def test_operator_equality(value: T, equal_value: T, unequal_value: T) -> None:
    """Tests the equality and inequality operators (==, !=) if they exist on the object.

    :param value: The base value.
    :param equal_value: The value equal to but not the same object as the base value.
    :param unequal_value: The value not equal to the base value.
    """
    _validate_input(value, equal_value, unequal_value, "unequal_value")

    assert value == value
    assert value == equal_value
    assert equal_value == value
    assert not value == unequal_value
    assert not value == None  # noqa
    assert not None == value  # noqa

    assert not value != value
    assert not value != equal_value
    assert not equal_value != value
    assert value != unequal_value
    assert value != None  # noqa
    assert None != value  # noqa


def _validate_input(value: T, equal_value: T, unequal_values: T | Sequence[T], unequal_name: str) -> None:
    assert value is not None, "Value cannot be null"
    assert equal_value is not None, "equal_value cannot be null"
    # TODO: This assertion seems fine, but... most of the main types in C# (Instant, Duration et al)
    #  are structs, i.e. value types. The same variable name might be passed to this method
    #  as both `value` and `equal_value`, but because of the nature of value types in C# (passed
    #  by value as opposed to passed by reference) they will pass this check.
    #  The concept of value types doesn't apply to Python; All types are passed by reference.
    #  Therefore I have commented this `assert x is not y` as it doesn't really matter for the vast
    #  majority of tests in Noda Time anyway.
    # assert value is not equal_value, "value and equal_value MUST be different objects"
    if not isinstance(unequal_values, Sequence):
        unequal_values = [unequal_values]
    for unequal_value in unequal_values:
        assert unequal_value is not None, f"{unequal_name} cannot be null"
        assert unequal_value is not value, f"{unequal_name} and value MUST be different objects"


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
    seconds += minutes * PyodaConstants.SECONDS_PER_MINUTE
    seconds += hours * PyodaConstants.SECONDS_PER_HOUR
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
