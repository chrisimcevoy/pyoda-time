# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import final

from pyoda_time import CalendarSystem, LocalDate, LocalTime, Offset, PyodaConstants
from pyoda_time._local_instant import _LocalInstant
from pyoda_time.time_zones._transition_mode import _TransitionMode
from pyoda_time.time_zones.io._i_date_time_zone_reader import _IDateTimeZoneReader
from pyoda_time.time_zones.io._i_date_time_zone_writer import _IDateTimeZoneWriter
from pyoda_time.utility._csharp_compatibility import _private, _sealed, _towards_zero_division
from pyoda_time.utility._hash_code_helper import _hash_code_helper
from pyoda_time.utility._preconditions import _Preconditions


@final
@_sealed
@_private
class _ZoneYearOffset:
    """Defines an offset within a year as an expression that can be used to reference multiple years.

    A year offset defines a way of determining an offset into a year based on certain criteria.
    The most basic is the month of the year and the day of the month. If only these two are
    supplied then the offset is always the same day of each year. The only exception is if the
    day is February 29th, then it only refers to those years that have a February 29th.

    If the day of the week is specified then the offset determined by the month and day are
    adjusted to the nearest day that falls on the given day of the week. If the month and day
    fall on that day of the week then nothing changes. Otherwise the offset is moved forward or
    backward up to 6 days to make the day fall on the correct day of the week. The direction the
    offset is moved is determined by the ``advance_day_of_week`` property.

    Finally the ``mode`` property determines whether the ``time_of_day`` value
    is added to the calculated offset to generate an offset within the day.
    """

    __day_of_month: int
    __day_of_week: int
    __month_of_year: int
    __add_day: bool
    __transition_mode: _TransitionMode
    __advance_day_of_week: bool
    __time_of_day: LocalTime

    @property
    def mode(self) -> _TransitionMode:
        """Gets the method by which offsets are added to Instants to get LocalInstants."""
        return self.__transition_mode

    @property
    def advance_day_of_week(self) -> bool:
        """Gets a value indicating whether [advance day of week]."""
        return self.__advance_day_of_week

    @property
    def time_of_day(self) -> LocalTime:
        """Gets the time of day when the rule takes effect."""
        return self.__time_of_day

    @classmethod
    def _ctor(
        cls,
        mode: _TransitionMode,
        month_of_year: int,
        day_of_month: int,
        day_of_week: int,
        advance: bool,
        time_of_day: LocalTime,
        add_day: bool = False,
    ) -> _ZoneYearOffset:
        """Initializes a new instance of the ``_ZoneYearOffset`` class.

        :param mode: The transition mode.
        :param month_of_year: The month year offset.
        :param day_of_month: The day of month. Negatives count from end of month.
        :param day_of_week: The day of week. 0 means not set.
        :param advance: if set to ``True`` [advance].
        :param time_of_day: The time of day at which the transition occurs.
        :param add_day: Whether to add an extra day (for 24:00 handling).
        :return: A new instance of the ``_ZoneYearOffset`` class.
        """
        self = super().__new__(cls)
        self.__verify_field_value(1, 12, "month_of_year", month_of_year, False)
        self.__verify_field_value(1, 31, "day_of_month", day_of_month, True)
        if day_of_week != 0:
            self.__verify_field_value(1, 7, "day_of_week", day_of_week, False)
        self.__transition_mode = mode
        self.__day_of_month = day_of_month
        self.__day_of_week = day_of_week
        self.__month_of_year = month_of_year
        self.__advance_day_of_week = advance
        self.__time_of_day = time_of_day
        self.__add_day = add_day
        return self

    @staticmethod
    def __verify_field_value(minimum: int, maximum: int, name: str, value: int, allow_negated: bool) -> None:
        """Verifies the input value against the valid range of the calendar field.

        :param minimum: The minimum valid value.
        :param maximum: The maximum valid value (inclusive).
        :param name: The name of the field for the error message.
        :param value: The value to check.
        :param allow_negated: if set to ``True`` all the range of value to be the negative as well.
        :raises ValueError: If the given value is not in the valid range of the given calendar field.
        """
        failed = False

        if allow_negated and value < 0:
            if value < -maximum or -minimum < value:
                failed = True
        else:
            if value < minimum or maximum < value:
                failed = True

        if failed:
            range_ = (
                f"[{minimum}, {maximum}] or [{-maximum}, {-minimum}]" if allow_negated else f"[{minimum}, {maximum}]"
            )
            raise ValueError(f"{name} is not in the valid range: {range_}")

    # region IEquatable<ZoneYearOffset> Members

    def equals(self, other: _ZoneYearOffset) -> bool:
        """Indicates whether the current object is equal to another object of the same type.

        :param other: An object to compare with this object.
        :return: True if the current object is equal to the ``other`` parameter; otherwise, False.
        """
        return self == other

    # endregion

    def __repr__(self) -> str:
        return (
            f"ZoneYearOffset["
            f"mode:{self.mode.name} "
            f"monthOfYear:{self.__month_of_year} "
            f"dayOfMonth:{self.__day_of_month} "
            f"dayOfWeek:{self.__day_of_week} "
            f"advance:{self.advance_day_of_week} "
            f"timeOfDay:{self.time_of_day:r} "
            f"addDay:{self.__add_day}"
            f"]"
        )

    def _get_occurrence_for_year(self, year: int) -> _LocalInstant:
        # TODO: unchecked
        actual_day_of_month = (
            self.__day_of_month
            if self.__day_of_month > 0
            else CalendarSystem.iso.get_days_in_month(year, self.__month_of_year) + self.__day_of_month + 1
        )

        if self.__month_of_year == 2 and self.__day_of_month == 29 and not CalendarSystem.iso.is_leap_year(year):
            # In zic.c, this would result in an error if dayOfWeek is 0 or AdvanceDayOfWeek is true.
            # However, it's very convenient to be able to ask any rule for its occurrence in any year.
            # We rely on genuine rules being well-written - and before releasing an nzd file we always
            # check that it's in line with zic anyway. Ignoring the brokenness is simpler than fixing
            # rules that are only in force for a single year.
            actual_day_of_month = 28  # We'll now look backwards for the right day-of-week.

        date = LocalDate(year, self.__month_of_year, actual_day_of_month)

        if self.__day_of_week != 0:
            # Optimized "go to next or previous occurrence of day or week". Try to do as few comparisons
            # as possible, and only fetch DayOfWeek once. (If we call Next or Previous, it will work it out again.)
            current_day_of_week = date.day_of_week
            if current_day_of_week != self.__day_of_week:
                diff = self.__day_of_week - current_day_of_week
                if diff > 0:
                    if not self.advance_day_of_week:
                        diff -= 7
                elif self.advance_day_of_week:
                    diff += 7
                date = date.plus_days(diff)

        if self.__add_day:
            # Adding a day to the last representable day will fail, but we can return an infinite value instead.
            if year == 9999 and date.month == 12 and date.day == 31:
                return _LocalInstant.after_max_value()
            date = date.plus_days(1)

        return (date + self.time_of_day)._to_local_instant()

    def _write(self, writer: _IDateTimeZoneWriter) -> None:
        """Writes this object to the given ``_IDateTimeZoneWriter``.

        :param writer: Where to send the output.
        """
        # Flags contains four pieces of information in a single byte:
        # 0MMDDDAP:
        # - MM is the mode (0-2)
        # - DDD is the day of week (0-7)
        # - A is the AdvanceDayOfWeek
        # - P is the "addDay" (24:00) flag
        flags: int = (
            (self.mode << 5)
            | (self.__day_of_week << 2)
            | (2 if self.advance_day_of_week else 0)
            | (1 if self.__add_day else 0)
        )
        writer.write_byte(flags)
        writer.write_count(self.__month_of_year)
        writer.write_signed_count(self.__day_of_month)
        # The time of day is written as a number of milliseconds for historical reasons.
        writer.write_milliseconds(
            _towards_zero_division(self.time_of_day.tick_of_day, PyodaConstants.TICKS_PER_MILLISECOND)
        )

    @classmethod
    def read(cls, reader: _IDateTimeZoneReader) -> _ZoneYearOffset:
        _Preconditions._check_not_null(reader, "reader")
        flags: int = reader.read_byte()
        mode = _TransitionMode(flags >> 5)
        day_of_week = (flags >> 2) & 7
        advance = (flags & 2) != 0
        add_day = (flags & 1) != 0
        month_of_year = reader.read_count()
        day_of_month = reader.read_signed_count()
        # The time of day is written as a number of milliseconds for historical reasons.
        time_of_day = LocalTime.from_milliseconds_since_midnight(reader.read_milliseconds())
        return _ZoneYearOffset._ctor(mode, month_of_year, day_of_month, day_of_week, advance, time_of_day, add_day)

    def _get_rule_offset(self, standard_offset: Offset, savings: Offset) -> Offset:
        """Returns the offset to use for this rule's ``TransitionMode``. The year/month/day/time for a rule is in a
        specific frame of reference: UTC, "wall" or "standard".

        :param standard_offset: The standard offset.
        :param savings: The daylight savings adjustment.
        :return: The base time offset as a ``Duration``.
        """
        match self.mode:
            case _TransitionMode.WALL:
                return standard_offset + savings
            case _TransitionMode.STANDARD:
                return standard_offset
            case _:
                return Offset.zero

    # region Object overrides

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _ZoneYearOffset):
            return NotImplemented
        return (
            self.mode == other.mode
            and self.__month_of_year == other.__month_of_year
            and self.__day_of_month == other.__day_of_month
            and self.__day_of_week == other.__day_of_week
            and self.advance_day_of_week == other.advance_day_of_week
            and self.time_of_day == other.time_of_day
            and self.__add_day == other.__add_day
        )

    def __hash__(self) -> int:
        return _hash_code_helper(
            self.mode,
            self.__month_of_year,
            self.__day_of_month,
            self.__day_of_week,
            self.advance_day_of_week,
            self.time_of_day,
            self.__add_day,
        )

    # endregion
