import types

import pytest

import pyoda_time


@pytest.mark.parametrize(
    "namespace",
    (
        pyoda_time,
        pyoda_time.calendars,
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
    # Special case for top-level namespace as it is used to import submodules
    if namespace is pyoda_time:
        public_symbols_not_included_in_all_list.remove("calendars")
        public_symbols_not_included_in_all_list.remove("utility")
    assert not public_symbols_not_included_in_all_list
