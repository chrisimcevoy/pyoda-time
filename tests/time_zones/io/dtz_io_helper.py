# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import TYPE_CHECKING

from pyoda_time.time_zones._zone_recurrence import _ZoneRecurrence
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.io._date_time_zone_reader import _DateTimeZoneReader
from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _private

from .io_stream import _IoStream

if TYPE_CHECKING:
    from pyoda_time._instant import Instant
    from pyoda_time._offset import Offset
    from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
    from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter


@_private
class _DtzIoHelper:
    """Wrapper around a DateTimeZoneWriter/DateTimeZoneReader pair that reads whatever is written to it."""

    __io_stream: _IoStream
    __string_pool: list[str] | None
    __reader: _DateTimeZoneReader
    __writer: _DateTimeZoneWriter

    @classmethod
    def __ctor(cls, string_pool: list[str] | None) -> _DtzIoHelper:
        self = super().__new__(cls)
        self.__io_stream = _IoStream()
        self.__reader = _DateTimeZoneReader._ctor(self.__io_stream.get_read_stream(), string_pool)
        self.__writer = _DateTimeZoneWriter._ctor(self.__io_stream.get_write_stream(), string_pool)
        self.__string_pool = string_pool
        return self

    @classmethod
    def _create_no_string_pool(cls) -> _DtzIoHelper:
        return cls.__ctor(None)

    @classmethod
    def _create_with_string_pool(cls) -> _DtzIoHelper:
        return cls.__ctor([])

    @property
    def _reader(self) -> _IDateTimeZoneReader:
        return self.__reader

    @property
    def _writer(self) -> _IDateTimeZoneWriter:
        return self.__writer

    def reset(self) -> None:
        self.__io_stream.reset()
        if self.__string_pool is not None:
            self.__string_pool.clear()

    def test_count(self, value: int, unread_contents: bytes | None = None) -> None:
        self.reset()
        self._writer.write_count(value)
        if unread_contents is None:
            actual = self._reader.read_count()
            assert actual == value
        else:
            self.__io_stream.assert_unread_contents(unread_contents)
        self.__io_stream.assert_end_of_stream()

    def test_signed_count(self, value: int, unread_contents: bytes | None = None) -> None:
        self.reset()
        self.__writer.write_signed_count(value)
        if unread_contents is None:
            actual = self._reader.read_signed_count()
            assert actual == value
        else:
            self.__io_stream.assert_unread_contents(unread_contents)
        self.__io_stream.assert_end_of_stream()

    def test_dictionary(self, expected: dict[str, str]) -> None:
        self.reset()
        self._writer.write_dictionary(expected)
        actual = self._reader.read_dictionary()
        assert actual == expected
        self.__io_stream.assert_end_of_stream()

    def test_zone_interval_transition(self, previous: Instant | None, expected: Instant) -> None:
        self.reset()
        self._writer.write_zone_interval_transition(previous, expected)
        actual = self._reader.read_zone_interval_transition(previous)
        assert actual == expected
        self.__io_stream.assert_end_of_stream()

    def test_offset(self, offset: Offset) -> None:
        self.reset()
        self._writer.write_offset(offset)
        actual = self._reader.read_offset()
        assert actual == offset
        self.__io_stream.assert_end_of_stream()

    def test_string(self, expected: str) -> None:
        self.reset()
        self._writer.write_string(expected)
        actual = self._reader.read_string()
        assert actual == expected
        self.__io_stream.assert_end_of_stream()

    def test_zone_recurrence(self, expected: _ZoneRecurrence) -> None:
        self.reset()
        expected._write(self.__writer)
        actual = _ZoneRecurrence.read(self._reader)
        assert actual == expected
        self.__io_stream.assert_end_of_stream()

    def test_zone_year_offset(self, expected: _ZoneYearOffset) -> None:
        self.reset()
        expected._write(self.__writer)
        actual = _ZoneYearOffset.read(self._reader)
        assert actual == expected
        self.__io_stream.assert_end_of_stream()
