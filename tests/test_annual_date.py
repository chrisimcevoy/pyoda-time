# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
import pytest

from pyoda_time import AnnualDate, LocalDate

from . import helpers


class TestAnnualDate:
    def test_feb_29(self) -> None:
        date = AnnualDate(2, 29)
        assert date.day == 29
        assert date.month == 2
        assert date.in_year(2016) == LocalDate(2016, 2, 29)
        assert date.is_valid_year(2016)
        assert date.in_year(2015) == LocalDate(2015, 2, 28)
        assert not date.is_valid_year(2015)

    def test_june_19th(self) -> None:
        date = AnnualDate(6, 19)
        assert date.day == 19
        assert date.month == 6
        assert date.in_year(2016) == LocalDate(2016, 6, 19)
        assert date.is_valid_year(2016)
        assert date.in_year(2015) == LocalDate(2015, 6, 19)
        assert date.is_valid_year(2015)

    def test_validation(self) -> None:
        # Feb 30th is invalid, but January 30th is fine
        with pytest.raises(ValueError):
            AnnualDate(2, 30)
        AnnualDate(1, 30)

        # 13th month is invalid
        with pytest.raises(ValueError):
            AnnualDate(13, 1)

    def test_equality(self) -> None:
        helpers.test_equals_struct(AnnualDate(3, 15), AnnualDate(3, 15), AnnualDate(4, 15), AnnualDate(3, 16))

    def test_default_value_is_january_1st(self) -> None:
        assert AnnualDate() == AnnualDate(1, 1)

    def test_comparison(self) -> None:
        helpers.test_compare_to_struct(AnnualDate(6, 19), AnnualDate(6, 19), AnnualDate(6, 20), AnnualDate(7, 1))

    def test_operators(self) -> None:
        helpers.test_operator_comparison_equality(
            AnnualDate(6, 19), AnnualDate(6, 19), AnnualDate(6, 20), AnnualDate(7, 1)
        )

    # TODO: [requires AnnualDatePattern]
    #  def test_to_string
    #  def test_to_string_with_format
