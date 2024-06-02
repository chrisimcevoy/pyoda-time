# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time._compatibility._culture_info import CultureInfo


@pytest.fixture
def default_locale_name() -> str:
    """The default locale name according to PyICU via CultureInfo."""
    default_locale_name: str | None = CultureInfo._get_default_locale_name()
    assert default_locale_name is not None
    return default_locale_name


def test_get_default_locale_name_does_not_contain_hyphen(default_locale_name: str) -> None:
    """Assert that the default locale name is set correctly."""
    assert "_" not in default_locale_name


@pytest.mark.parametrize(
    "icu_locale_name,expected",
    [
        # As observed in dotnet 8
        ("fr-FR", "dd/MM/yyyy"),
        ("fr_FR", "dd/MM/yyyy"),
        ("fr-CA", "yyyy-MM-dd"),
        ("fr_CA", "dd/MM/yyyy"),
        ("en-GB", "dd/MM/yyyy"),
        ("en_GB", "M/d/yyyy"),
        ("en-US", "M/d/yyyy"),
        ("en_US", "M/d/yyyy"),
        ("", "MM/dd/yyyy"),  # Invariant Culture
    ],
)
def test_short_date_pattern(icu_locale_name: str, expected: str) -> None:
    """Assert that the short date pattern matches the value observed in dotnet."""
    assert CultureInfo(icu_locale_name).date_time_format.short_date_pattern == expected


def test_user_default_culture_short_date_pattern(default_locale_name: str) -> None:
    """Assert that the user default culture's short date pattern matches that of a manually-constructed Culture."""
    user_default: CultureInfo = CultureInfo._get_user_default_culture()
    via_constructor: CultureInfo = CultureInfo(name=default_locale_name)

    assert user_default.date_time_format.short_date_pattern == via_constructor.date_time_format.short_date_pattern


def test_current_culture_short_date_pattern(default_locale_name: str) -> None:
    """Assert that the current culture's short date pattern matches that of a manually-constructed Culture."""
    current: CultureInfo = CultureInfo.current_culture
    expected: CultureInfo = CultureInfo.get_culture_info(name=default_locale_name)

    assert current.date_time_format.short_date_pattern == expected.date_time_format.short_date_pattern
