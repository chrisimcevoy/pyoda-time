# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import importlib
import pkgutil
from types import ModuleType
from typing import Generator

import pytest

import pyoda_time


def walk_package(package: ModuleType, seen: list[ModuleType] | None = None) -> Generator[ModuleType, None, None]:
    if seen is None:
        seen = []
    if package not in seen:
        seen.append(package)
        yield package
        if hasattr(package, "__path__"):
            for _, subpackage_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                # Only process sub-packages and modules that don't start with an underscore
                # (excluding __init__.py files)
                if not subpackage_name.split(".")[-1].startswith("_") or subpackage_name.endswith("__init__"):
                    subpackage = importlib.import_module(subpackage_name)
                    yield from walk_package(subpackage, seen=seen)


@pytest.mark.parametrize("namespace", [*walk_package(pyoda_time)])
def test_public_api(namespace: ModuleType) -> None:
    """Test that all "public" sub-packages and modules export all (and only) their public members.

    This is intended to ensure that our public API does not leak any internal classes, for example
    when `import *` is used.

    It is also intended to ensure that any public classes in a module are included in `__all__`.
    """
    assert hasattr(namespace, "__all__")
    assert isinstance(namespace.__all__, list)

    # __all__ should not contain any "internal" symbols
    internal_symbols_included_in_all_list = [symbol for symbol in namespace.__all__ if symbol.startswith("_")]
    assert not internal_symbols_included_in_all_list

    # __all__ should contain all "public" symbols
    public_symbols_not_included_in_all_list = [
        symbol for symbol in dir(namespace) if symbol not in namespace.__all__ and not symbol.startswith("_")
    ]
    assert not public_symbols_not_included_in_all_list
