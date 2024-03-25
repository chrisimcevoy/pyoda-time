# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.


class __GlobalizationModeSettingsMeta(type):
    @property
    def _invariant(cls) -> bool:
        # TODO: In .NET, this can be configured e.g. by environment variable.
        return False

    @property
    def _predefined_cultures_only(cls) -> bool:
        # TODO: In .NET, this can be configured e.g. by environment variable.
        return cls._invariant


class _GlobalizationModeSettings(metaclass=__GlobalizationModeSettingsMeta):
    pass


class _GlobalizationModeMeta(type):
    __settings = _GlobalizationModeSettings

    @property
    def _invariant(cls) -> bool:
        return cls.__settings._invariant

    @property
    def _predefined_cultures_only(cls) -> bool:
        return cls.__settings._predefined_cultures_only

    @property
    def _use_nls(self) -> bool:
        # TODO: Hard-coded here because we only support ICU
        return False


class _GlobalizationMode(metaclass=_GlobalizationModeMeta):
    """Rough sketch of GlobalizationMode in .NET."""
