# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing
from typing import final

from .._compatibility._culture_info import CultureInfo
from .._compatibility._date_time_format_info import DateTimeFormatInfo
from .._compatibility._i_format_provider import IFormatProvider
from .._offset import Offset
from ..calendars import Era

if typing.TYPE_CHECKING:
    from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
from ..utility import _Preconditions
from ..utility._csharp_compatibility import _sealed
from ._pattern_resources import _PatternResources


class _PyodaFormatInfoMeta(type):
    @property
    def invariant_info(self) -> _PyodaFormatInfo:
        """A ``_PyodaFormatInfo`` wrapping the invariant culture."""
        return _PyodaFormatInfo(CultureInfo.invariant_culture)

    @property
    def current_info(cls) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` object for the current thread."""
        return _PyodaFormatInfo.get_instance(CultureInfo.current_culture)


@final
@_sealed
class _PyodaFormatInfo(metaclass=_PyodaFormatInfoMeta):
    def __init__(self, culture_info: CultureInfo, date_time_format: DateTimeFormatInfo | None = None) -> None:
        _Preconditions._check_not_null(culture_info, "culture_info")
        # _Preconditions._check_not_null(date_time_format, "date_time_format")
        self.__culture_info: CultureInfo = culture_info
        self.__date_time_format: DateTimeFormatInfo = (
            culture_info.date_time_format if date_time_format is None else date_time_format
        )
        self.__era_descriptions: dict[Era, _EraDescription] = dict()

    @property
    def culture_info(self) -> CultureInfo:
        """Gets the culture info associated with this format provider."""
        return self.__culture_info

    @property
    def time_separator(self) -> str:
        """Gets the time separator."""
        return self.__date_time_format.time_separator

    @classmethod
    def get_instance(cls, provider: IFormatProvider | None) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` for the given ``IFormatProvider``.

        If the
        /// format provider is null then the format object for the current thread is returned. If it's
        /// a CultureInfo, that's used for everything. If it's a DateTimeFormatInfo, that's used for
        /// format strings, day names etc but the invariant culture is used for text comparisons and
        /// resource lookups. Otherwise, ``ValueError`` is thrown.
        """
        if provider is None:
            return cls.get_format_info(cls.current_info.culture_info)
        if isinstance(provider, CultureInfo):
            return cls.get_format_info(provider)
        if isinstance(provider, DateTimeFormatInfo):
            return _PyodaFormatInfo(CultureInfo.invariant_culture, provider)
        raise ValueError(f"Cannot use provider of type {type(provider).__name__} in Pyoda Time")

    def __str__(self) -> str:
        return f"PyodaFormatInfo[{self.__culture_info._name}]"

    @property
    def offset_pattern_parser(self) -> _FixedFormatInfoPatternParser[Offset]:
        from ..text._fixed_format_info_pattern_parser import _FixedFormatInfoPatternParser
        from ..text._offset_pattern_parser import _OffsetPatternParser

        return _FixedFormatInfoPatternParser[Offset](_OffsetPatternParser(), self)

    @property
    def offset_pattern_long(self) -> str:
        """Gets the ``Offset`` 'l' pattern."""
        return _PatternResources.OFFSET_PATTERN_LONG

    @property
    def offset_pattern_medium(self) -> str:
        """Gets the ``Offset`` 'm' pattern."""
        return _PatternResources.OFFSET_PATTERN_MEDIUM

    @property
    def offset_pattern_short(self) -> str:
        """Gets the ``Offset`` 's' pattern."""
        return _PatternResources.OFFSET_PATTERN_SHORT

    @property
    def offset_pattern_long_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'L' pattern."""
        return _PatternResources.OFFSET_PATTERN_LONG_NO_PUNCTUATION

    @property
    def offset_pattern_medium_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'M' pattern."""
        return _PatternResources.OFFSET_PATTERN_MEDIUM_NO_PUNCTUATION

    @property
    def offset_pattern_short_no_punctuation(self) -> str:
        """Gets the ``Offset`` 'S' pattern."""
        return _PatternResources.OFFSET_PATTERN_SHORT_NO_PUNCTUATION

    @classmethod
    def get_format_info(cls, culture_info: CultureInfo) -> _PyodaFormatInfo:
        """Gets the ``_PyodaFormatInfo`` for the given ``CultureInfo``."""
        _Preconditions._check_not_null(culture_info, "culture_info")
        if culture_info == CultureInfo.invariant_culture:
            return _PyodaFormatInfo.invariant_info
        # TODO: This is simplified to ignore caching and read-only cultures for now...
        return _PyodaFormatInfo(culture_info)


class _EraDescription:
    """The description for an era: the primary name and all possible names."""

    # TODO: EraDescription
    pass
