# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.

from __future__ import annotations

import abc

from ._era import Era


class _EraCalculator(abc.ABC):
    """Takes responsibility for all era-based calculations for a calendar.

    YearMonthDay arguments can be assumed to be valid for the relevant calendar, but other arguments should be
    validated. (Eras should be validated for nullity as well as for the presence of a particular era.)
    """

    def __init__(self, *eras: Era):
        self._eras = eras

    @abc.abstractmethod
    def _get_min_year_of_era(self, era: Era) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_max_year_of_era(self, era: Era) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_era(self, absolute_year: int) -> Era:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_year_of_era(self, absolute_year: int) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_absolute_year(self, year_of_era: int, era: Era) -> int:
        raise NotImplementedError
