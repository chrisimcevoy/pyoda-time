# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import typing as _typing

from ._fixed_length_date_period_field import _FixedLengthDatePeriodField
from ._months_period_field import _MonthsPeriodField
from ._years_period_field import _YearsPeriodField

if _typing.TYPE_CHECKING:
    pass

from ._i_date_period_field import _IDatePeriodField


class _DatePeriodFields:
    """All the period fields."""

    _days_field: _typing.Final[_IDatePeriodField] = _FixedLengthDatePeriodField(1)
    _weeks_field: _typing.Final[_IDatePeriodField] = _FixedLengthDatePeriodField(7)
    _months_field: _typing.Final[_IDatePeriodField] = _MonthsPeriodField()
    _years_field: _typing.Final[_IDatePeriodField] = _YearsPeriodField()
