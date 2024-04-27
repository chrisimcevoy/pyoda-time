# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import types

import pytest

import pyoda_time


@pytest.mark.parametrize(
    "namespace",
    (
        pyoda_time,
        pyoda_time.calendars,
        pyoda_time.fields,
        pyoda_time.time_zones,
        pyoda_time.utility,
    ),
)
def test_public_api_does_not_leak_imports(namespace: types.ModuleType) -> None:
    """Test that we don't leak imports to our public api."""

    # __all__ should be defined
    assert hasattr(namespace, "__all__")
    assert isinstance(namespace.__all__, list)

    # __all__ should not contain any "internal" symbols
    internal_symbols_included_in_all_list = [symbol for symbol in namespace.__all__ if symbol.startswith("_")]
    assert not internal_symbols_included_in_all_list

    # __all__ should contain all "public" symbols
    public_symbols_not_included_in_all_list = [
        symbol for symbol in dir(namespace) if symbol not in namespace.__all__ and not symbol.startswith("_")
    ]

    # TODO:
    #  Since implementing the `test_comparison_operator_consistency.py` test module, 'version.py' started
    #  causing this to fail. Must have only been detected as of the advent of that test module, because
    #  it uses inspect to walk the package recursively, looking for classes. Needs investigation.
    if namespace is pyoda_time:
        public_symbols_not_included_in_all_list.remove("version")

    assert not public_symbols_not_included_in_all_list
