# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import Annotated

import pytest

from pyoda_time.utility._csharp_compatibility import SEALED_CLASSES, _private, _sealed


def test_foo() -> None:
    """Proof-of-concept for porting a sealed C# class with no public constructor."""

    @_sealed
    @_private
    class Foo:
        arg: Annotated[int, "set via public classmethod"]

        @classmethod
        def create(cls, arg: int) -> Foo:
            instance = super().__new__(cls)
            super(Foo, instance).__init__()
            instance.arg = arg
            return instance

    expected_error_message = "Foo is not intended to be initialised directly."

    with pytest.raises(TypeError) as e:
        Foo()

    assert str(e.value) == expected_error_message

    with pytest.raises(TypeError) as e:
        o = object()
        Foo.__init__(o)

    assert str(e.value) == expected_error_message

    with pytest.raises(TypeError) as e:
        o = Foo.__new__(object)

    assert str(e.value) == expected_error_message

    with pytest.raises(TypeError) as e:
        o = Foo.__new__(Foo)

    assert str(e.value) == expected_error_message

    foo = Foo.create(5)
    assert foo.arg == 5

    with pytest.raises(TypeError) as e:

        class Bar(Foo):
            pass

    assert str(e.value) == "Foo is not intended to be subclassed."


@pytest.mark.parametrize("sealed_class", SEALED_CLASSES)
def test_sealed_class_is_decorated_with_typing_final(sealed_class: type) -> None:
    """Assert that all ``@sealed`` classes are also decorated with ``@typing.final``."""

    assert hasattr(sealed_class, "__final__")


@pytest.mark.parametrize("sealed_class", SEALED_CLASSES)
def test_sealed_class_raises_type_error_when_subclassed(sealed_class: type) -> None:
    """Assert that all classes decorated with ``@sealed`` raise TypeError when subclassed."""

    with pytest.raises(TypeError) as e:

        class Foo(sealed_class):  # type: ignore
            pass

    assert str(e.value) == f"{sealed_class.__name__} is not intended to be subclassed."
