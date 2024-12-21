# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

from typing import TYPE_CHECKING, final

from ..utility._hash_code_helper import _hash_code_helper
from ..utility._preconditions import _Preconditions

if TYPE_CHECKING:
    from .. import Instant, Offset
    from . import ZoneInterval
    from .io._i_date_time_zone_reader import _IDateTimeZoneReader

from .._date_time_zone import DateTimeZone
from ..utility._csharp_compatibility import _sealed


@_sealed
@final
class _FixedDateTimeZone(DateTimeZone):
    def __init__(self, offset: Offset, id_: str | None = None, name: str | None = None) -> None:
        from .. import Instant, Offset
        from . import ZoneInterval

        if id_ is None:
            id_ = self.__make_id(offset)
        if name is None:
            name = id_
        super().__init__(id_, True, offset, offset)
        self.__interval = ZoneInterval(
            name=name,
            start=Instant._before_min_value(),
            end=Instant._after_max_value(),
            wall_offset=offset,
            savings=Offset.zero,
        )

    def __make_id(self, offset: Offset) -> str:
        from .. import Offset

        if offset == Offset.zero:
            return self._UTC_ID
        return self._UTC_ID + str(offset)

    @classmethod
    def _get_fixed_zone_or_null(cls, id_: str) -> DateTimeZone | None:
        if not id_.startswith(cls._UTC_ID):
            return None
        if id_ == cls._UTC_ID:
            return cls.utc
        from pyoda_time.text import OffsetPattern, ParseResult

        parse_result: ParseResult[Offset] = OffsetPattern.general_invariant.parse(id_[len(cls._UTC_ID) :])
        return cls.for_offset(parse_result.value) if parse_result.success else None

    @property
    def offset(self) -> Offset:
        """Returns the fixed offset for this time zone.

        :return: The fixed offset for this time zone.
        """
        return self.max_offset

    @property
    def name(self) -> str:
        """Returns the name used for the zone interval for this time zone.

        :return: The name used for the zone interval for this time zone.
        """
        return self.__interval.name

    def get_zone_interval(self, instant: Instant) -> ZoneInterval:
        return self.__interval

    def get_utc_offset(self, instant: Instant) -> Offset:
        return self.max_offset

    @classmethod
    def read(cls, reader: _IDateTimeZoneReader, id_: str) -> DateTimeZone:
        """Reads a fixed time zone from the specified reader.

        :param reader: The reader.
        :param id_: The id.
        :return: The fixed time zone.
        """
        _Preconditions._check_not_null(reader, "reader")
        _Preconditions._check_not_null(id_, "id_")
        offset = reader.read_offset()
        name = reader.read_string() if reader.has_more_data else id_
        return cls(id_=id_, offset=offset, name=name)

    def equals(self, other: _FixedDateTimeZone) -> bool:
        """Indicates whether this instance and another instance are equal.

        :param other: Another instance to compare to.
        :return: True if the specified value is a ``_FixedDateTimeZone`` with the same name, ID and offset; otherwise,
            false.
        """
        return self == other

    def __eq__(self, other: object) -> bool:
        """Indicates whether this instance and another instance are equal.

        :param other: Another instance to compare to.
        :return: True if the specified value is a ``_FixedDateTimeZone`` with the same name, ID and offset; otherwise,
            false.
        """
        if not isinstance(other, _FixedDateTimeZone):
            return NotImplemented
        return self.offset == other.offset and self.id == other.id and self.name == other.name

    def __hash__(self) -> int:
        """Computes the hash code for this instance.

        :return: An integer that is the hash code for this instance.
        """
        return _hash_code_helper(self.offset, self.id, self.name)

    def __repr__(self) -> str:
        """Returns a string that represents this instance.

        :return: A string that represents this instance.
        """
        return self.id
