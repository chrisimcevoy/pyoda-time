# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from collections.abc import Callable, Generator, Sequence
from io import BytesIO
from typing import BinaryIO, TypeVar, final

from pyoda_time.utility._csharp_compatibility import _private, _sealed

from ...utility import InvalidPyodaDataError
from ._date_time_zone_reader import _DateTimeZoneReader
from ._tzdb_stream_field_id import _TzdbStreamFieldId

T = TypeVar("T")


@final
@_sealed
@_private
class _TzdbStreamField:
    """An unparsed field within a stream."""

    __data: bytes
    __id: _TzdbStreamFieldId

    @property
    def id(self) -> _TzdbStreamFieldId:
        return self.__id

    @classmethod
    def _ctor(cls, id_: _TzdbStreamFieldId, data: bytes) -> _TzdbStreamField:
        self = super().__new__(cls)
        self.__id = id_
        self.__data = data
        return self

    def _create_stream(self) -> BinaryIO:
        """Creates a new read-only stream over the data for this field."""
        return BytesIO(self.__data)

    def _extract_single_value(
        self, reader_function: Callable[[_DateTimeZoneReader], T], string_pool: Sequence[str] | None
    ) -> T:
        with self._create_stream() as stream:
            return reader_function(_DateTimeZoneReader._ctor(stream, string_pool))

    @classmethod
    def _read_fields(cls, stream: BinaryIO) -> Generator[_TzdbStreamField, None, None]:
        while True:
            field_id = stream.read(1)
            if not field_id:
                break
            id_ = _TzdbStreamFieldId(field_id[0])
            # Read 7-bit encoded length
            length = _DateTimeZoneReader._ctor(stream, None).read_count()
            data = bytearray()
            for offset in range(length):
                bytes_read: bytes = stream.read(1)
                if not bytes_read:
                    raise InvalidPyodaDataError(f"Stream ended after reading {offset} bytes out of {length}")
                data.extend(bytes_read)
            yield _TzdbStreamField._ctor(id_, data)
