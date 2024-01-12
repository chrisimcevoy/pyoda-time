# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

import pytest

from pyoda_time import PeriodBuilder, PeriodUnits


class TestPeriodBuilder:
    def test_indexer_getter_valid_units(self) -> None:
        builder = PeriodBuilder(
            months=1,
            weeks=2,
            days=3,
            hours=4,
            minutes=5,
            seconds=6,
            milliseconds=7,
            ticks=8,
            nanoseconds=9,
        )
        assert builder[PeriodUnits.YEARS] == 0
        assert builder[PeriodUnits.MONTHS] == 1
        assert builder[PeriodUnits.WEEKS] == 2
        assert builder[PeriodUnits.DAYS] == 3
        assert builder[PeriodUnits.HOURS] == 4
        assert builder[PeriodUnits.MINUTES] == 5
        assert builder[PeriodUnits.SECONDS] == 6
        assert builder[PeriodUnits.MILLISECONDS] == 7
        assert builder[PeriodUnits.TICKS] == 8
        assert builder[PeriodUnits.NANOSECONDS] == 9

    def test_index_getter_invalid_units(self) -> None:
        builder = PeriodBuilder()
        with pytest.raises(TypeError):  # TODO: ArgumentOutOfRangeException
            builder[0]  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentOutOfRangeException
            builder[-1]  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            builder[PeriodUnits.DATE_AND_TIME]

    def test_indexer_setter_valid_units(self) -> None:
        builder = PeriodBuilder()
        builder[PeriodUnits.MONTHS] = 1
        builder[PeriodUnits.WEEKS] = 2
        builder[PeriodUnits.DAYS] = 3
        builder[PeriodUnits.HOURS] = 4
        builder[PeriodUnits.MINUTES] = 5
        builder[PeriodUnits.SECONDS] = 6
        builder[PeriodUnits.MILLISECONDS] = 7
        builder[PeriodUnits.TICKS] = 8
        builder[PeriodUnits.NANOSECONDS] = 9
        expected = PeriodBuilder(
            years=0,
            months=1,
            weeks=2,
            days=3,
            hours=4,
            minutes=5,
            seconds=6,
            milliseconds=7,
            ticks=8,
            nanoseconds=9,
        ).build()
        assert builder.build() == expected

    def test_index_setter_invalid_units(self) -> None:
        builder = PeriodBuilder()
        with pytest.raises(TypeError):  # TODO: ArgumentOutOfRangeException
            builder[0] = 1  # type: ignore
        with pytest.raises(TypeError):  # TODO: ArgumentOutOfRangeException
            builder[-1] = 1  # type: ignore
        with pytest.raises(ValueError):  # TODO: ArgumentOutOfRangeException
            builder[PeriodUnits.DATE_AND_TIME] = 1
