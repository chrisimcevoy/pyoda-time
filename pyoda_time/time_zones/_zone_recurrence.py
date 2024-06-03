# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time._calendar_system import CalendarSystem
from pyoda_time._instant import Instant
from pyoda_time._local_instant import _LocalInstant
from pyoda_time._offset import Offset
from pyoda_time.calendars._gregorian_year_month_day_calculator import _GregorianYearMonthDayCalculator
from pyoda_time.time_zones._transition import _Transition
from pyoda_time.time_zones._zone_year_offset import _ZoneYearOffset
from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _CsharpConstants, _sealed
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
class _ZoneRecurrence:
    """Extends ``_ZoneYearOffset`` with a name and savings.

    This represents a recurring transition from or to a daylight savings time. The name is the name of the time zone
    during this period (e.g. PST or PDT). The savings is usually 0 or the daylight offset. This is also used to support
    some of the tricky transitions that occurred before the time zones were normalized (i.e. when they were still
    tightly longitude-based, with multiple towns in the same country observing different times).
    """

    @property
    def name(self) -> str:
        return self.__name

    @property
    def savings(self) -> Offset:
        return self.__savings

    @property
    def year_offset(self) -> _ZoneYearOffset:
        return self.__year_offset

    @property
    def from_year(self) -> int:
        return self.__from_year

    @property
    def to_year(self) -> int:
        return self.__to_year

    @property
    def is_infinite(self) -> bool:
        return self.to_year == _CsharpConstants.INT_MAX_VALUE

    def __init__(self, name: str, savings: Offset, year_offset: _ZoneYearOffset, from_year: int, to_year: int) -> None:
        """Initializes a new instance of the ``_ZoneRecurrence`` class.

        :param name: The name of the time zone period e.g. PST.
        :param savings: The savings for this period.
        :param year_offset: The year offset of when this period starts in a year.
        :param from_year: The first year in which this recurrence is valid
        :param to_year: The last year in which this recurrence is valid
        """
        _Preconditions._check_not_null(name, "name")
        _Preconditions._check_not_null(year_offset, "year_offset")

        _Preconditions._check_argument(
            from_year == _CsharpConstants.INT_MIN_VALUE or (-9998 <= from_year <= 9999),
            "from_year",
            "from_year must be in the range [-9998, 9999] or Int32.MinValue",
        )
        _Preconditions._check_argument(
            to_year == _CsharpConstants.INT_MAX_VALUE or (-9998 <= to_year <= 9999),
            "to_year",
            "to_year must be in the range [-9998, 9999] or Int32.MaxValue",
        )

        self.__name: str = name
        self.__savings: Offset = savings
        self.__year_offset: _ZoneYearOffset = year_offset
        self.__from_year: int = from_year
        self.__to_year: int = to_year
        self.__min_local_instant = (
            _LocalInstant.before_min_value()
            if from_year == _CsharpConstants.INT_MIN_VALUE
            else year_offset._get_occurrence_for_year(from_year)
        )
        self.__max_local_instant = (
            _LocalInstant.after_max_value()
            if to_year == _CsharpConstants.INT_MAX_VALUE
            else year_offset._get_occurrence_for_year(to_year)
        )

    def _with_name(self, name: str) -> _ZoneRecurrence:
        """Returns a new recurrence which has the same values as this, but a different name."""
        return _ZoneRecurrence(name, self.savings, self.year_offset, self.from_year, self.to_year)

    def _for_single_year(self, year: int) -> _ZoneRecurrence:
        """Returns a new recurrence which has the same values as this, but just for a single year."""
        return _ZoneRecurrence(self.name, self.savings, self.year_offset, year, year)

    # region IEquatable<ZoneOffset> members

    def equals(self, other: _ZoneRecurrence) -> bool:
        return self == other

    # endregion

    def _next(self, instant: Instant, standard_offset: Offset, previous_savings: Offset) -> _Transition | None:
        """Returns the first transition which occurs strictly after the given instant.

        If the given instant is before the starting year, the year of the given instant is
        adjusted to the beginning of the starting year. The first transition after the
        adjusted instant is determined. If the next adjustment is after the ending year, this
        method returns null; otherwise the next transition is returned.

        :param instant: The ``Instant`` lower bound for the next transition.
        :param standard_offset: The ``Offset`` standard offset.
        :param previous_savings: The ``Offset`` savings adjustment at the given Instant.
        :return: The next transition, or null if there is no next transition. The transition may be
            infinite, i.e. after the end of representable time.
        """
        rule_offset: Offset = self.year_offset._get_rule_offset(standard_offset, previous_savings)
        new_offset: Offset = standard_offset + self.savings

        safe_local: _LocalInstant = instant._safe_plus(rule_offset)

        if safe_local < self.__min_local_instant:
            # Asked for a transition after some point before the first transition:
            # crop to first year (so we get the first transition)
            target_year = self.from_year
        elif safe_local >= self.__max_local_instant:
            # Asked for a transition after our final transition... or both are beyond the end of time (in which case
            # we can return an infinite transition). This branch will always be taken for transitions beyond the end
            # of time.
            return (
                _Transition._ctor(Instant._after_max_value(), new_offset)
                if self.__max_local_instant == _LocalInstant.after_max_value()
                else None
            )
        elif safe_local == _LocalInstant.before_min_value():
            # We've been asked to find the next transition after some point which is a valid instant, but is before the
            # start of valid local time after applying the rule offset. For example, passing Instant.MinValue for a rule
            # which says "transition uses wall time, which is UTC-5". Proceed as if we'd been asked for something in
            # -9998. I *think* that works...
            target_year = _GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR
        else:
            # Simple case: we were asked for a "normal" value in the range of years for which this recurrence is valid.
            target_year, _ = CalendarSystem.iso._year_month_day_calculator._get_year(safe_local._days_since_epoch)

        transition: _LocalInstant = self.year_offset._get_occurrence_for_year(target_year)

        safe_transition: Instant = transition._safe_minus(rule_offset)

        if safe_transition > instant:
            return _Transition._ctor(safe_transition, new_offset)

        # We've got a transition earlier than we were asked for. Try next year.
        # Note that this will still be within the FromYear/ToYear range, otherwise
        # safeLocal >= maxLocalInstant would have been triggered earlier.
        target_year += 1
        # Handle infinite transitions
        if target_year > _GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR:
            return _Transition._ctor(Instant._after_max_value(), new_offset)

        # It's fine for this to be "end of time", and it can't be "start of time" because we're at least finding a
        # transition in -9997.
        safe_transition = self.year_offset._get_occurrence_for_year(target_year)._safe_minus(rule_offset)
        return _Transition._ctor(safe_transition, new_offset)

    def _previous_or_same(
        self, instant: Instant, standard_offset: Offset, previous_savings: Offset
    ) -> _Transition | None:
        """Returns the last transition which occurs before or on the given instant.

        :param instant: The ``Instant`` lower bound for the last transition.
        :param standard_offset: The ``Offset`` standard offset.
        :param previous_savings: The ``Offset`` savings adjustment at the given Instant.
        :return: The previous transition, or null if there is no previous transition. The transition may be
            infinite, i.e. before the start of representable time.
        """
        rule_offset: Offset = self.year_offset._get_rule_offset(standard_offset, previous_savings)
        new_offset: Offset = standard_offset + self.savings

        safe_local: _LocalInstant = instant._safe_plus(rule_offset)
        if safe_local > self.__max_local_instant:
            # Asked for a transition before some point after our last year: crop to last year.
            target_year = self.to_year
        # Deliberately < here; "previous or same" means if safeLocal==minLocalInstant,
        # we should compute it for this year.
        elif safe_local < self.__min_local_instant:
            # Asked for a transition before our first one
            return None
        elif not safe_local._is_valid:
            if safe_local == _LocalInstant.before_min_value():
                # We've been asked to find the next transition before some point which is a valid instant, but is before
                # the start of valid local time after applying the rule offset.  It's possible that the next transition
                # *would* be representable as an instant (e.g. 1pm Dec 31st -9999 with an offset of -5) but it's
                # reasonable to just return an infinite transition.
                return _Transition._ctor(Instant._before_min_value(), new_offset)
            else:
                # We've been asked to find the next transition before some point which is a valid instant, but is after
                # the end of valid local time after applying the rule offset. For example, passing Instant.MaxValue for
                # a rule which says "transition uses wall time, which is UTC+5". Proceed as if we'd been asked for
                # something in 9999. I *think* that works...
                target_year = _GregorianYearMonthDayCalculator._MAX_GREGORIAN_YEAR
        else:
            # Simple case: we were asked for a "normal" value in the range of years for which this recurrence is valid.
            target_year, _ = CalendarSystem.iso._year_month_day_calculator._get_year(safe_local._days_since_epoch)

        transition: _LocalInstant = self.year_offset._get_occurrence_for_year(target_year)

        safe_transition: Instant = transition._safe_minus(rule_offset)
        if safe_transition <= instant:
            return _Transition._ctor(safe_transition, new_offset)

        # We've got a transition later than we were asked for. Try next year.
        # Note that this will still be within the FromYear/ToYear range, otherwise
        # safeLocal < minLocalInstant would have been triggered earlier.
        target_year -= 1
        # Handle infinite transitions
        if target_year < _GregorianYearMonthDayCalculator._MIN_GREGORIAN_YEAR:
            return _Transition._ctor(Instant._before_min_value(), new_offset)
        # It's fine for this to be "start of time", and it can't be "end of time" because
        # we're at latest finding a transition in 9998.
        safe_transition = self.year_offset._get_occurrence_for_year(target_year)._safe_minus(rule_offset)
        return _Transition._ctor(safe_transition, new_offset)

    def _next_or_fail(self, instant: Instant, standard_offset: Offset, previous_savings: Offset) -> _Transition:
        """Piggy-backs onto Next, but fails with an InvalidOperationException if there's no such transition."""
        if (transition := self._next(instant, standard_offset, previous_savings)) is None:
            raise RuntimeError(
                f"Pyoda Time bug or bad data: Expected a transition later than {instant}; "
                f"standard offset = {standard_offset}; previousSavings = {previous_savings}; recurrence = {self}"
            )
        return transition

    def _previous_or_same_or_fail(
        self, instant: Instant, standard_offset: Offset, previous_savings: Offset
    ) -> _Transition:
        """Piggy-backs onto PreviousOrSame, but fails with a descriptive InvalidOperationException if there's no such
        transition."""
        if (transition := self._previous_or_same(instant, standard_offset, previous_savings)) is None:
            raise RuntimeError(
                f"Noda Time bug or bad data: Expected a transition earlier than {instant}; "
                f"standard offset = {standard_offset}; previousSavings = {previous_savings}; recurrence = {self}"
            )
        return transition

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        """Writes this object to the given ``_IDateTimeZoneWriter``.

        :param writer: Where to send the output.
        """
        writer.write_string(self.name)
        writer.write_offset(self.savings)
        self.year_offset._write(writer)
        # We'll never have time zones with recurrences between the beginning of time and 0AD,
        # so we can treat anything negative as 0, and go to the beginning of time when reading.
        writer.write_count(max(self.from_year, 0))
        writer.write_count(self.to_year)

    @classmethod
    def read(cls, reader: _IDateTimeZoneReader) -> _ZoneRecurrence:
        """Reads a recurrence from the specified reader.

        :param reader: The reader.
        :return: The recurrence read from the reader.
        """
        _Preconditions._check_not_null(reader, "reader")
        name: str = reader.read_string()
        savings: Offset = reader.read_offset()
        year_offset = _ZoneYearOffset.read(reader)
        from_year: int = reader.read_count()
        if from_year == 0:
            from_year = _CsharpConstants.INT_MIN_VALUE
        to_year: int = reader.read_count()
        return _ZoneRecurrence(name, savings, year_offset, from_year, to_year)

    # region Object overrides

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _ZoneRecurrence):
            return NotImplemented
        return (
            self.savings == other.savings
            and self.from_year == other.from_year
            and self.to_year == other.to_year
            and self.name == other.name
            and self.year_offset == other.year_offset
        )

    def __hash__(self) -> int:
        return _hash_code_helper(self.savings, self.name, self.year_offset)

    def __repr__(self) -> str:
        return f"{self.name} {self.savings} {self.year_offset} [{self.from_year}-{self.to_year}]"

    # endregion

    def _to_start_of_time(self) -> _ZoneRecurrence:
        """Returns either "this" (if this zone recurrence already has a from year of int.MinValue) or a new zone
        recurrence which is identical but with a from year of int.MinValue."""
        return (
            self
            if self.from_year == _CsharpConstants.INT_MIN_VALUE
            else _ZoneRecurrence(
                self.name, self.savings, self.year_offset, _CsharpConstants.INT_MIN_VALUE, self.to_year
            )
        )
