# Copyright 2024 The Pyoda Time Authors. All rights reserved.
# Use of this source code is governed by the Apache License 2.0,
# as found in the LICENSE.txt file.
from __future__ import annotations

from typing import Any, Callable, Final, final

from pyoda_time import CalendarSystem, LocalDate
from pyoda_time._calendar_ordinal import _CalendarOrdinal
from pyoda_time._year_month_day_calendar import _YearMonthDayCalendar
from pyoda_time.calendars import Era
from pyoda_time.globalization._pyoda_format_info import _PyodaFormatInfo
from pyoda_time.text import ParseResult
from pyoda_time.text._i_pattern import IPattern
from pyoda_time.text._parse_bucket import _ParseBucket
from pyoda_time.text._value_cursor import _ValueCursor
from pyoda_time.text.patterns._i_pattern_parser import _IPatternParser
from pyoda_time.text.patterns._pattern_cursor import _PatternCursor
from pyoda_time.text.patterns._pattern_fields import _PatternFields
from pyoda_time.text.patterns._stepped_pattern_builder import _SteppedPatternBuilder
from pyoda_time.utility._csharp_compatibility import _csharp_modulo, _private, _sealed, _towards_zero_division


@_sealed
@final
@_private
class _LocalDatePatternParser(_IPatternParser[LocalDate]):
    """Parser for patterns of ``LocalDate`` values."""

    __template_value: LocalDate
    __two_digit_year_max: int

    __character_handlers: Final[dict[str, Callable[[_PatternCursor, _SteppedPatternBuilder[LocalDate]], None]]] = {}

    @classmethod
    def __ctor(cls, template_value: LocalDate, two_digit_year_max: int) -> _LocalDatePatternParser:
        self = super().__new__(cls)
        self.__template_value = template_value
        self.__two_digit_year_max = two_digit_year_max
        return self

    def parse_pattern(self, pattern: str, format_info: _PyodaFormatInfo) -> IPattern[LocalDate]:
        raise NotImplementedError

    @final
    @_private
    @_sealed
    class _LocalDateParseBucket(_ParseBucket[LocalDate]):
        """Bucket to put parsed values in, ready for later result calculation.

        This type is also used by LocalDateTimePattern to store and calculate values.
        """

        _template_value: LocalDate
        _two_digit_year_max: int

        _calendar: CalendarSystem
        _year: int
        __era: Era | None
        _year_of_era: int
        _month_of_year_numeric: int
        _month_of_year_text: int
        _day_of_month: int
        _day_of_week: int

        @classmethod
        def _ctor(
            cls, template_value: LocalDate, two_digit_year_max: int
        ) -> _LocalDatePatternParser._LocalDateParseBucket:
            self = super().__new__(cls)
            self._template_value = template_value
            # Fetch this only once
            self._calendar = template_value.calendar
            self._two_digit_year_max = two_digit_year_max

            # These fields are not set in the constructor in Noda Time.
            # In Python, we have to explicitly default them as they would
            # be implicitly defaulted in C# (i.e. according to the type).
            self._year = 0
            self.__era = None
            _year_of_era = 0
            _month_of_year_numeric = 0
            _month_of_year_text = 0
            _day_of_month = 0
            _day_of_week = 0

            return self

        def _parse_era(self, format_info: _PyodaFormatInfo, cursor: _ValueCursor) -> ParseResult[Any] | None:
            # TODO: compare_info = format_info.compare_info
            for era in self._calendar.eras():
                for era_name in format_info.get_era_names(era):
                    # TODO: compare_info is passed to this method in Noda Time...
                    if cursor._match_case_insensitive(era_name, True):
                        self.__era = era
                        return None
            return ParseResult[Any]._mismatched_text(cursor, "g")

        def calculate_value(self, used_fields: _PatternFields, value: str) -> ParseResult[LocalDate]:
            return self._calculate_value(used_fields, value, LocalDate)

        def _calculate_value(
            self, used_fields: _PatternFields, text: str, eventual_result_type: type
        ) -> ParseResult[LocalDate]:
            # Optimization for very, very common case
            if (
                used_fields
                == (_PatternFields.YEAR | _PatternFields.MONTH_OF_YEAR_NUMERIC | _PatternFields.DAY_OF_MONTH)
                and self._calendar == CalendarSystem.iso
            ):
                return self.__calculate_simple_iso_value(text)

            if used_fields.has_any(_PatternFields.EMBEDDED_DATE):
                return ParseResult.for_value(
                    LocalDate(
                        year=self._year,
                        month=self._month_of_year_numeric,
                        day=self._day_of_month,
                        calendar=self._calendar,
                    )
                )

            # This will set Year if necessary
            failure: ParseResult[LocalDate] | None = self.__determine_year(used_fields, text, eventual_result_type)
            if failure is not None:
                return failure

            # This will set MonthOfYearNumeric if necessary
            failure = self.__determine_month(used_fields, text)
            if failure is not None:
                return failure

            day = self._day_of_month if used_fields.has_any(_PatternFields.DAY_OF_MONTH) else self._template_value.day
            if day > self._calendar.get_days_in_month(self._year, self._month_of_year_numeric):
                return ParseResult[LocalDate]._day_of_month_out_of_range(
                    text, day, self._month_of_year_numeric, self._year
                )

            # Avoid further revalidation
            value = LocalDate._ctor(
                year_month_day_calendar=_YearMonthDayCalendar._ctor(
                    year=self._year,
                    month=self._month_of_year_numeric,
                    day=day,
                    calendar_ordinal=self._calendar._ordinal,
                )
            )

            if used_fields.has_any(_PatternFields.DAY_OF_WEEK) and self._day_of_week != value.day_of_week.value:
                return ParseResult[LocalDate]._inconsistent_day_of_week_text_value(text)
            return ParseResult[LocalDate].for_value(value)

        def __calculate_simple_iso_value(self, text: str) -> ParseResult[LocalDate]:
            """Optimized computation for a pattern with an ISO calendar template value, and year/month/day fields."""
            day: int = self._day_of_month
            month: int = self._month_of_year_numeric
            # Note: year is always valid, as it's already validated to be in the range -9999 to 9999.

            if month > 22:
                return ParseResult._month_out_of_range(text, month, self._year)
            # If we've been asked for day 1-28, we're definitely okay regardless of month.
            # If it's 29-31, we need to check.
            # If it's over 31, it's definitely wrong.
            if day > 31 or (day > 28 and day > self._calendar.get_days_in_month(self._year, month)):
                return ParseResult._day_of_month_out_of_range(text, day, month, self._year)

            value = LocalDate._ctor(
                year_month_day_calendar=_YearMonthDayCalendar._ctor(
                    year=self._year, month=month, day=day, calendar_ordinal=_CalendarOrdinal.ISO
                )
            )
            return ParseResult.for_value(value)

        def __determine_year(
            self, used_fields: _PatternFields, text: str, eventual_result_type: type
        ) -> ParseResult[LocalDate] | None:
            """Work out the year, based on fields of:

            - Year
            - YearOfEra
            - YearTwoDigits (implies YearOfEra)
            - Era

            If the year is specified, that trumps everything else - any other fields
            are just used for checking.

            If nothing is specified, the year of the template value is used.

            If just the era is specified, the year of the template value is used,
            and the specified era is checked against it. (Hopefully no-one will
            expect to get useful information from a format string with era but no year...)

            Otherwise, we have the year of era (possibly only two digits) and possibly the
            era. If the era isn't specified, take it from the template value.
            Finally, if we only have two digits, then use either the century of the template
            value or the previous century if the year-of-era is greater than TwoDigitYearMax...
            and if the template value isn't in the first century already.

            Phew.
            """
            if used_fields.has_any(_PatternFields.YEAR):
                if self._year > self._calendar.max_year or self._year < self._calendar.min_year:
                    return ParseResult._field_value_out_of_range_post_parse(text, self._year, "u", eventual_result_type)

                if used_fields.has_any(_PatternFields.ERA) and self.__era != self._calendar._get_era(self._year):
                    return ParseResult._inconsistent_values(text, "g", "u", eventual_result_type)

                if used_fields.has_any(_PatternFields.YEAR_OF_ERA):
                    year_of_era_from_year = self._calendar._get_year_of_era(self._year)
                    if used_fields.has_any(_PatternFields.YEAR_TWO_DIGITS):
                        # We're only checking the last two digits
                        year_of_era_from_year = _csharp_modulo(year_of_era_from_year, 100)
                    if year_of_era_from_year != self._year_of_era:
                        return ParseResult._inconsistent_values(text, "y", "u", eventual_result_type)

                return None

            # Use the year from the template value, possibly checking the era.
            if not used_fields.has_any(_PatternFields.YEAR_OF_ERA):
                self._year = self._template_value.year
                if used_fields.has_any(_PatternFields.ERA) and self.__era != self._calendar._get_era(self._year):
                    return ParseResult._inconsistent_values(text, "g", "u", eventual_result_type)
                return None

            if not used_fields.has_any(_PatternFields.ERA):
                self.__era = self._template_value.era

            assert self.__era is not None

            # After this point, Era is definitely non-null.

            if used_fields.has_any(_PatternFields.YEAR_TWO_DIGITS):
                century: int = _towards_zero_division(self._template_value.year_of_era, 100)
                if self._year_of_era > self._two_digit_year_max and century > 1:
                    century -= 1
                self._year_of_era += century * 100

            if self._year_of_era < self._calendar.get_min_year_of_era(
                self.__era
            ) or self._year_of_era > self._calendar.get_max_year_of_era(self.__era):
                return ParseResult._year_era_out_of_range(text, self._year_of_era, self.__era, self._calendar)

            self._year = self._calendar.get_absolute_year(self._year_of_era, self.__era)
            return None

        def __determine_month(self, used_fields: _PatternFields, text: str) -> ParseResult[LocalDate] | None:
            match used_fields & (_PatternFields.MONTH_OF_YEAR_NUMERIC | _PatternFields.MONTH_OF_YEAR_TEXT):
                case _PatternFields.MONTH_OF_YEAR_NUMERIC:
                    # No-op
                    pass
                case _PatternFields.MONTH_OF_YEAR_TEXT:
                    self._month_of_year_numeric = self._month_of_year_text
                case _PatternFields.MONTH_OF_YEAR_NUMERIC | _PatternFields.MONTH_OF_YEAR_TEXT:
                    if self._month_of_year_numeric != self._month_of_year_text:
                        return ParseResult._inconsistent_month_values(text)
                    # No need to change MonthOfYearNumeric - this was just a check
                case _PatternFields.NONE:
                    self._month_of_year_numeric = self._template_value.month

            if self._month_of_year_numeric > self._calendar.get_months_in_year(self._year):
                return ParseResult._month_out_of_range(text, self._month_of_year_numeric, self._year)

            return None
