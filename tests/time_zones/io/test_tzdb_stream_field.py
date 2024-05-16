# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import io

import pytest

from pyoda_time.time_zones.io._date_time_zone_writer import _DateTimeZoneWriter
from pyoda_time.time_zones.io._tzdb_stream_field import _TzdbStreamField
from pyoda_time.utility import InvalidPyodaDataError


class TestTzdbStreamField:
    # Only tests for situations which aren't covered elsewhere

    def test_insufficient_data(self) -> None:
        stream = io.BytesIO()
        writer = _DateTimeZoneWriter._ctor(stream, None)
        writer.write_byte(1)
        writer.write_count(10)

        stream.seek(0)
        iterator = _TzdbStreamField._read_fields(stream)

        with pytest.raises(InvalidPyodaDataError):
            next(iterator)
